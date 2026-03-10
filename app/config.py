import os


class Config:
    """Base configuration for Flask app."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
    PPT_EMBED_BASE = os.environ.get(
        "PPT_EMBED_BASE",
        "https://onedrive.live.com/embed?resid=REPLACE_ME&em=2&wdAr=1.7777",
    )
    SLIDES_TOTAL = int(os.environ.get("SLIDES_TOTAL", "20"))

