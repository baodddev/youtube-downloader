"""Dán URL YouTube (video dài, Shorts, playlist) -> chọn độ phân giải / chỉ audio -> tải về downloads/."""
import sys
from pathlib import Path

import imageio_ffmpeg
import yt_dlp

OUT = Path(__file__).parent / "downloads"

BASE = {
    "outtmpl": str(OUT / "%(title)s [%(id)s].%(ext)s"),
    "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
    # YouTube needs a JS runtime to solve its player challenges; Node is already installed
    "js_runtimes": {"node": {}},
    "windowsfilenames": True,
}
# shortcut: playlists are listed flat (fast), so they get this fixed menu instead of real per-video resolutions
PLAYLIST_HEIGHTS = [2160, 1440, 1080, 720, 480, 360]


def mb(n):
    if not n:
        return "? MB"
    return f"~{n / 1048576:.0f} MB" if n >= 1048576 else "<1 MB"


def fsize(f):
    return f.get("filesize") or f.get("filesize_approx") or 0


def get_choices(info):
    """Return [(label, height or None)]; None = audio only."""
    formats = info.get("formats")
    if not formats:  # playlist
        n = len(list(info.get("entries") or []))
        print(f"Playlist: {info.get('title')} ({n} video) - tối đa độ phân giải chọn bên dưới")
        return [(f"{h}p", h) for h in PLAYLIST_HEIGHTS] + [("Chỉ audio (MP3)", None)]

    print(f"Video: {info.get('title')}")
    audio = [f for f in formats if f.get("vcodec") == "none" and f.get("acodec") not in (None, "none")]
    audio_size = max(map(fsize, audio), default=0)
    by_height = {}
    for f in formats:
        if f.get("vcodec") in (None, "none") or not f.get("height"):
            continue
        h = f["height"]
        # prefer mp4 (what we'll actually merge into), then larger
        key = (f.get("ext") == "mp4", fsize(f))
        if h not in by_height or key > by_height[h][0]:
            by_height[h] = (key, f)
    choices = []
    for h in sorted(by_height, reverse=True):
        f = by_height[h][1]
        fps = f.get("fps") or 0
        label = f"{h}p{int(fps) if fps > 30 else ''}"
        choices.append((f"{label:<8} {mb(fsize(f) + audio_size)}", h))
    choices.append((f"Chỉ audio (MP3) {mb(audio_size)}", None))
    return choices


def opts_for(height):
    if height is None:
        return {
            **BASE,
            "format": "ba/b",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }
    return {
        **BASE,
        "format": "bv*+ba/b",
        # best resolution <= height, preferring mp4/m4a so the merged mp4 plays everywhere
        "format_sort": [f"res:{height}", "ext:mp4:m4a"],
        "merge_output_format": "mp4",
    }


def handle(url):
    with yt_dlp.YoutubeDL({**BASE, "extract_flat": "in_playlist", "quiet": True, "no_warnings": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    choices = get_choices(info)
    for i, (label, _) in enumerate(choices, 1):
        print(f"  {i}. {label}")
    while True:
        pick = input(f"Chọn (1-{len(choices)}, Enter = 1): ").strip() or "1"
        if pick.isdigit() and 1 <= int(pick) <= len(choices):
            break
        print("Số không hợp lệ.")
    with yt_dlp.YoutubeDL(opts_for(choices[int(pick) - 1][1])) as ydl:
        ydl.download([url])
    print("Xong!")


def main():
    print(f"Video sẽ lưu vào: {OUT}")
    urls = sys.argv[1:]
    while True:
        url = urls.pop(0) if urls else input("\nDán URL (Enter trống để thoát): ").strip()
        if not url:
            break
        try:
            handle(url)
        except yt_dlp.utils.DownloadError as e:
            print(f"Lỗi: {e}")


if __name__ == "__main__":
    main()
