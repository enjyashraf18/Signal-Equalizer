from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QPushButton, QSlider
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from PyQt5 import uic, QtMultimedia
import pandas as pd
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Equalizer.ui", self)
        # VARIABLES
        self.mode = "Uniform"  # Change from dropdown menu

        # in case of .csv
        # self.time = None
        # self.amplitude = None

        # in case of .wav
        self.wav_file_path = None
        self.sampling_frequency = None
        self.magnitude = None
        self.time_axis = None
        self.sound = None
        self.frequencies = None
        self.positive_frequencies = None
        self.fft_data = None

        # UI
        self.setWindowTitle("Signal Equalizer")
        self.setWindowIcon(QIcon("Deliverables/equalizer_icon.png"))
        self.horizontal_layout = self.findChild(QHBoxLayout, "horizontalLayout_5")

        # Removing placeholder widgets
        self.old_original_time_plot = self.findChild(QWidget, "widget")
        self.old_modified_time_plot = self.findChild(QWidget, "widget_2")
        self.horizontal_layout.removeWidget(self.old_original_time_plot)
        self.horizontal_layout.removeWidget(self.old_modified_time_plot)
        self.old_original_time_plot.deleteLater()
        self.old_modified_time_plot.deleteLater()

        self.original_time_plot = pg.PlotWidget()
        self.modified_time_plot = pg.PlotWidget()
        self.horizontal_layout.addWidget(self.original_time_plot)
        self.horizontal_layout.addWidget(self.modified_time_plot)

        # Sliders
        self.sliders = []
        placeholder_slider = QSlider()
        self.sliders.append(placeholder_slider)
        for i in range(1, 11):
            slider = self.findChild(QSlider, f"verticalSlider_{i}")
            slider.valueChanged.connect(lambda value, index=i: self.on_slider_change(value, index))
            self.sliders.append(slider)

        # self.slider1 = self.findChild(QSlider, "verticalSlider_1")
        # self.slider2 = self.findChild(QSlider, "verticalSlider_2")
        # self.slider3 = self.findChild(QSlider, "verticalSlider_3")
        # self.slider4 = self.findChild(QSlider, "verticalSlider_4")
        # self.slider5 = self.findChild(QSlider, "verticalSlider_5")
        # self.slider6 = self.findChild(QSlider, "verticalSlider_6")
        # self.slider7 = self.findChild(QSlider, "verticalSlider_7")
        # self.slider8 = self.findChild(QSlider, "verticalSlider_8")
        # self.slider9 = self.findChild(QSlider, "verticalSlider_9")
        # self.slider10 = self.findChild(QSlider, "verticalSlider_10")
        #
        # self.slider1.valueChanged.connect(lambda: self.on_slider_change)
        # self.slider2.valueChanged.connect(self.on_slider_change)
        # self.slider3.valueChanged.connect(self.on_slider_change)
        # self.slider4.valueChanged.connect(self.on_slider_change)
        # self.slider5.valueChanged.connect(self.on_slider_change)
        # self.slider6.valueChanged.connect(self.on_slider_change)
        # self.slider7.valueChanged.connect(self.on_slider_change)
        # self.slider8.valueChanged.connect(self.on_slider_change)
        # self.slider9.valueChanged.connect(self.on_slider_change)
        # self.slider10.valueChanged.connect(self.on_slider_change)

        # self.slider1.setObjectName(f"slider1")
        # self.slider2.setObjectName(f"slider2")
        # self.slider3.setObjectName(f"slider3")
        # self.slider4.setObjectName(f"slider4")
        # self.slider5.setObjectName(f"slider5")
        # self.slider6.setObjectName(f"slider6")
        # self.slider7.setObjectName(f"slider7")
        # self.slider8.setObjectName(f"slider8")
        # self.slider9.setObjectName(f"slider9")
        # self.slider10.setObjectName(f"slider10")


        self.upload_button = QPushButton("Upload")  # Change to find child
        self.upload_button.clicked.connect(self.load_signal)
        self.horizontal_layout.addWidget(self.upload_button)

        self.play_button = self.findChild(QPushButton, "pushButton_4")
        self.play_button.clicked.connect(self.play_audio)
        # self.init_ui()
        self.center_on_screen()

    def init_ui(self):
        pass

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_signal(self):
        filename = QFileDialog.getOpenFileName(self, "Open CSV File", "", "Audio and CSV Files (*.wav *.csv)")
        self.wav_file_path = filename[0]
        if self.wav_file_path:
            if self.wav_file_path.lower().endswith('.wav'):
                try:
                    self.sampling_frequency, self.magnitude = wavfile.read(self.wav_file_path)
                    # If stereo, convert to mono by averaging the two channels
                    if self.magnitude.ndim > 1:
                        self.magnitude = np.mean(self.magnitude, axis=1)
                    self.time_axis = np.linspace(0, len(self.magnitude) / self.sampling_frequency, num=len(self.magnitude))
                    # print(f"Sampling Frequency: {self.sampling_frequency}")
                    # print(f"Magnitude: {self.magnitude}")
                except Exception as e:
                    print(f"Error. Couldn't upload: {e}")
                self.plot_signal()
            # elif path.lower().endswith('.csv'):
            #     try:
            #         df = pd.read_csv(path)
            #         self.time = df.iloc[:, 0].values
            #         self.amplitude = df.iloc[:, 1].values
            #     except Exception as e:
            #         print(f"Error. Couldn't upload: {e}")

    def play_audio(self):
        self.sound = QtMultimedia.QSound(self.wav_file_path)
        self.sound.play()

    def plot_signal(self):
        self.fourier_transform()
        magnitude = np.abs(self.fft_data)[:len(self.fft_data) // 2]  # Magnitude spectrum (second half is mirror)
        self.positive_frequencies = self.frequencies[
                                    :len(self.frequencies) // 2]  # +ve frequencies only (start to half)

        self.original_time_plot.plot(self.time_axis, self.magnitude.astype(float), pen='c')
        self.modified_time_plot.plot(self.positive_frequencies, magnitude, pen="m")  # Change to frequency plot when UI is done

        self.changing_slider_values()

    def changing_slider_values(self):
        if self.mode == "Uniform":
            min_frequency = self.positive_frequencies[0]
            range_of_frequencies = self.positive_frequencies[-1] - min_frequency
            step_size = range_of_frequencies/10
            print(f"range: {range_of_frequencies}")
            print(f"step: {step_size}")
            # example: 10 20 30 50 60 100 150 200 250
            # range: 240
            # each slider: 240/10 = 24 value
            i = 0
            j = 1
            for k in range(1, 11):
                slider = self.sliders[k]
                slider.setRange(int(min_frequency + i*step_size), int(min_frequency + j*step_size))
                print(f"slider{k} range: ({int(min_frequency + i*step_size)}, {int(min_frequency + j*step_size)})")
                i += 1
                j += 1

    def on_slider_change(self, value, index):
        print(f"index in change: {index}")
        slider = self.sliders[index]
        print(f"{slider.objectName()}, value: {value}")

    def fourier_transform(self):
        sampling_period = 1 / self.sampling_frequency
        self.fft_data = fft(self.magnitude)  # each value is a frequency component (mag & phase)
        self.frequencies = np.fft.fftfreq(len(self.fft_data), sampling_period) # carries value of each component (Hz)
        print(f"fft_data: {self.fft_data[0:3]}")
        print(f"frequencies: {self.frequencies}")

    # def upload(self, label):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.ReadOnly
    #
    #     filters = "Audio and CSV Files (*.wav *.csv)"
    #     file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileNames()", "", filters, options=options)
    #     self.media_playerIN.setMedia(QMediaContent())
    #     if file_path:
    #         # Store file name
    #         file_name = file_path.split('/')[-1]
    #         label.setText(file_name)
    #
    #         if file_path.lower().endswith('.wav'):
    #             if self.media_playerIN.state() == QMediaPlayer.StoppedState:
    #                 self.media_playerIN.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
    #
    #             # Open the .wav file for reading
    #             with wave.open(file_path, 'rb') as audio_file:  # reading file in binary mode
    #                 # Get the audio file's parameters
    #                 num_frames = audio_file.getnframes()
    #
    #                 # Read audio data as bytes
    #                 raw_audio_data = audio_file.readframes(num_frames)
    #
    #                 # Convert raw bytes to numerical values (assuming 16-bit PCM)
    #                 self.audio_data = np.frombuffer(raw_audio_data, dtype=np.int16)
    #                 self.edited_time_domain_signal = self.audio_data.copy()
    #
    #                 self.sample_rate = audio_file.getframerate()
    #                 self.time = np.arange(0, len(self.audio_data)) / self.sample_rate
    #
    #         elif file_path.lower().endswith('.csv'):
    #             data = np.loadtxt(file_path, delimiter=',', skiprows=1, usecols=(1,))
    #             self.audio_data = data[0:1000]
    #             self.edited_time_domain_signal = self.audio_data.copy()
    #             self.x = np.loadtxt(file_path, delimiter=',', skiprows=1, usecols=(0,))
    #             self.sample_rate = 1 / (self.x[1] - self.x[0])
    #             self.time = self.x[0:1000]


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
