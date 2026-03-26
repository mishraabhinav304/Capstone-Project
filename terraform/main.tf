terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_key_pair" "student_registry_key" {
  key_name   = "student-registry-key"
  public_key = file(var.public_key_path)
}

resource "aws_security_group" "student_registry_sg" {
  name        = "student-registry-sg"
  description = "Allow SSH, app, and K8s ports"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8080
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "student_registry" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.student_registry_key.key_name
  vpc_security_group_ids = [aws_security_group.student_registry_sg.id]

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  user_data = file("${path.module}/user_data.sh")

  tags = {
    Name    = "student-registry-k8s"
    Project = "student-registry"
  }
}

output "ec2_public_ip" {
  value = aws_instance.student_registry.public_ip
}
output "ec2_public_dns" {
  value = aws_instance.student_registry.public_dns
}
