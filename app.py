"""
╔══════════════════════════════════════════════════════════╗
║       NAOMI'S BLOG — Flask Backend                       ║
║       A futuristic anime romance love diary              ║
║       Author: Made with love ♥                           ║
╚══════════════════════════════════════════════════════════╝

Run:  python app.py
Prod: gunicorn app:app --workers 2 --bind 0.0.0.0:5000
"""

import os
import json
import time
import hashlib
import datetime
from pathlib import Path
from functools import wraps

from flask import (
    Flask, render_template, jsonify, request,
    send_from_directory, abort, session, redirect, url_for
)
from flask_cors import CORS

# ─── App Setup ───────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "naomi-love-secret-key-change-in-prod")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ─── Config ──────────────────────────────────────────────
DATA_DIR       = Path("data")
POSTS_FILE     = DATA_DIR / "posts.json"
REACTIONS_FILE = DATA_DIR / "reactions.json"
SETTINGS_FILE  = DATA_DIR / "settings.json"
PLAYLIST_FILE  = DATA_DIR / "playlist.json"
MEMORIES_FILE  = DATA_DIR / "memories.json"

# Admin password (set via env or change here — use env in production!)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "naomi2024♥")

# ─── Ensure data directory exists ────────────────────────
DATA_DIR.mkdir(exist_ok=True)

# ─── Default data initializers ───────────────────────────
def init_data():
    """Create default data files if they don't exist."""

    if not POSTS_FILE.exists():
        POSTS_FILE.write_text(json.dumps(DEFAULT_POSTS, indent=2, ensure_ascii=False))

    if not REACTIONS_FILE.exists():
        REACTIONS_FILE.write_text(json.dumps({}, indent=2))

    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(json.dumps(DEFAULT_SETTINGS, indent=2, ensure_ascii=False))

    if not PLAYLIST_FILE.exists():
        PLAYLIST_FILE.write_text(json.dumps(DEFAULT_PLAYLIST, indent=2, ensure_ascii=False))

    if not MEMORIES_FILE.exists():
        MEMORIES_FILE.write_text(json.dumps(DEFAULT_MEMORIES, indent=2, ensure_ascii=False))


# ─── Default Content ─────────────────────────────────────
DEFAULT_SETTINGS = {
    "site_title":       "Naomi ✦ Digital Love Diary",
    "anniversary_date": "2024-02-14",
    "owner_name":       "Naomi",
    "partner_name":     "My Love",
    "tagline":          "My beautiful universe in one person ✦",
    "love_messages": [
        "Every love story is beautiful, but ours is my favorite...",
        "You are my favorite notification, my favorite distraction...",
        "This space was made for you — beautiful, warm, and full of light...",
        "Somewhere in every poem is your name, even when I don't write it...",
    ],
    "surprise_messages": [
        {"emoji": "💌", "msg": "Did you know that you are the most beautiful thing in my universe? Not poetically. Literally. Scientifically."},
        {"emoji": "🌸", "msg": "I was just thinking about you. I wanted you to know. That's all. You were on my mind and my mind has very good taste."},
        {"emoji": "✨", "msg": "Somewhere in my chest there is a feeling I don't have a word for yet. It only happens when I think about you."},
        {"emoji": "💜", "msg": "I love you in the morning before you're fully awake. I love you in the afternoon when you're tired. I love you always."},
        {"emoji": "🌙", "msg": "If I could bottle up the feeling of being with you, I'd make it the rarest thing in the world. Because it already is."},
    ],
    "reasons": [
        {"icon": "🌸", "text": "Your laugh fills every room with warmth I never want to leave"},
        {"icon": "✨", "text": "The way your eyes light up when you're excited about something small"},
        {"icon": "💜", "text": "How you make ordinary moments feel like beautiful memories"},
        {"icon": "🌙", "text": "Your kindness toward everyone, even strangers — it reveals your heart"},
        {"icon": "🎵", "text": "The way you hum softly when you're lost in thought"},
        {"icon": "🌺", "text": "Your strength — gentle and fierce at exactly the right moments"},
        {"icon": "☁️",  "text": "How you make my world softer, warmer, and infinitely more beautiful"},
        {"icon": "🦋", "text": "The dreams you carry — vast, luminous, and uniquely yours"},
        {"icon": "🌟", "text": "Being near you feels like coming home to a place I never want to leave"},
    ]
}

DEFAULT_POSTS = [
    {
        "id": 1, "pinned": True, "published": True,
        "category": "Love Notes",
        "date": "2025-05-12",
        "title": "Everything I Never Said Out Loud",
        "excerpt": "There are a thousand ways I try to say I love you every day — a look, a text, the way I reach for your hand...",
        "content": "<p>There are a thousand ways I try to say I love you every day — a look, a text, the way I reach for your hand without thinking about it. But sometimes the biggest feelings hide in the smallest gestures.</p><blockquote>You are not just someone I love. You are the reason I understand what love actually means.</blockquote><p>I watch you sometimes when you don't notice, and I think: how did I get so lucky? Not in a disbelieving way. In the way where luck feels too small a word and the universe feels like it conspired, softly, on my behalf.</p><p>You are my favorite thing about being alive, <em>Naomi</em>. Every single day.</p>",
        "created_at": "2025-05-12T10:00:00"
    },
    {
        "id": 2, "pinned": False, "published": True,
        "category": "Memories",
        "date": "2025-04-28",
        "title": "The Night We Got Lost on Purpose",
        "excerpt": "We said we knew where we were going. We absolutely did not. And it became one of my favorite memories...",
        "content": "<p>We said we knew where we were going. We absolutely did not. And somewhere between the wrong turn and the unexpected little garden we stumbled into, it became one of my favorite memories of us.</p><p>You weren't annoyed. You laughed. You took a photo of a cat sitting in a window. You said <em>adventures are just wrong turns you enjoy.</em></p><blockquote>Adventures are just wrong turns you enjoy. — Naomi, being perfect</blockquote>",
        "created_at": "2025-04-28T18:30:00"
    },
    {
        "id": 3, "pinned": False, "published": True,
        "category": "Poems",
        "date": "2025-04-10",
        "title": "Written in Starlight",
        "excerpt": "If I could write your name in the sky — not just in stars but in the space between them...",
        "content": "<p style='white-space:pre-line;font-style:italic;line-height:2.2;'>If I could write your name in the sky\nNot just in stars but in the space between them\nThe quiet dark that holds everything together\n\nI would write it in the language\nThe universe used before words existed\nBefore sound, before light —\n\nIn the moment before the first breath\nOf everything\n\nThat is where you live in me.\n\nAlways.</p>",
        "created_at": "2025-04-10T09:00:00"
    },
    {
        "id": 4, "pinned": False, "published": True,
        "category": "Daily Thoughts",
        "date": "2025-05-01",
        "title": "I Thought of You at 3pm for No Reason",
        "excerpt": "Completely unprompted, in the middle of an ordinary afternoon, my mind just quietly said: Naomi.",
        "content": "<p>Completely unprompted. No notification. No reminder. In the middle of an ordinary Tuesday afternoon — my mind just quietly said: <em>Naomi.</em></p><p>And everything felt a little softer after that.</p><p>I think that's what it means to love someone. They become the weather inside you. A soft, warm front that rolls in without warning and makes ordinary moments feel like they're lit from somewhere inside.</p>",
        "created_at": "2025-05-01T15:00:00"
    },
    {
        "id": 5, "pinned": False, "published": True,
        "category": "Future Dreams",
        "date": "2025-03-20",
        "title": "All the Futures I Want With You",
        "excerpt": "Morning coffee by a window somewhere we haven't been yet. A quiet house. Your laughter echoing...",
        "content": "<p>Morning coffee by a window somewhere we haven't been yet. A quiet house that slowly fills with the things we love. Your laughter echoing off walls that are ours.</p><blockquote>I don't need the whole world. I just need you in whatever world we build.</blockquote>",
        "created_at": "2025-03-20T08:00:00"
    },
    {
        "id": 6, "pinned": False, "published": True,
        "category": "Daily Thoughts",
        "date": "2025-05-08",
        "title": "Good Morning, My Favorite Person",
        "excerpt": "Before the day begins, before anything requires my attention, my first thought is always you.",
        "content": "<p>Before the day begins. Before anything requires my attention or energy or effort — my first thought is always you.</p><p>Not dramatically. Just quietly. Like a door opening to let in light.</p><p>Good morning, <em>Naomi</em>. I hope today is as beautiful as you are.</p>",
        "created_at": "2025-05-08T07:00:00"
    }
]

DEFAULT_PLAYLIST = [
    {"id": 1, "title": "Ethereal Love",        "artist": "Soft Romance OST",    "emoji": "🎵", "pinned": True,  "url": ""},
    {"id": 2, "title": "Sakura Rain",           "artist": "Anime Piano Covers",  "emoji": "🌸", "pinned": False, "url": ""},
    {"id": 3, "title": "Our Quiet Universe",    "artist": "Lo-fi Romance",       "emoji": "💜", "pinned": False, "url": ""},
    {"id": 4, "title": "Holographic Heart",     "artist": "Future Ambient",      "emoji": "💎", "pinned": False, "url": ""},
    {"id": 5, "title": "Promise Under Stars",   "artist": "Cinematic Piano",     "emoji": "⭐", "pinned": False, "url": ""},
    {"id": 6, "title": "Tender Moments",        "artist": "Studio Ghibli Vibes", "emoji": "🌿", "pinned": False, "url": ""},
]

DEFAULT_MEMORIES = [
    {"date": "The Beginning",      "emoji": "✨", "title": "The Day I Met You",        "desc": "A meeting that quietly changed everything."},
    {"date": "First Laugh",        "emoji": "😄", "title": "When I Knew",              "desc": "Your laugh did something to me I still can't explain."},
    {"date": "First Adventure",    "emoji": "🌙", "title": "Under the Same Sky",       "desc": "We looked up at the same stars and I thought: never alone again."},
    {"date": "The Promise",        "emoji": "💜", "title": "When We Said Forever",     "desc": "Not loud. Not dramatic. Just quiet and certain, the way true things are."},
    {"date": "Today",              "emoji": "🌸", "title": "Still Here, Still Us",     "desc": "Every day with you is both the same and new. That's the magic."},
]


# ─── Helpers ─────────────────────────────────────────────
def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def next_id(items: list) -> int:
    return max((i.get("id", 0) for i in items), default=0) + 1

# ─── Admin auth decorator ────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════════
#  ROUTES — Pages
# ══════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the main blog page."""
    return send_from_directory(".", "index.html")


@app.route("/admin")
def admin_page():
    """Serve the admin panel page."""
    if not session.get("admin"):
        return redirect(url_for("admin_login_page"))
    return send_from_directory(".", "admin.html")


@app.route("/admin/login")
def admin_login_page():
    return send_from_directory(".", "login.html")


# ══════════════════════════════════════════════════════════
#  API — Auth
# ══════════════════════════════════════════════════════════

@app.route("/api/login", methods=["POST"])
def api_login():
    """Admin login endpoint."""
    data = request.get_json()
    if data and data.get("password") == ADMIN_PASSWORD:
        session["admin"] = True
        return jsonify({"success": True, "message": "Welcome back, love ♥"})
    return jsonify({"success": False, "message": "Incorrect password"}), 401


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("admin", None)
    return jsonify({"success": True})


@app.route("/api/auth/status")
def auth_status():
    return jsonify({"admin": bool(session.get("admin"))})


# ══════════════════════════════════════════════════════════
#  API — Settings
# ══════════════════════════════════════════════════════════

@app.route("/api/settings")
def get_settings():
    """Return public site settings."""
    settings = read_json(SETTINGS_FILE)
    return jsonify(settings)


@app.route("/api/settings", methods=["PUT"])
@admin_required
def update_settings():
    """Update site settings (admin only)."""
    data = request.get_json()
    settings = read_json(SETTINGS_FILE)
    settings.update(data)
    write_json(SETTINGS_FILE, settings)
    return jsonify({"success": True, "settings": settings})


# ══════════════════════════════════════════════════════════
#  API — Blog Posts
# ══════════════════════════════════════════════════════════

@app.route("/api/posts")
def get_posts():
    """Return all published posts, optionally filtered by category."""
    posts    = read_json(POSTS_FILE)
    category = request.args.get("category")
    search   = request.args.get("q", "").lower()

    # Filter by published
    posts = [p for p in posts if p.get("published", True)]

    # Filter by category
    if category and category != "all":
        posts = [p for p in posts if p["category"].lower() == category.lower()]

    # Search
    if search:
        posts = [
            p for p in posts
            if search in p["title"].lower()
            or search in p.get("excerpt", "").lower()
            or search in p.get("content", "").lower()
        ]

    # Sort: pinned first, then by date desc
    posts.sort(key=lambda p: (not p.get("pinned", False), p.get("date", "")), reverse=True)
    # Fix sort: pinned should come first so reverse only on date for non-pinned
    pinned    = [p for p in posts if p.get("pinned")]
    unpinned  = [p for p in posts if not p.get("pinned")]
    unpinned.sort(key=lambda p: p.get("date", ""), reverse=True)
    posts = pinned + unpinned

    return jsonify({"posts": posts, "total": len(posts)})


@app.route("/api/posts/<int:post_id>")
def get_post(post_id):
    """Return a single post by ID."""
    posts = read_json(POSTS_FILE)
    post  = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        abort(404)
    return jsonify(post)


@app.route("/api/posts", methods=["POST"])
@admin_required
def create_post():
    """Create a new blog post."""
    data  = request.get_json()
    posts = read_json(POSTS_FILE)

    new_post = {
        "id":         next_id(posts),
        "pinned":     data.get("pinned", False),
        "published":  data.get("published", True),
        "category":   data.get("category", "Daily Thoughts"),
        "date":       data.get("date", datetime.date.today().isoformat()),
        "title":      data.get("title", "Untitled"),
        "excerpt":    data.get("excerpt", ""),
        "content":    data.get("content", ""),
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
    }
    posts.append(new_post)
    write_json(POSTS_FILE, posts)
    return jsonify({"success": True, "post": new_post}), 201


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
@admin_required
def update_post(post_id):
    """Update an existing post."""
    data  = request.get_json()
    posts = read_json(POSTS_FILE)
    post  = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        abort(404)

    updatable = ["title","excerpt","content","category","date","pinned","published"]
    for key in updatable:
        if key in data:
            post[key] = data[key]
    post["updated_at"] = datetime.datetime.now().isoformat()

    write_json(POSTS_FILE, posts)
    return jsonify({"success": True, "post": post})


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
@admin_required
def delete_post(post_id):
    """Delete a post."""
    posts    = read_json(POSTS_FILE)
    filtered = [p for p in posts if p["id"] != post_id]
    if len(filtered) == len(posts):
        abort(404)
    write_json(POSTS_FILE, filtered)
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════
#  API — Reactions
# ══════════════════════════════════════════════════════════

@app.route("/api/reactions/<int:post_id>")
def get_reactions(post_id):
    reactions = read_json(REACTIONS_FILE)
    return jsonify(reactions.get(str(post_id), {"♥": 0, "✨": 0, "🌸": 0}))


@app.route("/api/reactions/<int:post_id>", methods=["POST"])
def add_reaction(post_id):
    data      = request.get_json()
    emoji     = data.get("emoji", "♥")
    reactions = read_json(REACTIONS_FILE)
    key       = str(post_id)

    if key not in reactions:
        reactions[key] = {"♥": 0, "✨": 0, "🌸": 0}
    reactions[key][emoji] = reactions[key].get(emoji, 0) + 1
    write_json(REACTIONS_FILE, reactions)
    return jsonify({"success": True, "reactions": reactions[key]})


# ══════════════════════════════════════════════════════════
#  API — Playlist
# ══════════════════════════════════════════════════════════

@app.route("/api/playlist")
def get_playlist():
    playlist = read_json(PLAYLIST_FILE)
    # Daily rotation: select starting index based on day of year
    day_index = datetime.date.today().timetuple().tm_yday % len(playlist)
    return jsonify({
        "playlist":    playlist,
        "daily_start": day_index,
        "total":       len(playlist)
    })


@app.route("/api/playlist", methods=["POST"])
@admin_required
def add_song():
    data     = request.get_json()
    playlist = read_json(PLAYLIST_FILE)
    song = {
        "id":     next_id(playlist),
        "title":  data.get("title", "Unknown"),
        "artist": data.get("artist", "Unknown"),
        "emoji":  data.get("emoji", "🎵"),
        "pinned": data.get("pinned", False),
        "url":    data.get("url", ""),
    }
    playlist.append(song)
    write_json(PLAYLIST_FILE, playlist)
    return jsonify({"success": True, "song": song}), 201


@app.route("/api/playlist/<int:song_id>", methods=["DELETE"])
@admin_required
def delete_song(song_id):
    playlist = read_json(PLAYLIST_FILE)
    filtered = [s for s in playlist if s["id"] != song_id]
    write_json(PLAYLIST_FILE, filtered)
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════
#  API — Memories / Timeline
# ══════════════════════════════════════════════════════════

@app.route("/api/memories")
def get_memories():
    return jsonify(read_json(MEMORIES_FILE))


@app.route("/api/memories", methods=["POST"])
@admin_required
def add_memory():
    data     = request.get_json()
    memories = read_json(MEMORIES_FILE)
    memories.append({
        "date":  data.get("date", ""),
        "emoji": data.get("emoji", "✨"),
        "title": data.get("title", ""),
        "desc":  data.get("desc", ""),
    })
    write_json(MEMORIES_FILE, memories)
    return jsonify({"success": True}), 201


# ══════════════════════════════════════════════════════════
#  API — Countdown
# ══════════════════════════════════════════════════════════

@app.route("/api/countdown")
def get_countdown():
    """Return time until next anniversary."""
    settings = read_json(SETTINGS_FILE)
    ann_str  = settings.get("anniversary_date", "2024-02-14")

    try:
        ann   = datetime.datetime.strptime(ann_str, "%Y-%m-%d")
        now   = datetime.datetime.now()
        next_ann = ann.replace(year=now.year)
        if next_ann <= now:
            next_ann = next_ann.replace(year=now.year + 1)

        diff     = next_ann - now
        total_s  = int(diff.total_seconds())
        days     = diff.days
        hours    = (total_s % 86400) // 3600
        minutes  = (total_s % 3600) // 60
        seconds  = total_s % 60
        months   = (next_ann.year - now.year) * 12 + (next_ann.month - now.month)

        # Days together
        start       = datetime.datetime.strptime(ann_str, "%Y-%m-%d")
        days_together = (now - start).days

    except Exception:
        months = days = hours = minutes = seconds = days_together = 0

    return jsonify({
        "months":        months,
        "days":          days,
        "hours":         hours,
        "minutes":       minutes,
        "seconds":       seconds,
        "days_together": days_together,
        "anniversary":   ann_str,
    })


# ══════════════════════════════════════════════════════════
#  API — Daily Message (AI-powered via Anthropic if key set)
# ══════════════════════════════════════════════════════════

@app.route("/api/daily-message")
def daily_message():
    """Return a romantic daily message. Uses AI if ANTHROPIC_API_KEY is set."""
    settings = read_json(SETTINGS_FILE)
    name     = settings.get("owner_name", "Naomi")

    # Try AI generation if key available
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            today  = datetime.date.today().strftime("%B %d")
            msg    = client.messages.create(
                model      = "claude-haiku-4-5-20251001",
                max_tokens = 120,
                messages   = [{
                    "role": "user",
                    "content": (
                        f"Write a single short romantic message (2-3 sentences max) "
                        f"for {name} on {today}. Make it poetic, warm, and specific to "
                        f"the day. No greeting needed. Just the message."
                    )
                }]
            )
            return jsonify({
                "message": msg.content[0].text.strip(),
                "ai":      True,
                "date":    today
            })
        except Exception:
            pass  # Fall through to static messages

    # Static fallback — rotates daily
    messages = settings.get("love_messages", ["Thinking of you always ♥"])
    day_idx  = datetime.date.today().timetuple().tm_yday % len(messages)
    return jsonify({
        "message": messages[day_idx],
        "ai":      False,
        "date":    datetime.date.today().strftime("%B %d")
    })


# ══════════════════════════════════════════════════════════
#  Static file serving (for dev; in prod use nginx)
# ══════════════════════════════════════════════════════════

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


@app.route("/favicon.ico")
def favicon():
    return "♥", 200, {"Content-Type": "text/plain"}


# ══════════════════════════════════════════════════════════
#  Error handlers
# ══════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500


# ══════════════════════════════════════════════════════════
#  Startup
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_data()
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    print(f"\n  ♥  Naomi's Blog is running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
