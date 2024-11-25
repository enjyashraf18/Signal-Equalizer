import sys
import numpy as np
import librosa
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel

class FrequencyPlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("STFT Magnitude Spectrum Plotter")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Button to load audio file
        self.load_button = QPushButton("Load Audio File")
        self.load_button.clicked.connect(self.load_audio)
        self.layout.addWidget(self.load_button)

        # Label to display the filename
        self.file_label = QLabel("No file loaded")
        self.layout.addWidget(self.file_label)

        # Create a plot widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

    def load_audio(self):
        # Open file dialog to select audio file
        filename, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.flac)")
        if filename:
            self.file_label.setText(f"Loaded: {filename}")
            self.plot_magnitude_spectrum(filename)

    def plot_magnitude_spectrum(self, filename):
        # Load the audio file
        y, sr = librosa.load(filename, sr=None)

        # Compute the STFT
        D = librosa.stft(y)

        # Convert to magnitude
        magnitude = np.abs(D)

        # Get frequencies
        frequencies = librosa.fft_frequencies(sr=sr)

        # Average the magnitude across time to get a single spectrum
        avg_magnitude = np.mean(magnitude, axis=1)

        # Clear the previous plot
        self.plot_widget.clear()

        # Plot frequency vs magnitude
        self.plot_widget.plot(frequencies, avg_magnitude, pen='b')
        self.plot_widget.setTitle("Magnitude Spectrum")
        self.plot_widget.setLabel('left', 'Magnitude')
        self.plot_widget.setLabel('bottom', 'Frequency (Hz)')
        self.plot_widget.showGrid(x=True, y=True)

def main():
    app = QApplication(sys.argv)
    window = FrequencyPlotter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()