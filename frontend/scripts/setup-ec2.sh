#!/bin/bash

# EC2 Initial Setup Script for Ubuntu 22.04
# Run this script once when setting up a new EC2 instance

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting EC2 setup for Seoul Economic Daily English Site...${NC}"

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install Node.js 20.x
echo -e "${YELLOW}Installing Node.js 20...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
echo -e "${YELLOW}Installing PM2...${NC}"
sudo npm install -g pm2

# Setup PM2 startup
pm2 startup systemd -u ubuntu --hp /home/ubuntu
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu

# Install Nginx
echo -e "${YELLOW}Installing Nginx...${NC}"
sudo apt install -y nginx

# Install Certbot for SSL
echo -e "${YELLOW}Installing Certbot...${NC}"
sudo apt install -y certbot python3-certbot-nginx

# Install Git
echo -e "${YELLOW}Installing Git...${NC}"
sudo apt install -y git

# Install build essentials
echo -e "${YELLOW}Installing build tools...${NC}"
sudo apt install -y build-essential

# Create application directories
echo -e "${YELLOW}Creating application directories...${NC}"
mkdir -p /home/ubuntu/en-sedaily
mkdir -p /home/ubuntu/logs
mkdir -p /home/ubuntu/backups

# Configure firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3000/tcp  # Next.js (temporary for testing)
sudo ufw --force enable

# Configure Nginx
echo -e "${YELLOW}Configuring Nginx...${NC}"
# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# The nginx.conf will be copied and linked during deployment

# Create swap file (recommended for t3.small)
echo -e "${YELLOW}Creating swap file...${NC}"
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Set swappiness
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# Install CloudWatch Agent (optional but recommended)
echo -e "${YELLOW}Installing CloudWatch Agent...${NC}"
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
rm amazon-cloudwatch-agent.deb

# Print system info
echo -e "${GREEN}=== System Information ===${NC}"
echo "Node.js version: $(node -v)"
echo "NPM version: $(npm -v)"
echo "PM2 version: $(pm2 -v)"
echo "Nginx version: $(nginx -v 2>&1)"
echo ""

# Instructions
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure your domain DNS to point to this EC2 instance"
echo "2. Copy nginx.conf to /etc/nginx/sites-available/sedaily-eng"
echo "3. Enable the site: sudo ln -s /etc/nginx/sites-available/sedaily-eng /etc/nginx/sites-enabled/"
echo "4. Obtain SSL certificate: sudo certbot --nginx -d en.sedaily.com -d en.sedaily.ai"
echo "5. Deploy the application using deploy-ec2.sh"
echo ""
echo -e "${YELLOW}Security reminders:${NC}"
echo "- Update EC2_HOST in deploy-ec2.sh with your EC2 IP"
echo "- Configure security group to only allow necessary ports"
echo "- Set up SSH key-based authentication only"
echo "- Consider using Elastic IP for stable addressing"
echo ""
echo -e "${GREEN}✓ EC2 setup complete!${NC}"