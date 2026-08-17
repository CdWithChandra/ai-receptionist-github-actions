resource "aws_kms_key" "app_secrets" {
  description             = "KMS key for AI Receptionist application secrets"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.cluster_name}-secret-key"
    Project     = "ai-receptionist-github-actions"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}

resource "aws_kms_alias" "app_secrets" {
  name          = "alias/${var.cluster_name}-secrets"
  target_key_id = aws_kms_key.app_secrets.key_id

}


# ---------------------------------------------------------
# AWS Secrets Manager
# ---------------------------------------------------------

resource "aws_secretsmanager_secret" "app" {
  name                    = "${var.cluster_name}/application"
  description             = "Application secrets for AI Receptionist"
  kms_key_id              = aws_kms_key.app_secrets.arn
  recovery_window_in_days = 7

  tags = {
    Name        = "${var.cluster_name}-application-secrets"
    Project     = "ai-receptionist-github-actions"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }

}
