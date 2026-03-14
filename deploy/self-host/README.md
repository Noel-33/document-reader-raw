# Self-Host the Backend on Your Own Computer

This project can run with:

- Firebase Hosting for the frontend
- your own computer for the FastAPI backend
- a public HTTPS tunnel in front of the backend

The easiest path is:

- run the backend locally on port `8000`
- expose it with Cloudflare Tunnel
- point the frontend at that HTTPS tunnel URL

## Why this works

Firebase Hosting is served over HTTPS. Browsers will block requests from your Firebase app to a plain HTTP backend, so the backend needs a public HTTPS URL. A tunnel gives you that without opening router ports.

## 1. Install backend dependencies

From `backend/`:

```bash
pip install -r requirements.txt
```

## 2. Configure backend env vars

Copy `backend/.env.example` and set:

- `FRONTEND_URLS=https://your-app.web.app,https://your-app.firebaseapp.com`
- `OPENAI_API_KEY=...` if you want OpenAI models enabled

You can also set these directly in your shell instead of using a file.

## 3. Run the backend

From `backend/`:

```bash
python run_server.py
```

That starts FastAPI on `http://localhost:8000`.

Health check:

```bash
http://localhost:8000/health
```

## 4. Create a public HTTPS URL with Cloudflare Tunnel

Quick temporary tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

That will return an HTTPS URL such as:

```text
https://random-name.trycloudflare.com
```

If you want a stable named tunnel, use the example config in `deploy/self-host/cloudflared/config.yml.example`.

## 5. Point the frontend at the backend

Set:

```bash
VITE_API_URL=https://YOUR-BACKEND-DOMAIN
```

Then rebuild and deploy:

```bash
cd frontend
npm run build
cd ..
firebase deploy --only hosting
```

## 6. CORS

The backend already supports multiple frontend origins through:

```text
FRONTEND_URLS=https://your-app.web.app,https://your-app.firebaseapp.com
```

## Practical notes

- Your computer has to stay on for the backend to stay online.
- If your internet drops, the backend goes offline.
- Uploaded files are still stored in memory only, so restarting the backend clears them.
- A tunnel is the easiest way to get HTTPS without opening ports on your home router.
