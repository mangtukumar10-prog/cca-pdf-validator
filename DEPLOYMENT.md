# SignValid CCA PDF Validator - Deployment Guide

## 1. Instant Live Public Access (Active Now)
The application is currently live and reachable over the global internet with end-to-end SSL encryption:

* **Live Public HTTPS URL:** [https://seeds-expense-attempts-races.trycloudflare.com](https://seeds-expense-attempts-races.trycloudflare.com)
* **Local Address:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

This tunnel connects to Cloudflare's global edge network, allowing access from mobile phones, external computers, and any internet connection with zero port-forwarding needed.

---

## 2. Deploy to Cloud (24/7 Hosting)

The repository includes pre-configured deployment manifests:
* `render.yaml` - 1-Click Render.com Blueprint
* `Dockerfile` - Container deployment for Fly.io, Railway, Google Cloud Run, AWS ECS
* `Procfile` - Process specification for PaaS providers (Heroku, Render, Railway)
* `requirements.txt` - All cryptographic and server dependencies

### Option A: Render.com (Free Tier)
1. Push the project files to a GitHub repository.
2. Sign in to [Render](https://render.com) and click **New + > Web Service**.
3. Select your repository.
4. Set the following settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Your service will be assigned a permanent `https://your-app.onrender.com` URL.

### Option B: Railway.app
1. Sign in to [Railway.app](https://railway.app).
2. Select **New Project > Deploy from GitHub repo**.
3. Railway automatically detects `Dockerfile` and `Procfile`.
4. Generate a public domain under **Settings > Networking > Generate Domain**.

### Option C: Docker Container (Self-Hosted VPS or Cloud)
Build and run the container locally or on any cloud server:
```bash
docker build -t signvalid-validator .
docker run -d -p 8000:8000 --name signvalid signvalid-validator
```

---

## 3. Persistent Custom Domain (e.g. `validate.yourdomain.com`)
To bind a permanent custom domain using Cloudflare Tunnels:
```bash
# 1. Login to Cloudflare
.\cloudflared.exe tunnel login

# 2. Create named tunnel
.\cloudflared.exe tunnel create signvalid-prod

# 3. Route DNS
.\cloudflared.exe tunnel route dns signvalid-prod validate.yourdomain.com

# 4. Run tunnel
.\cloudflared.exe tunnel run signvalid-prod
```
