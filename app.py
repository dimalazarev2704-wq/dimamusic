
from flask import Flask, request, render_template_string
from urllib.parse import urlparse, quote, parse_qs
from html import escape
import requests
import re

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DimaMusic</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 32px 18px;
            background: #10101b;
            color: #f6f3ff;
            font-family: Arial, sans-serif;
        }
        main { max-width: 720px; margin: 20px auto; }
        h1 { font-size: 38px; margin-bottom: 6px; }
        .muted { color: #b7b4cc; }
        .card {
            background: #1c1c2d;
            border: 1px solid #37364c;
            padding: 23px;
            border-radius: 18px;
            margin-top: 20px;
        }
        input, button {
            width: 100%;
            padding: 14px;
            margin-top: 12px;
            border-radius: 10px;
            font-size: 16px;
        }
        input {
            color: white;
            background: #11111d;
            border: 1px solid #55536c;
        }
        button {
            border: 0;
            background: #ae9bff;
            color: #171326;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { background: #c2b5ff; }
        .result {
            border-left: 4px solid #ae9bff;
            padding: 12px 16px;
            margin-top: 20px;
            background: #24243a;
            border-radius: 8px;
            overflow-wrap: anywhere;
        }
        a { color: #c4b7ff; }
        .label { color: #b7b4cc; font-size: 13px; }
        .value { font-size: 18px; margin: 5px 0 14px; }
    </style>
</head>
<body>
<main>
    <h1>🎵 DimaMusic</h1>
    <p class="muted">Your music. Your library. Your rules.</p>

    <section class="card">
        <h2>🔗 Find music details</h2>
        <p class="muted">
            Paste a YouTube or Spotify link to identify its content.
        </p>
        <form method="post" action="/recognize">
            <input type="url" name="link"
                   placeholder="Paste a music link here"
                   required>
            <button type="submit">Recognize link</button>
        </form>

        {% if result %}
        <div class="result" role="status">
            <p><strong>{{ result.service }}</strong></p>
            <p class="label">Content type</p>
            <p class="value">{{ result.kind }}</p>

            {% if result.title %}
            <p class="label">Title</p>
            <p class="value">{{ result.title }}</p>
            {% endif %}

            {% if result.creator %}
            <p class="label">Channel / creator</p>
            <p class="value">{{ result.creator }}</p>
            {% endif %}

            {% if result.item_id %}
            <p class="label">Content ID</p>
            <p class="value">{{ result.item_id }}</p>
            {% endif %}

            <p>{{ result.message }}</p>
            <p><a href="{{ result.url }}" target="_blank"
                  rel="noopener noreferrer">Open original link ↗</a></p>
        </div>
        {% endif %}
    </section>

    <section class="card">
        <h2>🎧 My Library</h2>
        <p class="muted">
            Your library feature is coming next. This version recognizes
            links; it does not extract audio from streaming services.
        </p>
    </section>
</main>
</body>
</html>
"""


def identify_link(raw_link):
    """Validate and classify supported music links."""
    parsed = urlparse(raw_link.strip())
    host = (parsed.hostname or "").lower()
    path = parsed.path.strip("/")
    query = parse_qs(parsed.query)

    if parsed.scheme not in ("http", "https"):
        return {"error": "Please enter a valid HTTP or HTTPS link."}

    # YouTube
    youtube_hosts = {
        "youtube.com", "www.youtube.com", "m.youtube.com",
        "music.youtube.com", "youtu.be", "www.youtu.be"
    }

    if host in youtube_hosts:
        video_id = None
        kind = "YouTube video"

        if host.endswith("youtu.be"):
            video_id = path.split("/")[0] if path else None
        elif path.startswith("shorts/"):
            kind = "YouTube Short"
            video_id = path.split("/", 1)[1].split("/")[0]
        elif path.startswith("live/"):
            kind = "YouTube live video"
            video_id = path.split("/", 1)[1].split("/")[0]
        elif path == "watch":
            video_id = query.get("v", [None])[0]
        elif path.startswith("embed/"):
            video_id = path.split("/", 1)[1].split("/")[0]
        elif path.startswith("playlist"):
            playlist_id = query.get("list", [None])[0]
            return {
                "service": "YouTube",
                "kind": "Playlist",
                "item_id": playlist_id,
                "title": None,
                "creator": None,
                "url": raw_link,
                "message": "Playlist recognized. Open YouTube to view its details."
            }

        if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id):
            return {"error": "That looks like a YouTube link, but no valid video ID was found."}

        result = {
            "service": "YouTube",
            "kind": kind,
            "item_id": video_id,
            "title": None,
            "creator": None,
            "url": f"https://www.youtube.com/watch?v={quote(video_id)}",
            "message": "Video recognized."
        }

        # YouTube oEmbed supplies the video title and channel name
        # for supported public videos. It does not verify the song artist.
        try:
            oembed_url = (
                "https://www.youtube.com/oembed?url="
                + quote(result["url"], safe="")
                + "&format=json"
            )
            response = requests.get(
                oembed_url,
                timeout=8,
                headers={"User-Agent": "DimaMusic/1.0"}
            )
            response.raise_for_status()
            details = response.json()
            result["title"] = details.get("title")
            result["creator"] = details.get("author_name")
            result["message"] = (
                "Video details retrieved. The channel may not be the song artist."
            )
        except (requests.RequestException, ValueError):
            result["message"] = (
                "Video recognized, but its details could not be retrieved. "
                "It may be private, unavailable, or unsupported."
            )

        return result

    # Spotify
    spotify_hosts = {"spotify.com", "open.spotify.com"}
    if host in spotify_hosts:
        parts = path.split("/")
        kind = None
        item_id = None

        for index, part in enumerate(parts):
            if part in {"track", "album", "playlist", "artist", "episode", "show"}:
                kind = part.capitalize()
                if index + 1 < len(parts):
                    item_id = parts[index + 1].split("?")[0]
                break

        if not kind or not item_id:
            return {
                "error": "Spotify link recognized, but the content type or ID was not found."
            }

        return {
            "service": "Spotify",
            "kind": f"Spotify {kind}",
            "item_id": item_id,
            "title": None,
            "creator": None,
            "url": raw_link,
            "message": (
                "Spotify content recognized. Its title and artist require "
                "metadata from Spotify's API or another authorized source."
            )
        }

    return {"error": "This link isn't from a supported YouTube or Spotify domain."}


@app.route("/", methods=["GET"])
def home():
    return render_template_string(PAGE, result=None)


@app.route("/recognize", methods=["POST"])
def recognize():
    link = request.form.get("link", "").strip()

    if len(link) > 2048:
        return render_template_string(
            PAGE,
            result={
                "service": "Link error",
                "kind": "Invalid link",
                "item_id": None,
                "title": None,
                "creator": None,
                "url": "/",
                "message": "Please enter a shorter link."
            }
        )

    data = identify_link(link)

    if "error" in data:
        data = {
            "service": "Link error",
            "kind": "Not recognized",
            "item_id": None,
            "title": None,
            "creator": None,
            "url": "/",
            "message": data["error"]
        }

    return render_template_string(PAGE, result=data)


if __name__ == "__main__":
    app.run(debug=True)
