from scipy.io import wavfile
from scipy.fft import fft, ifft
import numpy as np

sampling_frequency, magnitude = wavfile.read("../Audios/Uniform_Frequencies.wav")
if magnitude.ndim > 1:
    magnitude = np.mean(magnitude, axis=1)

sampling_period = 1 / sampling_frequency
fft_data = fft(magnitude)  # each value is a frequency component (mag & phase)
modified_fft_data = fft_data.copy()
frequencies = np.fft.fftfreq(len(fft_data), sampling_period)

positive_magnitudes = np.abs(fft_data)[:len(fft_data) // 2]  # Magnitude spectrum (second half is mirror)
positive_frequencies = frequencies[:len(frequencies) // 2]  # +ve frequencies only (start to half)
threshold = 0.15 * np.max(positive_magnitudes)  # 10% of the maximum magnitude
significant_indices = np.where(positive_magnitudes > threshold)[0]
significant_frequencies = positive_frequencies[significant_indices]
min_frequency = significant_frequencies[0]
range_of_frequencies = significant_frequencies[-1] - min_frequency
step_size = range_of_frequencies/10

minimum_value = 1000
maximum_value = 10000
new_percentage = 50
modified_frequencies_indices = np.where((minimum_value <= positive_frequencies) &
                                        (positive_frequencies <= maximum_value))[0]

for index in modified_frequencies_indices:
    modified_fft_data[index] *= 0
    modified_fft_data[len(modified_fft_data) - index - 1] *= 0  # modify negative component as well
modified_signal = ifft(modified_fft_data)

print(f"Difference: {fft_data[:20] - modified_fft_data[:20]}")


modified_file_path = "modified_signal_test.wav"
wavfile.write(modified_file_path, sampling_frequency, modified_signal.real.astype(np.int16))
