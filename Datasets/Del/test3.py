import numpy as np
from scipy.fft import fft, fftfreq
from scipy.io import wavfile


class AudioAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sampling_frequency, self.signal = wavfile.read(self.file_path)

        # If stereo, convert to mono by averaging the two channels
        if self.signal.ndim > 1:
            self.signal = np.mean(self.signal, axis=1)

    def fourier_transform(self):
        # Compute the sampling period
        sampling_period = 1 / self.sampling_frequency

        # Apply a window function (e.g., Hamming) to reduce spectral leakage
        windowed_data = self.signal * np.hamming(len(self.signal))

        # Perform FFT on windowed data
        self.fft_data = fft(windowed_data)

        # Get the frequency bins
        self.frequencies = fftfreq(len(self.fft_data), sampling_period)

    def extract_frequencies(self, target_frequencies):
        extracted_data = {}

        for target in target_frequencies:
            # Find the index of the frequency closest to the target frequency
            idx = np.argmin(np.abs(self.frequencies - target))

            # Extract the complex FFT value at this frequency
            fft_value = self.fft_data[idx]

            # Calculate magnitude and phase if needed
            magnitude = np.abs(fft_value)
            phase = np.angle(fft_value)

            # Store the values for further processing
            extracted_data[target] = {'magnitude': magnitude, 'phase': phase}

        return extracted_data


# Example usage
analyzer = AudioAnalyzer("../Audios/100-250-440-1000.wav")
analyzer.fourier_transform()
target_frequencies = [100, 250, 440, 1000]
frequency_data = analyzer.extract_frequencies(target_frequencies)

# Perform mathematical operations
for freq, data in frequency_data.items():
    magnitude = data['magnitude']
    phase = data['phase']

    # Example mathematical operations
    print(f"Frequency: {freq} Hz")
    print(f"  Magnitude: {magnitude}")
    print(f"  Phase: {phase} radians")
    print(f"  Magnitude in dB: {20 * np.log10(magnitude)} dB")
    print(f"  Phase in degrees: {np.degrees(phase)}°\n")
