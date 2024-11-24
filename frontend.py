import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QGridLayout, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class SoundDeviceController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main window settings
        self.setWindowTitle("Sound Device Controller")
        self.showFullScreen()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout setup
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(main_layout)

        # Container frame for panel
        container_frame = QFrame()
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignCenter)
        container_frame.setLayout(container_layout)
        main_layout.addWidget(container_frame, alignment=Qt.AlignCenter)

        # Title label
        title_label = QLabel("Sound Device Controller", self)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)

        # Control panel layout
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignCenter)
        container_layout.addLayout(control_layout)

        # Play/Stop button
        self.play_button = QPushButton("Play Sound")
        self.play_button.setIcon(QIcon("icons/play_icon.svg"))  # Replace with your SVG file
        self.play_button.clicked.connect(self.toggle_play_sound)
        control_layout.addWidget(self.play_button)

        # Record/Stop button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setIcon(QIcon("icons/record_icon.svg"))  # Replace with your SVG file
        self.record_button.clicked.connect(self.toggle_record_sound)
        control_layout.addWidget(self.record_button)

    def toggle_play_sound(self):
        # Placeholder function for play/stop button
        if self.play_button.text() == "Play Sound":
            print("Playing sound...")
            self.play_button.setText("Stop Sound")
        else:
            print("Stopping sound...")
            self.play_button.setText("Play Sound")

    def toggle_record_sound(self):
        # Placeholder function for record/stop button
        if self.record_button.text() == "Start Recording":
            print("Recording sound...")
            self.record_button.setText("Stop Recording")
        else:
            print("Stopping recording...")
            self.record_button.setText("Start Recording")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SoundDeviceController()
    window.show()
    sys.exit(app.exec_())
