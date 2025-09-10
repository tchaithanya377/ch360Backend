import os
import time
import json
import random
import string
from dataclasses import dataclass
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import subprocess
import sys
from pathlib import Path


"""
Accounts API simple test runner (RBAC + performance), written for clarity.

What this script does:
- Registers N test users
- Ensures roles exist and grants your admin the Admin role
- Logs in as admin and exercises Admin-only endpoints
- Checks RBAC (403 for normal user, 200 after role assignment)
- Measures simple latencies (avg/p50/p95/p99)

How to run (Windows PowerShell):
  $env:BASE_URL="http://localhost:8000"; `
  $env:USERS_COUNT="20"; `
  $env:ADMIN_EMAIL="admin"; `
  $env:ADMIN_PASSWORD="123456"; `
  .\.venv\Scripts\python scripts\accounts_api_test.py

Config via env vars:
- BASE_URL (default http://localhost:8000)
- USERS_COUNT (default 120)
- ADMIN_EMAIL, ADMIN_PASSWORD (defaults admin/123456)
"""


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
API_AUTH_TOKEN = f"{BASE_URL}/api/auth/token/"
API_REGISTER = f"{BASE_URL}/api/accounts/register/"
API_ME = f"{BASE_URL}/api/accounts/me/"
API_ROLES_PERMS = f"{BASE_URL}/api/accounts/me/roles-permissions/"
API_USERS = f"{BASE_URL}/api/accounts/users/"
API_ASSIGN_ROLE = f"{BASE_URL}/api/accounts/roles/assign/"
API_REVOKE_ROLE = f"{BASE_URL}/api/accounts/roles/revoke/"
API_ROLES_CATALOG = f"{BASE_URL}/api/accounts/roles/catalog/"

# Project root detection (assumes this file is in scripts/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANAGE_PY = PROJECT_ROOT / "manage.py"


INDIAN_UNI_ROLES = [
    # Core governance and administration
    "Admin", "Registrar", "Deputy Registrar", "Controller of Examinations",
    "Assistant Registrar", "Dean", "Associate Dean",
    # Academics
    "HOD", "Program Coordinator", "Faculty", "Visiting Faculty", "Teaching Assistant",
    # Student roles
    "Student", "Class Representative", "Research Scholar",
    # Services
    "Librarian", "Library Assistant", "IT Support", "Network Admin",
    # Finance and fees
    "Finance Officer", "Accounts Clerk",
    # Examination cell
    "Exam Cell Staff",
    # Placement and industry relations
    "Placement Officer", "Training Coordinator",
    # Hostel and transport
    "Hostel Warden", "Assistant Warden", "Transport Manager",
]


@dataclass
class LatencyStats:
    avg_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    count: int


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    k = int(round((p / 100.0) * (len(values_sorted) - 1)))
    return values_sorted[k]


def summarize_latencies(samples_ms: List[float]) -> LatencyStats:
    if not samples_ms:
        return LatencyStats(0, 0, 0, 0, 0)
    return LatencyStats(
        avg_ms=sum(samples_ms) / len(samples_ms),
        p50_ms=_percentile(samples_ms, 50),
        p95_ms=_percentile(samples_ms, 95),
        p99_ms=_percentile(samples_ms, 99),
        count=len(samples_ms),
    )


def auth_token(identifier: str, password: str) -> str:
    # Backend expects 'email' as the USERNAME_FIELD. Our API accepts email or username,
    # but serializer may still require the 'email' field. Send both to be safe.
    payload = {"email": identifier, "username": identifier, "password": password}
    resp = requests.post(API_AUTH_TOKEN, json=payload, timeout=30)
    if resp.status_code != 200:
        try:
            print("Token error:", resp.status_code, resp.text[:500])
        except Exception:
            pass
        resp.raise_for_status()
    return resp.json()["access"]


def register_user(email: str, password: str, username: str) -> requests.Response:
    return requests.post(API_REGISTER, json={"email": email, "password": password, "username": username}, timeout=30)


def bearer(session: requests.Session, token: str):
    session.headers.update({"Authorization": f"Bearer {token}"})


def rand_email() -> str:
    return f"user_{''.join(random.choices(string.ascii_lowercase+string.digits, k=10))}@example.edu"


def time_call(fn, *args, **kwargs) -> Tuple[float, requests.Response]:
    t0 = time.perf_counter()
    resp = fn(*args, **kwargs)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0, resp


# ---------- Pretty printing helpers ----------

def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_kv(key: str, value):
    print(f"- {key}: {value}")


def list_users(session: requests.Session) -> requests.Response:
    return session.get(API_USERS, timeout=30)


def assign_role(session: requests.Session, user_id: str, role_name: str) -> requests.Response:
    return session.post(API_ASSIGN_ROLE, json={"user_id": user_id, "role": role_name}, timeout=30)


def revoke_role(session: requests.Session, user_id: str, role_name: str) -> requests.Response:
    return session.post(API_REVOKE_ROLE, json={"user_id": user_id, "role": role_name}, timeout=30)


def roles_catalog(session: requests.Session) -> requests.Response:
    return session.get(API_ROLES_CATALOG, timeout=30)


def me_roles_perms(session: requests.Session) -> requests.Response:
    return session.get(API_ROLES_PERMS, timeout=30)


def run_manage(*args: str) -> tuple[int, str, str]:
    """Run a manage.py command using current Python executable.
    Returns (code, stdout, stderr).
    """
    cmd = [sys.executable, str(MANAGE_PY), *args]
    try:
        p = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as exc:
        return 1, "", f"run_manage error: {exc}"


def bootstrap_roles_and_assign_admin(admin_identifier: str) -> None:
    """Best-effort: seed RBAC roles and grant Admin role to the admin user.
    Requires management command 'seed_rbac' present in the project.
    """
    # Seed roles if command exists
    code, out, err = run_manage("help")
    if code == 0 and "seed_rbac" in out + err:
        run_manage("seed_rbac")
    # Assign Admin role to provided admin (by username or email)
    py = (
        "from django.contrib.auth import get_user_model;"
        "from accounts.models import Role, UserRole;"
        "U=get_user_model();"
        f"u=U.objects.filter(email='{admin_identifier}').first() or U.objects.filter(username='{admin_identifier}').first();"
        "print('admin_found', bool(u));"
        "r,_=Role.objects.get_or_create(name='Admin', defaults={'description':'System administrator'});"
        "print('role', r.name);"
        "print('assigned', bool(u and UserRole.objects.get_or_create(user=u, role=r)[1]));"
    )
    run_manage("shell", "-c", py)


def main():
    users_count = int(os.getenv("USERS_COUNT", "120"))
    # Defaults for local testing per request (admin/123456)
    admin_email = os.getenv("ADMIN_EMAIL", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "123456")

    print_section("Configuration")
    print_kv("BASE_URL", BASE_URL)
    print_kv("USERS_COUNT", users_count)

    # 1) Register users (serially but measured)
    print_section("1) Register test users")
    passwords = {}
    register_lat = []
    user_ids: List[str] = []
    for _ in range(users_count):
        email = rand_email()
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        username = email.split('@')[0]
        dt_ms, resp = time_call(register_user, email, password, username)
        register_lat.append(dt_ms)
        if resp.status_code not in (200, 201):
            print(f"Register failed {resp.status_code}: {resp.text[:200]}")
            continue
        user = resp.json()
        passwords[user["email"]] = password
        user_ids.append(user["id"])
    print_kv("Registered", len(user_ids))
    reg_stats = summarize_latencies(register_lat)
    print_kv("Register avg(ms)", f"{reg_stats.avg_ms:.1f}")
    print_kv("Register p50/p95/p99(ms)", f"{reg_stats.p50_ms:.1f}/{reg_stats.p95_ms:.1f}/{reg_stats.p99_ms:.1f}")

    # 2) Admin login
    print_section("2) Admin login & role bootstrap")
    # Ensure roles exist and admin has Admin role (best-effort)
    bootstrap_roles_and_assign_admin(admin_email)
    admin_token = auth_token(admin_email, admin_password)
    admin_sess = requests.Session()
    bearer(admin_sess, admin_token)

    # 3) Users list (sanity) and roles catalog
    dt_ms, resp = time_call(list_users, admin_sess)
    print_kv("GET /accounts/users status", f"{resp.status_code} ({dt_ms:.1f}ms)")

    dt_ms, resp = time_call(roles_catalog, admin_sess)
    print_kv("GET /accounts/roles/catalog status", f"{resp.status_code} ({dt_ms:.1f}ms)")
    existing_roles = set()
    if resp.status_code == 200:
        try:
            payload = resp.json()
            for r in payload.get("roles", []):
                existing_roles.add(r["name"]) if isinstance(r, dict) else existing_roles.add(str(r))
        except Exception:
            pass

    # 4) Concurrent auth + roles-perms fetch to gauge steady-state latency
    print_section("3) /me/roles-permissions latency (concurrent)")
    sample_emails = list(passwords.keys())[:50]
    lat_auth = []
    lat_roles = []
    def worker(email: str):
        token = auth_token(email, passwords[email])
        sess = requests.Session()
        bearer(sess, token)
        t, r = time_call(me_roles_perms, sess)
        return t

    with ThreadPoolExecutor(max_workers=20) as exe:
        futures = [exe.submit(worker, e) for e in sample_emails]
        for fut in as_completed(futures):
            try:
                lat_roles.append(fut.result())
            except Exception as e:
                print("roles-perms error:", e)

    roles_stats = summarize_latencies(lat_roles)
    print_kv("avg(ms)", f"{roles_stats.avg_ms:.1f}")
    print_kv("p50/p95/p99(ms)", f"{roles_stats.p50_ms:.1f}/{roles_stats.p95_ms:.1f}/{roles_stats.p99_ms:.1f}")

    # 5) Role/permission enforcement check for a sample user
    # Pick the first registered user and verify access control works
    if not user_ids:
        print("No registered users to test RBAC; exiting.")
        return
    sample_user_email = list(passwords.keys())[0]
    sample_user_pwd = passwords[sample_user_email]
    print_section("4) RBAC sanity (403 -> assign Admin -> 200)")
    print_kv("Sample user", sample_user_email)

    # Login as the sample user
    sample_token = auth_token(sample_user_email, sample_user_pwd)
    sample_sess = requests.Session()
    bearer(sample_sess, sample_token)

    # Try to access admin-only endpoint (should be 403)
    t, r = time_call(list_users, sample_sess)
    if r.status_code == 200:
        print_kv("RBAC", "WARNING: user has access without role (unexpected)")
    else:
        print_kv("Without role status", r.status_code)

    # Assign Admin role (if present), then try again
    if "Admin" in existing_roles:
        # Find the user's id
        # We captured ids as returned from register; map email->id if available
        # If not, fetch users and match by email
        sample_user_id = None
        if user_ids:
            # We registered in order; try to look up by calling users list
            pass
        # Simple lookup from admin list
        resp_list = admin_sess.get(API_USERS, timeout=30)
        try:
            data = resp_list.json()
            for item in data:
                if isinstance(item, dict) and item.get("email") == sample_user_email:
                    sample_user_id = item.get("id")
                    break
        except Exception:
            sample_user_id = None
        # Fall back to registration return if mapping existed
        if not sample_user_id and user_ids:
            sample_user_id = user_ids[0]

        if sample_user_id:
            t, r = time_call(assign_role, admin_sess, sample_user_id, "Admin")
            print_kv("Assign Admin", r.status_code)
            # New token to ensure fresh claims aren't required (backend checks DB each request)
            sample_token2 = auth_token(sample_user_email, sample_user_pwd)
            sample_sess2 = requests.Session()
            bearer(sample_sess2, sample_token2)
            t, r = time_call(list_users, sample_sess2)
            print_kv("After Admin role status", r.status_code)
        else:
            print("Could not resolve sample user id to assign role; skipping post-assign check.")
    else:
        print_kv("RBAC", "Role 'Admin' not present; skipping")

    # 6) Role matrix check: assign one distinct role per user and verify access
    # Expectation with current backend: only 'Admin' role can access /accounts/users/ (HasRole required_roles=['Admin'])
    if existing_roles:
        print_section("5) Role matrix (expect 200 only for Admin)")
        # Map roles deterministically across first len(existing_roles) users
        role_list = sorted(list(existing_roles))
        for idx, role_name in enumerate(role_list):
            if idx >= len(user_ids):
                break
            uid = user_ids[idx]
            # assign role
            _t, _r = time_call(assign_role, admin_sess, uid, role_name)
            # login as that user
            # we need that user's email
            # find email by querying admin users list and matching id
            email_for_uid = None
            al = admin_sess.get(API_USERS, timeout=30)
            try:
                for item in al.json():
                    if str(item.get('id')) == str(uid):
                        email_for_uid = item.get('email')
                        break
            except Exception:
                pass
            if not email_for_uid:
                continue
            try:
                tok = auth_token(email_for_uid, passwords[email_for_uid])
            except Exception:
                continue
            sess_r = requests.Session()
            bearer(sess_r, tok)
            tlat, resp_r = time_call(list_users, sess_r)
            status = resp_r.status_code
            ok_expected = (role_name == 'Admin')
            print_kv(f"Role={role_name}", f"status {status} (expected {'200' if ok_expected else '403'})")

    # 7) Assign roles to first K users (best-effort, skip missing roles)
    print_section("6) Bulk assign & revoke (best-effort)")
    assign_lat = []
    for i, uid in enumerate(user_ids[:30]):
        role = INDIAN_UNI_ROLES[i % len(INDIAN_UNI_ROLES)]
        if existing_roles and (role not in existing_roles):
            continue
        t, r = time_call(assign_role, admin_sess, uid, role)
        assign_lat.append(t)
    if assign_lat:
        astats = summarize_latencies(assign_lat)
        print_kv("Assign role avg/p95(ms)", f"{astats.avg_ms:.1f}/{astats.p95_ms:.1f}")

    # 8) Revoke roles for first 10 users (best-effort)
    revoke_lat = []
    for i, uid in enumerate(user_ids[:10]):
        role = INDIAN_UNI_ROLES[i % len(INDIAN_UNI_ROLES)]
        if existing_roles and (role not in existing_roles):
            continue
        t, r = time_call(revoke_role, admin_sess, uid, role)
        revoke_lat.append(t)
    if revoke_lat:
        rstats = summarize_latencies(revoke_lat)
        print_kv("Revoke role avg/p95(ms)", f"{rstats.avg_ms:.1f}/{rstats.p95_ms:.1f}")

    print_section("Done")


if __name__ == "__main__":
    main()


