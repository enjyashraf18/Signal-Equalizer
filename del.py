def modify_volume(self, slidervalue, object_number):
    print(f"gwa modify   value {slidervalue} object number {object_number}")
    start_freq, end_freq = 0, 0
    gain = 0
    if self.mode == "Animal":
        start_freq, end_freq = self.animals[object_number]
        gain = slidervalue / self.previous_animals_sliders_values[object_number - 1]
        self.previous_animals_sliders_values[object_number - 1] = slidervalue
        print(f"the start freq is {start_freq} and the end freq is {end_freq}. "
              f"max of freqs in all data is {max(self.original_freqs)}")

    elif self.mode == "Music":
        print("ana gwaa modify 1")
        start_freq, end_freq = self.final_music_freq[object_number]
        gain = slidervalue / self.previous_music_sliders_values[object_number - 1]
        self.previous_music_sliders_values[object_number - 1] = slidervalue
        print("ana gwaa modify 2")
        print(
            f"the start freq is {start_freq} and the end freq is {end_freq}. max of freqs in all data is {max(self.original_freqs)}")

    elif self.mode == "ECG":
        start_freq, end_freq = self.final_ECG_freq[object_number]
        gain = slidervalue * 10 / self.previous_ECG_sliders_values[object_number - 1]
        self.previous_ECG_sliders_values[object_number - 1] = slidervalue * 10
        print(
            f"the start freq is {start_freq} and the end freq is {end_freq}. max of freqs in all data is {max(self.original_freqs)}")

    elif self.mode == "Uniform":
        slider = self.sliders[object_number]
        label = self.sliders_labels[object_number].text()
        print(f"label: {label}")
        # start_freq = int(label.split('-')[0])
        # end_freq = int(label.split('-')[1].split(' ')[0])
        gain = slidervalue / 100
        self.modified_amplitudes = self.original_magnitudes.copy()


    start_idx = np.where(np.abs(self.original_freqs - start_freq) <= self.tolerance)[0]
    end_idx = np.where(np.abs(self.original_freqs - end_freq) <= self.tolerance)[0]
    print(f"the freq at start idx is {self.original_freqs[start_idx]} and the start idx is {start_idx}")
    print(f"shoghl habiba final {start_idx}, {end_idx}")
    # if len(start_idx) > 0 and len(end_idx) > 0:
    #     start_idx = start_idx[0]
    #     end_idx = end_idx[0]
    start_idx = int(start_idx[0]) if isinstance(start_idx, np.ndarray) else int(start_idx)
    end_idx = int(end_idx[0]) if isinstance(end_idx, np.ndarray) else int(end_idx)

    self.modified_amplitudes[start_idx:end_idx] *= gain
    print(f"Modified Amplitudes: {self.modified_amplitudes}")
    self.modified_time_signal = self.inverse_fourier_transform(self.modified_amplitudes)
    self.modified_time_plot.clear()
    time = np.linspace(0, len(self.modified_time_signal) / self.sampling_frequency,
                       num=len(self.modified_time_signal))

    self.modified_time_plot.plot(time, self.modified_time_signal, pen=(50, 100, 240))

    self.plot_spectrogram(self.modified_time_signal, self.sampling_frequency, self.spectrogram_modified_canvas,
                          self.spectrogram_modified_figure)
    self.change_frequency_plot()
    self.save_audio()