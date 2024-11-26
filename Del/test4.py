import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np

class AudiogramWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super(AudiogramWidget, self).__init__(parent)
        self.plot_audiogram()

    def plot_audiogram(self):
        # Sample frequency values and magnitudes from Fourier Transform
        frequencies = np.array([250, 500, 1000, 2000, 4000, 8000])
        magnitudes = np.array([0.1, 0.2, 0.15, 0.3, 0.25, 0.1])  # Example magnitudes

        # Convert magnitudes to decibels
        magnitudes_db = 20 * np.log10(magnitudes)

        # Plot the audiogram
        self.plot(frequencies, magnitudes_db, pen=None, symbol='o')
        self.setTitle('Audiogram')
        self.setLabel('bottom', 'Frequency (Hz)')
        self.setLabel('left', 'Hearing Level (dB)')
        self.getAxis('bottom').setTicks([[(f, str(f)) for f in frequencies]])
        self.invertY(True)  # Audiograms typically have inverted y-axis
        self.showGrid(x=True, y=True)

        # Move x-axis to the top
        self.getPlotItem().layout.removeItem(self.getPlotItem().getAxis('bottom'))
        self.getPlotItem().layout.addItem(self.getPlotItem().getAxis('bottom'), 1, 1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Audiogram Plot')
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        audiogram_widget = AudiogramWidget(self)
        layout.addWidget(audiogram_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
