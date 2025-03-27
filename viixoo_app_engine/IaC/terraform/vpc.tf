# ------------------------------------------------------------------------------
# VPC
# ------------------------------------------------------------------------------

resource "aws_vpc" "app_vpc" {
  cidr_block = "10.0.0.0/16" # You can adjust this CIDR block
  tags = {
    Name = "viixoo-hemago-app-vpc"
  }
}

# ------------------------------------------------------------------------------
# Subnets
# ------------------------------------------------------------------------------

resource "aws_subnet" "app_subnet_public" {
  vpc_id                  = aws_vpc.app_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = local.aws_subnet_zone
  map_public_ip_on_launch = true
  tags = {
    Name = "viixoo-hemago-app-subnet-public"
  }
}

# ------------------------------------------------------------------------------
# Internet Gateway
# ------------------------------------------------------------------------------

resource "aws_internet_gateway" "app_igw" {
  vpc_id = aws_vpc.app_vpc.id
  tags = {
    Name = "viixoo-hemago-app-igw"
  }
}

# ------------------------------------------------------------------------------
# Route Table
# ------------------------------------------------------------------------------

resource "aws_route_table" "app_route_table_public" {
  vpc_id = aws_vpc.app_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app_igw.id
  }
  tags = {
    Name = "viixoo-hemago-app-route-table-public"
  }
}

# ------------------------------------------------------------------------------
# Route Table Association
# ------------------------------------------------------------------------------

resource "aws_route_table_association" "app_rta_public" {
  subnet_id      = aws_subnet.app_subnet_public.id
  route_table_id = aws_route_table.app_route_table_public.id
}

# ------------------------------------------------------------------------------
# Security Group
# ------------------------------------------------------------------------------

resource "aws_security_group" "app_sg" {
  name        = "viixoo-hemago-app-sg"
  description = "Security group for Viixoo Hemago application"
  vpc_id      = aws_vpc.app_vpc.id # Associate with the VPC

  # Allow SSH access
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # TODO Consider restricting this to your IP
  }

  # Allow HTTP access
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTPS access
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow FastAPI (prod) access
  ingress {
    description = "FastAPI (prod)"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow FastAPI (dev) access
  ingress {
    description = "FastAPI (dev)"
    from_port   = 8002
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow React access
  ingress {
    description = "React"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
