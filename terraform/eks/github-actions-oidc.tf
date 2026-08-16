# ---------------------------------------------------------
# GitHub Actions OIDC Provider
# ---------------------------------------------------------

resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = [
    "sts.amazonaws.com"
  ]

  tags = {
    Name        = "ai-receptionist-github-actions-oidc"
    Project     = "ai-receptionist-github-actions"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }

}

# ---------------------------------------------------------
# GitHub Actions IAM Role
# ---------------------------------------------------------

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type = "Federated"
      identifiers = [
        aws_iam_openid_connect_provider.github_actions.arn

      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:CdWithChandra/ai-receptionist-github-actions:ref:refs/heads/main",
        "repo:CdWithChandra@*/ai-receptionist-github-actions@*:ref:refs/heads/main"
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name = "ai-receptionist-github-actions"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = {
    Name        = "ai-receptionist-github-actions"
    Project     = "ai-receptionist-github-actions"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }

}

# ---------------------------------------------------------
# ECR Permissions for GitHub Actions
# ---------------------------------------------------------

data "aws_iam_policy_document" "github_actions_ecr" {
  statement {
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken"
    ]

    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart"
    ]

    resources = [
      aws_ecr_repository.app.arn
    ]
  }
}
resource "aws_iam_policy" "github_actions_ecr" {
  name        = "ai-receptionist-github-actions-ecr"
  description = "ECR permissions for GitHub Actions"

  policy = data.aws_iam_policy_document.github_actions_ecr.json

  tags = {
    Name        = "ai-receptionist-github-actions-ecr"
    Project     = "ai-receptionist-github-actions"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "github_actions_ecr" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions_ecr.arn
}
