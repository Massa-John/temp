from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from urllib.parse import urlparse, parse_qs
import os
import uuid
import yt_dlp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "/app/downloads")
MAX_SIZE_MB = int(os.environ.get("MAX_SIZE_MB", "500"))
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ALLOWED_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
}

QUALITY_MAP = {
    "best": "bestvideo+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "audio": "bestaudio/best",
}


def is_valid_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"}:
            return False
        host = (parsed.netloc or "").lower()
        if host not in ALLOWED_HOSTS:
            return False

        if host in {"youtu.be", "www.youtu.be"}:
            return bool(parsed.path and parsed.path != "/")

        if "/shorts/" in parsed.path:
            shorts_id = parsed.path.split("/shorts/")[-1].strip("/")
            return bool(shorts_id)

        q = parse_qs(parsed.query)
        return bool(q.get("v", [""])[0])
    except Exception:
        return False


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", max_size_mb=MAX_SIZE_MB)


@app.route("/download", methods=["POST"])
def download_video():
    url = (request.form.get("url") or "").strip()
    quality = (request.form.get("quality") or "best").strip().lower()

    if not url:
        flash("Введите YouTube URL.", "error")
        return redirect(url_for("index"))

    if not is_valid_youtube_url(url):
        flash("Некорректный YouTube URL.", "error")
        return redirect(url_for("index"))

    if quality not in QUALITY_MAP:
        flash("Некорректное качество. Выберите: best, 720p, audio.", "error")
        return redirect(url_for("index"))

    request_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{request_id}.%(ext)s")

    ydl_opts = {
        "format": QUALITY_MAP[quality],
        "outtmpl": output_template,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "max_filesize": MAX_SIZE_MB * 1024 * 1024,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info)

            if quality != "audio" and not downloaded_path.endswith(".mp4"):
                candidate = f"{os.path.splitext(downloaded_path)[0]}.mp4"
                if os.path.exists(candidate):
                    downloaded_path = candidate

            if not os.path.exists(downloaded_path):
                base = os.path.splitext(downloaded_path)[0]
                for ext in [".mp4", ".webm", ".mkv", ".m4a", ".mp3", ".opus"]:
                    c = base + ext
                    if os.path.exists(c):
                        downloaded_path = c
                        break

        filename = os.path.basename(downloaded_path)
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "File is larger than max-filesize" in msg:
            flash(f"Файл превышает лимит {MAX_SIZE_MB} MB.", "error")
        else:
            flash("Не удалось скачать видео. Проверьте ссылку/качество и попробуйте снова.", "error")
        return redirect(url_for("index"))
    except Exception:
        flash("Внутренняя ошибка сервера при скачивании.", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
