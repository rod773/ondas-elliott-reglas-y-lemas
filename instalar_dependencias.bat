@echo off
echo ============================================
echo  Instalando dependencias para el generador
echo  de video - Ondas de Elliott
echo ============================================
echo.

pip install pymupdf Pillow moviepy gtts imageio imageio-ffmpeg

echo.
echo ============================================
echo  Instalacion completada.
echo  Ahora ejecuta: python crear_video_elliott.py
echo ============================================
pause
