import os
import re
import json
import time
import flask
import logging
import subprocess
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'wma', 'aiff'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_AUDIO_SIZE = 5 * 1024 * 1024  # 5MB max-limit for audio files
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB max-limit for image files

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list_audio_files', methods=['GET'])
def list_audio_files():
    audio_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
    audio_files = [f for f in os.listdir(audio_folder) if os.path.isfile(os.path.join(audio_folder, f))]
    return jsonify(audio_files)

@app.route('/list_image_files', methods=['GET'])
def list_image_files():
    image_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return jsonify(image_files)

@app.route('/list_video_files', methods=['GET'])
def list_video_files():
    video_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
    video_files = [f for f in os.listdir(video_folder) if os.path.isfile(os.path.join(video_folder, f))]
    return jsonify(video_files)

@app.route('/upload_audio', methods=['POST'])
@limiter.limit("10 per minute")
def upload_audio():
    logger.info('Received audio upload request')

    if 'audio' not in request.files:
        logger.error('No audio file provided')
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        logger.error('No audio file selected')
        return jsonify({'error': 'No audio file selected'}), 400
    
    if not allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
        logger.error(f'Invalid audio file type: {audio_file.filename}')
        return jsonify({'error': f'Invalid audio file type. Allowed types are: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'}), 400
    
    file_size = get_file_size(audio_file)
    if file_size > MAX_AUDIO_SIZE:
        logger.error(f'Audio file size exceeds limit: {file_size} bytes')
        return jsonify({'error': f'File size exceeds the limit of 5MB'}), 400

    try:
        filename = secure_filename(audio_file.filename or '')
        if not filename:
            raise ValueError("Invalid filename")
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename)
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        audio_file.save(audio_path)
        
        logger.info(f'Audio file {filename} uploaded successfully')
        return jsonify({'message': 'Audio uploaded successfully', 'path': audio_path})
    except Exception as e:
        logger.error(f'Error uploading audio file: {str(e)}', exc_info=True)
        return jsonify({'error': f'Error uploading audio file: {str(e)}'}), 500

@app.route('/upload_image', methods=['POST'])
@limiter.limit("10 per minute")
def upload_image():
    logger.info('Received image upload request')

    if 'image' not in request.files:
        logger.error('No image file provided')
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        logger.error('No image file selected')
        return jsonify({'error': 'No image file selected'}), 400
    
    if not allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
        logger.error(f'Invalid image file type: {image_file.filename}')
        return jsonify({'error': f'Invalid image file type. Allowed types are: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'}), 400
    
    file_size = get_file_size(image_file)
    if file_size > MAX_IMAGE_SIZE:
        logger.error(f'Image file size exceeds limit: {file_size} bytes')
        return jsonify({'error': f'File size exceeds the limit of 10MB'}), 400

    try:
        filename = secure_filename(image_file.filename or '')
        if not filename:
            raise ValueError("Invalid filename")
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image_file.save(image_path)
        
        logger.info(f'Image file {filename} uploaded successfully')
        return jsonify({'message': 'Image uploaded successfully', 'path': image_path})
    except Exception as e:
        logger.error(f'Error uploading image file: {str(e)}', exc_info=True)
        return jsonify({'error': f'Error uploading image file: {str(e)}'}), 500

def generate_video_filename(audio_filename):
    base_name = os.path.splitext(audio_filename)[0]
    video_filename = f"{base_name}.mp4"
    return video_filename

def get_audio_duration(audio_path):
    ffprobe_cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ]
    result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return float(result.stdout)

@app.route('/create_video', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def create_video():
    logger.info(f'Received video creation request: {request.method}')
    logger.debug(f'Request headers: {request.headers}')
    
    if request.method == 'GET':
        logger.info('GET request received, starting SSE connection')
        return Response(stream_with_context(generate_progress()), mimetype='text/event-stream')
    elif request.method == 'POST':
        data = request.json or {}
        logger.debug(f'Received POST data: {data}')
        
        audio_filename = data.get('audio_filename', '')
        image_filename = data.get('image_filename', '')
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', audio_filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', image_filename)
        resolution = data.get('resolution', '720p')
        quality = data.get('quality', 'medium')
        
        logger.info(f'Audio path: {audio_path}')
        logger.info(f'Image path: {image_path}')
        logger.info(f'Audio file exists: {os.path.exists(audio_path)}')
        logger.info(f'Image file exists: {os.path.exists(image_path)}')
        
        if not audio_filename or not image_filename:
            logger.error('Both audio and image filenames are required')
            return jsonify({'error': 'Both audio and image filenames are required'}), 400
        
        if not os.path.exists(audio_path) or not os.path.exists(image_path):
            logger.error('Audio or image file not found')
            return jsonify({'error': 'Audio or image file not found'}), 404
        
        audio_size = os.path.getsize(audio_path)
        image_size = os.path.getsize(image_path)
        total_size = audio_size + image_size
        
        if total_size > 100 * 1024 * 1024:  # 100 MB limit
            logger.error(f'Combined file size too large: {total_size / (1024 * 1024):.2f} MB')
            return jsonify({'error': 'Combined file size too large. Please use smaller files.'}), 413
        
        audio_duration = get_audio_duration(audio_path)
        flask.session['audio_duration'] = audio_duration
        
        flask.session['video_params'] = {
            'audio_path': audio_path,
            'image_path': image_path,
            'resolution': resolution,
            'quality': quality
        }
        
        logger.info('Video creation parameters stored in session')
        return jsonify({'message': 'Video creation started'}), 202
    else:
        logger.error(f'Method not allowed: {request.method}')
        return jsonify({'error': 'Method not allowed'}), 405

def generate_progress():
    start_time = time.time()
    try:
        logger.info('Starting generate_progress function')
        video_params = flask.session.get('video_params')
        audio_duration = flask.session.get('audio_duration', 0)
        if not video_params:
            logger.error('No video parameters found in session')
            yield f"data: {json.dumps({'error': 'No video parameters found'})}\n\n"
            return

        audio_path = video_params['audio_path']
        image_path = video_params['image_path']
        resolution = video_params['resolution']
        quality = video_params['quality']

        logger.info(f'Video creation parameters: audio={audio_path}, image={image_path}, resolution={resolution}, quality={quality}')

        audio_filename = os.path.basename(audio_path)
        video_filename = generate_video_filename(audio_filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_filename)
        
        if os.path.exists(video_path):
            os.remove(video_path)
        
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        if resolution == '480p':
            video_resolution = '640x480'
        elif resolution == '720p':
            video_resolution = '1280x720'
        elif resolution == '1080p':
            video_resolution = '1920x1080'
        else:
            video_resolution = '1280x720'

        if quality == 'low':
            video_bitrate = '1000k'
        elif quality == 'medium':
            video_bitrate = '2000k'
        else:
            video_bitrate = '4000k'

        ffmpeg_cmd = [
            'ffmpeg',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-vf', f'scale={video_resolution}',
            '-b:v', video_bitrate,
            video_path
        ]

        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        for line in process.stderr:
            if 'time=' in line:
                time_match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
                if time_match:
                    time_str = time_match.group(1)
                    time_parts = time_str.split(':')
                    seconds = float(time_parts[0]) * 3600 + float(time_parts[1]) * 60 + float(time_parts[2])
                    progress = min(int(seconds / float(audio_duration) * 100), 100)
                    yield f"data: {json.dumps({'progress': progress})}\n\n"
                    logger.debug(f'Video creation progress: {progress}%')

        process.wait()

        if process.returncode == 0:
            logger.info(f'Video created successfully: {video_filename}')
            yield f"data: {json.dumps({'message': 'Video created successfully', 'video_path': video_filename, 'download_url': f'/download_video/{video_filename}'})}\n\n"
        else:
            error_output = process.stderr.read()
            logger.error(f'Error creating video: {error_output}')
            yield f"data: {json.dumps({'error': f'Error creating video: {error_output}'})}\n\n"

    except Exception as e:
        logger.error(f'Unexpected error in generate_progress: {str(e)}', exc_info=True)
        yield f"data: {json.dumps({'error': f'Unexpected server error: {str(e)}'})}\n\n"
    finally:
        logger.info(f'Video creation process completed in {time.time() - start_time:.2f} seconds')
        logger.info('Ending generate_progress function')

@app.route('/download_video/<filename>', methods=['GET'])
def download_video(filename):
    logger.info(f'Received video download request for {filename}')

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
    if not os.path.exists(video_path):
        logger.error(f'Video file not found: {filename}')
        return jsonify({'error': 'Video file not found'}), 404

    return send_file(video_path, as_attachment=True)

def cleanup_old_files():
    logger.info('Starting cleanup of old files')
    current_time = datetime.now()
    cleanup_threshold = current_time - timedelta(hours=1)

    for folder in ['audio', 'images', 'videos']:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_modified_time < cleanup_threshold:
                os.remove(file_path)
                logger.info(f'Removed old file: {file_path}')

    logger.info('Cleanup of old files completed')

scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_files, trigger="interval", minutes=10)

if __name__ == '__main__':
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
