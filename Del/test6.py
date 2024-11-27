import sys
import librosa
import librosa.display
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets


class SpectrogramApp(QtWidgets.QMainWindow):
    def __init__(self, audio_path):
        super().__init__()
        self.setWindowTitle("Spectrogram Viewer")
        self.setGeometry(100, 100, 1000, 700)

        # Main widget and layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Plot widget for spectrogram
        self.spectrogram_widget = pg.PlotWidget()
        self.layout.addWidget(self.spectrogram_widget)

        # Load and process audio
        self.audio_path = audio_path
        self.plot_spectrogram()

    def plot_spectrogram(self):
        # Load audio file
        y, sr = librosa.load(self.audio_path, sr=None)

        # Generate the spectrogram
        S = librosa.stft(y)
        S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

        # Create image item for spectrogram
        img_item = pg.ImageItem()
        self.spectrogram_widget.addItem(img_item)

        # Display the spectrogram
        img_item.setImage(S_db, autoLevels=False)
        img_item.setRect(pg.QtCore.QRectF(0, 0, S_db.shape[1], S_db.shape[0]))

        # Set the color map
        lut = pg.colormap.get("inferno", source="matplotlib").getLookupTable()
        img_item.setLookupTable(lut)

        # Adjust axis
        self.spectrogram_widget.setLabel('left', 'Frequency (Hz)')
        self.spectrogram_widget.setLabel('bottom', 'Time (s)')
        self.spectrogram_widget.getAxis('left').setTicks(
            [[(i, f"{int(librosa.hz_to_mel(i))}") for i in np.linspace(0, sr // 2, num=10)]]
        )
        # self.spectrogram_widget.getAxis('bottom').setTicks(
        #     [[(i, f"{i / S_db:.}")]]
        # )

        def create_color_bar(self):
            # Add a color bar to represent the intensity of the spectrogram
            color_bar = pg.ColorBarItem(
                values=(-80, 0),  # Min and max dB values
                cmap=pg.colormap.get("inferno", source="matplotlib"),
                label="Intensity (dB)"
            )
            color_bar.setImageItem(self.spectrogram_widget.items[-1])  # Link to the spectrogram image
            self.layout.addWidget(color_bar)

    # Main function to run the application
def main():
    app = QtWidgets.QApplication(sys.argv)
    audio_path = QtWidgets.QFileDialog.getOpenFileName(
        caption="Select a WAV File", filter="WAV Files (*.wav)")[0]

    if audio_path:
        viewer = SpectrogramApp(audio_path)
        viewer.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()

