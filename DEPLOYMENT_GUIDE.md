# Deploying to GitHub & Running Live

## ✅ Yes, You Can Run This Live!

Here are your options for deploying this endurance racing tracker:

## Option 1: GitHub Pages + Backend on Render/Railway (Recommended)

### Frontend (GitHub Pages - FREE)
```bash
# 1. Create GitHub repository
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/endurance-racing-tracker.git
git push -u origin main

# 2. Enable GitHub Pages
# Go to Settings > Pages > Source: main branch > /frontend folder
```

### Backend (Render.com - FREE tier)
1. Create account at https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add environment variables (if needed)
6. Deploy!

**Your live URL**: `https://your-app.onrender.com`

---

## Option 2: Full Deployment on Railway (Easiest)

### Railway.app (FREE $5 credit/month)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize
railway init

# 4. Deploy
railway up
```

**Done!** Railway auto-detects Python and deploys everything.

---

## Option 3: Docker on Any Platform

### Using Docker Compose
```bash
# 1. Build and run
docker-compose up -d

# 2. Access at
http://localhost:8000/dashboard
```

**Deploy to:**
- **DigitalOcean App Platform** ($5/month)
- **AWS ECS** (pay-as-you-go)
- **Google Cloud Run** (free tier available)
- **Azure Container Instances**

---

## Option 4: Heroku (Simple but Paid)

### Heroku Deployment
```bash
# 1. Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create endurance-racing-tracker

# 4. Add Procfile
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 5. Deploy
git push heroku main

# 6. Open
heroku open
```

---

## 🚀 Recommended Setup for Live Racing

### Best Configuration:
1. **Frontend**: GitHub Pages (free, fast CDN)
2. **Backend**: Render.com (free tier, auto-sleep after 15 min)
3. **Database**: SQLite (included) or upgrade to PostgreSQL

### Why This Works:
- ✅ **100% Free** (with limitations)
- ✅ **Auto-scaling** during races
- ✅ **HTTPS** included
- ✅ **Easy updates** via git push

---

## 📝 Pre-Deployment Checklist

### 1. Update Frontend API URL
Edit `frontend/app.js`:
```javascript
// Change from localhost to your backend URL
const API_URL = 'https://your-backend.onrender.com';
```

### 2. Add CORS Support
Already included in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Environment Variables
Create `.env` file (already exists):
```env
WEC_TIMING_URL=https://timing.71wytham.org.uk/
IMSA_TIMING_URL=https://www.imsa.com/scoring/
```

### 4. Update Requirements
Your `requirements.txt` is ready!

---

## 🔥 Quick Deploy Commands

### Deploy to Render.com (Fastest)
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to render.com
# 3. Click "New Web Service"
# 4. Connect GitHub repo
# 5. Click "Create Web Service"
# Done in 2 minutes!
```

### Deploy to Railway
```bash
railway login
railway init
railway up
# Done!
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid |
|----------|-----------|------|
| **Render.com** | ✅ 750 hrs/month | $7/month |
| **Railway** | ✅ $5 credit/month | $5-20/month |
| **Heroku** | ❌ No free tier | $7/month |
| **DigitalOcean** | ❌ No free tier | $5/month |
| **Vercel** | ✅ Unlimited (frontend only) | Free |
| **GitHub Pages** | ✅ Unlimited (static) | Free |

---

## 🎯 Recommended: Render.com Setup

### Step-by-Step:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **Create Web Service**
   - Click "New +" → "Web Service"
   - Select your repository
   - Name: `endurance-racing-tracker`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

4. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes
   - Your app is live!

5. **Update Frontend**
   - Edit `frontend/app.js`
   - Change API_URL to your Render URL
   - Push changes

---

## 🌐 Your Live Dashboard

After deployment, your dashboard will be accessible at:
- **Render**: `https://endurance-racing-tracker.onrender.com/dashboard`
- **Railway**: `https://endurance-racing-tracker.up.railway.app/dashboard`
- **Heroku**: `https://endurance-racing-tracker.herokuapp.com/dashboard`

---

## 🔴 Live Race Monitoring

Once deployed:
1. ✅ Race monitor runs automatically
2. ✅ Detects live races every 5 minutes
3. ✅ Auto-starts scraping
4. ✅ Exports JSON when race ends
5. ✅ Video background works

**The system is production-ready!** 🏁

---

## 📞 Need Help?

Check deployment logs:
```bash
# Render
# View in dashboard: Logs tab

# Railway
railway logs

# Heroku
heroku logs --tail
```

**Your racing tracker can be live in under 5 minutes!** 🚀
