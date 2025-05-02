import sys
import threading
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import cv2
from driver_drowsiness import DrowsinessDetector
from dashboard import start_dashboard
import os






class DrowsinessUI(QMainWindow):
    def __init__(self, detector, log_file_path):
        super().__init__()
        self.detector = detector
        self.log_file_path = log_file_path
        self.initUI()

    def initUI(self):
        # Window setup
        self.setWindowTitle("Driver Drowsiness Detection")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)

        # Video feed label
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.layout.addWidget(self.video_label)

        # Status label
        self.status_label = QLabel("Status: Initializing...", self)
        self.layout.addWidget(self.status_label)

        # Redirect button
        self.dashboard_button = QPushButton("Open Dashboard", self)
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.layout.addWidget(self.dashboard_button)

        # Set the central widget
        self.setCentralWidget(self.central_widget)

        # Timer for video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30ms

    def update_frame(self):
        frame, _ = self.detector.process_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(image))

            # Update status label
            self.status_label.setText(f"Status: {self.detector.status}")

    def open_dashboard(self):
        webbrowser.open("http://127.0.0.1:8050")  # Open dashboard in the default browser

    def closeEvent(self, event):
        self.detector.cap.release()
        cv2.destroyAllWindows()
        event.accept()

# Main Application
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize the detector
    detector = DrowsinessDetector()

    # Log file path
    log_file_path = os.path.join("logs", f"drowsiness_log_{detector.session_timestamp}.csv")

    # Start Flask dashboard in a separate thread
    start_dashboard(log_file_path)

    # Start the UI
    main_window = DrowsinessUI(detector, log_file_path)
    main_window.show()
    sys.exit(app.exec_())
