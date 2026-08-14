pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        AWS_ACCOUNT_ID = '669294688092'
        ECR_REPOSITORY = 'ai-receptionist'
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

        IMAGE_TAG = "${BUILD_NUMBER}"
        IMAGE_NAME = "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

        K8S_NAMESPACE = 'ai-receptionist'
        K8S_DEPLOYMENT = 'ai-receptionist'
        K8S_CONTAINER = 'ai-receptionist'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Source') {
            steps {
                sh '''
                    set -e
                    pwd
                    ls -la
                    ls -la backend
                    ls -la k8s

                    test -f backend/Dockerfile
                    test -f backend/requirements.txt
                    test -f backend/.dockerignore
                    test -f k8s/deployment.yml
                    test -f k8s/namespace.yml
                    test -f k8s/service.yml
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    set -e

                    docker build \
                        -t "${IMAGE_NAME}" \
                        backend
                '''
            }
        }

                stage('Application Tests') {
            steps {
                sh '''
                    set -e

                    echo "Running application tests inside Docker image..."

                    docker run --rm \
                        "${IMAGE_NAME}" \
                        python -m pytest tests -q

                    echo "Application tests PASSED"
                '''
            }
        }

        stage('Docker Login to ECR') {
            steps {
                sh '''
                    set -e

                    aws ecr get-login-password \
                        --region "${AWS_REGION}" \
                    | docker login \
                        --username AWS \
                        --password-stdin "${ECR_REGISTRY}"
                '''
            }
        }

        stage('Push Image to ECR') {
            steps {
                sh '''
                    set -e
                    docker push "${IMAGE_NAME}"
                '''
            }
        }

        stage('Verify EKS Access') {
            steps {
                sh '''
                    set -e

                    aws eks update-kubeconfig \
                        --region "${AWS_REGION}" \
                        --name ai-receptionist-eks

                    kubectl get nodes
                    kubectl get namespace "${K8S_NAMESPACE}"
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                    set -e

                    kubectl -n "${K8S_NAMESPACE}" \
                        set image deployment/"${K8S_DEPLOYMENT}" \
                        "${K8S_CONTAINER}"="${IMAGE_NAME}"

                    kubectl -n "${K8S_NAMESPACE}" \
                        rollout status deployment/"${K8S_DEPLOYMENT}" \
                        --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -e

                    kubectl -n "${K8S_NAMESPACE}" \
                        get deployment "${K8S_DEPLOYMENT}"

                    kubectl -n "${K8S_NAMESPACE}" \
                        get pods -o wide

                    kubectl -n "${K8S_NAMESPACE}" \
                        get service
                '''
            }
        }
    }

    post {
        success {
            echo "PHASE 6 DEPLOYMENT SUCCESSFUL"
            echo "Image: ${IMAGE_NAME}"
        }

        failure {
            echo "PHASE 6 DEPLOYMENT FAILED"
        }

        always {
            sh '''
                docker image rm "${IMAGE_NAME}" 2>/dev/null || true
                docker image prune -f 2>/dev/null || true
            '''
        }
    }
}
