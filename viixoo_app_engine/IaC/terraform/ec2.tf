# ------------------------------------------------------------------------------
# EC2 Instance
# ------------------------------------------------------------------------------

data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-*-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.medium" # Or t3.micro
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  subnet_id              = aws_subnet.app_subnet_public.id          # Place in the public subnet
  user_data              = file("${path.module}/install_script.sh") # Read from the script file
  tags = {
    Name = "viixoo-hemago-app-server"
  }

  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
    http_endpoint               = "enabled"
    instance_metadata_tags      = "enabled"
  }
}

# ------------------------------------------------------------------------------
# Elastic IP (Optional)
# ------------------------------------------------------------------------------

resource "aws_eip" "app_eip" {
  instance = aws_instance.app_server.id
}
