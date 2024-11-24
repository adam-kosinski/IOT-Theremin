import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QFrame, QSizePolicy, QMessageBox, QComboBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from waveforms import waveform_dict as wd
from theremin import Theremin
import time

theremin_t = None

class SoundDeviceController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main window settings
        self.setWindowTitle("Sound Device Controller")
        self.resize(500, 300)

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
        container_frame.setFixedSize(300, 400)
        container_frame.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignCenter)
        container_frame.setLayout(container_layout)
        main_layout.addWidget(container_frame, alignment=Qt.AlignLeft)

                # Container frame for panel
        container_frame1 = QFrame()
        container_frame1.setFixedSize(300, 400)
        container_frame1.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        container_layout1 = QVBoxLayout()
        container_layout1.setAlignment(Qt.AlignCenter)
        container_frame1.setLayout(container_layout1)
        main_layout.addWidget(container_frame1, alignment=Qt.AlignRight)

        # Title label
        title_label = QLabel("Sound Device Controller", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
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
            "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 10px; font-size: 18px;"
        )
        self.record_button.clicked.connect(self.toggle_record_sound)
        control_layout.addWidget(self.record_button)

        # Playback layout
        playback_layout = QVBoxLayout()
        playback_layout.setAlignment(Qt.AlignTop)
        playback_layout.setSpacing(15)
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

        # Waveform selection input
        self.track_combo = QComboBox()
        self.track_combo.addItems(['Recording_1'])
        self.track_combo.currentIndexChanged.connect(self.change_track)
        self.track_combo.setStyleSheet(
            "font-size: 24px; padding: 10px; margin: 1px 50px; border: 2px solid #2c3e50; border-radius: 5px; background-color: #ffffff; color: #2c3e50;"
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
            "background-color: #95a5a6; color: #ffffff; border-radius: 10px; padding: 5px; font-size: 12px;"
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
        # Placeholder function for refreshing the tracks
        print("Refreshing track list...")

    def change_track(self):
        print(f"changing track to {self.track_combo.currentText()}")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
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
                "background-color: #e74c3c; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )
            theremin_t = Theremin()
            theremin_t.set_waveform(self.waveform_combo.currentText())

        else:
            print("Stopping sound...")
            self.play_button.setText("Play Sound")
            self.play_button.setStyleSheet(
                "background-color: #2ecc71; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )
            if self.record_button.text() == "Stop Recording":
                self.toggle_record_sound()
            if theremin_t is not None:
                theremin_t.cleanup()
            theremin_t = None

    def toggle_record_sound(self):
        global theremin_t

        if theremin_t is None:
            QMessageBox.critical(self, 'Error', 'To record audio, make sure to play sound', QMessageBox.Ok)
            return
        
        # Placeholder function for record/stop button
        if self.record_button.text() == "Start Recording":
            print("Recording sound...")
            self.record_button.setText("Stop Recording")
            self.record_button.setStyleSheet(
                "background-color: #e74c3c; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )

            theremin_t.start_recording(f"recording_{int(time.time())}.wav")
        else:
            print("Stopping recording...")
            self.record_button.setText("Start Recording")
            self.record_button.setStyleSheet(
                "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )
            theremin_t.stop_recording()
    
    def toggle_track(self):
        print("track playing on vs off")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SoundDeviceController()
    window.show()
    sys.exit(app.exec_())
