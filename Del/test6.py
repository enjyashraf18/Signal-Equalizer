import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Logarithmic Plot with Custom Axis')
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create a PlotWidget
        self.frequency_plot = pg.PlotWidget()
        layout.addWidget(self.frequency_plot)

        self.setCentralWidget(central_widget)

        # Define custom ticks
        ticks = [[(3*10, "3.10^1"), (3*(10**2), "3.10^2"), (3*(10**3), "3.10^3"), (2*(10**4), "2.10^4")]]

        # Set the x-axis ticks
        self.frequency_plot.getAxis('bottom').setTicks(ticks)

        # Plot data
        x = np.logspace(1, 4, 100)
        y = np.random.rand(100)
        self.frequency_plot.plot(x, y, pen='b')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
