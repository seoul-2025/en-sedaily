# Security Group for EC2 instance
resource "aws_security_group" "web_server" {
  name_prefix = "${var.project_name}-web-"
  description = "Security group for Seoul Economic Daily English web server"

  # HTTP access from CloudFront
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  # SSH access (restrict as needed)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  # Next.js application port
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Next.js application"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-web-sg"
  }
}

# Key Pair for EC2 access
resource "aws_key_pair" "web_server" {
  key_name   = var.key_name
  public_key = file("${path.root}/keys/sedaily-eng-key.pub")

  tags = {
    Name = "${var.project_name}-keypair"
  }
}

# EC2 Instance for web server
resource "aws_instance" "web_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name              = aws_key_pair.web_server.key_name
  vpc_security_group_ids = [aws_security_group.web_server.id]
  
  # User data script for initial setup
  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    
    # Install Node.js 18
    curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
    yum install -y nodejs
    
    # Install PM2 globally
    npm install -g pm2
    
    # Configure PM2 to start on boot
    pm2 startup
    
    # Create application directory
    mkdir -p /home/ec2-user/en-sedaily
    chown ec2-user:ec2-user /home/ec2-user/en-sedaily
    
    # Install git (if needed for deployment)
    yum install -y git
    
    # Install nginx as reverse proxy (optional)
    amazon-linux-extras install nginx1 -y
    systemctl start nginx
    systemctl enable nginx
  EOF
  )

  tags = {
    Name = "${var.project_name}-web-server"
  }
  
  lifecycle {
    # Prevent accidental termination
    prevent_destroy = true
    
    # Ignore changes to AMI to prevent rebuild
    ignore_changes = [
      ami,
      user_data,
    ]
  }
}

# Elastic IP for consistent public IP
resource "aws_eip" "web_server" {
  instance = aws_instance.web_server.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }

  depends_on = [aws_instance.web_server]
}

