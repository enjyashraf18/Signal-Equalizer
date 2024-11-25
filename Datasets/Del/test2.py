import sys
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft
from PyQt5 import QtWidgets, QtMultimedia
import pyqtgraph as pg
import os


class AudioAnalyzer(QtWidgets.QWidget):
    def __init__(self, wav_file):
        super().__init__()

        # Load .wav file
        self.wav_file = wav_file
        self.sampling_rate, self.data = wavfile.read(self.wav_file)

        # If stereo, convert to mono by averaging the two channels
        if self.data.ndim > 1:
            self.data = np.mean(self.data, axis=1)

        self.time_axis = np.linspace(0, len(self.data) / self.sampling_rate, num=len(self.data))

        # Perform Fourier Transform
        self.fft_data = fft(self.data)
        self.freqs = np.fft.fftfreq(len(self.fft_data), 1 / self.sampling_rate)

        # Set up PyQt5 UI
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Audio Frequency Analyzer")
        layout = QtWidgets.QVBoxLayout()

        # Time-domain plot
        self.time_plot = pg.PlotWidget(title="Time Domain - Amplitude vs Time")
        self.time_plot.plot(self.time_axis, self.data.astype(float), pen="c")  # Convert data to float
        layout.addWidget(self.time_plot)

        # Frequency-domain plot (Magnitude Spectrum)
        self.freq_plot = pg.PlotWidget(title="Frequency Domain - Magnitude vs Frequency")
        magnitude = np.abs(self.fft_data)[:len(self.fft_data) // 2]  # Magnitude spectrum
        positive_freqs = self.freqs[:len(self.freqs) // 2]  # Positive frequencies only
        self.freq_plot.plot(positive_freqs, magnitude, pen="m")
        layout.addWidget(self.freq_plot)

        # Play button
        self.play_button = QtWidgets.QPushButton("Play Audio")
        self.play_button.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button)

        self.setLayout(layout)

    def play_audio(self):
        # Play the audio file
        self.sound = QtMultimedia.QSound(self.wav_file)
        self.sound.play()


def main(wav_file):
    app = QtWidgets.QApplication(sys.argv)
    window = AudioAnalyzer(wav_file)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())


# Provide the path to your .wav file
main("../Audios/Uniform_Frequencies.wav")
