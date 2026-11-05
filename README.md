# YouTube Downloader

Tool tải video YouTube (video dài, Shorts, playlist) trên Windows: dán URL, chọn độ phân giải hoặc chỉ audio, xong.

Dùng [yt-dlp](https://github.com/yt-dlp/yt-dlp) và ffmpeg (qua [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg), không cần cài ffmpeg riêng).

## Yêu cầu

- Windows
- [Python 3](https://www.python.org/downloads/) (có `py` launcher, mặc định khi cài từ python.org)
- [Node.js](https://nodejs.org/) — yt-dlp cần để giải mã player của YouTube

## Cách dùng

Nhấp đúp `run.bat`. Lần đầu chạy sẽ tự tạo `.venv` và cài thư viện.

```
Dán URL (Enter trống để thoát): https://www.youtube.com/watch?v=dQw4w9WgXcQ
Video: Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)
  1. 2160p    ~232 MB
  2. 1440p    ~120 MB
  3. 1080p    ~80 MB
  ...
  9. Chỉ audio (MP3) ~3 MB
Chọn (1-9, Enter = 1):
```

- Video được lưu vào thư mục `downloads/` dạng MP4 (hình + tiếng đã ghép).
- Chọn "Chỉ audio" để lưu MP3 192kbps.
- Playlist: chọn độ phân giải tối đa, video nào không có mức đó sẽ lấy mức thấp hơn gần nhất.
- Có thể truyền URL qua dòng lệnh: `run.bat <url1> <url2>`.

## Lỗi thường gặp

YouTube hay thay đổi, nếu tải bị lỗi thì cập nhật yt-dlp: xóa thư mục `.venv` rồi chạy lại `run.bat`.

## Lưu ý

Chỉ tải nội dung bạn có quyền tải. Tuân thủ [Điều khoản dịch vụ của YouTube](https://www.youtube.com/t/terms).
