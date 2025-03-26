# ------------------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------------------

output "instance_public_ip" {
  value       = aws_instance.app_server.public_ip
  description = "Public IP of the EC2 instance"
}

output "instance_public_dns" {
  value       = aws_instance.app_server.public_dns
  description = "Public DNS of the EC2 instance"
}

#output "eip_address" {
#  value       = aws_eip.app_eip.public_ip
#  description = "Elastic IP address"
#}

output "vpc_id" {
  value       = aws_vpc.app_vpc.id
  description = "VPC ID"
}

output "subnet_id" {
  value       = aws_subnet.app_subnet_public.id
  description = "Public Subnet ID"
}