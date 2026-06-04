# Deployment Guide: AI-Powered Restaurant Recommendation System

This document outlines the step-by-step plan and configuration options to deploy your restaurant recommendation application to production for free, allowing you to share it with others.

---

## 1. Overview of Free Hosting Platforms

We recommend the following stack for hosting the application at zero cost:

| Tier | Platform | Why Choose It? | Limits / Caveats |
| :--- | :--- | :--- | :--- |
| **Frontend (Next.js)** | **Vercel** (Hobby Plan) | Native support for Next.js, automatic deployments on git push, free SSL, global CDN. | None (highly optimized for Next.js). |
| **Backend (FastAPI)** | **Render** (Free Tier) | Extremely simple setup, detects Python automatically, free SSL, custom domain support. | App spins down after 15 mins of inactivity (first request takes ~50s to load). |
| **Backend (Alternative)** | **Koyeb** (Free Tier) | High performance (512MB RAM), no cold start spin-down on active apps, quick deployment. | Free instance is paused after 10 days of inactivity but resumes instantly. |

---

## 2. Pre-Deployment Checklists

### 2.1 Backend Code Check
No code changes are required for the backend, as it is already configured to bind to dynamic port bindings:
- **Port Binding**: Production servers assign a dynamic port number in the `PORT` environment variable. Ensure the start command uses `$PORT` (e.g., `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`).
- **Data Path**: Keep `DATA_PATH` blank in production settings. The system will automatically fallback to the relative path `data/processed/restaurants.parquet` in the repository root.

### 2.2 Frontend API URL
Ensure your API calls use `process.env.NEXT_PUBLIC_API_URL` which is already wired into the frontend client in [api.ts](file:///e:/PM_Portfolio_Projects/AI-Powered-Restaurant-Recommendation-System/frontend/lib/api.ts).

---

## 3. Step-by-Step Deployment Plan

### Step 1: Push Project to GitHub
1. Create a repository on GitHub (e.g., `ai-restaurant-recommender`).
2. Initialize and push your project:
   ```bash
   git init
   git add .
   git commit -m "Prepare for deployment"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Deploy Backend (FastAPI) on Render
1. Go to [Render](https://render.com/) and log in (sign up using your GitHub account).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Set the following configurations:
   - **Name**: `restaurant-recommender-api` (or any custom name)
   - **Root Directory**: `backend` (Important: points Render to your python app subdirectory)
   - **Language / Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Select **Free**
5. Click **Advanced** and add the following **Environment Variables**:
   - `GROQ_API_KEY`: `your_groq_api_key_here`
   - `GROQ_MODEL`: `llama-3.3-70b-versatile`
   - `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app` (You can update this after deploying the frontend)
6. Click **Create Web Service**. Render will build and deploy your API. Once deployed, note down the URL (e.g., `https://restaurant-recommender-api.onrender.com`).

---

### Alternative: Deploy Backend using Docker (Koyeb / Fly.io / Hugging Face Spaces)
If you choose to deploy your backend using container hosting services, we have provided a production-ready `Dockerfile` in the `backend/` directory.

1. **Build the Docker Image** (from the repository root):
   ```bash
   docker build -t restaurant-backend -f backend/Dockerfile .
   ```
2. **Run the Container Locally**:
   ```bash
   docker run -p 8000:8000 --env-file backend/.env restaurant-backend
   ```
3. **Deploying**:
   - Ensure the build context is set to the repository root.
   - Set the Dockerfile path to `backend/Dockerfile`.
   - Configure environment variables (`GROQ_API_KEY`, `GROQ_MODEL`, `CORS_ORIGINS`) on your container platform.

---

### Step 3: Deploy Frontend (Next.js) on Vercel
1. Go to [Vercel](https://vercel.com/) and log in with your GitHub account.
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. Set the following configurations:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: `frontend` (Important: points Vercel to your Next.js subdirectory)
   - **Environment Variables**:
     - Add `NEXT_PUBLIC_API_URL` and set its value to your Render backend URL (e.g., `https://restaurant-recommender-api.onrender.com`).
5. Click **Deploy**. Vercel will build and launch your site.
6. Once deployed, note your production frontend domain (e.g. `https://your-app-name.vercel.app`).

---

### Step 4: Finalize CORS Configuration
1. Go back to your **Render Dashboard** -> **restaurant-recommender-api** -> **Environment**.
2. Update the `CORS_ORIGINS` variable:
   - Value: `https://your-app-name.vercel.app` (replacing the placeholder with your actual frontend URL).
3. Save the changes. Render will automatically redeploy the backend with the new CORS permissions.

---

## 4. Post-Deployment Verification

Once both deployments are complete, you can verify everything is working:

1. **Verify Backend**: Open `https://your-backend-url.onrender.com/health` in your browser. It should return:
   ```json
   {
     "status": "healthy",
     "data_ready": true,
     "data_path": "...",
     "restaurant_count": 50000
   }
   ```
2. **Verify Frontend**: Open your Vercel URL, fill out the preferences form, and press submit. Check if recommendations populate using the live Groq backend model.
