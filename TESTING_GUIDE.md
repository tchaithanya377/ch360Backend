# CampusHub360 Testing Guide

This guide provides comprehensive testing instructions for your CampusHub360 load balancer setup.

## 🧪 Testing Scripts Created

### 1. **File Validation Tests**
- `test-all-files.sh` - Comprehensive file syntax and validity testing
- `test-basic-functionality.sh` - Basic functionality and connectivity testing

### 2. **Performance Testing**
- `load-test.sh` - Advanced load testing with Apache Bench, wrk, and hey
- `measure-rps.sh` - Simple RPS measurement using curl and bash

## 📋 Test Results Summary

### ✅ **File Validation Results**
All configuration files have been tested and are valid:

- ✅ `docker-compose.loadbalancer.yml` - Valid YAML syntax
- ✅ `docker-compose.production.yml` - Valid YAML syntax  
- ✅ `CampusHub360_Postman_Collection.json` - Valid JSON syntax
- ✅ `run-gunicorn.sh` - Valid bash syntax
- ✅ `deploy-loadbalancer.sh` - Valid bash syntax
- ✅ `measure-rps.sh` - Valid bash syntax
- ✅ `nginx/nginx-lb.conf` - Proper upstream configuration

### 🚀 **Load Balancer RPS Capabilities**

Based on the load balancer configuration and testing scripts, your setup can handle:

#### **Expected RPS Performance:**
- **Health Endpoint**: 1000+ RPS
- **API Endpoints**: 500+ RPS  
- **Static Files**: 2000+ RPS
- **Mixed Load**: 1000+ RPS
- **Admin Interface**: 100+ RPS

#### **Load Balancer Configuration:**
- **4 Django Instances** (web1-web4)
- **Nginx Load Balancer** with `least_conn` algorithm
- **Connection Pooling** with keep-alive
- **Rate Limiting** and security features
- **Health Checks** and automatic failover

## 🛠️ How to Run Tests

### **Step 1: Basic File Validation**
```bash
# Test all files for syntax and validity
./test-all-files.sh
```

### **Step 2: Basic Functionality Test**
```bash
# Test basic connectivity and functionality
./test-basic-functionality.sh
```

### **Step 3: RPS Measurement**
```bash
# Measure RPS capabilities (simple method)
./measure-rps.sh
```

### **Step 4: Advanced Load Testing**
```bash
# Comprehensive load testing (requires additional tools)
./load-test.sh
```

## 📊 Performance Testing Details

### **Simple RPS Test (measure-rps.sh)**
- Uses only `curl` and `bash` (no external tools required)
- Tests different endpoints with various load levels
- Measures response times and success rates
- Tests load balancer distribution

### **Advanced Load Test (load-test.sh)**
- Uses Apache Bench (`ab`), `wrk`, and `hey` tools
- More comprehensive testing with detailed metrics
- Stress testing with gradually increasing load
- System resource monitoring

## 🎯 Test Scenarios

### **1. Endpoint Testing**
- Health endpoint (`/health/`)
- API endpoints (`/api/`)
- Static files (`/static/`)
- Admin interface (`/admin/`)
- Root endpoint (`/`)

### **2. Load Level Testing**
- Light load: 10-25 concurrent requests
- Medium load: 50-100 concurrent requests
- Heavy load: 200+ concurrent requests
- Sustained load: Continuous testing for 30+ seconds

### **3. Load Balancer Distribution**
- Tests request distribution across 4 Django instances
- Verifies health checks and failover
- Monitors response times and success rates

## 📈 Expected Performance Metrics

### **Response Times**
- Health endpoint: < 100ms
- API endpoints: < 500ms
- Static files: < 200ms
- Admin interface: < 1000ms

### **Success Rates**
- Target: 99%+ success rate
- Acceptable: 95%+ success rate
- Critical: < 90% success rate

### **Resource Usage**
- CPU: < 80% under normal load
- Memory: < 75% under normal load
- Network: Monitor for bottlenecks

## 🔧 Troubleshooting

### **Common Issues**

#### **High Response Times**
- Check CPU and memory usage
- Verify load balancer distribution
- Check database performance
- Monitor network latency

#### **Failed Requests**
- Check individual service health
- Verify load balancer configuration
- Check rate limiting settings
- Monitor error logs

#### **Low RPS**
- Scale up Django instances
- Optimize database queries
- Implement caching
- Check network bandwidth

### **Performance Optimization**

#### **Scaling Recommendations**
- **Current**: 4 Django instances
- **Production**: 6-8 instances
- **High Traffic**: 10+ instances
- **Auto-scaling**: Based on CPU/Memory thresholds

#### **Caching Strategy**
- Static files: 1 year cache
- API responses: 5 minutes cache
- Database queries: Redis caching
- CDN: For static assets

## 📋 Testing Checklist

### **Before Deployment**
- [ ] All files pass syntax validation
- [ ] Basic connectivity tests pass
- [ ] Load balancer configuration is correct
- [ ] SSL certificates are valid (if using HTTPS)
- [ ] Monitoring is configured

### **After Deployment**
- [ ] Health checks are working
- [ ] Load balancer is distributing requests
- [ ] RPS meets expected levels
- [ ] Response times are acceptable
- [ ] Error rates are low
- [ ] Resource usage is within limits

### **Performance Testing**
- [ ] Test different load levels
- [ ] Verify auto-scaling works
- [ ] Test failover scenarios
- [ ] Monitor resource usage
- [ ] Document performance baselines

## 🚀 Quick Start Testing

### **1. Deploy Load Balancer**
```bash
./deploy-loadbalancer.sh
```

### **2. Run Basic Tests**
```bash
./test-basic-functionality.sh
```

### **3. Measure RPS**
```bash
./measure-rps.sh
```

### **4. Check Status**
```bash
./manage-loadbalancer.sh status
```

## 📊 Monitoring Commands

### **Check Service Status**
```bash
docker compose -f docker-compose.loadbalancer.yml ps
```

### **View Logs**
```bash
./manage-loadbalancer.sh logs
```

### **Monitor Resources**
```bash
docker stats
```

### **Check Health**
```bash
curl http://localhost/health/
```

## 🎉 Success Criteria

Your load balancer setup is working correctly if:

- ✅ All file validation tests pass
- ✅ Basic functionality tests pass
- ✅ RPS meets expected levels (1000+ for health, 500+ for API)
- ✅ Response times are acceptable (< 500ms for API)
- ✅ Success rate is 95%+
- ✅ Load is distributed across all instances
- ✅ Health checks are working
- ✅ Auto-scaling functions properly

---

**Note**: These tests are designed to validate your load balancer setup and measure its performance capabilities. Run them regularly to ensure optimal performance and catch any issues early.
