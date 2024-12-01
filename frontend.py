import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QFrame, QSizePolicy, QMessageBox, QComboBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from waveforms import waveform_dict as wd
from theremin import Theremin
import time
import s3test
import subprocess

theremin_t = None
sound_file = ""

class UploadWorker(QThread):
    # Signal to notify about file upload status
    upload_done = pyqtSignal(str)
    upload_error = pyqtSignal(str)

    def __init__(self, file_name, bucket_name):
        super().__init__()
        self.file_name = file_name
        self.bucket_name = bucket_name

    def run(self):
        try:
            # Upload the recording to S3
            print(f"Uploading {self.file_name} to {self.bucket_name}")
            s3test.upload_to_s3(self.file_name, self.bucket_name)
            # Delete the local file after upload
            os.remove(self.file_name)
            print(f"Deleted local file: {self.file_name}")
            self.upload_done.emit(f"Upload complete: {self.file_name}")
        except Exception as e:
            # If there's an error, signal it
            self.upload_error.emit(f"Error uploading or deleting file {self.file_name}: {e}")



class SoundDeviceController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vlc_process = None
        self.initUI()

    def initUI(self):
        # Main window settings
        self.setWindowTitle("Sound Device Controller")
        self.showMaximized()

        # Set main window background color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#f0f0f0'))
        self.setPalette(palette)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

         # Main layout setup
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(50, 50, 50, 100)
        
        central_widget.setLayout(main_layout)
        

        # Container frame for panel
        container_frame = QFrame()
        container_frame.setFixedSize(350, 400)
        container_frame.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignCenter)
        container_frame.setLayout(container_layout)
        main_layout.addWidget(container_frame, alignment=Qt.AlignLeft)

                # Container frame for panel
        container_frame1 = QFrame()
        container_frame1.setFixedSize(335, 400)
        container_frame1.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        container_layout1 = QVBoxLayout()
        container_layout1.setAlignment(Qt.AlignCenter)
        container_frame1.setLayout(container_layout1)
        main_layout.addWidget(container_frame1, alignment=Qt.AlignRight)

        # Title label
        title_label = QLabel("Device", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; color: #2c3e50;")
        container_layout.addWidget(title_label)


        # Waveform label
        waveform_label = QLabel("Waveform:")
        waveform_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        waveform_label.setAlignment(Qt.AlignLeft)
        container_layout.addWidget(waveform_label)

        # Waveform selection input
        self.waveform_combo = QComboBox()
        self.waveform_combo.addItems(list(wd.keys()))
        self.waveform_combo.currentIndexChanged.connect(self.change_waveform)
        self.waveform_combo.setStyleSheet(
            "font-size: 24px; padding: 5px; margin: 2px 10px; border: 2px solid #2c3e50; border-radius: 5px; background-color: #ffffff; color: #2c3e50;"
        )
        self.waveform_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        container_layout.addWidget(self.waveform_combo)
        container_layout.setSpacing(30)  # Add spacing between elements for better visibility

        # Control panel layout
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignCenter)
        container_layout.addLayout(control_layout)

        # Play/Stop button
        self.play_button = QPushButton("Play Sound")
        self.play_button.setIcon(QIcon("icons/play_icon.svg"))  # Replace with your SVG file
        self.play_button.setStyleSheet(
            "background-color: #2ecc71; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 18px;"
        )
        self.play_button.clicked.connect(self.toggle_play_sound)
        control_layout.addWidget(self.play_button)

        # Record/Stop button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setIcon(QIcon("icons/record_icon.svg"))  # Replace with your SVG file
        self.record_button.setStyleSheet(
            "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 14px;"
        )
        self.record_button.clicked.connect(self.toggle_record_sound)
        control_layout.addWidget(self.record_button)

        # Playback layout
        playback_layout = QVBoxLayout()
        playback_layout.setAlignment(Qt.AlignTop)
        container_layout1.addLayout(playback_layout)

        # Title label
        playback_label = QLabel("Playback", self)
        playback_label.setAlignment(Qt.AlignCenter)
        playback_label.setStyleSheet("font-size: 36px; color: #2c3e50;")
        playback_layout.addWidget(playback_label)

        # Track label
        track_label = QLabel("Track:")
        track_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        track_label.setAlignment(Qt.AlignLeft)
        playback_layout.addWidget(track_label)

        # Track selection input
        self.track_combo = QComboBox()
        self.track_combo.addItems(s3test.list_files_in_bucket(s3test.bucket_name))
        self.track_combo.setMaxVisibleItems(3)
        self.track_combo.setStyleSheet(
            "font-size: 14px; padding: 5px; margin: 2px 10px; border: 2px solid #2c3e50; border-radius: 5px; background-color: #ffffff; color: #2c3e50;"
        )
        self.track_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        playback_layout.addWidget(self.track_combo)

        self.play_track = QPushButton("Play Track")
        self.play_track.setIcon(QIcon("icons/play_icon.svg"))  # Replace with your SVG file
        self.play_track.setStyleSheet(
            "background-color: #2ecc71; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 18px;"
        )
        self.play_track.clicked.connect(self.toggle_track)
        playback_layout.addWidget(self.play_track)

        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon("icons/refresh_icon.svg"))  # Replace with your SVG file
        self.refresh_button.setStyleSheet(
            "background-color: #95a5a6; color: #ffffff; border-radius: 10px; padding: 5px; font-size: 24px;"
        )
        self.refresh_button.setFixedWidth(50)
        self.refresh_button.clicked.connect(self.refresh_tracks)
        playback_layout.addWidget(self.refresh_button, alignment=Qt.AlignRight)


    def change_waveform(self):
        # Placeholder function for changing the waveform
        print(f"Waveform changed to: {self.waveform_combo.currentText()}")
        global theremin_t
        if(theremin_t):
            theremin_t.set_waveform(self.waveform_combo.currentText())
    
    def refresh_tracks(self):
        print("Refreshing track list...")
        new_tracks = s3test.list_files_in_bucket(s3test.bucket_name)
        self.track_combo.clear()
        self.track_combo.addItems(new_tracks)
        self.track_combo.setMaxVisibleItems(3)


    def closeEvent(self, event):
        global theremin_t
        reply = QMessageBox.question(self, 'Exit',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if theremin_t is not None:
                theremin_t.cleanup()
            theremin_t = None
            event.accept()
            
        else:
            event.ignore()

    def toggle_play_sound(self):
        global theremin_t
        # Placeholder function for play/stop button
        if self.play_button.text() == "Play Sound":
            print(f"Playing sound with {self.waveform_combo.currentText()} waveform...")
            self.play_button.setText("Stop Sound")
            self.play_button.setStyleSheet(
                "background-color: #e74c3c; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 18px;"
            )
            theremin_t = Theremin()
            theremin_t.set_waveform(self.waveform_combo.currentText())

        else:
            print("Stopping sound...")
            self.play_button.setText("Play Sound")
            self.play_button.setStyleSheet(
                "background-color: #2ecc71; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 18px;"
            )
            if self.record_button.text() == "Stop Recording":
                self.toggle_record_sound()
            if theremin_t is not None:
                theremin_t.cleanup()
            theremin_t = None

    def toggle_record_sound(self):
        global theremin_t
        global sound_file

        if theremin_t is None:
            QMessageBox.critical(self, 'Error', 'To record audio, make sure to play sound', QMessageBox.Ok)
            return
        
        # Placeholder function for record/stop button
        if self.record_button.text() == "Start Recording":
            print("Recording sound...")
            self.record_button.setText("Stop Recording")
            self.record_button.setStyleSheet(
                "background-color: #e74c3c; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 14px;"
            )
            sound_file = f"recording_{int(time.time())}.wav"
            theremin_t.start_recording(sound_file)
        elif self.record_button.text() == "Stop Recording":
            print("Stopping recording...")
            self.record_button.setText("Uploading!!!")
            self.record_button.setStyleSheet(
                "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 14px;"
            )
            theremin_t.stop_recording()

            # Start the upload worker to handle file upload and deletion in the background
            self.upload_worker = UploadWorker(sound_file, s3test.bucket_name)
            self.upload_worker.upload_done.connect(self.on_upload_done)
            self.upload_worker.upload_error.connect(self.on_upload_error)
            self.upload_worker.start()  # Start the worker thread

        else:
            QMessageBox.warning(self, "Warning", 
                            "Uploading in progress, please wait until uploading is finished to start a new recording", 
                            QMessageBox.Ok)

    def on_upload_done(self, message):
        print(message)  # You can use this to display the success message or update the UI
        
        self.record_button.setText("Start Recording")
        self.record_button.setStyleSheet(
            "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 14px;"
        )
        # Optionally, refresh track list after successful upload
        self.refresh_tracks()

    def on_upload_error(self, error_message):
        print(error_message)  # Display the error message
        QMessageBox.critical(self, "Upload Error", error_message, QMessageBox.Ok)
        self.record_button.setText("Start Recording")
        self.record_button.setStyleSheet(
            "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 14px;"
        )
            
    
    def toggle_track(self):
        print("track playing on vs off")

        if self.vlc_process:
        # Terminate the VLC process to stop the audio
            self.vlc_process.terminate()  
            self.vlc_process = None  # Clear the process reference
            print("Audio playback stopped.")
            return


        if self.record_button.text() == "Start Recording" and self.play_button.text() == "Play Sound":
            current_track = self.track_combo.currentText()
            url = s3test.get_presigned_url(s3test.bucket_name, current_track)
            self.vlc_process = subprocess.Popen(["vlc", "-I", "dummy", "--play-and-exit", url])  # Start subprocess for VLC
        # Show a warning modal if either is true
        else:
            QMessageBox.warning(self, "Warning", 
                            "Please stop playing or recording sound before listening to a previously recorded track.", 
                            QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SoundDeviceController()
    window.show()
    sys.exit(app.exec_())
