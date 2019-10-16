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
from car_sim_etti.utils.generic import (
    NOT_AVAILABLE,

    SIGNAL_FL_VEL,
    SIGNAL_FR_VEL,
    SIGNAL_RL_VEL,
    SIGNAL_RR_VEL,
    SIGNAL_FL_PRES,
    SIGNAL_FR_PRES,
    SIGNAL_RL_PRES,
    SIGNAL_RR_PRES,

    sim_profile_valid,
)


LOGGER = logging.getLogger(APP_SLUG)


class CarSimETTI(QMainWindow):
    """

    """
    def __init__(self):
        super(CarSimETTI, self).__init__()

        # simulation signals
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
        
        self.simulation_running = False
        self.simulation_index = 0
        self.simulation_stamps = -1

        self.__fps_task_started__ = False
        self.__stop_fps_task__ = False

        self.init_gui()

    def __reset_simulation_signals__(self):
        """__reset_simulation_signals__
        
            Remove values from simulation signals.
        :return: None
        """
        del self.fl_vel
        del self.fr_vel
        del self.rl_vel
        del self.rr_vel

        del self.fl_pres
        del self.fr_pres
        del self.rl_pres
        del self.rr_pres

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

        self.__reset_simulation_signals__()

        self.fl_vel = sim_profile[SIGNAL_FL_VEL]
        self.fr_vel = sim_profile[SIGNAL_FR_VEL]
        self.rl_vel = sim_profile[SIGNAL_RL_VEL]
        self.rr_vel = sim_profile[SIGNAL_RR_VEL]

        self.fl_pres = sim_profile[SIGNAL_FL_PRES]
        self.fr_pres = sim_profile[SIGNAL_FR_PRES]
        self.rl_pres = sim_profile[SIGNAL_RL_PRES]
        self.rr_pres = sim_profile[SIGNAL_RR_PRES]
        
        self.simulation_stamps = len(self.fl_vel)

        LOGGER.info('Simulation profile successfully loaded!')

        task_thread = threading.Thread(target=self.__fps_task__)
        task_thread.start()

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
        self.fl_pres_pbar.setOrientation(Qt.Vertical)
        self.fl_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.fl_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.fl_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.fl_pres_pbar.move(settings.FL_PRES_PBAR_X, settings.FL_PRES_PBAR_Y)
        self.fl_pres_pbar.show()

        self.fr_pres_pbar = QtWidgets.QProgressBar(self)
        self.fr_pres_pbar.setOrientation(Qt.Vertical)
        self.fr_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.fr_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.fr_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.fr_pres_pbar.move(settings.FR_PRES_PBAR_X, settings.FR_PRES_PBAR_Y)
        self.fr_pres_pbar.show()

        self.rl_pres_pbar = QtWidgets.QProgressBar(self)
        self.rl_pres_pbar.setOrientation(Qt.Vertical)
        self.rl_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.rl_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.rl_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.rl_pres_pbar.move(settings.RL_PRES_PBAR_X, settings.RL_PRES_PBAR_Y)
        self.rl_pres_pbar.show()

        self.rr_pres_pbar = QtWidgets.QProgressBar(self)
        self.rr_pres_pbar.setOrientation(Qt.Vertical)
        self.rr_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.rr_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.rr_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.rr_pres_pbar.move(settings.RR_PRES_PBAR_X, settings.RR_PRES_PBAR_Y)
        self.rr_pres_pbar.show()

    def run_simulation_profile(self):
        """
        
        :return: 
        """
        self.simulation_index = 0
        self.simulation_running = True

        LOGGER.info('Started simulation!')
    
    def __update_simulation_velocity__(self):
        """
        
        :return: 
        """
        self.fl_vel_label.setText('{}'.format(self.fl_vel[self.simulation_index]))
        self.fr_vel_label.setText('{}'.format(self.fr_vel[self.simulation_index]))
        self.rl_vel_label.setText('{}'.format(self.rl_vel[self.simulation_index]))
        self.rr_vel_label.setText('{}'.format(self.rr_vel[self.simulation_index]))
    
    def __update_simulation_pressure__(self):
        """
        
        :return: 
        """
        self.fl_pres_label.setText('{}'.format(self.fl_pres[self.simulation_index]))
        self.fr_pres_label.setText('{}'.format(self.fr_pres[self.simulation_index]))
        self.rl_pres_label.setText('{}'.format(self.rl_pres[self.simulation_index]))
        self.rr_pres_label.setText('{}'.format(self.rr_pres[self.simulation_index]))

        # try:
        #     self.fl_pres_pbar.setValue(int(self.fl_pres[self.simulation_index]))
        #     self.fr_pres_pbar.setValue(int(self.fr_pres[self.simulation_index]))
        #     self.rl_pres_pbar.setValue(int(self.rl_pres[self.simulation_index]))
        #     self.rr_pres_pbar.setValue(int(self.rr_pres[self.simulation_index]))
        # except Exception as err:
        #     LOGGER.error(err)

    def __fps_task__(self):
        """

        :return:
        """
        self.__fps_task_started__ = True
        LOGGER.info('__fps_task__ started!')
        while not self.__stop_fps_task__:
            sleep(1 / settings.FPS)
            if self.simulation_running:
                self.__update_simulation_velocity__()
                self.__update_simulation_pressure__()
                self.simulation_index += 1
                
                if self.simulation_index >= self.simulation_stamps:
                    self.simulation_running = False
                    LOGGER.info('Stopped simulation!')
                
        self.__fps_task_started__ = False
        LOGGER.info('__fps_task__ stopped!')

    def closeEvent(self, event):

        reply = QtWidgets.QMessageBox.question(self, 'Exit', "Are you sure?", QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.__stop_fps_task__ = True
            if self.__fps_task_started__:
                sleep(2 * (1 / settings.FPS))

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
