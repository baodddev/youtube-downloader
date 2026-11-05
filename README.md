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
Dán URL để thêm vào hàng chờ | q: xem hàng chờ | c: xóa hàng chờ | Enter: tải (hàng chờ trống thì thoát)
[0 mục] > https://www.youtube.com/watch?v=dQw4w9WgXcQ
Video: Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)
  1. 2160p    ~232 MB
  2. 1440p    ~120 MB
  3. 1080p    ~80 MB
  ...
  9. Chỉ audio (MP3) ~3 MB
Chọn (1-9, Enter = 1): 3
Đã thêm 1 mục vào hàng chờ.
[1 mục] >
```

1. Dán URL, chọn độ phân giải → video được thêm vào **hàng chờ** (chưa tải ngay). Dán thêm bao nhiêu link cũng được.
2. `q` để xem hàng chờ, `c` để xóa hết hàng chờ.
3. Nhấn Enter (để trống) để bắt đầu tải. Đang tải mà muốn dừng thì nhấn **Ctrl+C**: các mục chưa tải vẫn nằm trong hàng chờ, có thể xem/xóa/tải tiếp.

- Video được lưu vào thư mục `downloads/` dạng MP4 (hình + tiếng đã ghép).
- Chọn "Chỉ audio" để lưu MP3 192kbps.
- Link video đang nằm trong Mix/playlist (`watch?v=...&list=...`) chỉ tải đúng video đó. Muốn tải cả playlist thì dùng link `playlist?list=...`.
- Playlist: chọn độ phân giải tối đa, video nào không có mức đó sẽ lấy mức thấp hơn gần nhất. Mọi video trong playlist được thêm vào hàng chờ, xem bằng `q`.
- Có thể truyền URL qua dòng lệnh: `run.bat <url1> <url2>` (sẽ hỏi độ phân giải rồi thêm vào hàng chờ).

## Lỗi thường gặp

YouTube hay thay đổi, nếu tải bị lỗi thì cập nhật yt-dlp: xóa thư mục `.venv` rồi chạy lại `run.bat`.

## Lưu ý

Chỉ tải nội dung bạn có quyền tải. Tuân thủ [Điều khoản dịch vụ của YouTube](https://www.youtube.com/t/terms).
