# Document Reader

This repo is a split full-stack app:

- `frontend/`: React + Vite SPA
- `backend/`: FastAPI API with in-memory document storage and local embedding generation

The most practical setup for this codebase is:

- Firebase Hosting for the frontend
- Render for the Python backend

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

## 3. Deploy the frontend to Firebase Hosting

From the repo root:

```bash
cd frontend
VITE_API_URL=https://YOUR-RENDER-BACKEND.onrender.com npm run build
cd ..
firebase login
firebase use --add
firebase deploy --only hosting
```

This repo intentionally does not include `.firebaserc`, so you can bind it to your own Firebase project instead of a hard-coded one. If you prefer, you can also edit `frontend/.env.production` before building instead of passing `VITE_API_URL` inline.

## Recommended upgrades

- Move uploaded files to Google Cloud Storage.
- Persist metadata and chunk records in Firestore, Postgres, or another real datastore.
- Replace in-process embeddings with a durable vector store or precompute them asynchronously.
- Pin backend dependencies to tested versions to reduce deploy drift.
- Add backend health checks and structured logging.
- Add a proper root-level CI workflow for `frontend` build and backend smoke tests.
- Consider moving off Render if inference latency or memory usage becomes a problem; this backend is ML-heavy for a low-cost web service.

## Recommended cleanup

- Remove the root `package.json` and root `package-lock.json` if they are not intentionally used. The real web app lives under `frontend/`.
- Remove `frontend/package-lock 2.json`; it looks accidental and should not be kept.
- Stop committing `backend/__pycache__/` and local IDE files.
- Replace the Vite starter README in `frontend/README.md` with project-specific notes or remove it.
