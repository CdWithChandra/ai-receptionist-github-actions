resource "aws_ecr_repository" "app" {
  name                 = "ai-receptionist-github-actions"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "ai-receptionist-github-actions-ecr"
    Project     = "ai-receptionist-github-actions"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }

}
