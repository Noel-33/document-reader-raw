variable "aws_region" {
  description = "AWS region for ECS/Fargate resources."
  type        = string
  default     = "us-east-1"
}

variable "name_prefix" {
  description = "Prefix for AWS resource names."
  type        = string
  default     = "document-reader"
}

variable "vpc_id" {
  description = "Existing VPC ID for ECS and ALB."
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for the Application Load Balancer."
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks."
  type        = list(string)
}

variable "frontend_urls" {
  description = "Allowed frontend origins for CORS."
  type        = list(string)
}

variable "container_port" {
  description = "Backend container port."
  type        = number
  default     = 8080
}

variable "task_cpu" {
  description = "Fargate task CPU units."
  type        = number
  default     = 1024
}

variable "task_memory" {
  description = "Fargate task memory in MiB."
  type        = number
  default     = 2048
}

variable "desired_count" {
  description = "Desired number of ECS tasks."
  type        = number
  default     = 1
}

variable "image_tag" {
  description = "Container image tag to deploy from ECR."
  type        = string
  default     = "latest"
}

variable "openai_api_key_secret_arn" {
  description = "Optional Secrets Manager or SSM ARN for OPENAI_API_KEY."
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "Optional ACM certificate ARN for HTTPS on the ALB."
  type        = string
  default     = ""
}

variable "route53_zone_id" {
  description = "Optional Route53 hosted zone ID for an HTTPS alias record."
  type        = string
  default     = ""
}

variable "backend_domain_name" {
  description = "Optional DNS name to point at the ALB when using Route53 and ACM."
  type        = string
  default     = ""
}
