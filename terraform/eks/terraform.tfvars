aws_region         = "ap-south-1"
cluster_name       = "ai-receptionist-eks"
kubernetes_version = "1.36"

vpc_cidr = "10.0.0.0/16"

node_instance_type = "m7i-flex.large"

node_desired_size = 2
node_min_size     = 1
node_max_size     = 3
