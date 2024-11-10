
from scipy.io import wavfile
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg

# Read the .wav file
sample_rate, data_y = wavfile.read("Datasets/ECG/atrial_fibrilation.wav")

data_x = np.divide(np.linspace(0,len(data_y)),sample_rate)
print("Sample Rate:", sample_rate)
print("Data y Array:", data_y)
print("Data x Array:", data_x)


class SignalPlotter(QMainWindow):
    def __init__(self, signal_data):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Signal Display")
        self.setGeometry(100, 100, 1500, 600)
        
        # Create a central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Set up the pyqtgraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget2 = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.plot_widget2)
        
        # Plot the signal data
        self.frequency_domain()
        self.plot_signal(data_y)
        
    def plot_signal(self, signal_data):
        # Generate a time axis for the signal
        time_axis = np.arange(len(signal_data))
        
        # Plot the signal on the plot widget
        self.plot_widget.plot(time_axis, signal_data, pen='b')  # 'b' for blue line
        self.plot_widget2
    
    def frequency_domain(self):
        fft_result = np.fft.rfft(data_y)
        frequencies = np.fft.rfftfreq(len(fft_result), data_x[1] - data_x[0])
        max_frequency = np.max(frequencies)
        min_frequency = np.min(frequencies)
        print(f"the max_freq  is {max_frequency}")
        print(f"the min_freq  is {min_frequency}")
        magnitude = (np.abs(fft_result))/3000
        frequencies = frequencies[:len(frequencies)]
        print(f"the freq  is {frequencies}")
        self.plot_widget2.plot(
            frequencies,
            magnitude,
            pen=pg.mkPen(color="green", width=2.5),
        )

# Initialize the application
app = QApplication(sys.argv)
window = SignalPlotter(data_y)
window.show()
sys.exit(app.exec_())
