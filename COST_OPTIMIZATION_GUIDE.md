# 💰 AWS Cost Optimization Guide for CampsHub360

## 🎯 Cost Optimization Strategies

### **1. Right-Sizing Your Infrastructure**

#### **Start Small, Scale Up**
```bash
# Development Environment (Free Tier Eligible)
ECS: 1 task × 0.5 vCPU/1GB RAM = $15/month
RDS: db.t3.micro = $15/month
Redis: cache.t3.micro = $15/month
Total: ~$45/month

# Production Environment (Recommended)
ECS: 3 tasks × 2 vCPU/4GB RAM = $60/month
RDS: db.t3.medium = $45/month
Redis: cache.t3.micro = $15/month
Total: ~$175/month

# High-Traffic Environment
ECS: 5 tasks × 4 vCPU/8GB RAM = $200/month
RDS: db.r5.large = $180/month
Redis: cache.r5.large = $80/month
Total: ~$485/month
```

#### **Auto-Scaling Configuration**
```json
{
  "minCapacity": 2,
  "maxCapacity": 10,
  "targetTrackingScalingPolicies": [
    {
      "targetValue": 70.0,
      "scaleOutCooldown": 300,
      "scaleInCooldown": 300,
      "metricType": "ECSServiceAverageCPUUtilization"
    }
  ]
}
```

### **2. Reserved Instances & Savings Plans**

#### **RDS Reserved Instances**
```bash
# 1-Year Term (30% savings)
db.t3.medium: $45/month → $32/month (Save $13/month)
db.r5.large: $180/month → $126/month (Save $54/month)

# 3-Year Term (50% savings)
db.t3.medium: $45/month → $23/month (Save $22/month)
db.r5.large: $180/month → $90/month (Save $90/month)
```

#### **ECS Fargate Savings Plans**
```bash
# Compute Savings Plans (up to 17% savings)
$100/month commitment → Save $17/month
$500/month commitment → Save $85/month
```

### **3. Storage Optimization**

#### **S3 Intelligent Tiering**
```bash
# Automatic cost optimization
Standard → IA (30 days) → Glacier (90 days) → Deep Archive (365 days)
Savings: 40-68% on storage costs
```

#### **Database Storage**
```bash
# RDS Storage Optimization
- Use gp3 instead of gp2 (20% cheaper)
- Enable storage autoscaling
- Regular cleanup of old data
- Compress large tables
```

### **4. Network Cost Optimization**

#### **Data Transfer Optimization**
```bash
# Use CloudFront for static content
- Reduces origin server load
- Reduces data transfer costs
- Improves performance globally

# VPC Endpoints for AWS Services
- Reduces NAT Gateway costs
- Improves security
- Reduces data transfer charges
```

#### **ALB Optimization**
```bash
# Use Application Load Balancer efficiently
- Enable connection draining
- Use health checks to remove unhealthy targets
- Consider Network Load Balancer for high throughput
```

### **5. Monitoring and Alerting**

#### **Cost Monitoring Setup**
```bash
# Create billing alerts
aws budgets create-budget \
    --account-id $(aws sts get-caller-identity --query Account --output text) \
    --budget '{
        "BudgetName": "CampsHub360-Monthly",
        "BudgetLimit": {
            "Amount": "200",
            "Unit": "USD"
        },
        "TimeUnit": "MONTHLY",
        "BudgetType": "COST",
        "CostFilters": {
            "Service": ["Amazon Elastic Compute Cloud", "Amazon Relational Database Service", "Amazon ElastiCache"]
        }
    }'
```

#### **Cost Anomaly Detection**
```bash
# Enable Cost Anomaly Detection
aws ce create-anomaly-monitor \
    --anomaly-monitor '{
        "AnomalyMonitorName": "CampsHub360-Anomaly-Monitor",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE"
    }'
```

## 📊 Cost Breakdown by Service

### **Monthly Cost Analysis**

| Service | Configuration | Cost | Optimization | Optimized Cost |
|---------|---------------|------|--------------|----------------|
| **ECS Fargate** | 3 × 2vCPU/4GB | $60 | Reserved Capacity | $50 |
| **RDS PostgreSQL** | db.t3.medium | $45 | Reserved Instance | $32 |
| **ElastiCache Redis** | cache.t3.micro | $15 | - | $15 |
| **Application Load Balancer** | Standard | $20 | - | $20 |
| **CloudFront CDN** | 100GB transfer | $10 | Intelligent Tiering | $8 |
| **Route 53** | Hosted zone | $5 | - | $5 |
| **S3** | 50GB storage | $5 | Intelligent Tiering | $3 |
| **Data Transfer** | Inter-AZ + Internet | $15 | VPC Endpoints | $10 |
| **CloudWatch** | Logs + Metrics | $10 | Log retention | $5 |
| **Secrets Manager** | 2 secrets | $2 | - | $2 |
| **Total** | | **$187** | | **$150** |

### **Annual Cost Comparison**

| Scenario | Monthly Cost | Annual Cost | 3-Year Cost |
|----------|--------------|-------------|-------------|
| **Pay-as-you-go** | $187 | $2,244 | $6,732 |
| **With Optimizations** | $150 | $1,800 | $5,400 |
| **With Reserved Instances** | $120 | $1,440 | $4,320 |
| **Savings** | $67/month | $804/year | $2,412/3-years |

## 🛠️ Implementation Steps

### **Step 1: Enable Cost Monitoring**
```bash
# Create cost budget
./scripts/create-budget.sh

# Set up billing alerts
./scripts/setup-billing-alerts.sh

# Enable cost anomaly detection
./scripts/enable-anomaly-detection.sh
```

### **Step 2: Implement Auto-Scaling**
```bash
# Update ECS service with auto-scaling
aws ecs update-service \
    --cluster campushub-cluster \
    --service campushub-service \
    --desired-count 2

# Create auto-scaling policy
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/campushub-cluster/campushub-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10
```

### **Step 3: Optimize Storage**
```bash
# Enable S3 Intelligent Tiering
aws s3api put-bucket-intelligent-tiering-configuration \
    --bucket campushub-media \
    --id EntireBucket \
    --intelligent-tiering-configuration '{
        "Id": "EntireBucket",
        "Status": "Enabled",
        "Tierings": [
            {
                "Days": 30,
                "AccessTier": "ARCHIVE_ACCESS"
            },
            {
                "Days": 90,
                "AccessTier": "DEEP_ARCHIVE_ACCESS"
            }
        ]
    }'
```

### **Step 4: Purchase Reserved Instances**
```bash
# Purchase RDS Reserved Instance
aws rds purchase-reserved-db-instances-offering \
    --reserved-db-instances-offering-id 12345678-1234-1234-1234-123456789012 \
    --reserved-db-instance-id campushub-db-reserved \
    --db-instance-count 1
```

## 📈 Performance vs Cost Optimization

### **Cost-Performance Matrix**

| Configuration | Monthly Cost | Concurrent Users | RPS | Response Time | Use Case |
|---------------|--------------|------------------|-----|---------------|----------|
| **Development** | $45 | 100-500 | 100-500 | <500ms | Testing, Development |
| **Small Production** | $120 | 1,000-3,000 | 1,000-3,000 | <300ms | Small Campus |
| **Medium Production** | $175 | 5,000-10,000 | 5,000-8,000 | <200ms | Medium Campus |
| **Large Production** | $300 | 10,000-20,000 | 8,000-15,000 | <150ms | Large Campus |
| **Enterprise** | $485 | 20,000-50,000 | 15,000-25,000 | <100ms | University |

### **Scaling Recommendations**

#### **When to Scale Up:**
- CPU utilization consistently > 70%
- Memory utilization consistently > 80%
- Response time > 200ms (95th percentile)
- Error rate > 1%

#### **When to Scale Down:**
- CPU utilization consistently < 30%
- Memory utilization consistently < 50%
- Low traffic during off-peak hours
- Cost optimization needed

## 🔧 Cost Optimization Scripts

### **Daily Cost Check Script**
```bash
#!/bin/bash
# daily-cost-check.sh

# Get current month costs
CURRENT_COST=$(aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
    --output text)

# Check if cost exceeds budget
BUDGET_LIMIT=200
if (( $(echo "$CURRENT_COST > $BUDGET_LIMIT" | bc -l) )); then
    echo "⚠️ Monthly cost ($CURRENT_COST) exceeds budget ($BUDGET_LIMIT)"
    # Send alert notification
    aws sns publish \
        --topic-arn arn:aws:sns:us-east-1:account:cost-alerts \
        --message "CampsHub360 monthly cost ($CURRENT_COST) exceeds budget ($BUDGET_LIMIT)"
fi
```

### **Resource Cleanup Script**
```bash
#!/bin/bash
# resource-cleanup.sh

# Clean up old CloudWatch logs
aws logs describe-log-groups --query 'logGroups[?creationTime<`'$(date -d '30 days ago' +%s)'`].logGroupName' --output text | xargs -I {} aws logs delete-log-group --log-group-name {}

# Clean up old S3 objects
aws s3api list-objects-v2 --bucket campushub-media --query 'Contents[?LastModified<`'$(date -d '90 days ago' --iso-8601)'`].Key' --output text | xargs -I {} aws s3 rm s3://campushub-media/{}

# Clean up old ECR images
aws ecr list-images --repository-name campushub --filter tagStatus=UNTAGGED --query 'imageIds[*]' --output json | jq -r '.[] | @base64' | while read image; do
    aws ecr batch-delete-image --repository-name campushub --image-ids "$(echo $image | base64 -d)"
done
```

## 📊 Cost Monitoring Dashboard

### **Key Metrics to Track**
1. **Daily/Monthly Costs** by service
2. **Cost per user** (total cost / active users)
3. **Resource utilization** (CPU, Memory, Storage)
4. **Data transfer costs**
5. **Reserved Instance utilization**

### **Cost Alerts Setup**
```bash
# Create SNS topic for cost alerts
aws sns create-topic --name cost-alerts

# Subscribe to email notifications
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:account:cost-alerts \
    --protocol email \
    --notification-endpoint admin@yourdomain.com

# Create CloudWatch alarm for high costs
aws cloudwatch put-metric-alarm \
    --alarm-name "High-Monthly-Cost" \
    --alarm-description "Alert when monthly cost exceeds $200" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 200 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions arn:aws:sns:us-east-1:account:cost-alerts
```

## 🎯 Best Practices Summary

### **Immediate Actions (Week 1)**
1. ✅ Set up billing alerts and budgets
2. ✅ Enable auto-scaling for ECS services
3. ✅ Configure S3 Intelligent Tiering
4. ✅ Set up cost monitoring dashboard

### **Short-term Optimizations (Month 1)**
1. ✅ Purchase RDS Reserved Instances
2. ✅ Implement VPC endpoints
3. ✅ Optimize CloudWatch log retention
4. ✅ Set up automated resource cleanup

### **Long-term Optimizations (Quarter 1)**
1. ✅ Purchase ECS Savings Plans
2. ✅ Implement database optimization
3. ✅ Set up cost anomaly detection
4. ✅ Regular cost reviews and optimization

### **Ongoing Monitoring**
1. ✅ Weekly cost reviews
2. ✅ Monthly resource right-sizing
3. ✅ Quarterly reserved instance planning
4. ✅ Annual cost optimization assessment

---

## 💡 Pro Tips

1. **Start with the free tier** for development and testing
2. **Use spot instances** for non-critical workloads
3. **Implement proper tagging** for cost allocation
4. **Regular cleanup** of unused resources
5. **Monitor and optimize** continuously
6. **Use AWS Cost Explorer** for detailed analysis
7. **Consider multi-region** for disaster recovery only
8. **Implement proper caching** to reduce database costs

**Remember: The goal is to optimize costs while maintaining performance and reliability!**
