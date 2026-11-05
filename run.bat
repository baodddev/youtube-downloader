@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Lan dau chay: dang cai yt-dlp va ffmpeg...
    py -m venv .venv || goto :err
    .venv\Scripts\python -m pip install -q -U "yt-dlp[default]" imageio-ffmpeg || goto :err
)
.venv\Scripts\python yt.py %*
pause
exit /b

:err
echo Cai dat that bai.
pause
