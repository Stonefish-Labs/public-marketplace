---
name: fb-reel-downloader
description: Download public Facebook reels/videos to local MP4 files. Use when users ask to download a Facebook reel, Facebook watch URL, or fb.watch link, including requests like "save this reel," "grab this FB video," or "download this Facebook clip." Verifies ffmpeg first, then fetches and extracts HD/SD streams and muxes audio when needed.
---

# Facebook Reel Downloader

Download full-quality Facebook reels from public URLs.

## Prerequisites

- Python 3.8+
- `ffmpeg` (required for muxing separate audio/video streams)
- [uv](https://docs.astral.sh/uv/) (optional runner; useful for consistent script execution)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

If ffmpeg is missing, install it:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`
- Windows: `winget install ffmpeg`

## Usage

### As a Script

```bash
python scripts/fb_downloader.py <facebook_reel_url> [output_directory]
```

Optional via `uv` (script is stdlib-only, so this is equivalent):

```bash
uv run scripts/fb_downloader.py <facebook_reel_url> [output_directory]
```

Examples:

```bash
python scripts/fb_downloader.py https://www.facebook.com/reel/856954873853388
python scripts/fb_downloader.py https://www.facebook.com/watch?v=1234567890 ~/Downloads
python scripts/fb_downloader.py https://fb.watch/abcDEF12/
```

### Programmatic Usage

```python
from scripts.fb_downloader import download_reel

output_path = download_reel("https://www.facebook.com/reel/123456789")
```

## Supported URL Formats

- `https://www.facebook.com/reel/{id}`
- `https://www.facebook.com/watch?v={id}`
- `https://www.facebook.com/videos/{id}`
- `https://fb.watch/{shortcode}`

## Limitations

- Only works with public videos.
- Private or login-required videos will fail.
- Facebook page structure changes can break extraction patterns.

## Agent Instructions

When a user asks to download a Facebook reel/video:

1. Validate that the URL is a Facebook/Fb.watch URL.
2. Check ffmpeg availability: `ffmpeg -version`.
3. Run: `python <skill_path>/scripts/fb_downloader.py "<url>" [output_dir]`.
4. Report the final output file path on success.
