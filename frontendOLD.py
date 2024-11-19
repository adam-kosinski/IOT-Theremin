import threading
import pygame
import sounddevice as sd
import soundfile as sf
from flask import Flask, render_template_string
import webview

# Initialize Pygame mixer
pygame.mixer.init()

# Global variable to control recording
is_recording = False

# Flask app initialization
app = Flask(__name__)

# HTML template with buttons for controlling sound
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sound Device Controller</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            color: #333;
            line-height: 1.6;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }

        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
        }

        .control-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .control-button {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #3498db;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 20px;
            font-size: 18px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .control-button:hover {
            background-color: #2980b9;
        }

        .control-button:active {
            transform: scale(0.98);
        }

        .control-button i {
            font-size: 36px;
            margin-bottom: 10px;
        }

        .play { background-color: #2ecc71; }
        .play:hover { background-color: #27ae60; }

        .stop { background-color: #e74c3c; }
        .stop:hover { background-color: #c0392b; }

        .record { background-color: #e67e22; }
        .record:hover { background-color: #d35400; }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1>Sound Device Controller</h1>
        <div class="control-panel">
            <button id="playStopButton" class="control-button play" onclick="togglePlayStop()">
                <i class="fas fa-play"></i>
                <span>Play Sound</span>
            </button>
            <button id="recordStopButton" class="control-button record" onclick="toggleRecordStop()">
                <i class="fas fa-microphone"></i>
                <span>Start Recording</span>
            </button>
        </div>
    </div>

    <script>
        let isPlaying = false;
        let isRecording = false;

        function togglePlayStop() {
            const button = document.getElementById('playStopButton');
            const icon = button.querySelector('i');
            const text = button.querySelector('span');

            if (isPlaying) {
                window.pywebview.api.stop_sound();
                button.classList.remove('stop');
                button.classList.add('play');
                icon.classList.remove('fa-stop');
                icon.classList.add('fa-play');
                text.textContent = 'Play Sound';
            } else {
                window.pywebview.api.play_sound();
                button.classList.remove('play');
                button.classList.add('stop');
                icon.classList.remove('fa-play');
                icon.classList.add('fa-stop');
                text.textContent = 'Stop Sound';
            }

            isPlaying = !isPlaying;
        }

        function toggleRecordStop() {
            const button = document.getElementById('recordStopButton');
            const icon = button.querySelector('i');
            const text = button.querySelector('span');

            if (isRecording) {
                window.pywebview.api.stop_recording();
                button.classList.remove('stop');
                button.classList.add('record');
                icon.classList.remove('fa-microphone-slash');
                icon.classList.add('fa-microphone');
                text.textContent = 'Start Recording';
            } else {
                window.pywebview.api.record_sound();
                button.classList.remove('record');
                button.classList.add('stop');
                icon.classList.remove('fa-microphone');
                icon.classList.add('fa-microphone-slash');
                text.textContent = 'Stop Recording';
            }

            isRecording = !isRecording;
        }
    </script>
</body>
</html>
"""
# Main page route
@app.route('/')
def index():
    return render_template_string(html_template)

# PyWebview API class
class API:
    def play_sound(self):
        try:
            print("Playing sound...")
            pygame.mixer.music.load("output.wav")  # Replace with the path to your sound file
            pygame.mixer.music.play()
        except Exception as e:
            print(f"An error occurred: {e}")

    def stop_sound(self):
        try:
            print("Stopping sound...")
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"An error occurred: {e}")

    def record_sound(self):
        global is_recording
        try:
            print("Recording sound...")
            is_recording = True
            threading.Thread(target=record_audio).start()
        except Exception as e:
            print(f"An error occurred: {e}")

    def stop_recording(self):
        global is_recording
        try:
            print("Stopping recording...")
            is_recording = False
        except Exception as e:
            print(f"An error occurred: {e}")

# Record audio function
def record_audio():
    try:
        with sf.SoundFile("output.wav", mode='w', samplerate=44100, channels=1) as file:
            with sd.InputStream(samplerate=44100, channels=1) as stream:
                while is_recording:
                    data = stream.read(1024)
                    file.write(data[0])
    except Exception as e:
        print(f"An error occurred: {e}")

# Start Flask server in a separate thread
def start_flask():
    app.run(port=5004, debug=True, use_reloader=False)

# Start the Flask server
threading.Thread(target=start_flask).start()

# Create a PyWebview window to display the Flask app
def create_window():
    api = API()
    window = webview.create_window('Sound Device Controller', 'http://127.0.0.1:5004', js_api=api)
    webview.start()

# Start the PyWebview window
if __name__ == '__main__':
    create_window()

# Quit Pygame mixer when the application is closed
pygame.mixer.quit()
