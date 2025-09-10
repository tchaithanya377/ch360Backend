# 🚀 CampusHub360 API Testing Guide for Postman

## 📋 **Quick Setup (5 minutes)**

### **Step 1: Import Collection**
1. Open Postman
2. Click **Import** button
3. Select `CampusHub360_Postman_Collection.json`
4. Collection will be imported with all API endpoints

### **Step 2: Set Environment Variables**
1. Click **Environments** in left sidebar
2. Create new environment: `CampusHub360 Local`
3. Add these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | Your Django server URL |
| `access_token` | (leave empty) | Will be set after login |
| `admin_token` | (leave empty) | Will be set after admin login |
| `refresh_token` | (leave empty) | Will be set after login |
| `user_id` | (leave empty) | Will be set when needed |
| `student_id` | (leave empty) | Will be set when needed |
| `department_id` | (leave empty) | Will be set when needed |
| `program_id` | (leave empty) | Will be set when needed |

4. **Save** the environment
5. **Select** this environment in the top-right dropdown

## 🔐 **Authentication Testing**

### **Step 3: Test Admin Login**
1. Go to **Authentication** → **Login (Email)**
2. Click **Send**
3. **Expected Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "uuid-here",
        "email": "admin@gmail.com",
        "username": "admin"
    },
    "session": {
        "ip": "127.0.0.1",
        "login_at": "2025-09-10T23:30:00Z",
        "country": "Unknown",
        "region": "Unknown",
        "city": "Unknown",
        "latitude": null,
        "longitude": null
    }
}
```

4. **Copy the `access` token** and set it as `admin_token` in environment variables

### **Step 4: Test User Registration**
1. Go to **Authentication** → **Register User**
2. Modify the JSON body with unique data:
```json
{
    "username": "test_student_001",
    "email": "test_student_001@example.com",
    "password": "TestPass123!",
    "is_verified": true
}
```
3. Click **Send**
4. **Expected Response:** `201 Created` with user data

### **Step 5: Test User Login**
1. Go to **Authentication** → **Login (Username)**
2. Use the credentials from registration:
```json
{
    "username": "test_student_001",
    "password": "TestPass123!"
}
```
3. Click **Send**
4. **Copy the `access` token** and set it as `access_token` in environment variables

## 👤 **User Management Testing**

### **Step 6: Test User Profile**
1. Go to **User Management** → **Get Current User Profile**
2. Click **Send**
3. **Expected Response:** User profile data with roles and permissions

### **Step 7: Test User Sessions**
1. Go to **User Management** → **Get User Sessions**
2. Click **Send**
3. **Expected Response:** List of user login sessions with IP, location, timestamps

### **Step 8: Test Roles & Permissions**
1. Go to **Roles & Permissions** → **Get User Roles & Permissions**
2. Click **Send**
3. **Expected Response:**
```json
{
    "roles": ["Student"],
    "permissions": ["view_student", "add_student"]
}
```

## 🔧 **Admin Functions Testing**

### **Step 9: Test Admin User List**
1. Go to **Roles & Permissions** → **Get All Users (Admin Only)**
2. Click **Send**
3. **Expected Response:** List of all users in the system

### **Step 10: Test Roles Catalog**
1. Go to **Roles & Permissions** → **Get Roles Catalog (Admin Only)**
2. Click **Send**
3. **Expected Response:** Available roles and permissions

### **Step 11: Test Role Assignment**
1. Go to **Roles & Permissions** → **Assign Role to User (Admin Only)**
2. Set `user_id` in environment variables (from user registration response)
3. Click **Send**
4. **Expected Response:** Success message

## 🏥 **Health Check Testing**

### **Step 12: Test System Health**
1. Go to **Health & System** → **Health Check**
2. Click **Send**
3. **Expected Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-09-10T23:30:00Z",
    "version": "1.0.0"
}
```

### **Step 13: Test Detailed Health**
1. Go to **Health & System** → **Detailed Health Check**
2. Click **Send**
3. **Expected Response:** Detailed system status with database, cache, etc.

## 📚 **Academic Data Testing**

### **Step 14: Test Departments**
1. Go to **Departments** → **Get All Departments**
2. Click **Send**
3. **Expected Response:** List of departments
4. **Copy a department ID** and set it as `department_id` in environment variables

### **Step 15: Test Academic Programs**
1. Go to **Academic Programs** → **Get All Academic Programs**
2. Click **Send**
3. **Expected Response:** List of academic programs
4. **Copy a program ID** and set it as `program_id` in environment variables

### **Step 16: Test Students**
1. Go to **Students** → **Get All Students**
2. Click **Send**
3. **Expected Response:** List of students

### **Step 17: Test Student Creation**
1. Go to **Students** → **Create Student**
2. Click **Send**
3. **Expected Response:** Created student data
4. **Copy the student ID** and set it as `student_id` in environment variables

## 🎯 **Testing Checklist**

### **✅ Authentication Tests**
- [ ] Admin login works
- [ ] User registration works
- [ ] User login works
- [ ] Token refresh works
- [ ] Invalid credentials return 401

### **✅ User Management Tests**
- [ ] Get user profile works
- [ ] Update user profile works
- [ ] Get user sessions works
- [ ] Get active session works

### **✅ RBAC Tests**
- [ ] Get user roles/permissions works
- [ ] Admin can see all users
- [ ] Admin can assign roles
- [ ] Admin can revoke roles
- [ ] Regular users cannot access admin endpoints

### **✅ System Tests**
- [ ] Health check works
- [ ] Detailed health check works
- [ ] API health check works

### **✅ Data Tests**
- [ ] Get departments works
- [ ] Get academic programs works
- [ ] Get students works
- [ ] Create student works

## 🚨 **Common Issues & Solutions**

### **Issue: 401 Unauthorized**
**Solution:** 
- Check if token is set in environment variables
- Verify token is not expired
- Make sure Authorization header is: `Bearer {{access_token}}`

### **Issue: 403 Forbidden**
**Solution:**
- Check if user has required role/permission
- Use admin token for admin-only endpoints
- Verify RBAC is properly configured

### **Issue: 404 Not Found**
**Solution:**
- Check if Django server is running on `http://localhost:8000`
- Verify the endpoint URL is correct
- Check if the resource ID exists

### **Issue: 500 Internal Server Error**
**Solution:**
- Check Django server logs
- Verify database is running
- Check if all required data exists

## 📊 **Performance Testing**

### **Load Testing with Postman**
1. Go to **Collection Runner**
2. Select the collection
3. Set iterations to 100
4. Set delay to 0ms
5. Run the collection
6. Monitor response times and success rates

### **Expected Performance:**
- **Response Time:** < 500ms
- **Success Rate:** > 95%
- **Throughput:** 100+ requests/minute

## 🎉 **Success Indicators**

### **✅ All Tests Pass If:**
- Authentication returns valid tokens
- User management works without errors
- RBAC properly restricts access
- Health checks return "healthy"
- Data operations work correctly
- Response times are under 500ms

### **🏆 Excellent Performance If:**
- Response times under 200ms
- 100% success rate
- All endpoints respond quickly
- No authentication errors
- RBAC works perfectly

## 📝 **Notes**

- **Base URL:** Make sure Django server is running on `http://localhost:8000`
- **Admin Credentials:** `admin@gmail.com` / `123456`
- **Token Expiry:** Access tokens expire in 1 hour, refresh tokens in 7 days
- **Environment Variables:** Update them as you get responses from API calls
- **Testing Order:** Follow the steps in order for best results

**Happy Testing! 🚀**
