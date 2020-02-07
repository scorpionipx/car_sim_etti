import pyqtgraph as pg


from logging import getLogger


from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon


from car_sim_etti import settings
from car_sim_etti import APP_SLUG


LOGGER = getLogger(APP_SLUG)


class Signal:
    """

    """
    def __init__(self, label, color, data):
        """

        """
        self.label = label
        self.color = color
        self.data = data


class Plotter(QtWidgets.QWidget):
    """

    """
    DATA_BUFFER_SIZE = 1000

    def __init__(self, parent):
        """

        """
        super(Plotter, self).__init__(parent=parent)
        self.plot_widget = None
        self.signals = []
        self.plot_curves = []
        self.init_gui()

    def init_gui(self):
        h_box = QtWidgets.QVBoxLayout()
        self.setLayout(h_box)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setYRange(-1, 100)
        self.plot_widget.setXRange(0, self.DATA_BUFFER_SIZE)
        self.plot_widget.enableAutoRange('xy', False)
        h_box.addWidget(self.plot_widget)

    def init_signals(self, signals):
        """

        :param signals:
        :type signals: list of Signal
        :return:
        """
        self.DATA_BUFFER_SIZE = 1000
        self.plot_widget.clear()
        self.plot_widget.setXRange(0, self.DATA_BUFFER_SIZE)
        self.plot_widget.setYRange(-1, 100)

        del self.signals
        del self.plot_curves
        self.signals = []
        self.plot_curves = []

        maxim_val = -1
        for signal_index, signal in enumerate(signals):
            self.signals.append(signal)
            curve = pg.PlotCurveItem(pen=signal.color)
            self.plot_curves.append(curve)
            self.plot_widget.addItem(self.plot_curves[signal_index])
            maxim_val = max(max(signal.data), maxim_val)

        maxim_val += 50
        self.plot_widget.setYRange(-1, maxim_val)

    def display_data(self, max_index=1):
        """

        :param max_index:
        :return:
        """
        if max_index >= self.DATA_BUFFER_SIZE:
            self.DATA_BUFFER_SIZE += 500

        self.plot_widget.setXRange(0, self.DATA_BUFFER_SIZE)

        for plot_index, plot_curve in enumerate(self.plot_curves):
            plot_curve.setData(self.signals[plot_index].data[:max_index])


class DataViewer(QtWidgets.QMainWindow):
    """DataViewer

    """

    def __init__(self):
        super(DataViewer, self).__init__()

        self.plot_widget = None

        self.init_gui()
        self.speed_plot_labels = []
        self.pressure_plot_labels = []

        self.speed_plotter = Plotter(parent=self)
        self.speed_plotter.move(25, 25)
        self.speed_plotter.resize(self.width() - 150, self.height() // 2 - 50)

        self.pressure_plotter = Plotter(parent=self)
        self.pressure_plotter.move(25, 25 + self.height() // 2)
        self.pressure_plotter.resize(self.width() - 150, self.height() // 2 - 50)

        self.__main_window_close_event__ = False

    def init_gui(self):
        """

        :return:
        """
        self.setGeometry(100 + settings.WINDOW_WIDTH, 200, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setFixedSize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setWindowTitle('Data viewer')
        self.setWindowIcon(QIcon(settings.WINDOWS_ICON_PATH))
        self.setStyleSheet("QMainWindow {background: 'white';}")

    def closeEvent(self, event):
        """

        :param event:
        :return:
        """
        if self.__main_window_close_event__:
            LOGGER.info('Closing data viewer...')
            event.accept()
        else:
            QtWidgets.QMessageBox.question(self, 'Exit', "Please close main window!", QtWidgets.QMessageBox.Ok)
            event.ignore()

    def __prepare_for_closing__(self):
        """__prepare_for_closing__

        :return:
        """
        self.__main_window_close_event__ = True

    def init_speed_plotter(self, signals):
        """

        :param signals:
        :return:
        """
        for plot_label in self.speed_plot_labels:
            plot_label.hide()

        del self.speed_plot_labels
        self.speed_plot_labels = []

        for index, signal in enumerate(signals):

            c_label = QtWidgets.QLabel(parent=self)
            c_label.move(self.speed_plotter.x() + self.speed_plotter.width() + 25,
                         self.speed_plotter.y() + 32 + index * 25)
            c_label.setStyleSheet("QLabel { background-color : ~~color~~}; }".replace('~~color~~', signal.color))
            c_label.resize(15, 15)
            c_label.show()
            self.speed_plot_labels.append(c_label)

            label = QtWidgets.QLabel(parent=self)
            label.setText(signal.label)
            label.move(self.speed_plotter.x() + self.speed_plotter.width() + 50,
                       self.speed_plotter.y() + 25 + index * 25)
            label.show()
            self.speed_plot_labels.append(label)

        self.speed_plotter.init_signals(signals)

    def init_pressure_plotter(self, signals):
        """

        :param signals:
        :return:
        """
        for plot_label in self.pressure_plot_labels:
            plot_label.hide()

        del self.pressure_plot_labels
        self.pressure_plot_labels = []

        for index, signal in enumerate(signals):

            c_label = QtWidgets.QLabel(parent=self)
            c_label.move(self.pressure_plotter.x() + self.pressure_plotter.width() + 25,
                         self.pressure_plotter.y() + 32 + index * 25)
            c_label.setStyleSheet("QLabel { background-color : ~~color~~}; }".replace('~~color~~', signal.color))
            c_label.resize(15, 15)
            c_label.show()
            self.pressure_plot_labels.append(c_label)

            label = QtWidgets.QLabel(parent=self)
            label.setText(signal.label)
            label.move(self.pressure_plotter.x() + self.pressure_plotter.width() + 50,
                       self.pressure_plotter.y() + 25 + index * 25)
            label.show()
            self.pressure_plot_labels.append(label)

        self.pressure_plotter.init_signals(signals)


class DataViewerFull(QtWidgets.QMainWindow):
    """DataViewer

    """

    def __init__(self):
        super(DataViewerFull, self).__init__()

        self.plot_widget = None

        self.init_gui()
        self.plot_labels = []

        self.plotter = Plotter(parent=self)
        self.plotter.move(25, 25)
        self.plotter.resize(self.width() - 150, self.height() - 50)

        self.__main_window_close_event__ = False

    def init_gui(self):
        """

        :return:
        """
        self.setGeometry(100 + settings.WINDOW_WIDTH, 200, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setFixedSize(1200, 700)
        self.setWindowTitle('Data full viewer')
        self.setWindowIcon(QIcon(settings.WINDOWS_ICON_PATH))
        self.setStyleSheet("QMainWindow {background: 'white';}")

    def closeEvent(self, event):
        """

        :param event:
        :return:
        """
        if self.__main_window_close_event__:
            LOGGER.info('Closing data viewer...')
            event.accept()
        else:
            QtWidgets.QMessageBox.question(self, 'Exit', "Please close main window!", QtWidgets.QMessageBox.Ok)
            event.ignore()

    def __prepare_for_closing__(self):
        """__prepare_for_closing__

        :return:
        """
        self.__main_window_close_event__ = True

    def init_plotter(self, signals):
        """

        :param signals:
        :return:
        """
        for plot_label in self.plot_labels:
            plot_label.hide()

        del self.speed_plot_labels
        self.plot_labels = []

        for index, signal in enumerate(signals):

            c_label = QtWidgets.QLabel(parent=self)
            c_label.move(self.plotter.x() + self.plotter.width() + 25,
                         self.plotter.y() + 32 + index * 25)
            c_label.setStyleSheet("QLabel { background-color : ~~color~~}; }".replace('~~color~~', signal.color))
            c_label.resize(15, 15)
            c_label.show()
            self.plot_labels.append(c_label)

            label = QtWidgets.QLabel(parent=self)
            label.setText(signal.label)
            label.move(self.plotter.x() + self.plotter.width() + 50,
                       self.plotter.y() + 25 + index * 25)
            label.show()
            self.plot_labels.append(label)

        self.plotter.init_signals(signals)
