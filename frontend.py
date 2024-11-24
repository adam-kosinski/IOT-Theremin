import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QFrame, QSizePolicy, QMessageBox, QComboBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt

class SoundDeviceController(QMainWindow):
    def __init__(self):
        super().__init__()
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
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        central_widget.setLayout(main_layout)

        # Container frame for panel
        container_frame = QFrame()
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container_frame.setSizePolicy(size_policy)
        container_frame.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignCenter)
        container_frame.setLayout(container_layout)
        main_layout.addWidget(container_frame)

        # Title label
        title_label = QLabel("Sound Device Controller", self)
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
        self.waveform_combo.addItems(["Sine", "Square", "Triangle", "Sawtooth"])
        self.waveform_combo.setStyleSheet(
            "font-size: 24px; padding: 10px; margin: 10px; border: 2px solid #2c3e50; border-radius: 5px; background-color: #ffffff; color: #2c3e50;"
        )
        self.waveform_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
            "background-color: #2ecc71; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
        )
        self.play_button.clicked.connect(self.toggle_play_sound)
        control_layout.addWidget(self.play_button)

        # Record/Stop button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setIcon(QIcon("icons/record_icon.svg"))  # Replace with your SVG file
        self.record_button.setStyleSheet(
            "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
        )
        self.record_button.clicked.connect(self.toggle_record_sound)
        control_layout.addWidget(self.record_button)


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def toggle_play_sound(self):
        # Placeholder function for play/stop button
        if self.play_button.text() == "Play Sound":
            print(f"Playing sound with {self.waveform_combo.currentText()} waveform...")
            self.play_button.setText("Stop Sound")
            self.play_button.setStyleSheet(
                "background-color: #e74c3c; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )
        else:
            print("Stopping sound...")
            self.play_button.setText("Play Sound")
            self.play_button.setStyleSheet(
                "background-color: #2ecc71; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )

    def toggle_record_sound(self):
        # Placeholder function for record/stop button
        if self.record_button.text() == "Start Recording":
            print("Recording sound...")
            self.record_button.setText("Stop Recording")
            self.record_button.setStyleSheet(
                "background-color: #e74c3c; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )
        else:
            print("Stopping recording...")
            self.record_button.setText("Start Recording")
            self.record_button.setStyleSheet(
                "background-color: #e67e22; color: #ffffff; border-radius: 10px; padding: 20px; font-size: 36px;"
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SoundDeviceController()
    window.show()
    sys.exit(app.exec_())
