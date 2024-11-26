import librosa
from scipy.io import wavfile
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider
from PyQt5.QtCore import Qt
import pyqtgraph as pg

# Read the .wav file
sample_rate, data_y = wavfile.read("Datasets/ECG/atrial_flutter.wav")
signal, sr = librosa.load("Datasets/ECG/atrial_flutter.wav", sr=None)  # Load audio

data_x = np.divide(np.linspace(0, len(data_y)), sample_rate)
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

        self.signal = None
        self.sampling_frequency = None
        self.time_axis = None
        self.original_magnitudes = None
        self.original_phases = None
        self.modified_amplitudes = None
        self.original_freqs = None
        self.tolerance = 10

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
        self.slider.setMinimum(1)  # Minimum slider value
        self.slider.setMaximum(5)  # Maximum slider value
        self.slider.setValue(3)  # Initial slider value
        self.slider.setTickPosition(QSlider.TicksBelow)  # Tick marks below slider
        self.slider.setTickInterval(5)
        layout.addWidget(self.slider)

        # Plot the signal data
        # self.frequency_domain(self.signal_data_y)
        self.frequency_domain_with_librosa(signal, sr)
        self.plot_signal(data_y)

        self.slider.valueChanged.connect(lambda: self.Change_amp(1, 4.5))
        self.slider_mag = [0.01, 0.1, 1, 10, 100]

    def plot_signal(self, signal_data):
        # Generate a time axis for the signal
        time_axis = np.arange(len(signal_data))
        # Plot the signal on the plot widget
        self.plot_widget.plot(time_axis, signal_data, pen='b')  # 'b' for blue line
        self.plot_widget2



    def frequency_domain_with_librosa(self, signal_data_y, sr):
        # self.signal, self.sampling_frequency = librosa.load("Datasets/ECG/atrial_flutter.wav", sr=None, mono=True)
        # # self.time_axis = np.linspace(0, len(self.signal) / self.sampling_frequency,
        # #                              num=len(self.signal))
        # stft = librosa.stft(self.signal)
        # self.original_magnitudes, self.original_phases = librosa.magphase(stft)
        # self.modified_amplitudes = self.original_magnitudes.copy()
        # self.original_freqs = librosa.fft_frequencies(sr=self.sampling_frequency)
        stft_result = librosa.stft(signal_data_y, n_fft=len(signal_data_y), hop_length=len(signal_data_y), center=False)

        self.magnitude = np.abs(stft_result[:, 0])  # Only take the magnitude of the first frame
        self.phase = np.angle(stft_result[:, 0])  # Only take the phase of the first frame
        self.frequencies = librosa.fft_frequencies(sr=sr, n_fft=len(signal_data_y))

        # Find the min and max frequencies
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

    def inverse_fourier_transform(self, new_magnitudes):
        new_mag_conponent = new_magnitudes * np.exp(1j * self.phase)
        modified_signal = librosa.istft(new_mag_conponent)
        self.plot_widget.clear()
        self.plot_signal(modified_signal)

    def Change_amp(self, min_freq, max_freq):

        try:
            mag_change = self.slider_mag[self.slider.value()-1]
        except AttributeError as e:
            print(e)
        new_signal_data_y = self.magnitude.copy()
        indices = np.where((self.frequencies >= min_freq) & (self.frequencies <= max_freq))[0]

        # Step 3: Scale the magnitude of these frequencies in the copied magnitude array
        new_signal_data_y[indices] *= mag_change
        # self.plot_widget.clear()
        self.plot_widget2.clear()
        # self.plot_signal(new_signal_data_y)
        print("Shape of old_signal_data_y:", self.magnitude.shape)
        print("Shape of new_signal_data_y:", new_signal_data_y.shape)
        print("Shape of freq_data_y:", self.frequencies.shape)
        self.plot_widget2.plot(
            self.frequencies,
            new_signal_data_y,
            pen=pg.mkPen(color="green", width=2.5),
        )
        self.inverse_fourier_transform(new_signal_data_y)


# Initialize the application
app = QApplication(sys.argv)
window = SignalPlotter(data_y)
window.show()
sys.exit(app.exec_())
