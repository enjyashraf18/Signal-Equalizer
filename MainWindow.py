from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QHBoxLayout, QFileDialog, QPushButton, QSlider, QLabel,
                             QCheckBox, QComboBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt
import pyqtgraph as pg
from PyQt5 import uic, QtMultimedia
from PyQt5 import QtCore, QtGui
from pyqtgraph.Qt import QtCore, QtGui
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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.signal import butter, filtfilt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Equalizer.ui", self)
        # VARIABLES
        self.mode = "Uniform"  # Default Mode
        self.is_playing = False
        self.media_player = QMediaPlayer()

        # SHAHD #
        self.animals = {1: [47.0, 1172], 2: [2971.5, 5250],3: [1205,2863], 4: [7031,15796]}
        self.final_music_freq = {1: [20, 500], 2: [500, 2000], 3: [2000, 8000], 4: [8000, 16000]}

        self.final_ECG_freq = {1: [4, 6], 2: [1, 4.5], 3: [3, 8], 4: [700, 800]}
        self.magnitudes = [0.0001, 0.1, 1, 10, 100]
        self.uniform_label = {1: "0-10Hz", 2: "10-20Hz", 3: "20-30Hz", 4: "30-40Hz", 5: "40-50Hz", 6: "50-60Hz", 7: "60-70Hz", 8: "70-80Hz", 9: "80-90Hz", 10:"90-100Hz"}
        self.animals_labels = {1: "Lion", 2: "Bird", 3: "Monkey", 4: "Bat"}
        self.music_label = {1: "Bass", 2: "Piano", 3: "Guitar", 4: "Cymbal"}
        self.ecg_label = {1: "Normal ECG", 2: "Atrial Flutter", 3: "Atrial Fibrillation", 4: "Ventricular Tachycardia"}

        self.tolerance = 10
        self.previous_animals_sliders_values = [1] * 4   # we want to make it more generalized
        self.previous_music_sliders_values = [1] * 4  # we want to make it more generalized
        self.previous_ECG_sliders_values = [1] * 4  # we want to make it more generalized
        self.signal = None
        self.original_freqs = None
        self.modified_amplitudes = None
        self.original_phases = None
        self.original_magnitudes = None
        self.img_item = None
        self.modified_time_signal = []
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
        self.modified_signal = None

        #music
        self.final_music = None
        self.bass = None
        self.piano = None
        self.guitar = None
        self.cymbal = None
        self.is_resetting_sliders = False

        self.line_for_rewind = None

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
        # self.spectogram_original_data_graph = pg.PlotWidget()
        # self.spectogram_modified_data_graph = pg.PlotWidget()

        self.original_signal_layout.addWidget(self.original_time_plot)
        self.modified_signal_layout.addWidget(self.modified_time_plot)
        # self.original_spectrogram_layout.addWidget(self.spectogram_original_data_graph)
        # self.modified_spectrogram_layout.addWidget(self.spectogram_modified_data_graph)
        self.frequency_layout.addWidget(self.frequency_plot)

        self.original_time_plot_data_item = self.original_time_plot.plot([], [], pen='blue')
        self.modified_time_plot_data_item = self.modified_time_plot.plot([], [], pen='green')
        self.spectrogram_original_figure = Figure(facecolor='black')
        self.spectrogram_original_canvas = FigureCanvas(self.spectrogram_original_figure)
        self.spectrogram_original_canvas.setMinimumHeight(160)
        self.spectrogram_original_canvas.setMaximumHeight(16000)
        self.spectrogram_modified_figure = Figure(facecolor='black')
        self.spectrogram_modified_canvas = FigureCanvas(self.spectrogram_modified_figure)
        self.spectrogram_modified_canvas.setMinimumHeight(160)
        self.spectrogram_modified_canvas.setMaximumHeight(16000)

        # Add the canvas to your layout instead of pg.PlotWidget
        self.original_spectrogram_layout.addWidget(self.spectrogram_original_canvas)
        self.modified_spectrogram_layout.addWidget(self.spectrogram_modified_canvas)

        # Sliders and their labels
        self.sliders = []
        self.sliders_labels = []

        self.default_speed = 100

        self.speed_slider = self.findChild(QSlider, "speed_slider")
        # self.speed_slider.setValue(self.default_speed)
        self.speed_slider.setRange(1, 200)
        self.speed_slider.setValue(self.default_speed)
        self.speed_slider.valueChanged.connect(lambda value: self.change_speed(value))


        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.default_speed)
        self.timer.timeout.connect(self.cine_mode)

        self.modified_timer = QtCore.QTimer()
        self.modified_timer.setInterval(self.default_speed)
        self.modified_timer.timeout.connect(self.cine_mode)
        self.idx_original_time_signal = 0
        self.idx_modified_time_signal = 0
        self.time_data_original_signal = []
        self.magnitude_data_original_signal = []
        self.time_data_modified_signal = []
        self.magnitude_data_modified_signal = []

        # Avoiding Zero-Index Confusion
        placeholder_slider = QSlider()
        placeholder_slider_label = QLabel()
        self.sliders.append(placeholder_slider)
        self.sliders_labels.append(placeholder_slider_label)
        self.checked = False

        for i in range(1, 11):
            slider = self.findChild(QSlider, f"slider_{11-i}")
            # if self.mode == "Uniform":
            slider.setRange(0, 200)
            slider.setValue(100)
            slider.valueChanged.connect(lambda value, index=i: self.modify_volume(value, index))
            # else:
            #     print("INSIDE ELSE1")
            #     slider.setRange(0, 4)
            #     slider.setValue(2)
            #     slider.valueChanged.connect(lambda value, index=i: self.modify_volume(self.magnitudes[value], index))
            self.sliders.append(slider)
            slider_label = self.findChild(QLabel, f"label_slider{11 - i}")
            self.sliders_labels.append(slider_label)

        self.upload_button = self.findChild(QPushButton, "upload_button")
        self.upload_button.clicked.connect(self.load_signal)

        self.play_button = self.findChild(QPushButton, "play_signal")
        self.play_button.clicked.connect(self.togglePlaySignal)
        # self.play_button.toggled.connect(lambda checked: self.togglePlaySignal(self.checked))

        self.rewind_button = self.findChild(QPushButton, "rewind")
        self.rewind_button.clicked.connect(self.rewind_signal)

        self.zoom_in_button = self.findChild(QPushButton, "zoom_in")
        self.zoom_in_button.clicked.connect(lambda: self.zoom_for_both_signals(zoomIn=True))

        self.zoom_out_button = self.findChild(QPushButton, "zoom_out")
        self.zoom_out_button.clicked.connect(lambda: self.zoom_for_both_signals(zoomIn=False))

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
        self.iconplay = QtGui.QIcon()
        self.iconplay.addPixmap(QtGui.QPixmap("Deliverables/play-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.iconpause = QtGui.QIcon()
        self.iconpause.addPixmap(QtGui.QPixmap("Deliverables/video-pause-button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.spectrogram_original_label = self.findChild(QLabel, "original_spectrogram_label")
        self.spectrogram_modified_label = self.findChild(QLabel, "modified_spectrogram_label")
        self.spectrogram_checkbox = self.findChild(QCheckBox, "spectrogram_checkbox")
        self.spectrogram_checkbox.stateChanged.connect(
            lambda state: self.spectrogram_toggle(state))
        self.first_play_click = True

    def change_label(self,number_of_labels):
        if self.mode == "Uniform":
            for i in range(1, number_of_labels):
                self.sliders_labels[i].setText(self.uniform_label[i])

        elif self.mode == "Animal":
            for i in range(1, number_of_labels):
                # self.sliders_labels[i].setText(self.animals_labels[i])
                self.sliders_labels[i].setPixmap(QPixmap(f"Deliverables/{self.animals_labels[i]}.png"))

        elif self.mode == "Music":
            for i in range(1,number_of_labels):
                # self.sliders_labels[i].setText(self.music_label[i])
                self.sliders_labels[i].setPixmap(QPixmap(f"Deliverables/{self.music_label[i]}.png"))

        elif self.mode == "ECG":
            for i in range(1,number_of_labels):
                self.sliders_labels[i].setText(self.ecg_label[i])

    def hide_show_sliders(self,number_of_previous_sliders,number_of_new_sliders):
        for i in range(1,number_of_previous_sliders):
            self.sliders[i].hide()
            self.sliders_labels[i].hide()
        for i in range(1,number_of_new_sliders):
            self.sliders[i].show()
            self.sliders_labels[i].show()

        self.change_label(number_of_new_sliders)


    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_mode(self):
        self.mode = self.mode_combobox.currentText()
        print(f"{self.mode}")
        if self.mode != "Uniform":
            self.hide_show_sliders(11,5)
        else:
            self.hide_show_sliders(5, 11)
        self.reset_variables_and_graphs()


    # def update_mode(self):
    #     self.mode = self.mode_combobox.currentText()
    #     self.original_time_plot.clear()
    #     self.modified_time_plot.clear()
    #     self.spectogram_original_data_graph.clear()
    #     self.spectogram_modified_data_graph.clear()
    #     self.frequency_plot.clear()


    def bandwidth_filter(data, lower_freq, higher_freq, sr, order=5):
        # filtered_data el mafrod teb2a sos y3ni second order sections
        filtered_data = butter(order, [lower_freq, higher_freq], btype='band', fs=sr, output='sos')
        return sosfilt(filtered_data, data)

    def reset_variables_and_graphs(self):
        self.modified_amplitudes = None
        self.modified_time_signal = None
        self.original_magnitudes = None
        self.original_freqs = None
        self.frequency_magnitude = None
        self.original_time_plot.clear()
        self.modified_time_plot.clear()
        self.spectrogram_original_figure.clear()
        self.spectrogram_modified_figure.clear()
        self.frequency_plot.clear()

    def load_signal(self):
        self.reset_variables_and_graphs()
        filename = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.flac)")
        self.original_wav_file_path = filename[0]
        if self.original_wav_file_path:
            self.play_button.setIcon(self.iconplay)
            self.checked = True
            if self.original_wav_file_path.lower().endswith('.wav') or self.original_wav_file_path.lower().endswith(
                    '.mp3') or self.original_wav_file_path.lower().endswith('.flac'):
                try:
                    self.signal, self.sampling_frequency = librosa.load(self.original_wav_file_path, sr=None, mono=True)  # sr=None to keep original sampling rate
                    print(f"self.signal: {self.signal}")
                    if self.mode == "ECG":
                        self.time_axis = np.arange(len(self.signal))
                        data_x_ecg = np.divide(np.linspace(0, len(self.signal)), self.sampling_frequency)
                        # dy kda single array of frequency components
                        stft = np.fft.rfft(self.signal)
                        self.original_magnitudes = np.abs(stft)
                        self.original_phases = np.angle(stft)
                        self.frequency_magnitude = np.abs(stft)
                        self.original_freqs = np.fft.rfftfreq(len(self.signal), data_x_ecg[1] - data_x_ecg[0])
                    else:
                        if self.mode == "Uniform":
                            self.signal = librosa.effects.preemphasis(self.signal, coef=1)
                            self.signal = self.signal[1000:len(self.signal) - 1000]

                        self.time_axis = np.linspace(0, len(self.signal) / self.sampling_frequency, num=len(self.signal))

                        stft = librosa.stft(self.signal)
                        self.original_magnitudes, self.original_phases = librosa.magphase(stft)
                        self.frequency_magnitude = np.mean(np.abs(stft), axis=1)
                        self.original_freqs = librosa.fft_frequencies(sr=self.sampling_frequency)

                    self.modified_amplitudes = self.original_magnitudes.copy()

                    if self.mode == "Uniform":
                        # Filter out low frequencies (below 64 Hz)
                        low_freq_threshold = 64
                        # print(f"size: {len(self.signal)}")
                        significant_indices = np.where(self.frequency_magnitude > 0.05)[0]
                        self.original_magnitudes = self.original_magnitudes[significant_indices]
                        self.original_phases = self.original_phases[significant_indices]
                        self.frequency_magnitude = self.frequency_magnitude[significant_indices]
                        self.original_freqs = self.original_freqs[significant_indices]
                        self.modified_amplitudes = self.modified_amplitudes[significant_indices]

                    print(f"the len of the original freq is {self.original_freqs.shape} and the len of original mag is {self.original_magnitudes.shape}")
                    self.plot_signal()
                    self.reset_sliders()  # resetting sliders to 100 after each upload
                except Exception as e:
                    print(f"Error. Couldn't upload: {e}")
           # self.timer.start()
            #self.modified_timer.start()

    def plot_signal(self):
        print("and fl plot 1")
        # Clearing previous upload first
        self.original_time_plot.clear()
        self.modified_time_plot.clear()
        self.frequency_plot.clear()
        # self.fourier_transform()
        self.setting_slider_ranges()
        self.spectrogram_original_figure.clear()
        self.spectrogram_modified_figure.clear()
        # the below is the method to plot in uniform mode
        #self.original_time_plot.plot(self.time_axis, self.magnitude.astype(float), pen='c')
        print("and fl plot 2")
        self.original_time_plot.plot(self.time_axis, self.signal, pen='c')
        print("and fl plot 3")
        # if self.mode == "Uniform":
        #     # Filter the signal before passing it to the spectrogram
        #     low_freq_threshold = 64
        #     filtered_signal = self.high_pass_filter(self.signal, self.sampling_frequency, low_freq_threshold)
        #     self.plot_spectrogram(filtered_signal, self.sampling_frequency, self.spectrogram_original_canvas,
        #                           self.spectrogram_original_figure)
        #
        # else:
        self.plot_spectrogram(self.signal, self.sampling_frequency, self.spectrogram_original_canvas, self.spectrogram_original_figure)
        print("and fl plot 4")
        # print(f"the len of the freq mag is {self.frequency_magnitude.shape}")
        self.change_frequency_plot()
        print("and fl plot 5")
        # self.frequency_plot.plot(self.original_freqs, self.frequency_magnitude, pen="m")
        # self.frequency_plot.showGrid(x=False, y=False)
        # self.frequency_plot.setLabel('bottom', 'Frequency (Hz)')
        # self.frequency_plot.setLabel('left', 'Magnitude')


    def update_final_music(self, signal, sr):
        self.bass =self.bandwidth_filter(signal, 20, 500, sr)
        self.piano =self.bandwidth_filter(signal, 500, 2000, sr)
        self.guitar= self.bandwidth_filter(signal, 2000, 8000, sr)
        self.cymbal= self.bandwidth_filter(signal, 8000, 16000, sr)
        self.final_music = self.guitar + self.bass+ self.piano +self.cymbal
        self.final_music_freq = {1: [20, 500], 2: [500, 2000], 3: [2000, 8000], 4:[8000, 16000]}


    def spectrogram_toggle(self,state):
        if state == Qt.Checked: #hidespectrogram
            self.spectrogram_modified_canvas.hide()
            self.spectrogram_original_canvas.hide()
            self.spectrogram_modified_label.hide()
            self.spectrogram_original_label.hide()

        else:
            self.spectrogram_modified_canvas.show()
            self.spectrogram_original_canvas.show()
            self.spectrogram_modified_label.show()
            self.spectrogram_original_label.show()

    # def fourier_transform(self):
    #     if self.mode == "Uniform":
    #         sampling_period = 1 / self.sampling_frequency
    #         self.fft_data = fft(self.signal)  # each value is a frequency component (mag & phase)
    #         self.modified_fft_data = self.fft_data.copy()
    #         self.frequencies = np.fft.fftfreq(len(self.fft_data), sampling_period)  # carries value of each component (Hz)
    #
    #         self.positive_magnitudes = np.abs(self.fft_data)[
    #                                    :len(self.fft_data) // 2]  # Magnitude spectrum (second half is mirror)
    #         self.positive_frequencies = self.frequencies[
    #                                     :len(self.frequencies) // 2]  # +ve frequencies only (start to half)
    #
    #         threshold = 0.15 * np.max(self.positive_magnitudes)  # 10% of the maximum magnitude
    #         significant_indices = np.where(self.positive_magnitudes > threshold)[0]
    #         self.significant_frequencies = self.positive_frequencies[significant_indices]
    #         self.significant_magnitudes = self.positive_magnitudes[significant_indices]
    #         # self.positive_magnitudes_db = np.log10(self.significant_magnitudes)


    # def high_pass_filter(self, signal, sampling_rate, cutoff):
    #     nyquist = 0.5 * sampling_rate
    #     normal_cutoff = cutoff / nyquist
    #     b, a = butter(1, normal_cutoff, btype='high', analog=False)  # 1st-order filter
    #     filtered_signal = filtfilt(b, a, signal)
    #     return filtered_signal


    def plot_spectrogram(self, signal, sampling_frequency, plot_widget_draw, plot_widget_clear):
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal)
        # if self.mode == "Uniform":
            # significant_indices = np.where(signal > 0)[0]
            # signal = signal[significant_indices]
            # self.signal = self.high_pass_filter(self.signal, self.sampling_frequency, 150)

        stft = np.abs(librosa.stft(signal))

        plot_widget_clear.clear()
        ax = plot_widget_clear.add_subplot(111)
        ax.set_facecolor('black')

        img = librosa.display.specshow(librosa.amplitude_to_db(stft, ref=np.max),
                                       sr=sampling_frequency,
                                       y_axis='log',
                                       x_axis='time',
                                       ax=ax)

        plot_widget_clear.colorbar(img, ax=ax)
        #ax.axis('off')
        ax.tick_params(colors='gray')
        ax.xaxis.label.set_color('gray')
        ax.yaxis.label.set_color('gray')
        ax.title.set_color('gray')
        plot_widget_clear.subplots_adjust(left=0.15, right=1.1, top=1, bottom=0.15)
        y_ticks = ax.get_yticks()  # Get default tick positions
        y_tick_labels = []
        for tick in y_ticks:
            if tick >= 1000:
                y_tick_labels.append(f"{int(tick / 1000)} K")
            else:
                y_tick_labels.append(f"{int(tick)}")

        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_tick_labels, color='gray')
        plot_widget_draw.draw()

    def setting_slider_ranges(self):
        if self.mode == "Uniform":
            # threshold = 0.01 * np.max(self.frequency_magnitude)  # 15% of max magnitude
            # significant_indices = np.where(self.frequency_magnitude > threshold)[0]
            # self.significant_frequencies = self.original_freqs[significant_indices]
            # self.significant_magnitudes = self.frequency_magnitude[significant_indices]
            #
            # min_frequency = self.significant_frequencies[0]
            # max_frequency = self.significant_frequencies[-1]

            min_frequency = self.original_freqs[0]
            max_frequency = self.original_freqs[-1]
            print(f"min freq: {min_frequency} + max freq: {max_frequency}")
            range_of_frequencies = max_frequency - min_frequency
            step_size = range_of_frequencies / 10
            # example: 10 20 30 50 60 100 150 200 250
            # range: 240
            # each slider: 240/10 = 24 value
            i = 0
            j = 1
            for k in range(1, 11):
                slider = self.sliders[k]
                slider_label = self.sliders_labels[k]
                slider.setRange(0, 200)
                slider_label.setText(f"{int(min_frequency + i * step_size)}-{int(min_frequency + j * step_size)} Hz")
                i += 1
                j += 1

    def reset_sliders(self):
        self.is_resetting_sliders = True
        for i in range(1, 11):
            slider = self.sliders[i]
            # if self.mode == "Uniform":
            slider.setRange(0, 200)
            slider.setValue(100)
            # else:
            #     slider.setRange(0, 4)
            #     slider.setValue(2)
        self.is_resetting_sliders = False

    # def on_slider_change(self, value, index):
    #     if self.is_resetting_sliders:
    #         return
    #     if self.mode == "Uniform":
    #         self.modify_volume(value, index) # MERGE BOTH FUNCTIONS JUST FIND WHAT MODIFY VOLUME NEEDS FROM UNIFORM
    #
    #         slider = self.sliders[index]
    #         label = self.sliders_labels[index].text()
    #         minimum_value = int(label.split('-')[0])
    #         maximum_value = int(label.split('-')[1].split(' ')[0])
    #         new_percentage = slider.value()
    #         modified_frequencies_indices = np.where((minimum_value <= self.positive_frequencies) &
    #                                                 (self.positive_frequencies <= maximum_value))[0]
    #         # print(f"significant freq: {self.significant_frequencies}")
    #         # print(f"min: {minimum_value}")
    #         # print(f"max: {maximum_value}")
    #         # print(f"modified indices: {modified_frequencies_indices}")
    #         for index in modified_frequencies_indices:
    #             self.modified_fft_data[index] = self.fft_data[index] * (new_percentage / 100)
    #             self.modified_fft_data[-index - 1] = (self.fft_data[-index - 1] *
    #                                                   (new_percentage / 100))  # modify negative component as well
    #         self.modified_signal = ifft(self.modified_fft_data)
    #         self.modified_time_plot.clear()
    #         self.modified_time_plot.plot(self.time_axis, self.modified_signal.real.astype(float), pen='r')
    #
    #         self.change_frequency_plot()
    #         # self.modified_time_plot.clear()
    #         # self.modified_time_plot.plot(self.positive_frequencies, modified_positive_magnitudes, pen="m")
    #
    #         self.saved_audio_path = "modified_signal.wav"
    #         if os.path.exists(self.saved_audio_path):
    #             os.remove(self.saved_audio_path)
    #         wavfile.write(self.saved_audio_path, self.sampling_frequency, self.modified_signal.real.astype(np.int16))
    #         print(f"audio after uniform: {self.modified_signal.real}")
    #         self.media_player.setMedia(QMediaContent())  # Clearing media content so modified is refreshed
    #
    #         print(f"{slider.objectName()}: min:{minimum_value} + max: {maximum_value} + current value: {value}")
    #
    #     elif self.mode == "Animal" or self.mode == "Music" or self.mode == "ECG":
    #         print(f"gwa on_slider_chane  value {value} index {index}" )
    #         self.modify_volume(value, index)

    def play_audio(self, is_playing, audio_type):
        # if self.mode == "Uniform":
        if audio_type == "original_play_audio_button":  # Play original
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.original_wav_file_path)))
        elif audio_type == "modified_play_audio_button":  # Play modified
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.saved_audio_path)))

        self.media_player.stop() if is_playing else self.media_player.play()
        self.is_playing = not is_playing

        button = self.play_original_button if audio_type == 'original_play_audio_button' else self.play_modified_button
        icon = self.play_icon if is_playing else self.pause_icon
        text = "Play Audio" if is_playing else "Pause Audio"
        button.setIcon(icon)
        button.setText(text)

        # SHAHD
        # if self.mode == "Animal" or self.mode == "Music" or self.mode == "ECG":
        #     if hasattr(self, 'saved_audio_path') and self.saved_audio_path:
        #         # Play the modified and saved audio file
        #         self.sound = QtMultimedia.QSound(self.saved_audio_path)
        #         self.sound.play()

    def change_frequency_plot(self):
        self.frequency_plot.clear()
        if self.audiogram_checkbox.isChecked():
            self.frequency_plot.setLabel('bottom', 'Frequency (Hz)')
            self.frequency_plot.setLabel('left', 'Hearing Level')
            self.frequency_plot.showGrid(x=True, y=True)
            self.frequency_plot.setLogMode(x=True, y=False)
            # ticks = [(10, '10'), (100, '100'), (1000, '1000'), (10000, '10000')]
            # self.frequency_plot.getAxis('bottom').setTicks([ticks])
        else:  # Frequency vs Magnitude Mode
            self.frequency_plot.setLabel('bottom', 'Frequency (Hz)')
            self.frequency_plot.setLabel('left', 'Magnitude')
            self.frequency_plot.showGrid(x=True, y=True)
            self.frequency_plot.setLogMode(x=False, y=False)

        if self.modified_time_signal is None:
            print("gwa change freq is none")
            self.frequency_plot.plot(self.original_freqs, self.frequency_magnitude, pen="m")
        else:
            print("gwa change freq is not none")
            if self.mode == "ECG":
                self.frequency_plot.plot(self.original_freqs, self.modified_amplitudes, pen="m")
            else:
                self.frequency_plot.plot(self.original_freqs, np.mean(self.modified_amplitudes, axis=1), pen="m")

    def inverse_fourier_transform(self, new_magnitudes):
        if self.mode == "ECG":
            print("aaa")
            new_mag_conponent = new_magnitudes.astype(np.complex128)
            new_mag_conponent *= np.exp(1j * self.original_phases)
            modified_signal = np.fft.irfft(new_mag_conponent)
        else:
            new_mag_conponent = new_magnitudes * np.exp(1j * self.original_phases)
            modified_signal = librosa.istft(new_mag_conponent)
        return modified_signal

    def modify_volume(self, slider_value, object_number):
        if self.is_resetting_sliders:
            return
        start_freq, end_freq = 0, 0
        gain = 0
        if self.mode == "Animal":
            # slider_value = self.magnitudes[slider_value]
            print(f"gwa modify value {slider_value} object number {object_number}")
            start_freq, end_freq = self.animals[object_number]
            # gain = slider_value/self.previous_animals_sliders_values[object_number-1]
            gain = slider_value / 100
            self.previous_animals_sliders_values[object_number-1] = slider_value
            print(f"the start freq is {start_freq} and the end freq is {end_freq}. "
                  f"max of freqs in all data is {max(self.original_freqs)}")

        elif self.mode == "Music":
            print("ana gwaa modify 1")
            # slider_value = self.magnitudes[slider_value]
            print(f"gwa modify value {slider_value} object number {object_number}")
            start_freq, end_freq = self.final_music_freq[object_number]
            # gain = slider_value/self.previous_music_sliders_values[object_number-1]
            gain = slider_value / 100
            self.previous_music_sliders_values[object_number-1] = slider_value
            print("ana gwaa modify 2")
            print(f"the start freq is {start_freq} and the end freq is {end_freq}. max of freqs in all data is {max(self.original_freqs)}")

        elif self.mode == "ECG":
            # slider_value = self.magnitudes[slider_value]
            print(f"gwa modify value {slider_value} object number {object_number}")
            start_freq, end_freq = self.final_ECG_freq[object_number]
            print(f"start and end {start_freq, end_freq}")
            # gain = slider_value * 10/self.previous_ECG_sliders_values[object_number-1]
            gain = slider_value / 100
            self.previous_ECG_sliders_values[object_number-1] = slider_value* 10

        elif self.mode == "Uniform":
            # slider = self.sliders[object_number]
            label = self.sliders_labels[object_number].text()
            start_freq = int(label.split('-')[0])
            end_freq = int(label.split('-')[1].split(' ')[0])
            gain = slider_value / 100
            # self.modified_amplitudes = self.original_magnitudes.copy()

        if self.mode == "ECG":
            indices = np.where((self.original_freqs >= start_freq) & (self.original_freqs <= end_freq))[0]
            self.modified_amplitudes[indices] *= gain
        else:
            start_idx = np.where(np.abs(self.original_freqs - start_freq) <= self.tolerance)[0]
            end_idx = np.where(np.abs(self.original_freqs - end_freq) <= self.tolerance)[0]
            start_idx = int(start_idx[0]) if isinstance(start_idx, np.ndarray) else int(start_idx)
            end_idx = int(end_idx[0]) if isinstance(end_idx, np.ndarray) else int(end_idx)
            self.modified_amplitudes[start_idx:end_idx] = self.original_magnitudes[start_idx:end_idx] * gain
        self.modified_time_signal = self.inverse_fourier_transform(self.modified_amplitudes)
        self.modified_time_plot.clear()

        if self.mode == "ECG":
            time = np.arange(len(self.modified_time_signal))
        else:
            time = np.linspace(0, len(self.modified_time_signal) / self.sampling_frequency,
                               num=len(self.modified_time_signal))

        self.modified_time_plot.plot(time, self.modified_time_signal, pen=(50, 100, 240))

        self.plot_spectrogram(self.modified_time_signal, self.sampling_frequency, self.spectrogram_modified_canvas,
                              self.spectrogram_modified_figure)
        self.change_frequency_plot()
        self.save_audio()

    # def modify_volume(self, slider_value, object_number): #MN NADA
    #     if self.is_resetting_sliders:
    #         return
    #     print(f"gwa modify   value {slider_value} object number {object_number}")
    #     start_freq, end_freq = 0, 0
    #     gain = 0
    #     if self.mode == "Animal":
    #         start_freq, end_freq = self.animals[object_number]
    #         print(f"Slider value: {slider_value}")
    #         # gain = slider_value / self.previous_animals_sliders_values[object_number - 1]
    #         gain = slider_value / 100
    #         self.previous_animals_sliders_values[object_number - 1] = slider_value
    #         print(f"the start freq is {start_freq} and the end freq is {end_freq}. "
    #               f"max of freqs in all data is {max(self.original_freqs)}")
    #
    #     elif self.mode == "Music":
    #         print("ana gwaa modify 1")
    #         start_freq, end_freq = self.final_music_freq[object_number]
    #         print(f"Slider value: {slider_value}")
    #         # gain = slider_value / self.previous_music_sliders_values[object_number - 1]
    #         gain = slider_value / 100
    #         self.previous_music_sliders_values[object_number - 1] = slider_value
    #         print("ana gwaa modify 2")
    #         print(
    #             f"the start freq is {start_freq} and the end freq is {end_freq}. max of freqs in all data is {max(self.original_freqs)}")
    #
    #     elif self.mode == "ECG":
    #         start_freq, end_freq = self.final_ECG_freq[object_number]
    #         # gain = slider_value * 10 / self.previous_ECG_sliders_values[object_number - 1]
    #         gain = slider_value * 10
    #         self.previous_ECG_sliders_values[object_number - 1] = slider_value * 10
    #         print(
    #             f"the start freq is {start_freq} and the end freq is {end_freq}. max of freqs in all data is {max(self.original_freqs)}")
    #
    #     elif self.mode == "Uniform":
    #         # slider = self.sliders[object_number]
    #         label = self.sliders_labels[object_number].text()
    #         start_freq = int(label.split('-')[0])
    #         end_freq = int(label.split('-')[1].split(' ')[0])
    #         gain = slider_value / 100
    #         # self.modified_amplitudes = self.original_magnitudes.copy()
    #
    #     start_idx = np.where(np.abs(self.original_freqs - start_freq) <= self.tolerance)[0]
    #     end_idx = np.where(np.abs(self.original_freqs - end_freq) <= self.tolerance)[0]
    #     print(f"the freq at start idx is {self.original_freqs[start_idx]} and the start idx is {start_idx}")
    #     print(f"shoghl habiba final {start_idx}, {end_idx}")
    #
    #     start_idx = int(start_idx[0]) if isinstance(start_idx, np.ndarray) else int(start_idx)
    #     end_idx = int(end_idx[0]) if isinstance(end_idx, np.ndarray) else int(end_idx)
    #     self.modified_amplitudes[start_idx:end_idx] = self.original_magnitudes[start_idx:end_idx] * gain
    #     self.modified_time_signal = self.inverse_fourier_transform(self.modified_amplitudes)
    #     self.modified_time_plot.clear()
    #     time = np.linspace(0, len(self.modified_time_signal) / self.sampling_frequency,
    #                        num=len(self.modified_time_signal))
    #
    #     self.modified_time_plot.plot(time, self.modified_time_signal, pen=(50, 100, 240))
    #
    #     self.change_frequency_plot()
    #     self.plot_spectrogram(self.modified_time_signal, self.sampling_frequency, self.spectrogram_modified_canvas,
    #                           self.spectrogram_modified_figure)
    #     self.save_audio()

    def save_audio(self):

        save_dir = "./saved audios"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_dir, f"modified_audio_{timestamp}.wav")

        # self.modified_time_signal = np.clip(self.modified_time_signal, -1, 1)  # Ensure values are between -1 and 1
        sf.write(save_path, self.modified_time_signal,
                 self.sampling_frequency)
        self.saved_audio_path = save_path
        print(f"Audio saved at: {save_path}")

    def cine_mode(self):
        if self.signal is not None and len(self.signal) > 0:
            self.idx_original_time_signal, self.time_data_original_signal, self.magnitude_data_original_signal = self.update_graphs_cine_mode(
                self.signal, self.original_time_plot, self.idx_original_time_signal,
                self.time_data_original_signal, self.magnitude_data_original_signal,
                self.original_time_plot_data_item)
            if self.modified_time_signal is not None:
                self.modified_time_plot.clear()
                self.idx_modified_time_signal, self.time_data_modified_signal, self.magnitude_data_modified_signal = self.update_graphs_cine_mode(
                    self.modified_time_signal, self.modified_time_plot,
                    self.idx_modified_time_signal,
                    self.time_data_modified_signal, self.magnitude_data_modified_signal,
                    self.modified_time_plot_data_item)

    def update_graphs_cine_mode(self, signal, plot_widget, index, time, magnitude, plot_data_item):
        batch_size = 500
        length_in_one_frame = int(len(signal) / 10)
        if index < len(signal):
            for i in range(index, min(len(signal), index + batch_size)):
                time.append(self.time_axis[i])
                magnitude.append(signal[i])
            # plot_data_item.setData(time, magnitude)
            self.line_for_rewind = plot_widget.plot(time, magnitude, pen='blue')
            if len(time) > length_in_one_frame:
                plot_widget.setXRange(time[-length_in_one_frame], time[-1])
            else:
                plot_widget.setXRange(self.time_axis[0], self.time_axis[length_in_one_frame - 1])
            plot_widget.update()
            index += batch_size
        return index, time, magnitude

    def rewind_signal(self):
        self.play_button.setIcon(self.iconpause)
        self.checked = False
        self.timer.start()
        self.modified_timer.start()
        self.idx_original_time_signal = 0
        self.time_data_original_signal = []
        self.magnitude_data_original_signal = []
        self.idx_modified_time_signal = 0
        self.time_data_modified_signal = []
        self.magnitude_data_modified_signal = []
        self.original_time_plot.clear()
        self.modified_time_plot.clear()
        self.line_for_rewind.setData([], [])
        self.cine_mode()

    # def link_signals(self):
    #     self.Channel1Viewer.rewindSignal()
    #     self.Channel2Viewer.rewindSignal()
    #     self.PlayChannel2.toggled.disconnect()
    #     self.Channel2Editor.RewindButton.clicked.disconnect()
    #     self.Channel1Editor.SpeedSlider.valueChanged.disconnect()
    #     self.PlayChannel1.toggled.connect(lambda checked: self.togglePlaySignal(checked, "both"))
    #     self.Channel1Editor.RewindButton.clicked.connect(self.wrappedRewind)
    #     self.Channel2Editor.SpeedSlider.valueChanged.connect(self.syncSliders)


    def play_signal1(self):
        print("ana gwa play")
        if self.first_play_click:
            self.modified_time_plot.clear()
            self.original_time_plot.clear()
            self.first_play_click = False
        self.timer.start()
        self.modified_timer.start()
        return

    def pause_signal(self):
        print("ana gwa pause")
        self.timer.stop()
        self.modified_timer.stop()
        return


    def togglePlaySignal(self):
        if self.checked:
            self.play_signal1()
            self.play_button.setIcon(self.iconpause)
            self.checked = False
        else:
            self.pause_signal()
            self.play_button.setIcon(self.iconplay)
            self.checked = True

    def change_speed(self, value):
        self.default_speed = 200-value
        print(f"speed is {self.default_speed}")
        # self.default_speed = int(100/value)
        self.timer.setInterval(self.default_speed)
        self.modified_timer.setInterval(self.default_speed)
        return

    def zoom(self, zoomIn, plot_widget):

        view_box = plot_widget.getViewBox()
        x_range, y_range = view_box.viewRange()
        zoom_factor = 0.8 if zoomIn else 1.25
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        new_x_range = [
            x_center - (x_center - x_range[0]) * zoom_factor,
            x_center + (x_range[1] - x_center) * zoom_factor
        ]
        new_y_range = [
            y_center - (y_center - y_range[0]) * zoom_factor,
            y_center + (y_range[1] - y_center) * zoom_factor
        ]
        view_box.setRange(xRange=new_x_range, yRange=new_y_range)

    def zoom_for_both_signals(self, zoomIn=True):
        self.zoom(zoomIn,self.original_time_plot )
        self.zoom(zoomIn, self.modified_time_plot)
def main():
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
