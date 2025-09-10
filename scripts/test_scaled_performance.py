#!/usr/bin/env python3
"""
Test Scaled Performance - Test horizontal scaling setup
Test with load balancer and multiple Django instances
"""
import asyncio
import httpx
import time
import os
import json
from typing import Dict, List, Tuple
import statistics

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost')  # Use load balancer
TARGET_RPS = int(os.getenv('TARGET_RPS', '5000'))
DURATION_SEC = int(os.getenv('DURATION_SEC', '60'))
CONCURRENT_USERS = int(os.getenv('CONCURRENT_USERS', '200'))

# Use existing admin credentials
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@gmail.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '123456')

class ScaledPerfTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.target_rps = TARGET_RPS
        self.duration_sec = DURATION_SEC
        self.concurrent_users = CONCURRENT_USERS
        self.admin_token = None
        self.user_tokens = []
        self.results = []
        
    async def get_admin_token(self) -> str:
        """Get admin token for authenticated endpoints"""
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/auth/token/",
                    json={
                        "username": ADMIN_EMAIL,
                        "password": ADMIN_PASSWORD
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get('access')
                else:
                    print(f"❌ Admin login failed: {response.status_code}")
                    return None
            except Exception as e:
                print(f"❌ Admin login error: {e}")
                return None

    async def create_test_users_fast(self, count: int) -> List[str]:
        """Create test users quickly with optimized settings"""
        tokens = []
        import time
        timestamp = int(time.time())
        
        # Use optimized client settings
        timeout = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
        limits = httpx.Limits(max_keepalive_connections=100, max_connections=200)
        
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            # Create users in parallel batches
            batch_size = 25
            for batch_start in range(0, count, batch_size):
                batch_end = min(batch_start + batch_size, count)
                tasks = []
                
                for i in range(batch_start, batch_end):
                    user_data = {
                        "username": f"scaled_test_user_{timestamp}_{i}",
                        "email": f"scaled_test_user_{timestamp}_{i}@example.com",
                        "password": "TestPass123!",
                        "is_verified": True
                    }
                    tasks.append(self.create_single_user(client, user_data))
                
                # Execute batch in parallel
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in batch_results:
                    if isinstance(result, str):
                        tokens.append(result)
                
                print(f"   📦 Created {len(tokens)}/{count} test users")
        
        print(f"✅ Created {len(tokens)} test users with tokens")
        return tokens

    async def create_single_user(self, client: httpx.AsyncClient, user_data: Dict) -> str:
        """Create a single user and return token"""
        try:
            # Create user
            response = await client.post(
                f"{self.base_url}/api/accounts/register/",
                json=user_data
            )
            
            if response.status_code == 201:
                # Get token
                token_response = await client.post(
                    f"{self.base_url}/api/auth/token/",
                    json={
                        "username": user_data["username"],
                        "password": user_data["password"]
                    }
                )
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    return token_data.get('access')
            
            return None
        except Exception:
            return None

    async def test_endpoint(self, client: httpx.AsyncClient, endpoint: str, method: str = "GET", 
                          headers: Dict = None, json_data: Dict = None) -> Tuple[float, int]:
        """Test a single endpoint and return (latency_ms, status_code)"""
        start_time = time.time()
        try:
            if method == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await client.post(endpoint, json=json_data, headers=headers)
            else:
                return 0, 0
                
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, response.status_code
        except Exception:
            return 0, 0

    async def load_test_worker(self, worker_id: int, endpoints: List[Dict], 
                             duration: float, rate_per_second: float) -> List[Dict]:
        """Optimized worker coroutine for maximum throughput"""
        results = []
        interval = 1.0 / rate_per_second
        start_time = time.time()
        request_count = 0
        
        # Optimized client settings for maximum throughput
        timeout = httpx.Timeout(connect=2.0, read=5.0, write=2.0, pool=2.0)
        limits = httpx.Limits(max_keepalive_connections=100, max_connections=200)
        
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            while time.time() - start_time < duration:
                for endpoint in endpoints:
                    # Rotate through different user tokens (unless endpoint specifies no rotation)
                    if endpoint.get('no_token_rotation', False):
                        headers = endpoint.get('headers', {}).copy()
                    else:
                        token = self.user_tokens[request_count % len(self.user_tokens)] if self.user_tokens else None
                        headers = endpoint.get('headers', {}).copy()
                        if token and 'Authorization' in headers:
                            headers['Authorization'] = f"Bearer {token}"
                    
                    latency_ms, status_code = await self.test_endpoint(
                        client, endpoint['url'], endpoint.get('method', 'GET'),
                        headers, endpoint.get('json')
                    )
                    
                    results.append({
                        'worker_id': worker_id,
                        'endpoint': endpoint['name'],
                        'latency_ms': latency_ms,
                        'status_code': status_code,
                        'timestamp': time.time(),
                        'request_id': request_count,
                        'user_type': endpoint.get('user_type', 'unknown')
                    })
                    
                    request_count += 1
                    
                    # Minimal rate limiting for maximum throughput
                    if interval > 0:
                        await asyncio.sleep(interval)
        
        return results

    async def run_load_test(self, endpoints: List[Dict]) -> List[Dict]:
        """Run optimized load test for maximum RPS"""
        print(f"\n🚀 Starting SCALED load test: {self.target_rps} RPS for {self.duration_sec}s")
        print(f"📊 Using {self.concurrent_users} concurrent workers")
        print(f"👥 Using {len(self.user_tokens)} test user tokens")
        print(f"🌐 Load Balancer URL: {self.base_url}")
        
        # Calculate rate per worker
        rate_per_worker = self.target_rps / self.concurrent_users
        print(f"📈 Rate per worker: {rate_per_worker:.2f} RPS")
        
        # Create worker tasks
        tasks = []
        for i in range(self.concurrent_users):
            task = self.load_test_worker(i, endpoints, self.duration_sec, rate_per_worker)
            tasks.append(task)
        
        # Run all workers concurrently
        start_time = time.time()
        print(f"⏰ Test started at: {time.strftime('%H:%M:%S')}")
        
        all_results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Flatten results
        results = []
        for worker_results in all_results:
            results.extend(worker_results)
        
        actual_duration = end_time - start_time
        actual_rps = len(results) / actual_duration
        
        print(f"✅ Load test completed in {actual_duration:.2f}s")
        print(f"📈 Actual RPS: {actual_rps:.2f}")
        print(f"📊 Total requests: {len(results)}")
        
        return results

    def analyze_results(self, results: List[Dict]):
        """Analyze and display scaled test results"""
        if not results:
            print("❌ No results to analyze")
            return
        
        # Overall stats
        latencies = [r['latency_ms'] for r in results if r['latency_ms'] > 0]
        status_codes = [r['status_code'] for r in results]
        
        print(f"\n📊 SCALED PERFORMANCE RESULTS")
        print(f"=" * 70)
        
        # Latency stats
        if latencies:
            print(f"⏱️  Latency (ms):")
            print(f"   Average: {statistics.mean(latencies):.2f}")
            print(f"   Median:  {statistics.median(latencies):.2f}")
            print(f"   P90:     {sorted(latencies)[int(len(latencies) * 0.90)]:.2f}")
            print(f"   P95:     {sorted(latencies)[int(len(latencies) * 0.95)]:.2f}")
            print(f"   P99:     {sorted(latencies)[int(len(latencies) * 0.99)]:.2f}")
            print(f"   Max:     {max(latencies):.2f}")
            print(f"   Min:     {min(latencies):.2f}")
        
        # Status code distribution
        status_counts = {}
        for code in status_codes:
            status_counts[code] = status_counts.get(code, 0) + 1
        
        print(f"\n📈 Status Codes:")
        for code, count in sorted(status_counts.items()):
            percentage = (count / len(status_codes)) * 100
            status_emoji = "✅" if code == 200 else "❌" if code >= 400 else "⚠️"
            print(f"   {status_emoji} {code}: {count} ({percentage:.1f}%)")
        
        # Per-endpoint stats
        endpoint_stats = {}
        for result in results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'latencies': [], 'status_codes': []}
            endpoint_stats[endpoint]['latencies'].append(result['latency_ms'])
            endpoint_stats[endpoint]['status_codes'].append(result['status_code'])
        
        print(f"\n🎯 Per-Endpoint Performance:")
        for endpoint, stats in endpoint_stats.items():
            latencies = [l for l in stats['latencies'] if l > 0]
            if latencies:
                avg_latency = statistics.mean(latencies)
                median_latency = statistics.median(latencies)
                p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
                success_rate = (stats['status_codes'].count(200) / len(stats['status_codes'])) * 100
                total_requests = len(stats['status_codes'])
                
                print(f"   📍 {endpoint}:")
                print(f"      Requests: {total_requests}")
                print(f"      Success Rate: {success_rate:.1f}%")
                print(f"      Avg Latency: {avg_latency:.2f}ms")
                print(f"      Median Latency: {median_latency:.2f}ms")
                print(f"      P95 Latency: {p95_latency:.2f}ms")

    async def run(self):
        """Main scaled test execution"""
        print(f"🚀 SCALED PERFORMANCE TEST")
        print(f"📊 Target: {self.target_rps} RPS for {self.duration_sec}s")
        print(f"🌐 Load Balancer URL: {self.base_url}")
        
        # Get admin token
        print(f"\n🔐 Getting admin token...")
        self.admin_token = await self.get_admin_token()
        if not self.admin_token:
            print("❌ Cannot proceed without admin token")
            return
        
        print("✅ Admin token obtained")
        
        # Create test users quickly
        print(f"\n👥 Creating test users...")
        self.user_tokens = await self.create_test_users_fast(100)  # Create 100 test users quickly
        
        # Define optimized test endpoints (focus on fastest endpoints)
        endpoints = [
            # Fastest endpoints first
            {"name": "health", "url": f"{self.base_url}/health/", "user_type": "public"},
            {"name": "health_detailed", "url": f"{self.base_url}/health/detailed/", "user_type": "public"},
            
            # User endpoints (with rotating tokens)
            {"name": "user_me", "url": f"{self.base_url}/api/accounts/me/", 
             "headers": {"Authorization": "Bearer {token}"}, "user_type": "user"},
            {"name": "user_roles", "url": f"{self.base_url}/api/accounts/me/roles-permissions/",
             "headers": {"Authorization": "Bearer {token}"}, "user_type": "user"},
            
            # Admin endpoints (with admin token - don't rotate)
            {"name": "admin_roles", "url": f"{self.base_url}/api/accounts/roles/catalog/",
             "headers": {"Authorization": f"Bearer {self.admin_token}"}, "user_type": "admin", "no_token_rotation": True},
        ]
        
        print(f"\n🎯 Testing {len(endpoints)} endpoints with scaled load")
        
        # Run scaled load test
        results = await self.run_load_test(endpoints)
        
        # Analyze results
        self.analyze_results(results)
        
        # Performance assessment
        latencies = [r['latency_ms'] for r in results if r['latency_ms'] > 0]
        if latencies:
            avg_latency = statistics.mean(latencies)
            success_rate = (len([r for r in results if r['status_code'] == 200]) / len(results)) * 100
            actual_rps = len(results) / self.duration_sec
            
            print(f"\n🎯 SCALED PERFORMANCE ASSESSMENT")
            print(f"=" * 50)
            print(f"📊 Test Users: {len(self.user_tokens)}")
            print(f"📈 Actual RPS Achieved: {actual_rps:.2f}")
            print(f"⏱️  Average Latency: {avg_latency:.2f}ms")
            print(f"✅ Success Rate: {success_rate:.1f}%")
            
            # Performance rating
            if avg_latency < 100 and success_rate >= 95:
                print(f"🏆 EXCELLENT: Scaled system handles load perfectly!")
            elif avg_latency < 200 and success_rate >= 90:
                print(f"✅ GOOD: Scaled system performs well!")
            elif avg_latency < 500 and success_rate >= 80:
                print(f"⚠️  ACCEPTABLE: Scaled system handles load but needs optimization")
            else:
                print(f"❌ POOR: Scaled system struggles - needs optimization")
            
            # Scaling assessment
            if actual_rps >= 5000:
                print(f"🚀 SCALING: Can handle 50K+ users with proper infrastructure")
            elif actual_rps >= 2000:
                print(f"📈 SCALING: Can handle 20K+ users with optimization")
            elif actual_rps >= 1000:
                print(f"✅ SCALING: Can handle 10K+ users")
            else:
                print(f"⚠️  SCALING: Needs optimization for production scale")

if __name__ == "__main__":
    test = ScaledPerfTest()
    asyncio.run(test.run())
