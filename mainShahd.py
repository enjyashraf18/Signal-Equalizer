# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QPushButton, QSlider
# from PyQt5.QtGui import QIcon
# import pyqtgraph as pg
# from PyQt5 import uic, QtMultimedia
# import pandas as pd
# import numpy as np
# from pyqtgraph import ImageItem
# from scipy.io import wavfile
# from scipy.fft import fft
# from animal import Animal
# import os
# import time
# import librosa
# import soundfile as sf
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         uic.loadUi("EqualizerOld.ui", self)
#         # VARIABLES
#         self.mode = "Animal"  # Change from dropdown menu
#         self.animals ={1:[47.0, 1172],2:[2971.5,5250]}
#         self.tolerance = 10
#
#         # in case of .csv
#         # self.time = None
#         # self.amplitude = None
#
#         # in case of .wav
#         self.previous_animals_sliders_values =[1]*4   # we want to make it more generalized
#         self.wav_file_path = None
#         self.sampling_frequency = None
#         self.magnitude = None
#         self.time_axis = None
#         self.sound = None
#         self.frequencies = None
#         self.positive_frequencies = None
#         self.fft_data = None
#         self.signal = None
#
#         # UI
#         self.setWindowTitle("Signal Equalizer")
#         self.setWindowIcon(QIcon("Deliverables/equalizer_icon.png"))
#         self.horizontal_layout = self.findChild(QHBoxLayout, "horizontalLayout_5")
#
#         self.specto_layout = self.findChild(QHBoxLayout,"horizontalLayout_27")
#
#         # Removing placeholder widgets
#         self.old_original_time_plot = self.findChild(QWidget, "widget")
#         self.old_modified_time_plot = self.findChild(QWidget, "widget_2")
#         self.horizontal_layout.removeWidget(self.old_original_time_plot)
#         self.horizontal_layout.removeWidget(self.old_modified_time_plot)
#
#         self.old_original_time_plot.deleteLater()
#         self.old_modified_time_plot.deleteLater()
#
#         self.original_time_plot = pg.PlotWidget()
#         self.modified_time_plot = pg.PlotWidget()
#
#         self.spectogram_original_data_graph = pg.PlotWidget()
#         self.spectogram_modified_data_graph = pg.PlotWidget()
#
#         self.horizontal_layout.addWidget(self.original_time_plot)
#         self.horizontal_layout.addWidget(self.modified_time_plot)
#
#         self.specto_layout.addWidget(self.spectogram_original_data_graph)
#         self.specto_layout.addWidget(self.spectogram_modified_data_graph)
#
#
#         # Sliders
#         self.sliders = []
#         placeholder_slider = QSlider()
#         self.sliders.append(placeholder_slider)
#         for i in range(1, 11):
#             slider = self.findChild(QSlider, f"verticalSlider_{i}")
#             slider.valueChanged.connect(lambda value, index=i: self.on_slider_change(value, index))
#             slider.setRange(1, 10)
#             self.sliders.append(slider)
#
#         self.upload_button = QPushButton("Upload")  # Change to find child
#         self.upload_button.clicked.connect(self.load_signal)
#         self.horizontal_layout.addWidget(self.upload_button)
#
#         self.play_button = self.findChild(QPushButton, "pushButton_4")
#         self.play_button.clicked.connect(self.play_audio)
#         # self.init_ui()
#         self.center_on_screen()
#
#     def init_ui(self):
#         pass
#
#     def center_on_screen(self):
#         qr = self.frameGeometry()
#         cp = QApplication.desktop().screenGeometry().center()
#         qr.moveCenter(cp)
#         self.move(qr.topLeft())
#
#     def load_signal(self):
#         filename = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.flac)")
#         self.wav_file_path = filename[0]
#         if self.wav_file_path:
#             if self.wav_file_path.lower().endswith('.wav') or self.wav_file_path.lower().endswith(
#                     '.mp3') or self.wav_file_path.lower().endswith('.flac'):
#                 try:
#                     self.signal, self.sampling_frequency = librosa.load(self.wav_file_path, sr=None,mono=True)  # sr=None to keep original sampling rate
#                     self.time_axis = np.linspace(0, len(self.signal) / self.sampling_frequency,num=len(self.signal))
#                     stft = librosa.stft(self.signal)
#                     self.original_magnitudes, self.original_phases = librosa.magphase(stft)
#                     self.modified_amplitudes = self.original_magnitudes.copy()
#                     self.original_freqs = librosa.fft_frequencies(sr=self.sampling_frequency)
#                     self.plot_signal()
#                     #.plot_frequency_magnitude()
#                 except Exception as e:
#                     print(f"Error. Couldn't upload: {e}")
#
#
#     def play_audio(self):
#         if hasattr(self, 'saved_audio_path') and self.saved_audio_path:
#             # Play the modified and saved audio file
#             self.sound = QtMultimedia.QSound(self.saved_audio_path)
#             self.sound.play()
#
#
#     def plot_signal(self):
#         self.original_time_plot.plot(self.time_axis, self.signal, pen='c')
#         self.plot_spectrogram(self.signal, self.sampling_frequency, self.spectogram_original_data_graph)
#
#     def plot_spectrogram(self, signal, sampling_frequency, plot_widget):
#         stft = librosa.stft(signal)
#         spectrogram_data, _ = librosa.magphase(stft)
#         spectrogram_db = librosa.amplitude_to_db(spectrogram_data, ref=np.max)
#         plot_widget.clear()
#         self.img_item = ImageItem()
#         plot_widget.addItem(self.img_item)
#         cmap = pg.colormap.get('viridis')
#         self.img_item.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256))
#
#         self.img_item.setImage(spectrogram_db, autoLevels=True)
#
#         time_bins = spectrogram_db.shape[1]
#         freq_bins = spectrogram_db.shape[0]
#         self.img_item.setRect(0, 0, time_bins, freq_bins)
#
#         plot_widget.setAspectLocked(False)
#
#         plot_widget.getAxis('bottom').setTicks(
#             [[(i, f"{i / sampling_frequency:.2f}") for i in range(0, time_bins, max(1, time_bins // 10))]])
#         plot_widget.getAxis('left').setTicks([[(i, f"{i * (sampling_frequency / 2) / freq_bins:.0f}") for i in
#                                                     range(0, freq_bins, max(1, freq_bins // 10))]])
#
#         plot_widget.autoRange()
#
#     def changing_slider_values(self):
#         if self.mode == "Uniform":
#             min_frequency = self.positive_frequencies[0]
#             range_of_frequencies = self.positive_frequencies[-1] - min_frequency
#             step_size = range_of_frequencies/10
#             # print(f"range: {range_of_frequencies}")
#             # print(f"step: {step_size}")
#             # example: 10 20 30 50 60 100 150 200 250
#             # range: 240
#             # each slider: 240/10 = 24 value
#             i = 0
#             j = 1
#             for k in range(1, 11):
#                 slider = self.sliders[k]
#                 slider.setRange(int(min_frequency + i*step_size), int(min_frequency + j*step_size))
#                 # print(f"slider{k} range: ({int(min_frequency + i*step_size)}, {int(min_frequency + j*step_size)})")
#                 i += 1
#                 j += 1
#
#     def on_slider_change(self, value, index):
#         if self.mode == "Animal":
#             self.modify_volume(value, index)
#
#     # def fourier_transform(self):
#     #     sampling_period = 1 / self.sampling_frequency
#     #     self.fft_data = np.fft.rfft(self.current_signal)  # return the mag of positive part with (mag & phases)
#     #     self.frequencies = np.fft.rfftfreq(len(self.fft_data), sampling_period) # carries value of each component (Hz)
#     #
#     #     # print(f"fft_data: {self.fft_data[0:3]}")
#     #     # print(f"frequencies: {self.frequencies}")
#     #     return np.abs(self.fft_data), np.angle(self.fft_data), self.frequencies # return the mag , phase and real freq:positive part
#     def inverse_fourier_transform(self, new_magnitudes):
#         new_mag_conponent = new_magnitudes * np.exp(1j * self.original_phases)
#         modified_signal = librosa.istft(new_mag_conponent)
#         return modified_signal
#     def modify_volume(self, slidervalue, object_number):
#         start_freq, end_freq = 0,0
#         gain = 0
#         if self.mode == "Animal":
#             start_freq, end_freq = self.animals[object_number]
#             gain = slidervalue/self.previous_animals_sliders_values[object_number-1]
#             self.previous_animals_sliders_values[object_number-1] = slidervalue
#             print(f"the start freq is {start_freq} and the end freq is {end_freq}. max of freqs in all data is {max(self.original_freqs)}")
#         start_idx = np.where(np.abs(self.original_freqs - start_freq) <= self.tolerance)[0]
#         end_idx = np.where(np.abs(self.original_freqs - end_freq) <= self.tolerance)[0]
#         print(f"the freq at start idx is {self.original_freqs[start_idx]} and the start idx is {start_idx}")
#         # if len(start_idx) > 0 and len(end_idx) > 0:
#         #     start_idx = start_idx[0]
#         #     end_idx = end_idx[0]
#         start_idx = int(start_idx[0]) if isinstance(start_idx, np.ndarray) else int(start_idx)
#         end_idx = int(end_idx[0]) if isinstance(end_idx, np.ndarray) else int(end_idx)
#         self.modified_amplitudes[start_idx:end_idx] *= gain
#         self.modified_time_signal = self.inverse_fourier_transform(self.modified_amplitudes)
#         self.modified_time_plot.clear()
#         time = np.linspace(0, len(self.modified_time_signal) / self.sampling_frequency,num=len(self.modified_time_signal))
#         self.modified_time_plot.plot(time, self.modified_time_signal, pen=(50,100,240))
#         self.plot_spectrogram(self.modified_time_signal, self.sampling_frequency, self.spectogram_modified_data_graph)
#         self.save_audio()
#
#     def save_audio(self):
#         save_dir = "./AnimalAudios"
#         timestamp = time.strftime("%Y%m%d_%H%M%S")
#         save_path = os.path.join(save_dir, f"modified_audio_{timestamp}.wav")
#
#         #self.modified_time_signal = np.clip(self.modified_time_signal, -1, 1)  # Ensure values are between -1 and 1
#         sf.write(save_path, self.modified_time_signal,
#                  self.sampling_frequency)
#         self.saved_audio_path = save_path
#         print(f"Audio saved at: {save_path}")
#
#
#
# def main():
#     app = QApplication([])
#     main_window = MainWindow()
#     main_window.show()
#     app.exec_()
#
#
# if __name__ == "__main__":
#     main()