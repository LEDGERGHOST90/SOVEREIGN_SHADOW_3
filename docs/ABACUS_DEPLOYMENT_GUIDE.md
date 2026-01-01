# Deploying SovereignShadow to Abacus AI

> **NOTE:** AbacusAI URLs in this doc are deprecated. Active endpoints: Replit Dashboard (`1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev`) and AlphaRunner GCP (`shadow-ai-alpharunner-33906555678.us-west1.run.app`). See BRAIN.json.

## Quick Start (Local Testing)

```bash
# Run everything locally first
./start_unified.sh

# This starts:
# - API Backend: http://localhost:8000
# - Gemini App: http://localhost:5173
```

## Abacus AI Deployment

### Step 1: Prepare Environment Variables

In your Abacus AI dashboard, set these secrets (NEVER commit to git):

```
COINBASE_API_KEY=your_key
COINBASE_API_SECRET=your_secret
KRAKEN_API_KEY=your_key
KRAKEN_API_SECRET=your_secret
GEMINI_API_KEY=your_gemini_key
```

### Step 2: Deploy Backend (Python)

Option A: **Abacus Functions**
- Upload `api/sovereign_api.py` as an Abacus Function
- Configure the function to run FastAPI
- Set environment variables in Abacus console

Option B: **External Hosting** (Railway/Render)
```bash
# requirements.txt
fastapi
uvicorn
pydantic

# Procfile
web: uvicorn api.sovereign_api:app --host 0.0.0.0 --port $PORT
```

### Step 3: Deploy Frontend (React)

Option A: **Abacus Static Hosting**
```bash
cd Sov.Shade{11:21:25}-GeminiAi
npm run build
# Upload dist/ folder to Abacus
```

Option B: **Vercel/Netlify**
- Connect GitHub repo
- Build command: `npm run build`
- Output directory: `dist`

### Step 4: Update API URLs

In `Sov.Shade{11:21:25}-GeminiAi/services/sovereignApi.ts`:

```typescript
const API_BASE = import.meta.env.PROD
  ? 'https://sovereignnshadowii.abacusai.app/api'  // Your Abacus URL
  : 'http://localhost:8000/api';
```

### Step 5: Configure DNS (if custom domain)

Point `sovereignnshadowii.abacusai.app` to:
- Frontend: `/` (static files)
- Backend: `/api/*` (Python functions)

## Architecture on Abacus

```
sovereignnshadowii.abacusai.app
├── / (React frontend - static)
├── /api/* (FastAPI backend - functions)
├── /dashboard (existing auth page)
└── Database (Abacus storage or Supabase)
```

## Database Migration

### Option A: Abacus Built-in Storage

```python
# Use Abacus's storage API
from abacus import Storage
storage = Storage()
storage.set("strategies", strategies_list)
```

### Option B: Supabase (Recommended for production)

```bash
# Install
pip install supabase

# Configure
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
```

```python
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Save strategy
supabase.table("strategies").insert(strategy).execute()
```

## Security Checklist

- [ ] All API keys in environment variables (not code)
- [ ] CORS restricted to your domain only
- [ ] Rate limiting enabled
- [ ] JWT authentication for sensitive endpoints
- [ ] HTTPS only in production

## Monitoring

Add these endpoints for observability:

- `/api/health` - System health
- `/api/metrics` - Performance metrics
- `/api/logs` - Recent activity

## Rollback Plan

If deployment fails:
1. Keep local system running as backup
2. Use ngrok tunnel: `ngrok http 8000`
3. Point frontend to ngrok URL temporarily

## Cost Estimate

| Service | Free Tier | Paid |
|---------|-----------|------|
| Abacus Functions | Limited | ~$20/mo |
| Supabase DB | 500MB | ~$25/mo |
| Vercel (alt) | Hobby free | ~$20/mo |

## Support

- Abacus docs: https://docs.abacus.ai
- Discord: Your trading community
- GitHub Issues: Your repo
