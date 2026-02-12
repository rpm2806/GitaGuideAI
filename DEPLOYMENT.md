# GitaGuideAI Deployment Guide

This guide details how to deploy the **FastAPI Backend** to Render and the **Next.js Frontend** to Vercel using their free tiers.

## Prerequisites
- GitHub account
- Render.com account
- Vercel.com account
- Groq API Key
- HuggingFace Token

---

## 1. Backend Deployment (Render)

### Step 1: Create Web Service
1.  Push your code to a GitHub repository.
2.  Log in to [Render Dashboard](https://dashboard.render.com/).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.

### Step 2: Configure Service
*   **Name**: `gitaguide-backend`
*   **Region**: Choose closest to you (e.g., Singapore/Oregon).
*   **Branch**: `main`
*   **Root Directory**: `backend` (Important!)
*   **Runtime**: **Python 3**
*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
*   **Instance Type**: **Free**

### Step 3: Environment Variables
Scroll down to **Environment Variables** and add:
*   `PYTHON_VERSION`: `3.11.9`
*   `GROQ_API_KEY`: `your_groq_key` (Required for RAG, Translation, and Chat)
*   `HF_TOKEN`: `your_hf_token` (Optional if using public models, recommended for higher rate limits)
*   `CORS_ORIGINS`: `https://your-vercel-app.vercel.app` (Add this *after* deploying frontend, initially use `*`)
*   `CHROMA_PERSIST_DIRECTORY`: `./data/chroma_db` (Ensure you committed this folder to Git!)

### Step 4: Deploy
*   Click **Create Web Service**.
*   Wait for the build to finish.
*   **Note**: The free tier spins down after inactivity. First request may take ~50s.

---

## 2. Frontend Deployment (Vercel)

### Step 1: Import Project
1.  Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2.  Click **Add New...** -> **Project**.
3.  Import the same GitHub repository.

### Step 2: Configure Project
*   **Framework Preset**: **Next.js**
*   **Root Directory**: click **Edit** and select `frontend`.
*   **Build Command**: Leave default (`next build`).

### Step 3: Environment Variables
Expand **Environment Variables** and add:
*   `NEXT_PUBLIC_API_URL`: `https://gitaguide-backend.onrender.com` (The URL provided by Render in Step 1)

### Step 4: Deploy
*   Click **Deploy**.
*   Vercel will build and assign a domain (e.g., `gitaguide-frontend.vercel.app`).

---

## 3. Final Configuration
1.  Copy your new Vercel domain (e.g., `https://gitaguide-frontend.vercel.app`).
2.  Go back to **Render Dashboard** -> **Environment Variables**.
3.  Update `CORS_ORIGINS` to your Vercel domain (remove trailing slash).
4.  **Redeploy** Render for changes to take effect.

## Free Tier Limitations
*   **Cold Starts**: Render Backend will sleep after 15 mins of inactivity.
*   **Compute**: Backend limited to 0.1 CPU / 512MB RAM.
*   **Persistence**: Render disk is ephemeral. **Do not save new data to disk at runtime**; it will vanish on restart. The `chroma_db` folder MUST be committed to Git to be available.
