# ---------------------------------------------------------
# Kubernetes Provider
# ---------------------------------------------------------

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.38"
    }
  }
}

provider "kubernetes" {
  host = aws_eks_cluster.main.endpoint

  cluster_ca_certificate = base64decode(
    aws_eks_cluster.main.certificate_authority[0].data
  )

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"

    args = [
      "eks",
      "get-token",
      "--cluster-name",
      aws_eks_cluster.main.name,
      "--region",
      var.aws_region
    ]
  }
}

# ---------------------------------------------------------
# GitHub Actions IAM Role in aws-auth
# ---------------------------------------------------------

resource "kubernetes_config_map_v1_data" "aws_auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    mapRoles = <<-EOT
      - rolearn: ${aws_iam_role.eks_node_role.arn}
        groups:
        - system:bootstrappers
        - system:nodes
        username: system:node:{{EC2PrivateDNSName}}

      - rolearn: ${aws_iam_role.github_actions.arn}
        groups:
        - system:masters
        username: github-actions
    EOT
  }

  force = true

  depends_on = [
    aws_eks_node_group.main
  ]
}
