output "ecr_repository_url" {
  description = "ECR repository URL for the backend image."
  value       = aws_ecr_repository.api.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.api.name
}

output "ecs_service_name" {
  description = "ECS service name."
  value       = aws_ecs_service.api.name
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name."
  value       = aws_lb.api.dns_name
}

output "backend_url" {
  description = "Best available backend URL. HTTPS requires ACM + Route53 inputs."
  value = local.use_route53_record ? "https://${var.backend_domain_name}" : (
    local.use_https ? "https://${aws_lb.api.dns_name}" : "http://${aws_lb.api.dns_name}"
  )
}
