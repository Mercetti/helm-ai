# Helm AI AWS Free Tier Setup Guide

## 🚀 AWS Free Tier Account Setup

### Step 1: Create AWS Account
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create a Free Account"
3. Enter email address and password
4. Choose "Personal" account type
5. Enter credit card (required for verification, but won't be charged for free tier usage)
6. Verify phone number
7. Select support plan (Basic is free)

### Step 2: Access AWS Management Console
1. Log in to AWS Console
2. Navigate to Services > Compute > EC2
3. Review Free Tier limitations:
   - 750 hours/month of EC2 t2.micro or t3.micro
   - 5 GB of S3 storage
   - 1 million Lambda requests/month
   - 25 GB of RDS storage

## 🖥️ EC2 Instance Setup

### Create Security Group
1. Navigate to VPC > Security Groups
2. Click "Create security group"
3. Name: `helm-ai-sg`
4. Description: "Security group for Helm AI MVP"
5. Inbound rules:
   - SSH (22): Your IP address
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - Custom TCP (8501): 0.0.0.0/0 (for Streamlit)

### Launch EC2 Instance
1. Navigate to EC2 > Instances
2. Click "Launch instances"
3. Name: `helm-ai-mvp`
4. AMI: Ubuntu Server 22.04 LTS
5. Instance type: t2.micro (Free Tier)
6. Key pair: Create new key pair (download .pem file)
7. Security group: Select `helm-ai-sg`
8. Click "Launch instance"

## 📁 S3 Storage Setup

### Create S3 Bucket
1. Navigate to S3
2. Click "Create bucket"
3. Bucket name: `helm-ai-mvp-data` (must be unique)
4. Region: US East (N. Virginia)
5. Block all public access: Keep checked
6. Click "Create bucket"

### Configure S3 for Static Hosting
1. Select the bucket
2. Click "Properties"
3. Enable "Static website hosting"
4. Index document: `index.html`
5. Error document: `error.html`

## 🗄️ RDS Database Setup (Optional)

### Create RDS Instance
1. Navigate to RDS
2. Click "Create database"
3. Choose "Free tier templates"
4. Engine: PostgreSQL
5. DB instance identifier: `helm-ai-db`
6. Master username: `helm_ai`
7. Password: Generate strong password
8. VPC security group: Create new or use existing

## 🚀 Deployment Script

### SSH into EC2 Instance
```bash
chmod 400 your-key-pair.pem
ssh -i your-key-pair.pem ubuntu@your-ec2-public-ip
```

### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Install Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

### Clone and Deploy MVP
```bash
# Clone repository
git clone https://github.com/your-username/helm-ai-mvp.git
cd helm-ai-mvp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Streamlit
pip install streamlit

# Test the application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Create Systemd Service
```bash
sudo tee /etc/systemd/system/helm-ai.service > /dev/null <<EOF
[Unit]
Description=Helm AI MVP
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/helm-ai-mvp
Environment=PATH=/home/ubuntu/helm-ai-mvp/venv/bin
ExecStart=/home/ubuntu/helm-ai-mvp/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable helm-ai
sudo systemctl start helm-ai
```

## 🔒 Security Configuration

### Configure Firewall
```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501
sudo ufw enable
```

### SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate (if you have a domain)
sudo certbot --nginx -d yourdomain.com
```

## 📊 Monitoring Setup

### CloudWatch Monitoring
1. Navigate to CloudWatch
2. Create custom dashboard for:
   - EC2 CPU utilization
   - Network traffic
   - Disk usage
   - Application metrics

### Set Up Alerts
1. Create CloudWatch alarms for:
   - CPU > 80% for 5 minutes
   - Memory > 80% for 5 minutes
   - Disk space > 80%

## 💰 Cost Optimization

### Free Tier Monitoring
1. Set up AWS Budgets
2. Create monthly budget: $10
3. Set alerts at 50%, 80%, 100%

### Cost Saving Tips
- Use t2.micro instance (Free Tier)
- Monitor data transfer costs
- Use S3 Intelligent-Tiering
- Schedule instance start/stop if not needed 24/7

## 🔄 Automated Deployment

### Create Deployment Script
```bash
#!/bin/bash
# deploy.sh

# Pull latest code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart helm-ai

echo "Deployment completed at $(date)"
```

### Set Up Cron Job
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/ubuntu/helm-ai-mvp/backup.sh

# Add weekly deployment check
0 9 * * 1 /home/ubuntu/helm-ai-mvp/deploy.sh
```

## 📱 Access Your MVP

1. **Public IP**: `http://your-ec2-public-ip:8501`
2. **Domain**: `https://yourdomain.com` (if configured)
3. **SSH Access**: `ssh -i your-key.pem ubuntu@your-ec2-ip`

## 🔧 Troubleshooting

### Common Issues
1. **Port 8501 not accessible**: Check security group rules
2. **Service not starting**: Check logs with `sudo journalctl -u helm-ai`
3. **Out of memory**: Monitor with `free -h` and consider upgrading instance
4. **High CPU**: Check with `top` and optimize code

### Log Files
- Application logs: `sudo journalctl -u helm-ai`
- System logs: `/var/log/syslog`
- Nginx logs: `/var/log/nginx/`

## 📋 Next Steps

1. **Domain Setup**: Purchase domain and point to EC2
2. **SSL Certificate**: Configure HTTPS
3. **CDN Setup**: Use CloudFront for static assets
4. **Database**: Set up RDS for production data
5. **Backup Strategy**: Implement automated backups
6. **Monitoring**: Set up comprehensive monitoring

---

## 🎯 Success Metrics

### Performance Targets
- **Response Time**: < 2 seconds
- **Uptime**: > 99%
- **Cost**: < $10/month (Free Tier)
- **Scalability**: Handle 100 concurrent users

### Monitoring KPIs
- CPU utilization < 70%
- Memory usage < 80%
- Disk space < 80%
- Network latency < 100ms

---

**🛡️ Helm AI - Cloud Infrastructure Ready for MVP Deployment**
