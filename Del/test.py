import sys
import librosa
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import QApplication


def plot_wav_file(file_path):
    # Load the WAV file
    y, sr = librosa.load(file_path, sr=None)

    # Create a PyQt application
    app = QApplication(sys.argv)

    # Create a main window
    win = pg.GraphicsLayoutWidget(show=True, title="Waveform Plot")
    win.resize(800, 400)

    # Add a plot to the main window
    plot = win.addPlot(title="Waveform")

    # Plot the waveform
    plot.plot(y, pen='b')

    # Start the PyQt event loop
    QtGui.QGuiApplication.instance().exec_()


if __name__ == "__main__":
    file_path = 'Audios/Uniform_Frequencies.wav'  # Replace with your WAV file path
    plot_wav_file(file_path)
