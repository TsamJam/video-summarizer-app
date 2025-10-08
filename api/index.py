import os
import io
import base64
import uuid
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import yt_dlp
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)

# --- Helper Functions from your Notebook ---

def download_video(url, cookies_path, output_path):
    """Downloads a video from a URL using yt-dlp, requires cookies for private content."""
    # Generate a unique filename to avoid conflicts
    unique_filename = f"{output_path}_{uuid.uuid4()}.mp4"
    ydl_opts = {
        'outtmpl': unique_filename,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True,
        'cookiefile': cookies_path,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        return unique_filename
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def extract_frames(video_path, num_frames=10):
    """Extracts a specified number of frames evenly from a video."""
    frames = []
    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not total_frames > 0:
            return []
        
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        for i in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        cap.release()
        return frames
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return []

def frame_to_gemini_input(frame):
    """Converts a video frame (NumPy array) to a base64 encoded JPEG for the Gemini API."""
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='JPEG')
    byte_content = byte_arr.getvalue()
    return {
        "mime_type": "image/jpeg",
        "data": base64.b64encode(byte_content).decode()
    }

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handles the video summarization request."""
    # Get data from the form
    video_url = request.form.get('video_url')
    api_key = request.form.get('api_key')
    cookies_file = request.files.get('cookies_file')

    if not all([video_url, api_key, cookies_file]):
        return jsonify({'error': 'Missing required fields: URL, API Key, and cookies.txt are required.'}), 400

    # Securely configure the Gemini API
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash') # Using Flash for speed
    except Exception as e:
        return jsonify({'error': f"Invalid API Key or configuration error: {e}"}), 400
    
    # Save the uploaded cookies file temporarily
    cookies_path = f"temp_cookies_{uuid.uuid4()}.txt"
    cookies_file.save(cookies_path)
    
    video_path = None
    try:
        # 1. Download Video
        video_path = download_video(video_url, cookies_path, "downloaded_video")
        if not video_path:
            raise Exception("Video download failed. Check the URL and ensure your cookies are valid and not expired.")

        # 2. Extract Frames
        frames = extract_frames(video_path)
        if not frames:
            raise Exception("Could not extract any frames from the video.")

        # 3. Analyze each frame
        frame_descriptions = []
        prompt_parts = ["Describe what is happening in this image from a video in one or two sentences.", ""]
        for frame in frames:
            image_part = frame_to_gemini_input(frame)
            prompt_parts[1] = image_part
            response = model.generate_content(prompt_parts)
            frame_descriptions.append(response.text)
        
        # 4. Generate Final Summary
        combined_text = "\n".join(f"- {desc}" for desc in frame_descriptions)
        summary_prompt = f"Based on the following descriptions of key moments from a video, create a concise, engaging summary of the video's overall theme and content:\n\n{combined_text}"
        
        summary_response = model.generate_content(summary_prompt)
        final_summary = summary_response.text

        return jsonify({
            'summary': final_summary,
            'frame_descriptions': frame_descriptions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # 5. Cleanup temporary files
        if os.path.exists(cookies_path):
            os.remove(cookies_path)
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


#if __name__ == '__main__':
#    app.run(debug=True)