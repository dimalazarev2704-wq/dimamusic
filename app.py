from flask import Flask, render_template_string, request
from urllib.parse import parse_qs, urlparse
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DimaMusic</title>
    <style>
        :root {
            color-scheme: dark;
            --bg: #0d0e13;
            --panel: #171922;
            --line: rgba(255, 255, 255, .09);
            --text: #f7f6fb;
            --muted: #a5a5b5;
            --purple: #b19aff;
            --green: #b6f09c;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            color: var(--text);
            background:
                radial-gradient(ellipse at 75% 0%, rgba(112, 76, 198, .18), transparent 38rem),
                radial-gradient(ellipse at 0% 55%, rgba(41, 105, 80, .1), transparent 32rem),
                var(--bg);
            font: 15px/1.55 Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
        }

        a { color: inherit; }

        .topbar {
            width: min(1120px, calc(100% - 44px));
            height: 82px;
            margin: auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255, 255, 255, .07);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 11px;
            color: var(--text);
            text-decoration: none;
            font-size: 19px;
            font-weight: 750;
            letter-spacing: -.03em;
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 36px;
            height: 36px;
            border-radius: 12px;
            color: #191525;
            background: linear-gradient(145deg, #d4c5ff, #a78bfa 65%, #8b70e8);
            box-shadow: 0 5px 22px rgba(160, 132, 255, .2);
            font-size: 19px;
        }

        .top-note { color: var(--muted); font-size: 13px; }

        main {
            width: min(1040px, calc(100% - 44px));
            margin: auto;
            padding: 72px 0 70px;
        }

        .hero { max-width: 720px; margin-bottom: 34px; }

        .eyebrow {
            color: var(--green);
            font-size: 12px;
            font-weight: 750;
            letter-spacing: .14em;
            text-transform: uppercase;
        }

        h1 {
            margin: 13px 0 14px;
            font-size: clamp(38px, 6vw, 64px);
            line-height: 1.05;
            letter-spacing: -.055em;
        }

        .hero p {
            max-width: 610px;
            margin: 0;
            color: var(--muted);
            font-size: 17px;
        }

        .layout {
            display: grid;
            grid-template-columns: minmax(0, 1.55fr) minmax(250px, .8fr);
            gap: 18px;
            align-items: stretch;
        }

        .card {
            border: 1px solid var(--line);
            border-radius: 20px;
            background: linear-gradient(145deg, rgba(29, 32, 42, .96), rgba(20, 22, 30, .98));
            box-shadow: 0 20px 60px rgba(0, 0, 0, .16);
        }

        .recognizer { padding: 28px; }

        .section-heading {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            margin-bottom: 24px;
        }

        .icon-box {
            flex: none;
            display: grid;
            place-items: center;
            width: 44px;
            height: 44px;
            border: 1px solid rgba(177, 154, 255, .2);
            border-radius: 14px;
            color: var(--purple);
            background: rgba(177, 154, 255, .09);
            font-size: 21px;
        }

        h2 { margin: 0; font-size: 19px; letter-spacing: -.025em; }

        .section-heading p {
            margin: 4px 0 0;
            color: var(--muted);
            font-size: 13px;
        }

        label {
            display: block;
            margin-bottom: 9px;
            color: #dedde7;
            font-size: 13px;
            font-weight: 650;
        }

        .input-row { display: flex; gap: 10px; }

        input {
            flex: 1;
            min-width: 0;
            height: 52px;
            padding: 0 15px;
            border: 1px solid rgba(255, 255, 255, .12);
            border-radius: 12px;
            outline: none;
            color: var(--text);
            background: #101219;
            font: inherit;
        }

        input::placeholder { color: #777989; }

        input:focus {
            border-color: var(--purple);
            box-shadow: 0 0 0 3px rgba(177, 154, 255, .12);
        }

        button {
            flex: none;
            min-width: 138px;
            height: 52px;
            padding: 0 17px;
            border: 0;
            border-radius: 12px;
            color: #1b1725;
            background: linear-gradient(135deg, #d0c0ff, #a78bfa);
            font: inherit;
            font-size: 14px;
            font-weight: 750;
            cursor: pointer;
            box-shadow: 0 7px 20px rgba(167, 139, 250, .2);
            transition: transform .16s, filter .16s;
        }

        button:hover { filter: brightness(1.08); transform: translateY(-1px); }

        .hint { margin: 11px 0 0; color: #858696; font-size: 12px; }

        .services {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 25px;
            padding-top: 21px;
            border-top: 1px solid var(--line);
        }

        .pill {
            padding: 6px 10px;
            border: 1px solid var(--line);
            border-radius: 99px;
            color: #c5c4d0;
            background: rgba(255, 255, 255, .025);
            font-size: 12px;
        }

        .side-card {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 100%;
            padding: 25px;
        }

        .side-card h2 { margin-top: 16px; font-size: 18px; }
        .side-card p { color: var(--muted); font-size: 13px; }
        .side-icon { font-size: 29px; }

        .mini-note {
            margin-top: 20px;
            padding: 13px 14px;
            border-radius: 12px;
            color: #c2bdcf;
            background: rgba(255, 255, 255, .045);
            font-size: 12px;
        }

        .result { margin-top: 18px; padding: 23px 26px; }

        .result-title {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 17px;
        }

        .result-title h2 { font-size: 18px; }

        .result-grid {
            display: grid;
            grid-template-columns: 120px 1fr;
            gap: 9px 15px;
            margin: 0;
            font-size: 13px;
        }

        .result-grid dt { color: var(--muted); }
        .result-grid dd { min-width: 0; margin: 0; overflow-wrap: anywhere; }
        .title-hint { color: #ded5ff; }

        .result-foot {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            margin-top: 20px;
            padding-top: 17px;
            border-top: 1px solid var(--line);
        }

        .result-foot p { margin: 0; color: var(--muted); font-size: 12px; }

        .open-link {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            color: var(--purple);
            font-size: 13px;
            font-weight: 700;
            text-decoration: none;
            white-space: nowrap;
        }

        .open-link:hover { text-decoration: underline; }
        .error { color: #ffaaaa; }

        footer {
            width: min(1040px, calc(100% - 44px));
            margin: auto;
            padding: 18px 0 28px;
            border-top: 1px solid rgba(255, 255, 255, .06);
            color: #737584;
            font-size: 12px;
        }

        @media (max-width: 720px) {
            main { padding-top: 48px; }
            .layout { grid-template-columns: 1fr; }
            .side-card { min-height: 220px; }
        }

        @media (max-width: 520px) {
            .topbar, main, footer { width: calc(100% - 30px); }
            .topbar { height: 68px; }
            .top-note { font-size: 11px; }
            main { padding-top: 38px; }
            .hero p { font-size: 15px; }
            .recognizer { padding: 21px; }
            .input-row { flex-direction: column; }
            button { width: 100%; }
            .result-foot { align-items: flex-start; flex-direction: column; }
        }
    </style>
</head>
<body>
    <header class="topbar">
        <a class="brand" href="/" aria-label="DimaMusic home">
            <span class="brand-mark">♫</span><span>DimaMusic</span>
        </a>
        <span class="top-note">Your music, in one place</span>
    </header>

    <main>
        <section class="hero">
            <div class="eyebrow">Your personal music space</div>
            <h1>Find the music<br>behind the link.</h1>
            <p>Drop in a YouTube or Spotify link and DimaMusic will tell you what it points to, then take you straight to the source.</p>
        </section>

        <div class="layout">
            <section class="card recognizer">
                <div class="section-heading">
                    <div class="icon-box">↗</div>
                    <div>
                        <h2>Recognize a music link</h2>
                        <p>Paste a link to see its service and details.</p>
                    </div>
                </div>

                <form action="/recognize" method="post">
                    <label for="music-link">Music link</label>
                    <div class="input-row">
                        <input id="music-link" type="url" name="link"
                               placeholder="https://open.spotify.com/..." required>
                        <button type="submit">Check link <span aria-hidden="true">→</span></button>
                    </div>
                    <p class="hint">Works with YouTube videos and Shorts, plus Spotify tracks, albums, playlists, and artists.</p>
                </form>

                <div class="services" aria-label="Supported services">
                    <span class="pill">▶ YouTube</span>
                    <span class="pill">♫ Spotify</span>
                    <span class="pill">Private by design</span>
                </div>
            </section>

            <aside class="card side-card">
                <div>
                    <div class="side-icon">🎧</div>
                    <h2>A little more context.<br>A lot less guesswork.</h2>
                    <p>See the link type and its service ID at a glance. If the URL includes a title hint, we’ll show it as a hint—never as verified song information.</p>
                </div>
                <div class="mini-note">DimaMusic opens the original page on YouTube or Spotify. A link doesn’t contain downloadable audio.</div>
            </aside>
        </div>

        {% if result %}
        <section class="card result" aria-live="polite">
            {% if result.error %}
                <div class="result-title">
                    <span class="icon-box error">!</span>
                    <h2 class="error">{{ result.error }}</h2>
                </div>
            {% else %}
                <div class="result-title">
                    <span class="icon-box">{{ result.emoji }}</span>
                    <h2>{{ result.service }} {{ result.kind }} found</h2>
                </div>
                <dl class="result-grid">
                    <dt>Service</dt><dd>{{ result.service }}</dd>
                    <dt>Link type</dt><dd>{{ result.kind }}</dd>
                    <dt>Link ID</dt><dd>{{ result.item_id }}</dd>
                    {% if result.title_hint %}
                        <dt>Title hint</dt><dd class="title-hint">{{ result.title_hint }}</dd>
                    {% endif %}
                </dl>
                <div class="result-foot">
                    <p>This identifies a {{ result.kind|lower }}. It does not provide downloadable audio.</p>
                    <a class="open-link" href="{{ result.open_url }}" target="_blank" rel="noopener noreferrer">
                        Open on {{ result.service }} <span aria-hidden="true">↗</span>
                    </a>
                </div>
            {% endif %}
        </section>
        {% endif %}
    </main>

    <footer>DimaMusic · Your music. Your library. Your rules.</footer>
</body>
</html>
"""

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
SPOTIFY_HOSTS = {"spotify.com", "www.spotify.com", "open.spotify.com"}
SPOTIFY_TYPES = {"track": "Track", "album": "Album", "playlist": "Playlist", "artist": "Artist"}
YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{6,}$")
SPOTIFY_ID = re.compile(r"^[A-Za-z0-9]{10,64}$")


def title_hint(parsed):
    """Return a short hint only when the URL explicitly includes title=..."""
    values = parse_qs(parsed.query, keep_blank_values=False).get("title", [])
    if not values:
        return None
    hint = " ".join(values[0].split())
    hint = "".join(char for char in hint if char.isprintable())[:120]
    return hint or None


def recognize_link(link):
    try:
        parsed = urlparse(link.strip())
        host = (parsed.hostname or "").lower().rstrip(".")
        _ = parsed.port
    except ValueError:
        return {"error": "Please enter a valid web link."}

    if parsed.scheme not in ("http", "https") or not host or parsed.username or parsed.password:
        return {"error": "Please enter a valid http or https music link."}

    segments = [part for part in parsed.path.split("/") if part]
    query = parse_qs(parsed.query)
    hint = title_hint(parsed)

    if host == "youtu.be" or host in YOUTUBE_HOSTS:
        item_id = None
        if host == "youtu.be":
            item_id = segments[0] if segments else None
        elif segments and segments[0] == "watch":
            item_id = query.get("v", [None])[0]
        elif len(segments) >= 2 and segments[0] in {"shorts", "embed", "live"}:
            item_id = segments[1]

        if not item_id or not YOUTUBE_ID.fullmatch(item_id):
            return {"error": "That YouTube link doesn't contain a recognizable video."}

        return {
            "service": "YouTube",
            "emoji": "▶",
            "kind": "Video",
            "item_id": item_id,
            "open_url": f"https://www.youtube.com/watch?v={item_id}",
            "title_hint": hint,
        }

    if host in SPOTIFY_HOSTS:
        if len(segments) >= 2 and segments[0] == "intl-en":
            segments = segments[1:]

        if len(segments) >= 2 and segments[0] in SPOTIFY_TYPES:
            link_type, item_id = segments[0], segments[1]
            if not SPOTIFY_ID.fullmatch(item_id):
                return {"error": "That Spotify link doesn't contain a recognizable item ID."}

            return {
                "service": "Spotify",
                "emoji": "♫",
                "kind": SPOTIFY_TYPES[link_type],
                "item_id": item_id,
                "open_url": f"https://open.spotify.com/{link_type}/{item_id}",
                "title_hint": hint,
            }

        return {"error": "Use a Spotify track, album, playlist, or artist link."}

    return {"error": "That link isn't from a supported YouTube or Spotify domain."}


@app.route("/")
def home():
    return render_template_string(HTML, result=None)


@app.route("/recognize", methods=["POST"])
def recognize():
    return render_template_string(
        HTML, result=recognize_link(request.form.get("link", ""))
    )


if __name__ == "__main__":
    app.run(debug=True)