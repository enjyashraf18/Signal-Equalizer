
from scipy.io import wavfile
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider
from PyQt5.QtCore import Qt
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
        
        self.signal_data_y = signal_data
        self.frequencies = []
        self.amplitudes = []


        # Create a central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Set up the pyqtgraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget2 = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.plot_widget2)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)       # Minimum slider value
        self.slider.setMaximum(5)     # Maximum slider value
        self.slider.setValue(1)        # Initial slider value
        self.slider.setTickPosition(QSlider.TicksBelow)   # Tick marks below slider
        self.slider.setTickInterval(5)  
        layout.addWidget(self.slider)
        
        # Plot the signal data
        self.frequency_domain(self.signal_data_y)
        self.plot_signal(data_y)

        self.slider.valueChanged.connect(lambda: self.Change_amp(500,600))
        
    def plot_signal(self, signal_data):
        # Generate a time axis for the signal
        time_axis = np.arange(len(signal_data))
        
        # Plot the signal on the plot widget
        self.plot_widget.plot(time_axis, signal_data, pen='b')  # 'b' for blue line
        self.plot_widget2
    
    def frequency_domain(self,signal_data_y):

        # Perform FFT on the input signal
        self.fft_result = np.fft.rfft(signal_data_y)
        self.phase = np.angle(self.fft_result)
        # Compute the frequency values based on the length of the input data_y
        self.frequencies = np.fft.rfftfreq(len(signal_data_y), data_x[1] - data_x[0])
        
        # Compute magnitudes and check min/max frequencies
        self.magnitude = np.abs(self.fft_result) / 3000  # Adjust scaling if necessary
        max_frequency = np.max(self.frequencies)
        min_frequency = np.min(self.frequencies)
        print(f"The max frequency is {max_frequency}")
        print(f"The min frequency is {min_frequency}")
        print(f"The frequencies are {self.frequencies}")
        print(f"no. of frequencies are {len(self.frequencies)}")

        # Plot frequency vs magnitude
        self.plot_widget2.plot(
            self.frequencies,
            self.magnitude,
            pen=pg.mkPen(color="green", width=2.5),
        )

    def inverse_fft(self,new_magnitude_data_y):
        new_magnitude_data_y = new_magnitude_data_y.astype(np.complex128)
        new_magnitude_data_y *= np.exp(1j * self.phase)
        modified_signal = np.fft.irfft(new_magnitude_data_y) * 3000
        self.plot_widget.clear()
        self.plot_signal(modified_signal)

    def Change_amp(self, min_freq, max_freq):
        
        try:
            mag_change = self.slider.value()
        except AttributeError as e:
            print(e)
        new_signal_data_y = self.magnitude.copy()
        indices = np.where((self.frequencies >= min_freq) & (self.frequencies <= max_freq))[0]
    
        # Step 3: Scale the magnitude of these frequencies in the copied magnitude array
        new_signal_data_y[indices] *= mag_change 
        # self.plot_widget.clear()
        self.plot_widget2.clear()
        # self.plot_signal(new_signal_data_y)
        self.plot_widget2.plot(
            self.frequencies,
            new_signal_data_y,
            pen=pg.mkPen(color="green", width=2.5),
        )
        self.inverse_fft(new_signal_data_y)

# Initialize the application
app = QApplication(sys.argv)
window = SignalPlotter(data_y)
window.show()
sys.exit(app.exec_())
