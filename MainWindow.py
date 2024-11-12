from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QPushButton, QSlider, QLabel,
                             QCheckBox, QComboBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import pyqtgraph as pg
from PyQt5 import uic, QtMultimedia
import numpy as np
from pyqtgraph import ImageItem
from scipy.io import wavfile
from scipy.fft import fft, ifft
from animal import Animal
import time
import librosa
import soundfile as sf
import os
from scipy.signal import butter, sosfilt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Equalizer.ui", self)
        # VARIABLES
        self.mode = "Uniform"  # Default Mode
        self.is_playing = False
        self.media_player = QMediaPlayer()

        # SHAHD #
        self.animals = {1: [47.0, 1172], 2: [2971.5, 5250]}
        self.final_music_freq = {1: [20, 500], 2: [500, 2000], 3: [2000, 8000], 4: [8000, 16000], 5: [20, 500], 6: [500, 2000], 7: [2000, 8000], 8: [8000, 16000], 9: [2000, 8000], 10: [8000, 16000]}
        self.tolerance = 10
        self.previous_animals_sliders_values = [1] * 10   # we want to make it more generalized
        self.previous_music_sliders_values = [1] * 10  # we want to make it more generalized
        self.signal = None
        self.original_freqs = None
        self.modified_amplitudes = None
        self.original_phases = None
        self.original_magnitudes = None
        self.img_item = None
        self.modified_time_signal = None
        self.saved_audio_path = None
        # SHAHD #

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

        #music
        self.final_music = None
        self.bass = None
        self.piano = None
        self.guitar = None
        self.cymbal = None

        # UI
        self.setWindowTitle("Signal Equalizer")
        self.setWindowIcon(QIcon("Deliverables/equalizer_icon.png"))
        self.original_signal_layout = self.findChild(QHBoxLayout, "original_signal_layout")
        self.modified_signal_layout = self.findChild(QHBoxLayout, "modified_signal_layout")
        self.original_spectrogram_layout = self.findChild(QHBoxLayout, "original_spectrogram_layout")
        self.modified_spectrogram_layout = self.findChild(QHBoxLayout, "modified_spectrogram_layout")
        self.frequency_layout = self.findChild(QHBoxLayout, "frequency_layout")
        self.sliders_layout = self.findChild(QHBoxLayout, "sliders")

        # Removing placeholder widgets
        self.old_original_time_plot = self.findChild(QWidget, "original_signal_widget")
        self.old_modified_time_plot = self.findChild(QWidget, "modified_signal_widget")
        self.old_original_spectrogram_widget = self.findChild(QWidget, "original_spectrogram_widget")
        self.old_modified_spectrogram_widget = self.findChild(QWidget, "modified_spectrogram_widget")
        self.old_frequency_plot = self.findChild(QWidget, "frequency_widget")

        self.original_signal_layout.removeWidget(self.old_original_time_plot)
        self.modified_signal_layout.removeWidget(self.old_modified_time_plot)
        self.original_spectrogram_layout.removeWidget(self.old_original_spectrogram_widget)
        self.modified_spectrogram_layout.removeWidget(self.old_modified_spectrogram_widget)
        self.frequency_layout.removeWidget(self.old_frequency_plot)

        self.old_original_time_plot.deleteLater()
        self.old_modified_time_plot.deleteLater()
        self.old_original_spectrogram_widget.deleteLater()
        self.old_modified_spectrogram_widget.deleteLater()
        self.old_frequency_plot.deleteLater()

        self.original_time_plot = pg.PlotWidget()
        self.modified_time_plot = pg.PlotWidget()
        self.frequency_plot = pg.PlotWidget()
        self.spectogram_original_data_graph = pg.PlotWidget()
        self.spectogram_modified_data_graph = pg.PlotWidget()

        self.original_signal_layout.addWidget(self.original_time_plot)
        self.modified_signal_layout.addWidget(self.modified_time_plot)
        self.original_spectrogram_layout.addWidget(self.spectogram_original_data_graph)
        self.modified_spectrogram_layout.addWidget(self.spectogram_modified_data_graph)
        self.frequency_layout.addWidget(self.frequency_plot)

        # Sliders and their labels
        self.sliders = []
        self.sliders_labels = []

        # Avoiding Zero-Index Confusion
        placeholder_slider = QSlider()
        placeholder_slider_label = QLabel()
        self.sliders.append(placeholder_slider)
        self.sliders_labels.append(placeholder_slider_label)

        for i in range(1, 11):
            slider = self.findChild(QSlider, f"slider_{i}")
            slider.setRange(0, 100)
            slider.setValue(100)
            slider.valueChanged.connect(lambda value, index=i: self.on_slider_change(value, index))
            # slider.setRange(1, 10)
            self.sliders.append(slider)

            slider_label = QLabel()  # replace with find child
            self.sliders_layout.addWidget(slider_label)  # remove later
            self.sliders_labels.append(slider_label)

        self.upload_button = self.findChild(QPushButton, "upload_button")
        self.upload_button.clicked.connect(self.load_signal)

        # Audio Buttons
        self.play_original_button = self.findChild(QPushButton, "original_play_audio_button")
        self.play_original_button.clicked.connect(lambda: self.play_audio(self.is_playing,
                                                                          self.play_original_button.objectName()))
        self.play_modified_button = self.findChild(QPushButton, "modified_play_audio_button")
        self.play_modified_button.clicked.connect(lambda: self.play_audio(self.is_playing,
                                                                          self.play_modified_button.objectName()))
        self.play_icon = QIcon("Deliverables/play-button-arrowhead.png")
        self.pause_icon = QIcon("Deliverables/pause_button.png")

        self.audiogram_checkbox = self.findChild(QCheckBox, "audiogram_checkbox")
        self.audiogram_checkbox.stateChanged.connect(self.change_frequency_plot)

        # Mode Combobox
        self.mode_combobox = self.findChild(QComboBox, "mode_combobox")
        modes = ["Uniform", "Animal", "Music", "ECG"]
        self.mode_combobox.addItems(modes)
        self.mode_combobox.currentIndexChanged.connect(self.update_mode)

        self.center_on_screen()

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



    # def update_mode(self):
    #     self.mode = self.mode_combobox.currentText()
    #     self.original_time_plot.clear()
    #     self.modified_time_plot.clear()
    #     self.spectogram_original_data_graph.clear()
    #     self.spectogram_modified_data_graph.clear()
    #     self.frequency_plot.clear()

    def update_mode(self):
        self.mode = self.mode_combobox.currentText()
        if self.mode != "Uniform":
            for slider in self.sliders:
                # slider.setValue(1)
                slider.setRange(1, 10)
        self.original_time_plot.clear()
        self.modified_time_plot.clear()
        self.spectogram_original_data_graph.clear()
        self.spectogram_modified_data_graph.clear()
        self.frequency_plot.clear()


    def bandwidth_filter(data, lower_freq, higher_freq, sr, order=5):
        # filtered_data el mafrod teb2a sos y3ni second order sections
        filtered_data = butter(order, [lower_freq, higher_freq], btype='band', fs=sr, output='sos')
        return sosfilt(filtered_data, data)


    def load_signal(self):
        filename = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.flac)")
        self.original_wav_file_path = filename[0]
        if self.original_wav_file_path:
            if self.mode == "Uniform":
                if self.original_wav_file_path.lower().endswith('.wav'):
                    try:
                        self.sampling_frequency, self.magnitude = wavfile.read(self.original_wav_file_path)
                        # If stereo, convert to mono by averaging the two channels
                        if self.magnitude.ndim > 1:
                            self.magnitude = np.mean(self.magnitude, axis=1)
                        self.time_axis = np.linspace(0, len(self.magnitude)
                                                     / self.sampling_frequency, num=len(self.magnitude))
                    except Exception as e:
                        print(f"Error. Couldn't upload: {e}")
                    self.plot_signal()
                    self.reset_sliders()  # resetting sliders to 100 after each upload

            elif self.mode == "Animal" or self.mode == "Music":
                if self.original_wav_file_path.lower().endswith('.wav') or self.original_wav_file_path.lower().endswith(
                        '.mp3') or self.original_wav_file_path.lower().endswith('.flac'):
                    try:
                        self.signal, self.sampling_frequency = librosa.load(self.original_wav_file_path, sr=None, mono=True)  # sr=None to keep original sampling rate
                        self.time_axis = np.linspace(0, len(self.signal) / self.sampling_frequency,
                                                     num=len(self.signal))
                        stft = librosa.stft(self.signal)
                        self.original_magnitudes, self.original_phases = librosa.magphase(stft)
                        self.modified_amplitudes = self.original_magnitudes.copy()
                        self.original_freqs = librosa.fft_frequencies(sr=self.sampling_frequency)
                        self.plot_signal()
                        # .plot_frequency_magnitude()
                    except Exception as e:
                        print(f"Error. Couldn't upload: {e}")

    def plot_signal(self):
        if self.mode == "Uniform":
            # Clearing previous upload first
            self.original_time_plot.clear()
            self.modified_time_plot.clear()
            self.frequency_plot.clear()

            self.fourier_transform()

            self.original_time_plot.plot(self.time_axis, self.magnitude.astype(float), pen='c')
            self.frequency_plot.plot(self.positive_frequencies,
                                         self.positive_magnitudes, pen="m")  # Change to frequency plot when UI is done

            self.setting_slider_ranges()

        elif self.mode == "Animal" or self.mode == "Music":
            self.original_time_plot.plot(self.time_axis, self.signal, pen='c')
            self.plot_spectrogram(self.signal, self.sampling_frequency, self.spectogram_original_data_graph)

    def update_final_music(self, signal, sr):
        self.bass =self.bandwidth_filter(signal, 20, 500, sr)
        self.piano =self.bandwidth_filter(signal, 500, 2000, sr)
        self.guitar= self.bandwidth_filter(signal, 2000, 8000, sr)
        self.cymbal= self.bandwidth_filter(signal, 8000, 16000, sr)
        self.final_music = self.guitar + self.bass+ self.piano +self.cymbal
        self.final_music_freq = {1: [20, 500], 2: [500, 2000], 3: [2000, 8000], 4:[8000, 16000]}

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

    def plot_spectrogram(self, signal, sampling_frequency, plot_widget):
        stft = librosa.stft(signal)
        spectrogram_data, _ = librosa.magphase(stft)
        spectrogram_db = librosa.amplitude_to_db(spectrogram_data, ref=np.max)
        plot_widget.clear()
        self.img_item = ImageItem()
        plot_widget.addItem(self.img_item)
        cmap = pg.colormap.get('viridis')
        self.img_item.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256))

        self.img_item.setImage(spectrogram_db, autoLevels=True)

        time_bins = spectrogram_db.shape[1]
        freq_bins = spectrogram_db.shape[0]
        self.img_item.setRect(0, 0, time_bins, freq_bins)

        plot_widget.setAspectLocked(False)

        plot_widget.getAxis('bottom').setTicks(
            [[(i, f"{i / sampling_frequency:.2f}") for i in range(0, time_bins, max(1, time_bins // 10))]])
        plot_widget.getAxis('left').setTicks([[(i, f"{i * (sampling_frequency / 2) / freq_bins:.0f}") for i in
                                             range(0, freq_bins, max(1, freq_bins // 10))]])

        plot_widget.autoRange()

    def setting_slider_ranges(self):
        if self.mode == "Uniform":
            min_frequency = self.significant_frequencies[0]
            max_frequency = self.significant_frequencies[-1]
            range_of_frequencies = max_frequency - min_frequency
            step_size = range_of_frequencies/10
            # example: 10 20 30 50 60 100 150 200 250
            # range: 240
            # each slider: 240/10 = 24 value
            i = 0
            j = 1
            for k in range(1, 11):
                slider = self.sliders[k]
                slider_label = self.sliders_labels[k]
                slider.setRange(0, 100)
                slider_label.setText(f"{int(min_frequency + i * step_size)}-{int(min_frequency + j * step_size)} Hz")
                i += 1
                j += 1

    def reset_sliders(self):
        for i in range(1, 11):
            slider = self.sliders[i]
            slider.setValue(100)

    def on_slider_change(self, value, index):
        if self.mode == "Uniform":
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
                self.modified_fft_data[-index - 1] = (self.fft_data[-index - 1] *
                                                      (new_percentage / 100))  # modify negative component as well
            modified_signal = ifft(self.modified_fft_data)
            self.modified_time_plot.clear()
            self.modified_time_plot.plot(self.time_axis, modified_signal.real.astype(float), pen='r')

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

        elif self.mode == "Animal" or self.mode == "Music":
            print(f"gwa on_slider_chane  value {value} index {index}" )
            self.modify_volume(value, index)

    def play_audio(self, is_playing, audio_type):
        if self.mode == "Uniform":
            if audio_type == "original_play_audio_button":  # Play original
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.original_wav_file_path)))
            elif audio_type == "modified_play_audio_button":  # Play modified
                modified_file_path = "modified_signal.wav"  # Path to the modified signal
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(modified_file_path)))

            self.media_player.stop() if is_playing else self.media_player.play()
            self.is_playing = not is_playing

            button = self.play_original_button if audio_type == 'original_play_audio_button' else self.play_modified_button
            icon = self.play_icon if is_playing else self.pause_icon
            button.setIcon(icon)

        # SHAHD
        if self.mode == "Animal" or self.mode == "Music":
            if hasattr(self, 'saved_audio_path') and self.saved_audio_path:
                # Play the modified and saved audio file
                self.sound = QtMultimedia.QSound(self.saved_audio_path)
                self.sound.play()

    def change_frequency_plot(self):
        self.frequency_plot.clear()
        if self.audiogram_checkbox.isChecked():
            print(f"freq: {len(self.significant_magnitudes)} + mag: {len(self.positive_magnitudes_db)}")
            # self.modified_time_plot.setTitle('Audiogram')  # change the label in
            self.frequency_plot.setLabel('bottom', 'Frequency (Hz)')
            self.frequency_plot.setLabel('left', 'Hearing Level (dB)')
            self.frequency_plot.getAxis('bottom').setTicks([[(f, str(f)) for f in self.positive_frequencies]])
            self.frequency_plot.invertY(True)  # Audiograms typically have inverted y-axis
            self.frequency_plot.showGrid(x=True, y=True)

            # Move x-axis to the top
            self.frequency_plot.getPlotItem().layout.removeItem(
                self.frequency_plot.getPlotItem().getAxis('bottom'))
            self.frequency_plot.getPlotItem().layout.addItem(
                self.frequency_plot.getPlotItem().getAxis('bottom'), 1, 1)

            self.frequency_plot.plot(self.significant_frequencies, self.positive_magnitudes_db,
                                         pen=None, symbol='o')
        else:
            # Move x-axis to the bottom again
            # self.frequency_plot.getPlotItem().layout.removeItem(self.modified_
            # time_plot.getPlotItem().getAxis('bottom'), 1, 1)
            # self.frequency_plot.getPlotItem().layout.addItem(
            # self.frequency_plot.getPlotItem().getAxis('bottom'))
            if self.modified_positive_magnitudes is not None:
                self.frequency_plot.plot(self.positive_frequencies, self.modified_positive_magnitudes, pen="m")
            else:
                self.frequency_plot.plot(self.positive_frequencies, self.positive_magnitudes, pen="m")

    def inverse_fourier_transform(self, new_magnitudes):
        new_mag_conponent = new_magnitudes * np.exp(1j * self.original_phases)
        modified_signal = librosa.istft(new_mag_conponent)
        return modified_signal

    def modify_volume(self, slidervalue, object_number):
        print(f"gwa modify   value {slidervalue} object number {object_number}")
        start_freq, end_freq = 0, 0
        gain = 0
        if self.mode == "Animal":
            start_freq, end_freq = self.animals[object_number]
            gain = slidervalue/self.previous_animals_sliders_values[object_number-1]
            self.previous_animals_sliders_values[object_number-1] = slidervalue
            print(f"the start freq is {start_freq} and the end freq is {end_freq}. "
                  f"max of freqs in all data is {max(self.original_freqs)}")
        elif self.mode == "Music":
            print("ana gwaa modify 1")
            start_freq, end_freq = self.final_music_freq[object_number]
            gain = slidervalue/self.previous_music_sliders_values[object_number-1]
            self.previous_music_sliders_values[object_number-1] = slidervalue
            print("ana gwaa modify 2")
            print(f"the start freq is {start_freq} and the end freq is {end_freq}. max of freqs in all data is {max(self.original_freqs)}")

        start_idx = np.where(np.abs(self.original_freqs - start_freq) <= self.tolerance)[0]
        end_idx = np.where(np.abs(self.original_freqs - end_freq) <= self.tolerance)[0]
        print(f"the freq at start idx is {self.original_freqs[start_idx]} and the start idx is {start_idx}")
        # if len(start_idx) > 0 and len(end_idx) > 0:
        #     start_idx = start_idx[0]
        #     end_idx = end_idx[0]
        start_idx = int(start_idx[0]) if isinstance(start_idx, np.ndarray) else int(start_idx)
        end_idx = int(end_idx[0]) if isinstance(end_idx, np.ndarray) else int(end_idx)
        self.modified_amplitudes[start_idx:end_idx] *= gain
        self.modified_time_signal = self.inverse_fourier_transform(self.modified_amplitudes)
        self.modified_time_plot.clear()
        time = np.linspace(0, len(self.modified_time_signal) / self.sampling_frequency,
                           num=len(self.modified_time_signal))
        self.modified_time_plot.plot(time, self.modified_time_signal, pen=(50, 100, 240))
        self.plot_spectrogram(self.modified_time_signal, self.sampling_frequency, self.spectogram_modified_data_graph)
        self.save_audio()

    def save_audio(self):
        if self.mode == "Animal":
            save_dir = "./AnimalAudios"
        if self.mode == "Music":
            save_dir = "./music"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_dir, f"modified_audio_{timestamp}.wav")

        # self.modified_time_signal = np.clip(self.modified_time_signal, -1, 1)  # Ensure values are between -1 and 1
        sf.write(save_path, self.modified_time_signal,
                 self.sampling_frequency)
        self.saved_audio_path = save_path
        print(f"Audio saved at: {save_path}")


def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
