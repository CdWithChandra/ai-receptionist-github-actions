# AI Receptionist


A FastAPI-based AI receptionist that handles appointment conversations, booking, availability checks, updates, cancellations, and general questions. The service is packaged as a Docker image and deployed to Amazon EKS through GitHub Actions, Amazon ECR, Terraform, and Kubernetes manifests.

> **Production status:** The repository includes a complete deployment path, but the default application configuration still uses a local SQLite database and process-local conversation state. Review the production-readiness checklist before exposing this service to real users or scaling beyond one replica.

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Run locally](#run-locally)
- [API](#api)
- [Docker](#docker)
- [AWS and Kubernetes deployment](#aws-and-kubernetes-deployment)
- [CI/CD](#cicd)
- [Testing](#testing)
- [Production-readiness checklist](#production-readiness-checklist)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- FastAPI HTTP API with automatic OpenAPI documentation.
- Conversational appointment booking through `POST /chat`.
- Appointment CRUD operations through the booking endpoints.
- Intent detection for greetings, booking, listing, updating, and cancelling appointments.
- OpenAI fallback responses using the `gpt-4.1-mini` model for unsupported requests.
- Duplicate appointment and time-slot conflict checks.
- SQLite persistence through SQLAlchemy for local development.
- Containerized deployment to Kubernetes on Amazon EKS.
- GitHub Actions deployment using AWS OIDC rather than long-lived AWS access keys.
- Terraform-managed VPC, EKS, ECR, IAM/OIDC, KMS, and Secrets Manager resources.

## Architecture

```text
Client
  |
  v
Kubernetes LoadBalancer Service :80
  |
  v
FastAPI application :8000
  |-- /chat ------------------> ChatService -> BookingAgent / AIService -> OpenAI
  |-- /booking ----------------> BookingService -> SQLAlchemy -> SQLite
  |-- /appointments -----------> BookingService -> SQLAlchemy -> SQLite
  `-- /health, / --------------> application status endpoints

GitHub Actions (main push)
  |-- pytest
  |-- Docker build
  |-- Push image to Amazon ECR
  `-- kubectl rollout to Amazon EKS
```

The HTTP routes are defined in `backend/app/api/routes.py`. `ChatService` coordinates conversational state and delegates booking operations to `BookingService`. `BookingAgent` performs lightweight intent and field extraction; requests it cannot classify are passed to `AIService`, which calls OpenAI. The application creates the SQLAlchemy tables on startup in `backend/app/main.py`.

## Repository layout

```text
.
├── backend/
│   ├── app/
│   │   ├── ai/                 OpenAI client and booking intent extraction
│   │   ├── api/                FastAPI route handlers
│   │   ├── core/               Logging and exception handlers
│   │   ├── database/           SQLAlchemy session and appointment model
│   │   ├── prompts/            Receptionist system prompt
│   │   ├── schemas/            Pydantic request and response models
│   │   ├── services/           Chat, booking, AI, and conversation services
│   │   ├── config.py            Environment-based application settings
│   │   └── main.py              FastAPI application entry point
│   ├── tests/                  API and appointment lifecycle tests
│   ├── Dockerfile              Python container image definition
│   ├── requirements.txt        Pinned Python dependencies
│   └── .env.example            Local configuration template
├── k8s/                        Kubernetes namespace, deployment, service, and policy
├── terraform/eks/              AWS/EKS infrastructure definitions
├── .github/workflows/ci-cd.yml Build, test, ECR push, and EKS deployment workflow
└── .gitignore
```

## Requirements

- Python 3.14
- Docker (for container builds)
- `kubectl` and AWS CLI (for deployment)
- Terraform 1.x and AWS credentials (for infrastructure provisioning)
- An OpenAI API key for fallback AI responses
- An AWS account with permissions to provision the Terraform resources

## Configuration

### Local application configuration

Copy the example file and set the API key in a secret-managed local file:

```bash
cp backend/.env.example backend/.env
```

| Variable | Required | Default | Description |
|---|---:|---|---|
| `OPENAI_API_KEY` | For AI fallback | — | OpenAI API key. Do not commit it. |
| `APP_NAME` | No | `AI Receptionist API` | FastAPI application name. |
| `APP_VERSION` | No | `1.0.0` | API version reported by `/health`. |
| `HOST` | No | `127.0.0.1` | Local host setting. |
| `PORT` | No | `8000` | Local application port. |

The current database URL is hard-coded as `sqlite:///./ai_receptionist.db` in `backend/app/database/session.py`. The current conversation workflow is stored in memory by `ConversationManager`.

### GitHub Actions configuration

The deployment workflow reads these GitHub Actions repository variables:

- `AWS_REGION` — AWS region, matching the EKS cluster.
- `AWS_ROLE_ARN` — IAM role ARN trusted by GitHub Actions OIDC.

The workflow currently targets:

- ECR repository: `ai-receptionist-github-actions`
- EKS cluster: `ai-receptionist-github-actions-eks`
- Kubernetes namespace: `ai-receptionist`

Do not put `OPENAI_API_KEY` in workflow files or Git history. Provision it through a Kubernetes secret or an external secrets integration before production deployment; the current manifests do not yet wire the Terraform Secrets Manager secret into the Pod.

## Run locally

```bash
git clone https://github.com/CdWithChandra/ai-receptionist-github-actions.git
cd ai-receptionist-github-actions

python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

cp backend/.env.example backend/.env
# Edit backend/.env and set OPENAI_API_KEY when AI fallback is required.

cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open the interactive API documentation at <http://127.0.0.1:8000/docs> or the ReDoc documentation at <http://127.0.0.1:8000/redoc>.

## API

The application exposes the following routes:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Welcome response. |
| `GET` | `/health` | Health response with application version. |
| `POST` | `/chat` | Process a receptionist message. |
| `POST` | `/booking` | Create an appointment. |
| `GET` | `/appointments` | List appointments. |
| `PUT` | `/booking/{appointment_id}` | Update an appointment. |
| `DELETE` | `/booking/{appointment_id}` | Delete an appointment. |

Example booking request:

```bash
curl -X POST http://127.0.0.1:8000/booking \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "Chandra",
    "appointment_date": "2099-12-31",
    "appointment_time": "11:59 PM"
  }'
```

Example chat request:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Book an appointment"}'
```

Request and response models are defined in `backend/app/schemas/booking.py` and `backend/app/schemas/chat.py`. Dates and times are currently represented as strings and validated by application logic for conversational flows.

## Docker

Build and run the backend from the repository root:

```bash
docker build -t ai-receptionist:local ./backend
docker run --rm -p 8000:8000 \
  --env-file backend/.env \
  ai-receptionist:local
```

The image starts `uvicorn app.main:app` on port `8000`. The Dockerfile is in `backend/Dockerfile`.

## AWS and Kubernetes deployment

### 1. Provision AWS infrastructure

Terraform in `terraform/eks` provisions the AWS foundation, including the VPC, EKS cluster and node group, ECR repository, GitHub Actions OIDC trust, IAM policies, KMS key, and Secrets Manager secret.

Review `terraform.tfvars` before applying. The checked-in values currently target `ap-south-1`, use cluster name `ai-receptionist-github-actions-eks`, and configure a small one-to-two-node group.

```bash
cd terraform/eks
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
terraform output
```

Use a remote, encrypted Terraform backend and state locking for shared or production environments. Do not store secrets in `terraform.tfvars`.

### 2. Configure GitHub Actions

Set the repository variables described in [GitHub Actions configuration](#github-actions-configuration), then verify that the IAM trust policy is restricted to the intended repository and branch. The workflow needs permission to push to ECR and access the EKS cluster.

### 3. Apply Kubernetes resources

```bash
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name ai-receptionist-github-actions-eks

kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/serviceaccount.yml
kubectl apply -f k8s/network-policy.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml

kubectl -n ai-receptionist get deployment,pods,service
kubectl -n ai-receptionist rollout status deployment/ai-receptionist
```

The service is exposed as a Kubernetes `LoadBalancer` on port `80` and forwards to the container on port `8000`. The GitHub Actions workflow applies the namespace, deployment, and service and then updates the deployment image with the commit SHA. Apply the service account and network policy separately until the workflow is extended to manage them.

## CI/CD

`.github/workflows/ci-cd.yml` runs on pushes to `main` and manual dispatches. It:

1. Authenticates to AWS with GitHub OIDC.
2. Installs Python 3.14 dependencies.
3. Runs `pytest -v` in `backend`.
4. Builds and pushes commit-SHA and `latest` tags to ECR.
5. Configures `kubectl` for EKS.
6. Applies Kubernetes resources and waits for the rollout.

For production, prefer immutable image references (commit SHA or digest) and avoid relying on the mutable `latest` tag for rollback decisions.

## Testing

Run the test suite from the backend directory:

```bash
cd backend
pytest -v
```

The current tests cover root and health endpoints, appointment create/list/update/delete behavior, request validation, and missing-appointment behavior. Tests use the application database configuration, so isolate the test database before running tests against shared environments.

## Production-readiness checklist

Before production use, complete the following:

- [ ] Replace SQLite with a managed, multi-connection database such as PostgreSQL.
- [ ] Move `DATABASE_URL` and other runtime settings into environment-based configuration.
- [ ] Replace process-global `ConversationManager` state with session-scoped state in Redis or a database; otherwise multiple users and replicas can share conversation data.
- [ ] Add authentication, authorization, rate limiting, and request-size limits to appointment and chat endpoints.
- [ ] Store `OPENAI_API_KEY` in Secrets Manager and mount it through a supported Kubernetes secret or external-secrets controller.
- [ ] Add database migrations instead of relying on `Base.metadata.create_all()` at application import time.
- [ ] Add readiness and liveness probes to the Deployment and configure resource requests/limits.
- [ ] Run multiple replicas only after conversation state and persistence are distributed safely.
- [ ] Add TLS, a managed ingress/API gateway, a custom domain, and appropriate CORS policy.
- [ ] Add structured, redacted logs, metrics, tracing, and alerting.
- [ ] Add backup, restore, retention, and disaster-recovery procedures.
- [ ] Pin and regularly review dependency versions and scan container images.
- [ ] Restrict IAM policies and verify the GitHub OIDC trust condition for the intended repository only.
- [ ] Add deployment rollback, approval, and environment protection rules to GitHub Actions.
- [ ] Validate dates and times as typed values and define the business timezone.
- [ ] Add authorization and tenant isolation before exposing appointment data through `GET /appointments`.

## Security

- Never commit `.env`, API keys, Terraform state, kubeconfig files, or credentials.
- Use GitHub Actions OIDC instead of static AWS credentials.
- Keep Terraform state in an encrypted, access-controlled remote backend.
- Treat appointment data as sensitive operational data; add access controls and audit logging before production use.
- Review the Kubernetes `NetworkPolicy` when adding databases, DNS, telemetry, or other egress destinations.
- Do not return raw provider or unexpected exception text to clients in a production API; log details server-side and return stable error responses.

## Troubleshooting

### The API starts but AI responses fail

Set `OPENAI_API_KEY` in `backend/.env` or the container/Kubernetes environment and restart the process. Deterministic greeting and appointment flows do not require OpenAI, but unknown requests use the OpenAI fallback.

### The deployment cannot pull the image

Confirm that the ECR repository exists, the image tag was pushed, the node role can pull from ECR, and the deployment image reference matches the AWS account and region.

### GitHub Actions cannot authenticate to AWS

Check `AWS_REGION`, `AWS_ROLE_ARN`, the IAM OIDC provider, and the role trust policy. The trust policy must match the exact repository and `main` branch used by the workflow.

### Kubernetes reports a failed rollout

```bash
kubectl -n ai-receptionist describe deployment ai-receptionist
kubectl -n ai-receptionist get pods
kubectl -n ai-receptionist logs deployment/ai-receptionist
```

## Contributing

1. Create a feature branch.
2. Make the smallest focused change.
3. Add or update tests for behavior changes.
4. Run `pytest -v` and `terraform validate` when applicable.
5. Open a pull request with deployment and configuration impacts clearly documented.

## License

No license file is currently present in the repository. Add a license before distributing or accepting external contributions.
