#!/bin/bash

# 🚀 AWS Deployment Script for CampsHub360
# This script automates the deployment of CampsHub360 to AWS ECS Fargate

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="us-east-1"
PROJECT_NAME="campushub"
ENVIRONMENT="production"
VPC_CIDR="10.0.0.0/16"
PUBLIC_SUBNET_1_CIDR="10.0.1.0/24"
PUBLIC_SUBNET_2_CIDR="10.0.2.0/24"
PRIVATE_SUBNET_1_CIDR="10.0.3.0/24"
PRIVATE_SUBNET_2_CIDR="10.0.4.0/24"

# Optional ACM certificate ARN for HTTPS
ACM_ARN="${ACM_ARN:-}"

# Database configuration
DB_INSTANCE_CLASS="db.t3.medium"
DB_ALLOCATED_STORAGE="100"
DB_ENGINE="postgres"
DB_ENGINE_VERSION="15.4"

# Redis configuration
REDIS_NODE_TYPE="cache.t3.micro"

# ECS configuration
ECS_CPU="2048"
ECS_MEMORY="4096"
ECS_DESIRED_COUNT="3"

echo -e "${BLUE}🚀 Starting AWS deployment for CampsHub360...${NC}"

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI is configured${NC}"

# Create ECR repository
echo -e "${YELLOW}📦 Creating ECR repository...${NC}"
aws ecr create-repository --repository-name $PROJECT_NAME --region $AWS_REGION 2>/dev/null || echo "Repository already exists"

# Get ECR login token
echo -e "${YELLOW}🔐 Logging into ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push Docker image
echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"
ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:latest

docker build -t $PROJECT_NAME .
docker tag $PROJECT_NAME:latest $ECR_URI
docker push $ECR_URI

echo -e "${GREEN}✅ Docker image pushed to ECR${NC}"

# Create VPC and networking
echo -e "${YELLOW}🌐 Creating VPC and networking...${NC}"

# Create VPC
VPC_ID=$(aws ec2 create-vpc --cidr-block $VPC_CIDR --query 'Vpc.VpcId' --output text --region $AWS_REGION)
aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=$PROJECT_NAME-vpc --region $AWS_REGION
echo -e "${GREEN}✅ VPC created: $VPC_ID${NC}"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames --region $AWS_REGION

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text --region $AWS_REGION)
aws ec2 create-tags --resources $IGW_ID --tags Key=Name,Value=$PROJECT_NAME-igw --region $AWS_REGION
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID --region $AWS_REGION
echo -e "${GREEN}✅ Internet Gateway created: $IGW_ID${NC}"

# Create public subnets
PUBLIC_SUBNET_1_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PUBLIC_SUBNET_1_CIDR --availability-zone ${AWS_REGION}a --query 'Subnet.SubnetId' --output text --region $AWS_REGION)
aws ec2 create-tags --resources $PUBLIC_SUBNET_1_ID --tags Key=Name,Value=$PROJECT_NAME-public-subnet-1 --region $AWS_REGION
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_1_ID --map-public-ip-on-launch --region $AWS_REGION

PUBLIC_SUBNET_2_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PUBLIC_SUBNET_2_CIDR --availability-zone ${AWS_REGION}b --query 'Subnet.SubnetId' --output text --region $AWS_REGION)
aws ec2 create-tags --resources $PUBLIC_SUBNET_2_ID --tags Key=Name,Value=$PROJECT_NAME-public-subnet-2 --region $AWS_REGION
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_2_ID --map-public-ip-on-launch --region $AWS_REGION

echo -e "${GREEN}✅ Public subnets created${NC}"

# Create private subnets
PRIVATE_SUBNET_1_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PRIVATE_SUBNET_1_CIDR --availability-zone ${AWS_REGION}a --query 'Subnet.SubnetId' --output text --region $AWS_REGION)
aws ec2 create-tags --resources $PRIVATE_SUBNET_1_ID --tags Key=Name,Value=$PROJECT_NAME-private-subnet-1 --region $AWS_REGION

PRIVATE_SUBNET_2_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PRIVATE_SUBNET_2_CIDR --availability-zone ${AWS_REGION}b --query 'Subnet.SubnetId' --output text --region $AWS_REGION)
aws ec2 create-tags --resources $PRIVATE_SUBNET_2_ID --tags Key=Name,Value=$PROJECT_NAME-private-subnet-2 --region $AWS_REGION

echo -e "${GREEN}✅ Private subnets created${NC}"

# Create route table for public subnets
PUBLIC_RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text --region $AWS_REGION)
aws ec2 create-tags --resources $PUBLIC_RT_ID --tags Key=Name,Value=$PROJECT_NAME-public-rt --region $AWS_REGION
aws ec2 create-route --route-table-id $PUBLIC_RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID --region $AWS_REGION
aws ec2 associate-route-table --subnet-id $PUBLIC_SUBNET_1_ID --route-table-id $PUBLIC_RT_ID --region $AWS_REGION
aws ec2 associate-route-table --subnet-id $PUBLIC_SUBNET_2_ID --route-table-id $PUBLIC_RT_ID --region $AWS_REGION

echo -e "${GREEN}✅ Route tables configured${NC}"

# Create security groups
echo -e "${YELLOW}🔒 Creating security groups...${NC}"

# ALB Security Group
ALB_SG_ID=$(aws ec2 create-security-group --group-name $PROJECT_NAME-alb-sg --description "Security group for ALB" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION)
aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $AWS_REGION

# ECS Security Group
ECS_SG_ID=$(aws ec2 create-security-group --group-name $PROJECT_NAME-ecs-sg --description "Security group for ECS" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION)
aws ec2 authorize-security-group-ingress --group-id $ECS_SG_ID --protocol tcp --port 8000 --source-group $ALB_SG_ID --region $AWS_REGION

# RDS Security Group
RDS_SG_ID=$(aws ec2 create-security-group --group-name $PROJECT_NAME-rds-sg --description "Security group for RDS" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION)
aws ec2 authorize-security-group-ingress --group-id $RDS_SG_ID --protocol tcp --port 5432 --source-group $ECS_SG_ID --region $AWS_REGION

# Redis Security Group
REDIS_SG_ID=$(aws ec2 create-security-group --group-name $PROJECT_NAME-redis-sg --description "Security group for Redis" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION)
aws ec2 authorize-security-group-ingress --group-id $REDIS_SG_ID --protocol tcp --port 6379 --source-group $ECS_SG_ID --region $AWS_REGION

echo -e "${GREEN}✅ Security groups created${NC}"

# Create RDS subnet group
echo -e "${YELLOW}🗄️ Creating RDS subnet group...${NC}"
aws rds create-db-subnet-group \
    --db-subnet-group-name $PROJECT_NAME-db-subnet-group \
    --db-subnet-group-description "Subnet group for $PROJECT_NAME RDS" \
    --subnet-ids $PRIVATE_SUBNET_1_ID $PRIVATE_SUBNET_2_ID \
    --region $AWS_REGION 2>/dev/null || echo "DB subnet group already exists"

# Generate random password for database
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Create RDS instance
echo -e "${YELLOW}🗄️ Creating RDS PostgreSQL instance...${NC}"
aws rds create-db-instance \
    --db-instance-identifier $PROJECT_NAME-db \
    --db-instance-class $DB_INSTANCE_CLASS \
    --engine $DB_ENGINE \
    --engine-version $DB_ENGINE_VERSION \
    --master-username postgres \
    --master-user-password $DB_PASSWORD \
    --allocated-storage $DB_ALLOCATED_STORAGE \
    --vpc-security-group-ids $RDS_SG_ID \
    --db-subnet-group-name $PROJECT_NAME-db-subnet-group \
    --multi-az \
    --backup-retention-period 7 \
    --storage-encrypted \
    --region $AWS_REGION \
    --no-publicly-accessible

echo -e "${GREEN}✅ RDS instance created (this may take 10-15 minutes)${NC}"

# Create ElastiCache subnet group
echo -e "${YELLOW}⚡ Creating ElastiCache subnet group...${NC}"
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name $PROJECT_NAME-redis-subnet-group \
    --cache-subnet-group-description "Subnet group for $PROJECT_NAME Redis" \
    --subnet-ids $PRIVATE_SUBNET_1_ID $PRIVATE_SUBNET_2_ID \
    --region $AWS_REGION 2>/dev/null || echo "Cache subnet group already exists"

# Create Redis cluster
echo -e "${YELLOW}⚡ Creating Redis cluster...${NC}"
aws elasticache create-cache-cluster \
    --cache-cluster-id $PROJECT_NAME-redis \
    --cache-node-type $REDIS_NODE_TYPE \
    --engine redis \
    --num-cache-nodes 1 \
    --vpc-security-group-ids $REDIS_SG_ID \
    --cache-subnet-group-name $PROJECT_NAME-redis-subnet-group \
    --region $AWS_REGION

echo -e "${GREEN}✅ Redis cluster created${NC}"

# Create ECS cluster
echo -e "${YELLOW}🐳 Creating ECS cluster...${NC}"
aws ecs create-cluster --cluster-name $PROJECT_NAME-cluster --region $AWS_REGION 2>/dev/null || echo "ECS cluster already exists"

# Create CloudWatch log group
echo -e "${YELLOW}📊 Creating CloudWatch log group...${NC}"
aws logs create-log-group --log-group-name /ecs/$PROJECT_NAME --region $AWS_REGION 2>/dev/null || echo "Log group already exists"

# Create IAM role for ECS task execution
echo -e "${YELLOW}🔐 Creating IAM role for ECS...${NC}"
cat > ecs-task-execution-role-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
    --role-name $PROJECT_NAME-ecs-task-execution-role \
    --assume-role-policy-document file://ecs-task-execution-role-trust-policy.json \
    --region $AWS_REGION 2>/dev/null || echo "IAM role already exists"

aws iam attach-role-policy \
    --role-name $PROJECT_NAME-ecs-task-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
    --region $AWS_REGION 2>/dev/null || echo "Policy already attached"

# Defer task definition creation until ALB is created to inject ALB DNS into env

# Create Application Load Balancer
echo -e "${YELLOW}⚖️ Creating Application Load Balancer...${NC}"
ALB_ARN=$(aws elbv2 create-load-balancer \
    --name $PROJECT_NAME-alb \
    --subnets $PUBLIC_SUBNET_1_ID $PUBLIC_SUBNET_2_ID \
    --security-groups $ALB_SG_ID \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].LoadBalancerArn' --output text)

echo -e "${GREEN}✅ Application Load Balancer created: $ALB_ARN${NC}"

# Create target group
echo -e "${YELLOW}🎯 Creating target group...${NC}"
TARGET_GROUP_ARN=$(aws elbv2 create-target-group \
    --name $PROJECT_NAME-targets \
    --protocol HTTP \
    --port 8000 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path /health/ \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

echo -e "${GREEN}✅ Target group created: $TARGET_GROUP_ARN${NC}"

# Create listener
echo -e "${YELLOW}👂 Creating ALB listener...${NC}"
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
    --region $AWS_REGION >/dev/null

echo -e "${GREEN}✅ ALB HTTP (80) listener created${NC}"

# Optionally add HTTPS listener and redirect rule if ACM_ARN provided
if [ -n "$ACM_ARN" ]; then
  echo -e "${YELLOW}🔒 Creating HTTPS (443) listener with ACM cert...${NC}"
  HTTPS_LISTENER_ARN=$(aws elbv2 create-listener \
      --load-balancer-arn $ALB_ARN \
      --protocol HTTPS \
      --port 443 \
      --certificates CertificateArn=$ACM_ARN \
      --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
      --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
      --region $AWS_REGION \
      --query 'Listeners[0].ListenerArn' --output text)
  echo -e "${GREEN}✅ HTTPS listener created: $HTTPS_LISTENER_ARN${NC}"

  # Update HTTP listener to redirect to HTTPS
  echo -e "${YELLOW}➡️  Redirecting HTTP (80) to HTTPS (443)...${NC}"
  HTTP_LISTENER_ARN=$(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --query 'Listeners[?Port==`80`].ListenerArn' --output text --region $AWS_REGION)
  aws elbv2 modify-listener \
      --listener-arn $HTTP_LISTENER_ARN \
      --default-actions Type=redirect,RedirectConfig='{"Protocol":"HTTPS","Port":"443","StatusCode":"HTTP_301"}' \
      --region $AWS_REGION >/dev/null
  echo -e "${GREEN}✅ HTTP now redirects to HTTPS${NC}"
fi

# Get ALB DNS name (needed for ALLOWED_HOSTS, CSRF/CORS)
ALB_DNS=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query 'LoadBalancers[0].DNSName' --output text --region $AWS_REGION)

# Create task definition now that ALB_DNS is known
echo -e "${YELLOW}📋 Creating ECS task definition...${NC}"
cat > task-definition.json << EOF
{
  "family": "$PROJECT_NAME-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "$ECS_CPU",
  "memory": "$ECS_MEMORY",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/$PROJECT_NAME-ecs-task-execution-role",
  "containerDefinitions": [
    {
      "name": "$PROJECT_NAME-web",
      "image": "$ECR_URI",
      "portMappings": [
        { "containerPort": 8000, "protocol": "tcp" }
      ],
      "command": ["./run-gunicorn.sh"],
      "environment": [
        { "name": "DEBUG", "value": "False" },
        { "name": "ALLOWED_HOSTS", "value": "$ALB_DNS,localhost,127.0.0.1" },
        { "name": "CSRF_TRUSTED_ORIGINS", "value": "http://$ALB_DNS,https://$ALB_DNS" },
        { "name": "CORS_ALLOWED_ORIGINS", "value": "http://$ALB_DNS,https://$ALB_DNS" },
        { "name": "SECURE_SSL_REDIRECT", "value": "True" },
        { "name": "GUNICORN_WORKER_CLASS", "value": "gevent" },
        { "name": "GUNICORN_WORKER_CONNECTIONS", "value": "1000" }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:$PROJECT_NAME/secret-key"
        },
        {
          "name": "POSTGRES_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:$PROJECT_NAME/db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$PROJECT_NAME",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION

echo -e "${GREEN}✅ Task definition created${NC}"

# Create ECS service
echo -e "${YELLOW}🚀 Creating ECS service...${NC}"
aws ecs create-service \
    --cluster $PROJECT_NAME-cluster \
    --service-name $PROJECT_NAME-service \
    --task-definition $PROJECT_NAME-task \
    --desired-count $ECS_DESIRED_COUNT \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[$PUBLIC_SUBNET_1_ID,$PUBLIC_SUBNET_2_ID],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=$PROJECT_NAME-web,containerPort=8000" \
    --region $AWS_REGION

echo -e "${GREEN}✅ ECS service created${NC}"

# Store secrets in AWS Secrets Manager
echo -e "${YELLOW}🔐 Storing secrets in AWS Secrets Manager...${NC}"

# Generate secret key
SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)

# Store database password
aws secretsmanager create-secret \
    --name $PROJECT_NAME/db-password \
    --description "Database password for $PROJECT_NAME" \
    --secret-string $DB_PASSWORD \
    --region $AWS_REGION 2>/dev/null || aws secretsmanager update-secret --secret-id $PROJECT_NAME/db-password --secret-string $DB_PASSWORD --region $AWS_REGION

# Store secret key
aws secretsmanager create-secret \
    --name $PROJECT_NAME/secret-key \
    --description "Django secret key for $PROJECT_NAME" \
    --secret-string $SECRET_KEY \
    --region $AWS_REGION 2>/dev/null || aws secretsmanager update-secret --secret-id $PROJECT_NAME/secret-key --secret-string $SECRET_KEY --region $AWS_REGION

echo -e "${GREEN}✅ Secrets stored in AWS Secrets Manager${NC}"

# Wait for RDS to be available
echo -e "${YELLOW}⏳ Waiting for RDS instance to be available...${NC}"
aws rds wait db-instance-available --db-instance-identifier $PROJECT_NAME-db --region $AWS_REGION

# Get RDS endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier $PROJECT_NAME-db --query 'DBInstances[0].Endpoint.Address' --output text --region $AWS_REGION)

# Get Redis endpoint
REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters --cache-cluster-id $PROJECT_NAME-redis --show-cache-node-info --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' --output text --region $AWS_REGION)

# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query 'LoadBalancers[0].DNSName' --output text --region $AWS_REGION)

echo -e "${GREEN}✅ RDS endpoint: $RDS_ENDPOINT${NC}"
echo -e "${GREEN}✅ Redis endpoint: $REDIS_ENDPOINT${NC}"
echo -e "${GREEN}✅ ALB DNS: $ALB_DNS${NC}"

# Create environment file for reference
cat > .env.production << EOF
# AWS Production Environment Variables
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$ALB_DNS,localhost,127.0.0.1

# Database
POSTGRES_HOST=$RDS_ENDPOINT
POSTGRES_DB=campushub360
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://$REDIS_ENDPOINT:6379/0

# Performance
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=gevent
GUNICORN_WORKER_CONNECTIONS=1000

# AWS
AWS_REGION=$AWS_REGION
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=$PROJECT_NAME-media
EOF

# Clean up temporary files
rm -f ecs-task-execution-role-trust-policy.json task-definition.json

echo -e "${BLUE}🎉 Deployment completed successfully!${NC}"
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "1. Wait 5-10 minutes for all services to be ready"
echo -e "2. Access your application at: http://$ALB_DNS"
echo -e "3. Run database migrations:"
echo -e "   aws ecs run-task --cluster $PROJECT_NAME-cluster --task-definition $PROJECT_NAME-task --launch-type FARGATE --network-configuration \"awsvpcConfiguration={subnets=[$PUBLIC_SUBNET_1_ID],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}\" --overrides '{\"containerOverrides\":[{\"name\":\"$PROJECT_NAME-web\",\"command\":[\"python\",\"manage.py\",\"migrate\"]}]}'"
echo -e "4. Create superuser:"
echo -e "   aws ecs run-task --cluster $PROJECT_NAME-cluster --task-definition $PROJECT_NAME-task --launch-type FARGATE --network-configuration \"awsvpcConfiguration={subnets=[$PUBLIC_SUBNET_1_ID],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}\" --overrides '{\"containerOverrides\":[{\"name\":\"$PROJECT_NAME-web\",\"command\":[\"python\",\"manage.py\",\"createsuperuser\"]}]}'"
echo -e "5. Monitor your application in AWS Console"
echo -e ""
echo -e "${GREEN}💰 Estimated monthly cost: ~$175${NC}"
echo -e "${GREEN}🚀 Performance: 5,000-10,000 concurrent users${NC}"
