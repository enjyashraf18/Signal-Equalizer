import sounddevice as sd
import numpy as np
#from MainWindow import MainWindow
class Animal():
    def __init__(self):
        super().__init__()
        self.animals ={1:[47.0, 1172],2:[2972,5254.10]}
        self.tolerance = 5

    # def modify_volume(self, slidervalue, num_animal):
    #     phases, amplitudes, frequencies = MainWindow.fourier_transform()
    #     start_freq, end_freq = self.animals[num_animal]
    #     start_idx = np.where(np.abs(frequencies - start_freq) < self.tolerance)[0]
    #     end_idx = np.where(np.abs(frequencies - end_freq) < self.tolerance)[0]
    #     amplitudes[start_idx : end_idx+1] *= slidervalue
    #     modified_time_signal = MainWindow.inverse_fourier_transform(amplitudes, phases)
    #     MainWindow.modified_time_plot.clear()
    #     MainWindow.modified_time_plot.plot(MainWindow.time_axis, modified_time_signal, pen=(50,100,240))









