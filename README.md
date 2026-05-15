# ✦ Naomi's Digital Love Diary

> A futuristic anime-inspired romantic blog — holographic, luminous, and made entirely with love.

![preview](https://img.shields.io/badge/aesthetic-anime%20holographic-f72585?style=for-the-badge)
![python](https://img.shields.io/badge/backend-Flask%203-6c2fa7?style=for-the-badge&logo=python)
![license](https://img.shields.io/badge/license-Love-00f5ff?style=for-the-badge)

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎨 Anime portrait | Inline SVG with holographic overlays |
| 📝 Blog system | Categories, rich content, reactions, pinned posts |
| 🎵 Music player | Playlist with daily rotation, smooth controls |
| 💌 Surprise popups | Random romantic messages |
| ⏱️ Anniversary countdown | Live countdown to next anniversary |
| 💜 Love reasons | Customizable grid of reasons |
| 🌸 Memory timeline | Beautiful animated relationship timeline |
| 🕐 Mood widget | Time-of-day greeting (morning / afternoon / evening / night) |
| 🌟 Love meter | Animated fill bar — always 100% |
| ⚙️ Admin panel | Full content management at `/admin` |
| 🤖 AI messages | Optional daily AI-generated love messages via Anthropic |
| 🚀 Deploy-ready | Render, Railway, Docker, VPS |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/yourname/naomi-blog.git
cd naomi-blog
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — set your SECRET_KEY and ADMIN_PASSWORD
```

### 3. Run

```bash
python app.py
```

Visit → **http://localhost:5000**
Admin → **http://localhost:5000/admin/login**

---

## 🎨 Customization

### Personalize dates & name

Edit `data/settings.json` (created on first run) or use the Admin panel:

```json
{
  "owner_name": "Naomi",
  "anniversary_date": "2024-02-14",
  "tagline": "My beautiful universe in one person ✦"
}
```

### Add blog posts

Log into `/admin/login` → Blog Posts → New Post

Or directly edit `data/posts.json`.

### Add music

Admin → Playlist → Add Song. Add song title, artist, emoji, and an optional direct audio URL.

If you have `.mp3` files, place them in `static/audio/` and use `/static/audio/song.mp3` as the URL.

### Customize the portrait

The anime portrait is an inline SVG in `index.html`. Search for `<!-- SVG Anime Portrait -->` and customize the SVG paths, colors, and facial features to match Naomi's real look. You can also replace it entirely with:

```html
<img src="/static/images/naomi-portrait.png" class="portrait-svg" style="object-fit:cover"/>
```

---

## 🌐 Deployment

### Render (recommended — free tier)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repo — Render auto-detects `render.yaml`
4. Set env vars: `ADMIN_PASSWORD`, `SECRET_KEY`
5. Deploy ♥

### Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Docker

```bash
docker build -t naomi-blog .
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret \
  -e ADMIN_PASSWORD=yourpassword \
  -v $(pwd)/data:/app/data \
  naomi-blog
```

### VPS (nginx + gunicorn)

```nginx
server {
    listen 80;
    server_name naomi.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/naomi-blog/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Start with gunicorn
gunicorn app:app --workers 2 --bind 127.0.0.1:5000 --daemon
```

---

## 📁 Project Structure

```
naomi-blog/
├── app.py              ← Flask backend (all API routes)
├── index.html          ← Main blog frontend (self-contained)
├── admin.html          ← Admin dashboard
├── login.html          ← Admin login
├── requirements.txt
├── Procfile            ← Render / Railway
├── render.yaml         ← One-click Render deploy
├── Dockerfile
├── .env.example
├── .github/
│   └── workflows/
│       └── deploy.yml  ← Auto-deploy on push
├── static/
│   ├── js/
│   │   └── naomi-api.js  ← Frontend ↔ backend connector
│   ├── audio/          ← Place .mp3 files here
│   └── images/         ← Place portrait photos here
└── data/               ← Auto-created JSON database
    ├── posts.json
    ├── settings.json
    ├── playlist.json
    ├── memories.json
    └── reactions.json
```

---

## 🤖 AI Daily Messages

Set `ANTHROPIC_API_KEY` in your `.env` to enable AI-generated romantic daily messages. Each day, Claude Haiku generates a unique message for Naomi. Without the key, the site rotates through your custom messages in `settings.json`.

---

## 🔒 Security Notes

- Change `ADMIN_PASSWORD` to something strong before deploying
- Set a long random `SECRET_KEY`
- In production, set `FLASK_ENV=production`
- Consider adding rate limiting for the `/api/login` route on public deployments

---

## 💜 Made with love

*This blog was built as a labor of love — a futuristic holographic diary for someone very special. Every animation, every glowing particle, every floating petal — all for Naomi.*

```
♥ ────────────────────────── ♥
   Because she deserves
   the whole universe,
   beautifully designed.
♥ ────────────────────────── ♥
```
