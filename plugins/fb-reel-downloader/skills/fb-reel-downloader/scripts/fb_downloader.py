#!/usr/bin/env python3
"""
Facebook Reel Downloader
Downloads full-quality Facebook reels by extracting HD video + audio streams and muxing with ffmpeg.
Uses only Python stdlib + ffmpeg.
"""

import urllib.request
import urllib.parse
import re
import subprocess
import tempfile
import os
import sys
import random
import string
import hashlib


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: ffmpeg not found.")
        print("Install it first:")
        print("  macOS:   brew install ffmpeg")
        print("  Ubuntu:  sudo apt install ffmpeg")
        print("  Windows: winget install ffmpeg")
        return False


def rand_str(n):
    """Generate random string for cookies."""
    return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=n))


def get_headers():
    """Get browser-like headers."""
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Cookie': f'sb={rand_str(24)}; datr={rand_str(24)}; wd=1920x1080; ps_l=1; ps_n=1'
    }


def fetch_page(url):
    """Fetch the Facebook page HTML."""
    print(f"Fetching: {url}")
    
    req = urllib.request.Request(url, headers=get_headers())
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Unescape backslashes that Facebook uses in JSON
            return html.replace('\\/', '/').replace('\\"', '"')
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None


def extract_video_urls(html):
    """Extract video and audio URLs from page HTML."""
    
    video_url = None
    audio_url = None
    sd_url = None
    
    # Clean up escaped characters for regex matching
    html_clean = html.replace('\\u0025', '%').replace('\\/', '/')
    
    # Pattern 1: HD video URL (browser_native_hd_url)
    hd_patterns = [
        r'browser_native_hd_url":"(https?://[^"]+)"',
        r'"playable_url_quality_hd":"(https?://[^"]+)"',
        r'"hd_src":"(https?://[^"]+)"',
        r'"hd_src_no_ratelimit":"(https?://[^"]+)"',
    ]
    
    for pattern in hd_patterns:
        match = re.search(pattern, html_clean)
        if match:
            video_url = match.group(1)
            video_url = video_url.replace('\\u0025', '%').replace('\\', '')
            print(f"Found HD video URL")
            break
    
    # Pattern 2: SD video URL (fallback)
    sd_patterns = [
        r'browser_native_sd_url":"(https?://[^"]+)"',
        r'"playable_url":"(https?://[^"]+)"',
        r'"sd_src":"(https?://[^"]+)"',
        r'"sd_src_no_ratelimit":"(https?://[^"]+)"',
    ]
    
    for pattern in sd_patterns:
        match = re.search(pattern, html_clean)
        if match:
            sd_url = match.group(1)
            sd_url = sd_url.replace('\\u0025', '%').replace('\\', '')
            print(f"Found SD video URL")
            break
    
    # Pattern 3: Audio URL (for HD videos that have separate audio)
    audio_patterns = [
        r'"audio":\s*\{[^}]*"url":"(https?://[^"]+)"',
        r'"audio_url":"(https?://[^"]+)"',
        r'"audio":\s*\[\s*\{[^}]*"url":"(https?://[^"]+)"',
    ]
    
    for pattern in audio_patterns:
        match = re.search(pattern, html_clean)
        if match:
            audio_url = match.group(1)
            audio_url = audio_url.replace('\\u0025', '%').replace('\\', '')
            print(f"Found audio URL")
            break
    
    # Use HD if available, otherwise SD
    final_video = video_url or sd_url
    
    if not final_video:
        # Try one more approach - look for video URLs in the page
        video_match = re.search(r'https://video[^"\\]+\.mp4[^"\\]*', html_clean)
        if video_match:
            final_video = video_match.group(0)
            print(f"Found video URL via fallback pattern")
    
    return final_video, audio_url, sd_url


def download_file(url, dest_path):
    """Download a file from URL to destination path."""
    print(f"Downloading to: {os.path.basename(dest_path)}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.facebook.com/',
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            total_size = response.headers.get('Content-Length')
            if total_size:
                total_size = int(total_size)
                print(f"  Size: {total_size / (1024*1024):.1f} MB")
            
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            with open(dest_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        pct = (downloaded / total_size) * 100
                        print(f"\r  Progress: {pct:.1f}%", end='', flush=True)
            
            print()  # Newline after progress
            return True
            
    except Exception as e:
        print(f"Download error: {e}")
        return False


def mux_video_audio(video_path, audio_path, output_path):
    """Combine video and audio streams using ffmpeg."""
    print(f"Muxing video + audio -> {os.path.basename(output_path)}")
    
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-i', video_path,
        '-i', audio_path,
        '-c', 'copy',  # No re-encoding
        '-shortest',  # Match shortest stream
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Muxing complete!")
            return True
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Muxing error: {e}")
        return False


def extract_reel_id(url):
    """Extract reel ID from URL for output filename."""
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)

    # Try /reel/ID pattern
    match = re.search(r'/reel/(\d+)', parsed.path)
    if match:
        return match.group(1)
    
    # Try video ID in URL
    match = re.search(r'/videos/(\d+)', parsed.path)
    if match:
        return match.group(1)

    # Facebook watch URLs carry the video ID in ?v=
    watch_id = query.get('v', [None])[0]
    if watch_id and re.fullmatch(r'\d+', watch_id):
        return watch_id

    # fb.watch links use a shortcode in the path
    if parsed.netloc.lower().endswith('fb.watch'):
        shortcode = parsed.path.strip('/').split('/')[0]
        if shortcode:
            safe_shortcode = re.sub(r'[^A-Za-z0-9_-]', '', shortcode)
            if safe_shortcode:
                return f"fbwatch_{safe_shortcode}"
    
    # Fallback keeps filename deterministic and avoids collisions.
    short_hash = hashlib.sha1(url.encode('utf-8')).hexdigest()[:8]
    return f'facebook_video_{short_hash}'


def download_reel(url, output_dir=None):
    """Main function to download a Facebook reel."""
    
    # Check ffmpeg first
    if not check_ffmpeg():
        return None
    
    # Validate URL
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower().split(':')[0]
    allowed_hosts = {'facebook.com', 'www.facebook.com', 'm.facebook.com', 'fb.watch', 'www.fb.watch', 'fb.com', 'www.fb.com'}
    if host not in allowed_hosts and not host.endswith('.facebook.com'):
        print("ERROR: Not a valid Facebook URL")
        return None
    
    # Fetch page
    html = fetch_page(url)
    if not html:
        print("ERROR: Could not fetch page")
        return None
    
    # Extract URLs
    video_url, audio_url, _sd_url = extract_video_urls(html)
    
    if not video_url:
        print("ERROR: Could not find video URL in page")
        print("The video might be private or the page structure changed.")
        return None
    
    # Determine output path
    reel_id = extract_reel_id(url)
    output_dir = output_dir or os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{reel_id}.mp4")
    
    # If we have separate audio, download both and mux
    if audio_url:
        print("HD video with separate audio detected - will mux streams")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_tmp = os.path.join(tmp_dir, 'video.mp4')
            audio_tmp = os.path.join(tmp_dir, 'audio.m4a')
            
            # Download video
            if not download_file(video_url, video_tmp):
                print("ERROR: Failed to download video stream")
                return None
            
            # Download audio
            if not download_file(audio_url, audio_tmp):
                print("ERROR: Failed to download audio stream")
                return None
            
            # Mux them
            if not mux_video_audio(video_tmp, audio_tmp, output_path):
                print("ERROR: Failed to mux streams")
                return None
    else:
        # Single stream (SD or muxed HD)
        print("Single stream video - downloading directly")
        if not download_file(video_url, output_path):
            print("ERROR: Failed to download video")
            return None
    
    print(f"\nSaved: {output_path}")
    return output_path


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/fb_downloader.py <facebook_reel_url> [output_dir]")
        print("\nExample:")
        print("  python scripts/fb_downloader.py https://www.facebook.com/reel/830509436508428")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = download_reel(url, output_dir)
    
    if result:
        print("\nDownload successful!")
        sys.exit(0)
    else:
        print("\nDownload failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
