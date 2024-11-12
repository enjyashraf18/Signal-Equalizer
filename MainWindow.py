from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QPushButton, QSlider, QLabel, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudioFormat, QAudioOutput
from PyQt5.QtCore import QBuffer, QByteArray
from PyQt5.QtCore import QUrl
import pyqtgraph as pg
from PyQt5 import uic, QtMultimedia
import pandas as pd
import numpy as np
from scipy.io import wavfile
from scipy.io.wavfile import write
from scipy.fft import fft, ifft
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Equalizer.ui", self)
        # VARIABLES
        self.mode = "Uniform"  # Change from dropdown menu
        self.is_playing = False
        self.media_player = QMediaPlayer()
        # self.audio_output = QAudioOutput()

        # in case of .csv
        # self.time = None
        # self.amplitude = None

        # in case of .wav
        self.original_wav_file_path = None
        self.sampling_frequency = None
        self.magnitude = None
        self.time_axis = None
        self.sound = None
        self.frequencies = None
        self.positive_frequencies = None
        self.positive_magnitudes = None
        self.positive_magnitudes_db = None
        self.modified_positive_magnitudes = None
        self.significant_frequencies = None
        self.significant_magnitudes = None
        self.fft_data = None
        self.modified_fft_data = None

        # UI
        self.setWindowTitle("Signal Equalizer")
        self.setWindowIcon(QIcon("Deliverables/equalizer_icon.png"))
        self.horizontal_layout = self.findChild(QHBoxLayout, "horizontalLayout_5")
        self.horizontal_layout_7 = self.findChild(QHBoxLayout, "horizontalLayout_7") # original signal specto

        # Removing placeholder widgets
        self.old_original_time_plot = self.findChild(QWidget, "widget")
        self.old_modified_time_plot = self.findChild(QWidget, "widget_2") # widget 6
        self.old_frequency_plot = self.findChild(QWidget, "widget_3")  # change to correct widget
        self.horizontal_layout.removeWidget(self.old_original_time_plot)
        self.horizontal_layout.removeWidget(self.old_modified_time_plot)
        self.horizontal_layout_7.removeWidget(self.old_frequency_plot) # change to correct layout
        self.old_original_time_plot.deleteLater()
        self.old_modified_time_plot.deleteLater()
        self.old_frequency_plot.deleteLater()

        self.original_time_plot = pg.PlotWidget()
        self.modified_time_plot = pg.PlotWidget()
        self.frequency_plot = pg.PlotWidget()
        self.horizontal_layout.addWidget(self.original_time_plot)
        self.horizontal_layout.addWidget(self.modified_time_plot)
        self.horizontal_layout_7.addWidget(self.frequency_plot)  # change to correct layout

        # Sliders and their labels
        self.sliders = []
        self.sliders_labels = []

        # Avoiding Zero-Index Confusion
        placeholder_slider = QSlider()
        placeholder_slider_label = QLabel()
        self.sliders.append(placeholder_slider)
        self.sliders_labels.append(placeholder_slider_label)

        for i in range(1, 11):
            slider = self.findChild(QSlider, f"verticalSlider_{i}")
            slider.setRange(0, 100)  # contribution of frequency range in percentage
            slider.setValue(100)
            slider.valueChanged.connect(lambda value, index=i: self.on_slider_change(value, index))
            self.sliders.append(slider)

            slider_label = QLabel()  # replace with find child
            self.horizontal_layout.addWidget(slider_label)  # remove later
            self.sliders_labels.append(slider_label)

        self.upload_button = self.findChild(QPushButton, "uploadButton")
        self.upload_button.clicked.connect(self.load_signal)

        # Audio Buttons
        self.play_original_button = self.findChild(QPushButton, "uploadButton_2")
        self.play_original_button.clicked.connect(lambda: self.play_audio(self.is_playing,
                                                                          self.play_original_button.objectName()))
        self.play_modified_button = self.findChild(QPushButton, "uploadButton_3")
        self.play_modified_button.clicked.connect(lambda: self.play_audio(self.is_playing,
                                                                          self.play_modified_button.objectName()))
        self.play_icon = QIcon("Deliverables/play-button-arrowhead.png")
        self.pause_icon = QIcon("Deliverables/pause_button.png")

        self.audiogram_checkbox = self.findChild(QCheckBox, "checkBox_2")
        self.audiogram_checkbox.stateChanged.connect(self.change_frequency_plot)

        self.center_on_screen()

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_signal(self):
        filename = QFileDialog.getOpenFileName(self, "Open CSV File", "", "Audio and CSV Files (*.wav *.csv)")
        self.original_wav_file_path = filename[0]
        if self.original_wav_file_path:
            if self.original_wav_file_path.lower().endswith('.wav'):
                try:
                    self.sampling_frequency, self.magnitude = wavfile.read(self.original_wav_file_path)
                    # If stereo, convert to mono by averaging the two channels
                    if self.magnitude.ndim > 1:
                        self.magnitude = np.mean(self.magnitude, axis=1)
                    self.time_axis = np.linspace(0, len(self.magnitude) / self.sampling_frequency, num=len(self.magnitude))
                except Exception as e:
                    print(f"Error. Couldn't upload: {e}")
                self.plot_signal()
                self.reset_sliders()  # resetting sliders to 100 after each upload
            # elif path.lower().endswith('.csv'):
            #     try:
            #         df = pd.read_csv(path)
            #         self.time = df.iloc[:, 0].values
            #         self.amplitude = df.iloc[:, 1].values
            #     except Exception as e:
            #         print(f"Error. Couldn't upload: {e}")

    def plot_signal(self):
        # Clearing previous upload first
        self.original_time_plot.clear()
        self.modified_time_plot.clear()
        self.frequency_plot.clear()

        self.fourier_transform()

        self.original_time_plot.plot(self.time_axis, self.magnitude.astype(float), pen='c')
        self.modified_time_plot.plot(self.positive_frequencies, self.positive_magnitudes, pen="m")  # Change to frequency plot when UI is done

        self.setting_slider_ranges()

    def fourier_transform(self):
        sampling_period = 1 / self.sampling_frequency
        self.fft_data = fft(self.magnitude)  # each value is a frequency component (mag & phase)
        self.modified_fft_data = self.fft_data.copy()
        self.frequencies = np.fft.fftfreq(len(self.fft_data), sampling_period)  # carries value of each component (Hz)

        self.positive_magnitudes = np.abs(self.fft_data)[
                                   :len(self.fft_data) // 2]  # Magnitude spectrum (second half is mirror)
        self.positive_frequencies = self.frequencies[
                                    :len(self.frequencies) // 2]  # +ve frequencies only (start to half)

        threshold = 0.15 * np.max(self.positive_magnitudes)  # 10% of the maximum magnitude
        significant_indices = np.where(self.positive_magnitudes > threshold)[0]
        self.significant_frequencies = self.positive_frequencies[significant_indices]
        self.significant_magnitudes = self.positive_magnitudes[significant_indices]

        self.positive_magnitudes_db = np.log10(self.significant_magnitudes)

        # print(f"fft_data: {self.fft_data}")
        # print(f"frequencies: {self.frequencies}")

    def setting_slider_ranges(self):
        if self.mode == "Uniform":
            min_frequency = self.significant_frequencies[0]
            max_frequency = self.significant_frequencies[-1]
            range_of_frequencies = max_frequency - min_frequency
            step_size = range_of_frequencies/10
            # print(f"min freq: {self.significant_frequencies[0]}")
            # print(f"max freq: {self.significant_frequencies[-1]}")
            # print(f"range: {range_of_frequencies}")
            # print(f"step: {step_size}")
            # example: 10 20 30 50 60 100 150 200 250
            # range: 240
            # each slider: 240/10 = 24 value
            i = 0
            j = 1
            for k in range(1, 11):
                slider = self.sliders[k]
                slider_label = self.sliders_labels[k]

                slider.setRange(0, 100)
                # slider_label.setText(f"{int(min_frequency + i * step_size)}-{int(min_frequency + j * step_size)} Hz")
                i += 1
                j += 1

    def reset_sliders(self):
        for i in range(1, 11):
            slider = self.sliders[i]
            slider.setValue(100)

    def on_slider_change(self, value, index):
        # # Stop sound when modifying
        # if self.media_player.state() == QMediaPlayer.PlayingState:
        #     self.media_player.stop()

        slider = self.sliders[index]
        label = self.sliders_labels[index].text()
        minimum_value = int(label.split('-')[0])
        maximum_value = int(label.split('-')[1].split(' ')[0])
        new_percentage = slider.value()
        modified_frequencies_indices = np.where((minimum_value <= self.positive_frequencies) &
                                                (self.positive_frequencies <= maximum_value))[0]
        # print(f"significant freq: {self.significant_frequencies}")
        # print(f"min: {minimum_value}")
        # print(f"max: {maximum_value}")
        # print(f"modified indices: {modified_frequencies_indices}")
        for index in modified_frequencies_indices:
            self.modified_fft_data[index] = self.fft_data[index] * (new_percentage / 100)
            self.modified_fft_data[-index - 1] = self.fft_data[-index - 1] * (new_percentage / 100)  # modify negative component as well
        # print(f"diff: {self.fft_data} - {self.modified_fft_data}")
        modified_signal = ifft(self.modified_fft_data)
        self.frequency_plot.clear()
        self.frequency_plot.plot(self.time_axis, modified_signal.real.astype(float), pen='r')

        self.modified_positive_magnitudes = np.abs(self.modified_fft_data)[:len(self.modified_fft_data) // 2]
        self.change_frequency_plot()
        # self.modified_time_plot.clear()
        # self.modified_time_plot.plot(self.positive_frequencies, modified_positive_magnitudes, pen="m")

        modified_file_path = "modified_signal.wav"
        if os.path.exists(modified_file_path):
            os.remove(modified_file_path)
        wavfile.write(modified_file_path, self.sampling_frequency, modified_signal.real.astype(np.int16))
        self.media_player.setMedia(QMediaContent())  # Clearing media content so modified is refreshed

        print(f"{slider.objectName()}: min:{minimum_value} + max: {maximum_value} + current value: {value}")

    def play_audio(self, is_playing, audio_type):
        if audio_type == "uploadButton_2":  # Play original
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.original_wav_file_path)))
        elif audio_type == "uploadButton_3":  # Play modified
            modified_file_path = "modified_signal.wav"  # Path to the modified signal
            print("setting media player")
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(modified_file_path)))

        self.media_player.stop() if is_playing else self.media_player.play()

        self.is_playing = not is_playing

        button = self.play_original_button if audio_type == 'uploadButton_2' else self.play_modified_button
        icon = self.play_icon if is_playing else self.pause_icon
        button.setIcon(icon)

    def change_frequency_plot(self):
        self.modified_time_plot.clear()
        if self.audiogram_checkbox.isChecked():
            print(f"freq: {len(self.significant_magnitudes)} + mag: {len(self.positive_magnitudes_db)}")
            # self.modified_time_plot.setTitle('Audiogram')  # change the label in
            self.modified_time_plot.setLabel('bottom', 'Frequency (Hz)')
            self.modified_time_plot.setLabel('left', 'Hearing Level (dB)')
            self.modified_time_plot.getAxis('bottom').setTicks([[(f, str(f)) for f in self.positive_frequencies]])
            self.modified_time_plot.invertY(True)  # Audiograms typically have inverted y-axis
            self.modified_time_plot.showGrid(x=True, y=True)

            # Move x-axis to the top
            self.modified_time_plot.getPlotItem().layout.removeItem(self.modified_time_plot.getPlotItem().getAxis('bottom'))
            self.modified_time_plot.getPlotItem().layout.addItem(self.modified_time_plot.getPlotItem().getAxis('bottom'), 1, 1)

            self.modified_time_plot.plot(self.significant_frequencies, self.positive_magnitudes_db, pen=None,symbol='o')
        else:
            # Move x-axis to the bottom again
            self.modified_time_plot.getPlotItem().layout.removeItem(self.modified_time_plot.getPlotItem().getAxis('bottom'), 1, 1)
            self.modified_time_plot.getPlotItem().layout.addItem(self.modified_time_plot.getPlotItem().getAxis('bottom'))
            if self.modified_positive_magnitudes:
                self.modified_time_plot.plot(self.positive_frequencies, self.modified_positive_magnitudes, pen="m")
            else:
                self.modified_time_plot.plot(self.positive_frequencies, self.positive_magnitudes, pen="m")



def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
