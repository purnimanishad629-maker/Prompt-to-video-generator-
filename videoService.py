import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

def create_avatar_video(avatar_path, audio_path, output_folder, video_id):
    """Create video with avatar and audio"""
    
    # Load avatar image
    if not os.path.exists(avatar_path):
        # Use default image if avatar not found
        avatar_path = 'static/avatars/default.png'
    
    img = cv2.imread(avatar_path)
    if img is None:
        # Create blank white image if nothing works
        img = np.ones((720, 1280, 3), dtype=np.uint8) * 255
    
    height, width = img.shape[:2]
    
    # Resize to standard YouTube Shorts size (1080x1920 or 720x1280)
    target_height = 1280
    target_width = 720
    
    if height > width:
        # Portrait mode
        img = cv2.resize(img, (target_width, target_height))
    else:
        # Landscape - add padding
        img = cv2.resize(img, (target_width, target_height))
    
    # Load audio to get duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # Create video writer
    temp_video_path = os.path.join(output_folder, f'{video_id}_temp.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_path, fourcc, 24, (target_width, target_height))
    
    # Write frames
    fps = 24
    total_frames = int(duration * fps)
    
    for i in range(total_frames):
        # Add subtle animation - slight zoom effect
        scale = 1 + (i / total_frames) * 0.02  # 2% zoom
        
        # Zoom effect (optional - if you want animation)
        # This is simplified, can be enhanced
        
        out.write(img)
    
    out.release()
    
    # Combine video with audio
    video_clip = VideoFileClip(temp_video_path)
    final_clip = video_clip.set_audio(audio_clip)
    
    # Save final video
    final_path = os.path.join(output_folder, f'{video_id}.mp4')
    final_clip.write_videofile(final_path, codec='libx264', audio_codec='aac')
    
    # Clean up temp file
    video_clip.close()
    audio_clip.close()
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
    
    return final_path

def add_text_overlay(image, text, font_size=40):
    """Add text overlay to image (for lyrics/poetry)"""
    # Convert OpenCV to PIL
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    
    draw = ImageDraw.Draw(pil_image)
    
    # Try to load a Hindi font, use default if not available
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Split text into lines
    lines = text.split('\n')
    
    # Draw each line
    y_offset = 100
    for line in lines:
        draw.text((50, y_offset), line, fill=(255, 255, 255), font=font)
        y_offset += font_size + 10
    
    # Convert back to OpenCV
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
