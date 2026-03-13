# Document Reader

This repo is a split full-stack app:

- `frontend/`: React + Vite SPA
- `backend/`: FastAPI API with in-memory document storage and local embedding generation

The most practical setup for this codebase is:

- Firebase Hosting for the frontend
- Render for the Python backend

The backend is also prepared for AWS container deployment with:

- `backend/Dockerfile`
- `backend/.dockerignore`
- port `8080` exposed for App Runner, ECS, or Elastic Beanstalk
- `infra/aws/terraform` for ECS/Fargate + ECR + ALB + security groups

## Current production risks

- Uploaded files are stored only in memory and disappear whenever the backend restarts.
- Embeddings are generated with `sentence-transformers` inside the API container, which makes the image large and cold starts slower.
- The backend accepts uploads and serves previews directly from process memory, so horizontal scaling can produce inconsistent state across instances.
- OpenAI-backed chat needs `OPENAI_API_KEY` in the deployed backend environment.

This setup is good enough for a demo or internal prototype, but not for durable production use without persistent storage.

## Deploy architecture

Frontend requests should point directly to the deployed Render backend domain. This repo is configured for that via `frontend/.env.production` and `frontend/src/api.ts`.

Firebase Hosting routes:

- `/**` -> `frontend/dist/index.html`

## Prerequisites

- Node.js 20+
- Python 3.11+
- Render account
- `firebase-tools` installed and authenticated

## 1. Build the frontend

```bash
cd frontend
npm install
npm run build
```

## 2. Deploy the backend to Render

This repo includes a Render blueprint in `render.yaml`.

In Render:

1. Create a new Blueprint instance from this repo, or create a Web Service manually.
2. Use `backend/` as the root directory.
3. Set these values:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `FRONTEND_URL=https://YOUR_FIREBASE_DOMAIN`
- Environment variable: `OPENAI_API_KEY=...` if you want OpenAI models enabled

Notes:

- Render injects `PORT`, and the backend is already compatible with that.
- Render free/starter-style instances may cold start slowly, which will be noticeable because `sentence-transformers` is heavy.
- Replace `YOUR_FIREBASE_DOMAIN` with your real Firebase domain after Hosting is live.

## AWS backend deployment

This repo is now prepared specifically for ECS/Fargate deployment with:

- GitHub Actions workflow: `.github/workflows/aws.yml`
- ECS task definition template: `.aws/task-definition.json`
- Backend container image: `backend/Dockerfile`
- Terraform stack: `infra/aws/terraform`

### ECS/Fargate setup

1. Create an ECR repository named `document-reader-api`, or change the name in `.github/workflows/aws.yml`.
2. Create an ECS cluster and service.
3. Copy `.aws/task-definition.json` and replace every placeholder ARN, account ID, region, and domain.
4. Add GitHub Actions secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Terraform path

If you want AWS to create the ECS service, ALB, security groups, ECR repo, log group, and IAM roles for you, use `infra/aws/terraform`.

Files:

- `infra/aws/terraform/main.tf`
- `infra/aws/terraform/variables.tf`
- `infra/aws/terraform/outputs.tf`
- `infra/aws/terraform/terraform.tfvars.example`

Quick start:

```bash
cd infra/aws/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

What it creates:

- ECR repository for the backend image
- ECS cluster, task definition, and Fargate service
- public Application Load Balancer
- security groups
- CloudWatch log group
- IAM execution/task roles
- optional HTTPS listener and Route53 alias if you provide ACM + Route53 values

Important note for Firebase:

- Firebase Hosting is HTTPS, so your backend also needs HTTPS in production.
- For the Terraform stack, that means setting `certificate_arn`, `route53_zone_id`, and `backend_domain_name`.
- The ALB health check is configured to use `/health`, which the backend now exposes.

Example image build and push flow:

```bash
aws ecr create-repository --repository-name document-reader-api

aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS \
  --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker build -t document-reader-api ./backend

docker tag document-reader-api:latest \
  YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/document-reader-api:latest

docker push \
  YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/document-reader-api:latest
```

Task definition values you must replace in `.aws/task-definition.json`:

- `executionRoleArn`
- `taskRoleArn`
- ECR image account ID and region
- `FRONTEND_URL`
- SSM parameter ARN for `OPENAI_API_KEY`

Recommended ECS service baseline:

- Launch type: Fargate
- Task size: `1 vCPU / 2 GB`
- Container port: `8080`
- Health check path: `/`

The GitHub Actions workflow will:

- build the backend image from `backend/Dockerfile`
- push it to ECR
- inject the new image into `.aws/task-definition.json`
- deploy the updated task definition to your ECS service

## 3. Deploy the frontend to Firebase Hosting

From the repo root:

```bash
cd frontend
VITE_API_URL=https://YOUR_BACKEND_DOMAIN npm run build
cd ..
firebase login
firebase use --add
firebase deploy --only hosting
```

This repo intentionally does not include `.firebaserc`, so you can bind it to your own Firebase project instead of a hard-coded one. If you prefer, you can also edit `frontend/.env.production` before building instead of passing `VITE_API_URL` inline. On the backend side, set `FRONTEND_URLS` to your Firebase domains so CORS allows production traffic.

## Recommended upgrades

- Move uploaded files to Google Cloud Storage.
- Persist metadata and chunk records in Firestore, Postgres, or another real datastore.
- Replace in-process embeddings with a durable vector store or precompute them asynchronously.
- Pin backend dependencies to tested versions to reduce deploy drift.
- Add backend health checks and structured logging.
- Add a proper root-level CI workflow for `frontend` build and backend smoke tests.
- Consider moving off Render if inference latency or memory usage becomes a problem; this backend is ML-heavy for a low-cost web service.
- Move uploaded file persistence off process memory before using autoscaling AWS services.

## Recommended cleanup

- Remove the root `package.json` and root `package-lock.json` if they are not intentionally used. The real web app lives under `frontend/`.
- Remove `frontend/package-lock 2.json`; it looks accidental and should not be kept.
- Stop committing `backend/__pycache__/` and local IDE files.
- Replace the Vite starter README in `frontend/README.md` with project-specific notes or remove it.
