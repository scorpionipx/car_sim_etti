import json
import logging
import sys
import threading

from time import sleep

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


from car_sim_etti import settings, APP_SLUG
from car_sim_etti.utils.gauge import AnalogGaugeWidget
from car_sim_etti.utils.generic import (
    NOT_AVAILABLE,

    SIGNAL_SAMPLING_PERIOD,

    SIGNAL_ABS_REF,

    SIGNAL_FL_VEL,
    SIGNAL_FR_VEL,
    SIGNAL_RL_VEL,
    SIGNAL_RR_VEL,

    SIGNAL_FL_PRES,
    SIGNAL_FR_PRES,
    SIGNAL_RL_PRES,
    SIGNAL_RR_PRES,

    sim_profile_valid,
    __get_fps_growth__,
)

LOGGER = logging.getLogger(APP_SLUG)


class CarSimETTI(QMainWindow):
    """

    """
    def __init__(self):
        super(CarSimETTI, self).__init__()

        # simulation signals
        self.abs_ref = []

        self.fl_vel = []
        self.fr_vel = []
        self.rl_vel = []
        self.rr_vel = []

        self.fl_pres = []
        self.fr_pres = []
        self.rl_pres = []
        self.rr_pres = []

        # widgets
        # widgets generic
        self.load_sim_profile_button = None
        self.start_sim_profile_button = None
        self.time_base_combo_box = None
        
        # widgets simulation
        self.fl_vel_label = None
        self.fr_vel_label = None
        self.rl_vel_label = None
        self.rr_vel_label = None
        
        self.fl_pres_label = None
        self.fr_pres_label = None
        self.rl_pres_label = None
        self.rr_pres_label = None
        
        self.fl_pres_pbar = None
        self.fr_pres_pbar = None
        self.rl_pres_pbar = None
        self.rr_pres_pbar = None

        self.speed_gauge = None

        self.simulation_progress_label = None

        self.simulation_profile = None
        self.simulation_running = False
        self.simulation_index = 0
        self.simulation_index_growth = -1
        self.simulation_stamps = -1
        self.simulation_time_base = 1
        self.simulation_fps = -1
        self.simulation_period = -1

        self.__fps_task_started__ = False
        self.__stop_fps_task__ = False

        self.init_gui()

    def __reset_simulation_signals__(self):
        """__reset_simulation_signals__
        
            Remove values from simulation signals.
        :return: None
        """
        del self.abs_ref

        del self.fl_vel
        del self.fr_vel
        del self.rl_vel
        del self.rr_vel

        del self.fl_pres
        del self.fr_pres
        del self.rl_pres
        del self.rr_pres

        self.abs_ref = []

        self.fl_vel = []
        self.fr_vel = []
        self.rl_vel = []
        self.rr_vel = []

        self.fl_pres = []
        self.fr_pres = []
        self.rl_pres = []
        self.rr_pres = []

    def load_simulation_profile(self):
        """load_simulation_profile

            Load signals values from simulation profile file.
        :return: process result
        :rtype: bool
        """
        file = self.__get_file__()
        if not file:
            warning = 'Invalid simulation profile file! {}'.format(file)
            LOGGER.warning(warning)
            return False

        LOGGER.info('Loading simulation profile: {}'.format(file))

        try:
            file_handler = open(file, 'r')
            file_content = file_handler.read()
            file_handler.close()
        except Exception as err:
            error = 'Failed to load simulation profile! {}'.format(err)
            LOGGER.error(error)
            return False

        try:
            sim_profile = json.loads(file_content)
        except Exception as err:
            error = 'Failed to parse simulation profile file content! {}'.format(err)
            LOGGER.error(error)
            return False

        if not sim_profile_valid(sim_profile):
            error = 'Invalid simulation profile! {}'.format(file)
            LOGGER.error(error)
            return False

        self.simulation_profile = sim_profile
        del sim_profile

        self.simulation_index_growth = 2
        self.simulation_period = 0.04

        self.__reset_simulation_signals__()

        self.abs_ref = self.simulation_profile[SIGNAL_ABS_REF]

        self.fl_vel = self.simulation_profile[SIGNAL_FL_VEL]
        self.fr_vel = self.simulation_profile[SIGNAL_FR_VEL]
        self.rl_vel = self.simulation_profile[SIGNAL_RL_VEL]
        self.rr_vel = self.simulation_profile[SIGNAL_RR_VEL]

        self.fl_pres = self.simulation_profile[SIGNAL_FL_PRES]
        self.fr_pres = self.simulation_profile[SIGNAL_FR_PRES]
        self.rl_pres = self.simulation_profile[SIGNAL_RL_PRES]
        self.rr_pres = self.simulation_profile[SIGNAL_RR_PRES]

        self.simulation_stamps = len(self.fl_vel)

        LOGGER.info('Simulation profile successfully loaded!')
        return True

    def __get_file__(self):
        """__get_file__

            Get file absolute path.
        :return: file's path
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load simulation profile", "",
                                                        "JSON (*.json);;All Files (*);;Python Files (*.py)",
                                                        options=options)
        if file:
            return file
        return None

    def init_gui(self):
        self.setGeometry(100, 200, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setWindowTitle(settings.WINDOW_TITLE)
        self.setWindowIcon(QIcon(settings.WINDOWS_ICON_PATH))

        self.load_sim_profile_button = QtWidgets.QPushButton(self)
        self.load_sim_profile_button.setText('Load sim profile')
        # noinspection PyTypeChecker
        self.load_sim_profile_button.clicked.connect(self.load_simulation_profile)
        self.load_sim_profile_button.move(100, 10)
        self.load_sim_profile_button.show()

        self.start_sim_profile_button = QtWidgets.QPushButton(self)
        self.start_sim_profile_button.setText('Start sim profile')
        # noinspection PyTypeChecker
        self.start_sim_profile_button.clicked.connect(self.run_simulation_profile)
        self.start_sim_profile_button.move(250, 10)
        self.start_sim_profile_button.show()

        self.time_base_combo_box = QtWidgets.QComboBox(self)
        self.time_base_combo_box.addItem('1x')
        self.time_base_combo_box.addItem('0.5x')
        self.time_base_combo_box.addItem('0.25x')
        self.time_base_combo_box.addItem('0.1x')
        self.time_base_combo_box.move(210, 210)
        self.time_base_combo_box.show()
        self.time_base_combo_box.currentTextChanged.connect(self.update_time_base)

        self.fl_vel_label = QtWidgets.QLabel(self)
        self.fl_vel_label.setText(NOT_AVAILABLE)
        self.fl_vel_label.move(settings.FL_VEL_LABEL_X, settings.FL_VEL_LABEL_Y)
        self.fl_vel_label.show()

        self.fr_vel_label = QtWidgets.QLabel(self)
        self.fr_vel_label.setText(NOT_AVAILABLE)
        self.fr_vel_label.move(settings.FR_VEL_LABEL_X, settings.FR_VEL_LABEL_Y)
        self.fr_vel_label.show()

        self.rl_vel_label = QtWidgets.QLabel(self)
        self.rl_vel_label.setText(NOT_AVAILABLE)
        self.rl_vel_label.move(settings.RL_VEL_LABEL_X, settings.RL_VEL_LABEL_Y)
        self.rl_vel_label.show()

        self.rr_vel_label = QtWidgets.QLabel(self)
        self.rr_vel_label.setText(NOT_AVAILABLE)
        self.rr_vel_label.move(settings.RR_VEL_LABEL_X, settings.RR_VEL_LABEL_Y)
        self.rr_vel_label.show()

        self.fl_pres_label = QtWidgets.QLabel(self)
        self.fl_pres_label.setText(NOT_AVAILABLE)
        self.fl_pres_label.move(settings.FL_PRES_LABEL_X, settings.FL_PRES_LABEL_Y)
        self.fl_pres_label.show()

        self.fr_pres_label = QtWidgets.QLabel(self)
        self.fr_pres_label.setText(NOT_AVAILABLE)
        self.fr_pres_label.move(settings.FR_PRES_LABEL_X, settings.FR_PRES_LABEL_Y)
        self.fr_pres_label.show()

        self.rl_pres_label = QtWidgets.QLabel(self)
        self.rl_pres_label.setText(NOT_AVAILABLE)
        self.rl_pres_label.move(settings.RL_PRES_LABEL_X, settings.RL_PRES_LABEL_Y)
        self.rl_pres_label.show()

        self.rr_pres_label = QtWidgets.QLabel(self)
        self.rr_pres_label.setText(NOT_AVAILABLE)
        self.rr_pres_label.move(settings.RR_PRES_LABEL_X, settings.RR_PRES_LABEL_Y)
        self.rr_pres_label.show()

        self.fl_pres_pbar = QtWidgets.QProgressBar(self)
        self.fl_pres_pbar.setGeometry(50, 50, 20, 100)
        self.fl_pres_pbar.setOrientation(Qt.Vertical)
        self.fl_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.fl_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.fl_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.fl_pres_pbar.move(settings.FL_PRES_PBAR_X, settings.FL_PRES_PBAR_Y)
        self.fl_pres_pbar.setValue(15)
        self.fl_pres_pbar.setValue(125)
        self.fl_pres_pbar.show()

        self.fr_pres_pbar = QtWidgets.QProgressBar(self)
        self.fr_pres_pbar.setGeometry(50, 50, 20, 100)
        self.fr_pres_pbar.setOrientation(Qt.Vertical)
        self.fr_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.fr_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.fr_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.fr_pres_pbar.move(settings.FR_PRES_PBAR_X, settings.FR_PRES_PBAR_Y)
        self.fr_pres_pbar.show()

        self.rl_pres_pbar = QtWidgets.QProgressBar(self)
        self.rl_pres_pbar.setGeometry(50, 50, 20, 100)
        self.rl_pres_pbar.setOrientation(Qt.Vertical)
        self.rl_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.rl_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.rl_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.rl_pres_pbar.move(settings.RL_PRES_PBAR_X, settings.RL_PRES_PBAR_Y)
        self.rl_pres_pbar.show()

        self.rr_pres_pbar = QtWidgets.QProgressBar(self)
        self.rr_pres_pbar.setGeometry(50, 50, 20, 100)
        self.rr_pres_pbar.setOrientation(Qt.Vertical)
        self.rr_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.rr_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.rr_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.rr_pres_pbar.move(settings.RR_PRES_PBAR_X, settings.RR_PRES_PBAR_Y)
        self.rr_pres_pbar.show()

        self.speed_gauge = AnalogGaugeWidget(self)
        self.speed_gauge.set_MinValue(0)
        self.speed_gauge.set_MaxValue(220)
        self.speed_gauge.resize(200, 200)
        self.speed_gauge.move(420, 120)
        self.speed_gauge.show()

        self.simulation_progress_label = QtWidgets.QLabel(self)
        self.simulation_progress_label.setText('~')
        self.simulation_progress_label.move(10, 10)
        self.simulation_progress_label.show()

    def update_time_base(self, value):
        self.simulation_time_base = float(value.replace('x', ''))
        LOGGER.info('Changed simulation time base to {}'.format(self.simulation_time_base))

    def run_simulation_profile(self):
        """
        
        :return: 
        """

        if not self.simulation_profile:
            LOGGER.info('No simulation profile loaded!')
            return

        sampling_period = self.simulation_profile[SIGNAL_SAMPLING_PERIOD]
        fps, growth = __get_fps_growth__(sampling_period, self.simulation_time_base)

        self.simulation_period = 1 / fps
        self.simulation_index_growth = growth

        LOGGER.info('Simulation period: {}\nSimulation index growth: {}'
                    .format(self.simulation_period, self.simulation_index_growth))

        self.simulation_index = 0
        self.simulation_running = True

        self.__stop_fps_task__ = False
        self.start_sim_profile_button.setEnabled(False)

        sleep(.5)
        task_thread = threading.Thread(target=self.__fps_task__)

        task_thread.start()
        LOGGER.info('Started simulation!')
    
    def __update_simulation_velocity__(self):
        """
        
        :return: 
        """
        self.fl_vel_label.setText('{0:.2f}'.format(self.fl_vel[self.simulation_index]))
        self.fr_vel_label.setText('{0:.2f}'.format(self.fr_vel[self.simulation_index]))
        self.rl_vel_label.setText('{0:.2f}'.format(self.rl_vel[self.simulation_index]))
        self.rr_vel_label.setText('{0:.2f}'.format(self.rr_vel[self.simulation_index]))

        self.speed_gauge.update_value(self.abs_ref[self.simulation_index])
    
    def __update_simulation_pressure__(self):
        """
        
        :return: 
        """
        self.fl_pres_label.setText('{0:.2f}'.format(self.fl_pres[self.simulation_index]))
        self.fr_pres_label.setText('{0:.2f}'.format(self.fr_pres[self.simulation_index]))
        self.rl_pres_label.setText('{0:.2f}'.format(self.rl_pres[self.simulation_index]))
        self.rr_pres_label.setText('{0:.2f}'.format(self.rr_pres[self.simulation_index]))

        try:
            pass
            self.fr_pres_pbar.setValue(int(self.fr_pres[self.simulation_index]))
            # self.rl_pres_pbar.setValue(int(self.rl_pres[self.simulation_index]))
            # self.rr_pres_pbar.setValue(int(self.rr_pres[self.simulation_index]))
        except Exception as err:
            LOGGER.error(err)

    def __fps_task__(self):
        """

        :return:
        """
        self.__fps_task_started__ = True
        LOGGER.info('__fps_task__ started!')
        stop_sim_signal = False
        sim_progress = -1
        old_simulation_progress = -1
        while not self.__stop_fps_task__:
            sleep(self.simulation_period)
            if self.simulation_running:

                sim_progress = int((self.simulation_index * 100) / self.simulation_stamps)

                self.__update_simulation_velocity__()
                self.__update_simulation_pressure__()

                if sim_progress != old_simulation_progress:
                    self.simulation_progress_label.setText('{}%'.format(sim_progress))
                    old_simulation_progress = sim_progress

                if stop_sim_signal:
                    self.simulation_running = False
                    self.__stop_fps_task__ = True
                    self.start_sim_profile_button.setEnabled(True)
                    LOGGER.info('Stopped simulation!')

                self.simulation_index += self.simulation_index_growth
                
                if self.simulation_index >= self.simulation_stamps:
                    self.simulation_index = - 1
                    stop_sim_signal = True
                
        self.__fps_task_started__ = False
        LOGGER.info('__fps_task__ stopped!')

    def closeEvent(self, event):

        reply = QtWidgets.QMessageBox.question(self, 'Exit', "Are you sure?", QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.__stop_fps_task__ = True

            counter = 0
            period = 0.01
            while self.__fps_task_started__:
                sleep(period)
                counter += period
                if counter >= 3:
                    break
            event.accept()
        else:
            event.ignore()


def run_application():
    app = QApplication(sys.argv)
    win = CarSimETTI()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_application()
