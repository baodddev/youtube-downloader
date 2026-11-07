"""Dán URL YouTube (video dài, Shorts, playlist) -> chọn độ phân giải / chỉ audio -> tải về downloads/."""
import shutil
import sys
import zipfile
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
    # watch?v=X&list=RD... (Mix) -> only video X; a pure playlist?list= link is still a playlist
    "noplaylist": True,
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


def opts_for(height, outtmpl):
    base = {**BASE, "outtmpl": outtmpl}
    if height is None:
        return {
            **base,
            "format": "ba/b",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }
    return {
        **base,
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
    height = choices[int(pick) - 1][1]
    if info.get("formats"):  # single video
        print("Đã thêm 1 mục vào hàng chờ.")
        return [(info["title"], info["webpage_url"], height, BASE["outtmpl"])]
    # playlist -> downloads/<playlist title>/001 - <video title> [id].ext, numbered in playlist order
    folder = yt_dlp.utils.sanitize_filename(info.get("title") or info["id"]).replace("%", "%%")
    items = [
        (e.get("title") or e["url"], e["url"], height, str(OUT / folder / f"{i:03d} - %(title)s [%(id)s].%(ext)s"))
        for i, e in enumerate(info.get("entries") or [], 1)
    ]
    print(f"Đã thêm {len(items)} mục vào hàng chờ, sẽ lưu vào thư mục: {OUT / folder}")
    return items


def show_queue(queue):
    if not queue:
        print("Hàng chờ trống.")
    for i, (title, _, height, outtmpl) in enumerate(queue, 1):
        folder = Path(outtmpl).parent
        where = f"{folder.name}/" if folder != OUT else ""
        print(f"  {i}. [{f'{height}p' if height else 'MP3'}] {where}{title}")


def zip_folder(folder):
    """downloads/<playlist>/ -> downloads/<playlist>.zip (unzips back to the folder), then delete the folder."""
    files = sorted(p for p in folder.iterdir() if p.is_file())
    if not files:
        return
    zip_path = folder.parent / f"{folder.name}.zip"  # not with_suffix: "Top 10.5" would become "Top 10.zip"
    tmp = folder.parent / f"{folder.name}.zip.tmp"
    # ZIP_STORED: mp4/mp3 are already compressed, deflating them only wastes time
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_STORED) as z:
        for p in files:
            z.write(p, f"{folder.name}/{p.name}")
    with zipfile.ZipFile(tmp) as z:
        if z.testzip() is not None or len(z.namelist()) != len(files):
            print(f"Zip lỗi, giữ nguyên thư mục: {folder}")
            tmp.unlink()
            return
    tmp.replace(zip_path)
    shutil.rmtree(folder)
    print(f"Đã nén playlist thành: {zip_path}")


def download_queue(queue):
    """Download and pop items one by one; Ctrl+C stops and keeps the rest queued."""
    try:
        while queue:
            title, url, height, outtmpl = queue[0]
            print(f"\n=== Đang tải ({len(queue)} còn lại): {title}")
            try:
                with yt_dlp.YoutubeDL(opts_for(height, outtmpl)) as ydl:
                    ydl.download([url])
            except yt_dlp.utils.DownloadError as e:
                print(f"Lỗi, bỏ qua: {e}")
            queue.pop(0)
            folder = Path(outtmpl).parent
            # last queued video of this playlist done -> zip it
            if folder != OUT and folder.is_dir() and all(Path(o).parent != folder for *_, o in queue):
                zip_folder(folder)
        print("\nXong hết!")
    except KeyboardInterrupt:
        print(f"\nĐã dừng. Còn {len(queue)} mục trong hàng chờ (q: xem, c: xóa, Enter: tải tiếp).")


HELP = "\nDán URL để thêm vào hàng chờ | q: xem hàng chờ | c: xóa hàng chờ | Enter: tải (hàng chờ trống thì thoát)"


def main():
    print(f"Video sẽ lưu vào: {OUT}")
    queue = []
    urls = sys.argv[1:]
    while True:
        cmd = urls.pop(0) if urls else input(f"{HELP}\n[{len(queue)} mục] > ").strip()
        if cmd.lower() == "q":
            show_queue(queue)
        elif cmd.lower() == "c":
            queue.clear()
            print("Đã xóa hàng chờ.")
        elif cmd:
            try:
                queue += handle(cmd)
            except yt_dlp.utils.DownloadError as e:
                print(f"Lỗi: {e}")
        elif queue:
            download_queue(queue)
        else:
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):  # Ctrl+C / closed input at the prompt
        pass
