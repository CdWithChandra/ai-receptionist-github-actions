# ---------------------------------------------------------
# AI Receptionist Pod Identity IAM Role
# ---------------------------------------------------------

resource "aws_iam_role" "ai_receptionist_pod_role" {
  name = "${var.cluster_name}-pod-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "pods.eks.amazonaws.com"
        }

        Action = [
          "sts:AssumeRole",
          "sts:TagSession"
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.cluster_name}-pod-role"
    Project     = "ai-receptionist-github-actions"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}

# ---------------------------------------------------------
# Pod Role - Secrets Manager Access
# ---------------------------------------------------------

data "aws_iam_policy_document" "ai_receptionist_secrets" {

  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]

    resources = [
      aws_secretsmanager_secret.app.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "kms:Decrypt"
    ]

    resources = [
      aws_kms_key.app_secrets.arn
    ]
  }
}

resource "aws_iam_policy" "ai_receptionist_secrets" {
  name   = "${var.cluster_name}-pod-secrets"
  policy = data.aws_iam_policy_document.ai_receptionist_secrets.json

  tags = {
    Name        = "${var.cluster_name}-pod-secrets"
    Project     = "ai-receptionist-github-actions"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}

resource "aws_iam_role_policy_attachment" "ai_receptionist_secrets" {
  role       = aws_iam_role.ai_receptionist_pod_role.name
  policy_arn = aws_iam_policy.ai_receptionist_secrets.arn
}

# ---------------------------------------------------------
# EKS Pod Identity Association
# ---------------------------------------------------------

resource "aws_eks_pod_identity_association" "ai_receptionist" {
  cluster_name    = aws_eks_cluster.main.name
  namespace       = "ai-receptionist"
  service_account = "ai-receptionist"
  role_arn        = aws_iam_role.ai_receptionist_pod_role.arn

  depends_on = [
    aws_eks_addon.pod_identity_agent
  ]
}
