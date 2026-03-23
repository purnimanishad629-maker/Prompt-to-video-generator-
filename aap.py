from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import os
import uuid
import threading
import time

# Load environment variables
load_dotenv()

# Import our services
from service import generate_audio_elevenlabs, generate_audio_gtts
from videoService import create_avatar_video

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/output'
app.config['AUDIO_FOLDER'] = 'static/audio'
app.config['AVATAR_FOLDER'] = 'static/avatars'

# Create folders if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

# Store video status
video_status = {}
@app.route('/')
def index():
    """Home page"""
    # Get list of available avatars
    avatars = []
    if os.path.exists(app.config['AVATAR_FOLDER']):
        avatars = [f for f in os.listdir(app.config['AVATAR_FOLDER']) 
                   if f.endswith(('.png', '.jpg', '.jpeg'))]
    return render_template('index.html', avatars=avatars)

@app.route('/generate', methods=['POST'])
def generate_video():
    """Generate video from prompt"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        avatar = data.get('avatar', 'default.png')
        voice_type = data.get('voice_type', 'elevenlabs')  # 'elevenlabs' or 'gtts'
        
        # Generate unique ID for this video
        video_id = str(uuid.uuid4())[:8]
        
        # Start video generation in background
        thread = threading.Thread(
            target=generate_video_background,
            args=(video_id, prompt, avatar, voice_type)
        )
        thread.start()
        
        return jsonify({
            'status': 'processing',
            'video_id': video_id,
            'message': 'Video is being generated'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/status/<video_id>')
def check_status(video_id):
    """Check video generation status"""
    if video_id in video_status:
        return jsonify(video_status[video_id])
    return jsonify({'status': 'not_found'})

@app.route('/download/<video_id>')
def download_video(video_id):
    """Download generated video"""
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}.mp4')
    if os.path.exists(video_path):
        return send_file(video_path, as_attachment=True)
    return jsonify({'error': 'Video not found'})
  def generate_video_background(video_id, prompt, avatar, voice_type):
    """Background task to generate video"""
    try:
        # Update status: starting
        video_status[video_id] = {'status': 'starting', 'progress': 0}
        
        # Step 1: Generate Audio (40%)
        video_status[video_id] = {'status': 'generating_audio', 'progress': 40}
        
        audio_path = None
        if voice_type == 'elevenlabs':
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if api_key and api_key != 'your_key_here':
                audio_path = generate_audio_elevenlabs(
                    prompt, api_key, app.config['AUDIO_FOLDER'], video_id
                )
        
        # Fallback to gTTS if ElevenLabs fails
        if not audio_path:
            audio_path = generate_audio_gtts(
                prompt, app.config['AUDIO_FOLDER'], video_id
            )
        
        # Step 2: Create Video (80%)
        video_status[video_id] = {'status': 'creating_video', 'progress': 80}
        
        avatar_path = os.path.join(app.config['AVATAR_FOLDER'], avatar)
        video_path = create_avatar_video(
            avatar_path, audio_path, app.config['UPLOAD_FOLDER'], video_id
        )
        
        # Step 3: Complete
        video_status[video_id] = {
            'status': 'completed',
            'progress': 100,
            'video_url': f'/download/{video_id}'
        }
        
    except Exception as e:
        video_status[video_id] = {
            'status': 'error',
            'error': str(e)
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
  
