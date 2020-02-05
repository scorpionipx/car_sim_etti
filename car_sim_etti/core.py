import json
import logging
import numpy
import os
import sys
import threading


from time import sleep, time as now

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal


from car_sim_etti import settings, APP_SLUG
from car_sim_etti.utils.gauge import AnalogGaugeWidget
from car_sim_etti.utils.data_viewer import DataViewer, Signal as PlotterSignal
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

    BRAKING_SYSTEM_OVERVIEW_IMG,

    sim_profile_valid,
    __get_fps_growth__,
)

LOGGER = logging.getLogger(APP_SLUG)


SIMULATION_THREAD_TIMEOUT = 300  # seconds, same as 5 minutes
RELEASED = False

CURRENT_DIR = os.path.dirname(__file__)
SIM_PROFILES_PATH = os.path.join(CURRENT_DIR, 'static', 'simulation_profiles', 'ABS')


class SimulationThread(QThread):
    """SimulationThread

    """
    counted = pyqtSignal(int)
    running = False
    stop_sim_signal = False

    def __init__(self, period=.01):
        super(SimulationThread, self).__init__()
        self.period = period

    def run(self):

        count = 0
        loop_index = 0
        LOGGER.info('Simulation thread started!')
        self.running = True
        start = now()
        while count < SIMULATION_THREAD_TIMEOUT:

            if self.stop_sim_signal:
                end = now()
                LOGGER.info('Simulation thread stopped! {}s'.format(end - start))
                self.running = False
                sleep(1)
                break

            count += self.period
            self.counted.emit(loop_index)
            loop_index += 1

            sleep(self.period)

        if not self.stop_sim_signal:
            end = now()
            LOGGER.info('Simulation thread stopped after timeout [{}] reached! {}s'
                        .format(SIMULATION_THREAD_TIMEOUT, end - start))


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
        self.load_and_start_sim_profile_button = None
        self.stop_sim_profile_button = None
        self.time_base_combo_box = None
        self.simulation_profile_label = None

        # sim values
        self.target_speed = 0

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
        self.braking_system_overview_label = None

        self.simulation_progress_label = None
        self.simulation_progress_pbar = None
        self.simulation_progress = -1
        self.simulation_progress_old = -1

        self.set_target_speed_slider = None
        self.target_speed_label = None
        self.set_road_friction_coefficient_slider = None
        self.road_friction_coefficient_label = None
        self.split_road_friction_coefficient_checkbox = None

        self.simulation_thread = None
        self.simulation_profile = None
        self.simulation_running = False
        self.simulation_index = 0
        self.simulation_index_growth = -1
        self.simulation_stamps = -1
        self.simulation_time_base = 1
        self.simulation_fps = -1
        self.simulation_period = -1
        self.stop_sim_signal = False

        self.__fps_task_started__ = False
        self.__stop_fps_task__ = False

        self.init_gui()
        self.data_viewer = DataViewer()
        self.data_viewer.show()

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

    def load_simulation_profile(self, specific_file=None, skip_until_index=0):
        """load_simulation_profile

            Load signals values from simulation profile file.
        :return: process result
        :rtype: bool
        """
        if specific_file is None:
            file = self.__get_file__()
            if not file:
                warning = 'Invalid simulation profile file! {}'.format(file)
                LOGGER.warning(warning)
                return False
        else:
            file = specific_file

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

        LOGGER.info('MAX SPEED: {}km/h'.format(max(self.abs_ref)))

        self.fl_vel = self.simulation_profile[SIGNAL_FL_VEL]
        self.fr_vel = self.simulation_profile[SIGNAL_FR_VEL]
        self.rl_vel = self.simulation_profile[SIGNAL_RL_VEL]
        self.rr_vel = self.simulation_profile[SIGNAL_RR_VEL]

        self.fl_pres = self.simulation_profile[SIGNAL_FL_PRES]
        self.fr_pres = self.simulation_profile[SIGNAL_FR_PRES]
        self.rl_pres = self.simulation_profile[SIGNAL_RL_PRES]
        self.rr_pres = self.simulation_profile[SIGNAL_RR_PRES]

        self.abs_ref = self.abs_ref[skip_until_index:]

        self.fl_vel = self.fl_vel[skip_until_index:]
        self.fr_vel = self.fr_vel[skip_until_index:]
        self.rl_vel = self.rl_vel[skip_until_index:]
        self.rr_vel = self.rr_vel[skip_until_index:]

        self.fl_pres = self.fl_pres[skip_until_index:]
        self.fr_pres = self.fr_pres[skip_until_index:]
        self.rl_pres = self.rl_pres[skip_until_index:]
        self.rr_pres = self.rr_pres[skip_until_index:]

        for index, abs_ref in enumerate(self.fl_vel):
            if abs_ref > self.target_speed + 1 and self.abs_ref[index] > self.target_speed + 1:
                raw_time = int(str(now()).split('.')[1])
                offset = (raw_time % 20) / 10
                sleep(0.001)
                self.fl_vel[index] = float('{0:.2f}'.format(self.target_speed + 0.69 + offset))

        for index, abs_ref in enumerate(self.fr_vel):
            if abs_ref > self.target_speed + 1 and self.abs_ref[index] > self.target_speed + 1:
                raw_time = int(str(now()).split('.')[1])
                offset = (raw_time % 20) / 10
                sleep(0.001)
                self.fr_vel[index] = float('{0:.2f}'.format(self.target_speed + 0.69 + offset))

        for index, abs_ref in enumerate(self.rl_vel):
            if abs_ref > self.target_speed + 1 and self.abs_ref[index] > self.target_speed + 1:
                raw_time = int(str(now()).split('.')[1])
                offset = (raw_time % 20) / 10
                sleep(0.001)
                self.rl_vel[index] = float('{0:.2f}'.format(self.target_speed + 0.69 + offset))

        for index, abs_ref in enumerate(self.rr_vel):
            if abs_ref > self.target_speed + 1 and self.abs_ref[index] > self.target_speed + 1:
                raw_time = int(str(now()).split('.')[1])
                offset = (raw_time % 20) / 10
                sleep(0.001)
                self.rr_vel[index] = float('{0:.2f}'.format(self.target_speed + 0.69 + offset))

        for index, abs_ref in enumerate(self.abs_ref):
            if abs_ref > self.target_speed + 1:
                raw_time = int(str(now()).split('.')[1])
                offset = (raw_time % 20) / 10
                sleep(0.001)
                self.abs_ref[index] = self.target_speed + offset

        self.simulation_stamps = len(self.fl_vel)

        LOGGER.info('Simulation profile successfully loaded!')

        velocity_plot_signals = []

        fl_vel_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.fl_vel):
            fl_vel_p_signal_data[index] = val

        fl_vel_p_signal = PlotterSignal(
            label='FL_SPEED',
            color='#ff8000',
            data=fl_vel_p_signal_data
        )
        velocity_plot_signals.append(fl_vel_p_signal)

        fr_vel_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.fr_vel):
            fr_vel_p_signal_data[index] = val

        fr_vel_p_signal = PlotterSignal(
            label='FR_SPEED',
            color='#848000',
            data=fr_vel_p_signal_data
        )
        velocity_plot_signals.append(fr_vel_p_signal)

        rl_vel_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.rl_vel):
            rl_vel_p_signal_data[index] = val

        rl_vel_p_signal = PlotterSignal(
            label='RL_SPEED',
            color='#bb4f66',
            data=rl_vel_p_signal_data
        )
        velocity_plot_signals.append(rl_vel_p_signal)

        rr_vel_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.rr_vel):
            rr_vel_p_signal_data[index] = val

        rr_vel_p_signal = PlotterSignal(
            label='RR_SPEED',
            color='#09dd66',
            data=rr_vel_p_signal_data
        )
        velocity_plot_signals.append(rr_vel_p_signal)
        
        pressure_plot_signals = []

        fl_pres_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.fl_pres):
            fl_pres_p_signal_data[index] = val

        fl_pres_p_signal = PlotterSignal(
            label='FL_PRES',
            color='#ff8000',
            data=fl_pres_p_signal_data
        )
        pressure_plot_signals.append(fl_pres_p_signal)

        fr_pres_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.fr_pres):
            fr_pres_p_signal_data[index] = val

        fr_pres_p_signal = PlotterSignal(
            label='FR_PRES',
            color='#848000',
            data=fr_pres_p_signal_data
        )
        pressure_plot_signals.append(fr_pres_p_signal)

        rl_pres_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.rl_pres):
            rl_pres_p_signal_data[index] = val

        rl_pres_p_signal = PlotterSignal(
            label='RL_PRES',
            color='#bb4f66',
            data=rl_pres_p_signal_data
        )
        pressure_plot_signals.append(rl_pres_p_signal)

        rr_pres_p_signal_data = numpy.zeros(self.simulation_stamps)
        for index, val in enumerate(self.rr_pres):
            rr_pres_p_signal_data[index] = val

        rr_pres_p_signal = PlotterSignal(
            label='RR_PRES',
            color='#09dd66',
            data=rr_pres_p_signal_data
        )
        pressure_plot_signals.append(rr_pres_p_signal)

        try:
            self.data_viewer.init_speed_plotter(velocity_plot_signals)
            self.data_viewer.init_pressure_plotter(pressure_plot_signals)
        except Exception as exception:
            LOGGER.error(exception)

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
        self.setFixedSize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.setWindowTitle(settings.WINDOW_TITLE)
        self.setWindowIcon(QIcon(settings.WINDOWS_ICON_PATH))
        self.setStyleSheet("QMainWindow {background: 'white';}")

        self.load_sim_profile_button = QtWidgets.QPushButton(self)
        self.load_sim_profile_button.setText('Load sim profile')
        # noinspection PyTypeChecker
        self.load_sim_profile_button.clicked.connect(self.load_simulation_profile)
        self.load_sim_profile_button.move(400, 60)
        self.load_sim_profile_button.show()
        if RELEASED:
            self.load_sim_profile_button.hide()

        x = 20
        y = 15
        simulation_profile_label = QtWidgets.QLabel(self)
        simulation_profile_label.setText('ABS SIMULATION PROFILE')
        simulation_profile_label.resize(simulation_profile_label.sizeHint())
        simulation_profile_label.move(x, y)
        simulation_profile_label.show()

        self.set_target_speed_slider = QtWidgets.QSlider(self)
        self.set_target_speed_slider.setOrientation(Qt.Horizontal)
        self.set_target_speed_slider.setMinimum(50)
        self.set_target_speed_slider.setMaximum(130)
        self.set_target_speed_slider.setValue(50)
        self.set_target_speed_slider.valueChanged.connect(self.__update_target_speed__)
        self.set_target_speed_slider.move(x, y + 30)
        self.set_target_speed_slider.show()

        static_target_speed_label = QtWidgets.QLabel(self)
        static_target_speed_label.setText('target speed:')
        static_target_speed_label.resize(static_target_speed_label.sizeHint())
        static_target_speed_label.move(x, y + 15)
        static_target_speed_label.show()

        self.target_speed_label = QtWidgets.QLabel(self)
        self.target_speed_label.setText('50km/h')
        self.target_speed_label.resize(static_target_speed_label.size())
        self.target_speed_label.move(x + static_target_speed_label.width() + 2, static_target_speed_label.y())
        self.target_speed_label.show()

        x = 20
        y = 65
        self.set_road_friction_coefficient_slider = QtWidgets.QSlider(self)
        self.set_road_friction_coefficient_slider.setOrientation(Qt.Horizontal)
        self.set_road_friction_coefficient_slider.setMinimum(3)
        self.set_road_friction_coefficient_slider.setMaximum(9)
        self.set_road_friction_coefficient_slider.valueChanged.connect(self.__update_road_friction_coefficient__)
        self.set_road_friction_coefficient_slider.move(x, y + 30)
        self.set_road_friction_coefficient_slider.show()
        
        static_road_friction_coefficient_label = QtWidgets.QLabel(self)
        static_road_friction_coefficient_label.setText('road friction coefficient:')
        static_road_friction_coefficient_label.resize(static_road_friction_coefficient_label.sizeHint())
        static_road_friction_coefficient_label.move(x, y + 15)
        static_road_friction_coefficient_label.show()

        self.road_friction_coefficient_label = QtWidgets.QLabel(self)
        self.road_friction_coefficient_label.setText('0.3')
        self.road_friction_coefficient_label.resize(static_road_friction_coefficient_label.size())
        self.road_friction_coefficient_label.move(x + static_road_friction_coefficient_label.width() + 2,
                                                  static_road_friction_coefficient_label.y())
        self.road_friction_coefficient_label.show()

        self.split_road_friction_coefficient_checkbox = QtWidgets.QCheckBox(self)
        self.split_road_friction_coefficient_checkbox.setChecked(False)
        self.split_road_friction_coefficient_checkbox.resize(self.split_road_friction_coefficient_checkbox.sizeHint())
        self.split_road_friction_coefficient_checkbox.move(x + self.set_road_friction_coefficient_slider.width() + 5,
                                                           self.set_road_friction_coefficient_slider.y() + 5)
        self.split_road_friction_coefficient_checkbox.clicked.connect(self.__update_road_friction_coefficient_split__)
        self.split_road_friction_coefficient_checkbox.show()

        split_road_friction_coefficient_label = QtWidgets.QLabel(self)
        split_road_friction_coefficient_label.setText('split')
        split_road_friction_coefficient_label.resize(split_road_friction_coefficient_label.sizeHint())
        split_road_friction_coefficient_label.move(self.split_road_friction_coefficient_checkbox.x() +
                                                   self.split_road_friction_coefficient_checkbox.width() + 2,
                                                   self.split_road_friction_coefficient_checkbox.y())
        split_road_friction_coefficient_label.show()

        x = 20
        y = 130

        time_base_label = QtWidgets.QLabel(self)
        time_base_label.setText('time base:')
        time_base_label.resize(time_base_label.sizeHint())
        time_base_label.move(x, y)
        time_base_label.show()

        self.time_base_combo_box = QtWidgets.QComboBox(self)
        self.time_base_combo_box.addItem('8x')
        self.time_base_combo_box.addItem('4x')
        self.time_base_combo_box.addItem('2x')
        self.time_base_combo_box.addItem('1x')
        self.time_base_combo_box.addItem('0.5x')
        self.time_base_combo_box.addItem('0.25x')
        self.time_base_combo_box.addItem('0.1x')
        self.time_base_combo_box.setCurrentIndex(3)
        self.time_base_combo_box.resize(50, 20)
        self.time_base_combo_box.move(x + time_base_label.width() + 2, y - 3)
        self.time_base_combo_box.show()
        self.time_base_combo_box.currentTextChanged.connect(self.update_time_base)

        self.simulation_profile_label = QtWidgets.QLabel(self)
        self.simulation_profile_label.setText('none'*20)
        self.simulation_profile_label.resize(self.simulation_profile_label.sizeHint())
        self.simulation_profile_label.setText('none')
        self.simulation_profile_label.move(x, y + 50)
        self.simulation_profile_label.show()
        if RELEASED:
            self.simulation_profile_label.hide()

        self.start_sim_profile_button = QtWidgets.QPushButton(self)
        self.start_sim_profile_button.setText('Start sim profile')
        # noinspection PyTypeChecker
        self.start_sim_profile_button.clicked.connect(self.start_simulation)
        self.start_sim_profile_button.move(400, 10)
        self.start_sim_profile_button.show()
        if RELEASED:
            self.start_sim_profile_button.hide()

        self.load_and_start_sim_profile_button = QtWidgets.QPushButton(self)
        self.load_and_start_sim_profile_button.setText('Start sim profile')
        # noinspection PyTypeChecker
        self.load_and_start_sim_profile_button.clicked.connect(self.load_and_start_simulation_profile)
        self.load_and_start_sim_profile_button.move(180, 10)
        self.load_and_start_sim_profile_button.resize(100, 60)
        self.load_and_start_sim_profile_button.show()

        self.stop_sim_profile_button = QtWidgets.QPushButton(self)
        self.stop_sim_profile_button.setText('Stop sim')
        # noinspection PyTypeChecker
        self.stop_sim_profile_button.clicked.connect(self.stop_simulation)
        self.stop_sim_profile_button.move(180, 20 + self.load_and_start_sim_profile_button.height())
        self.stop_sim_profile_button.resize(100, 60)
        self.stop_sim_profile_button.setEnabled(False)
        self.stop_sim_profile_button.show()

        braking_system_overview_pixmap = QPixmap(BRAKING_SYSTEM_OVERVIEW_IMG)
        self.braking_system_overview_label = QtWidgets.QLabel(self)
        self.braking_system_overview_label.setPixmap(braking_system_overview_pixmap)
        self.braking_system_overview_label.resize(
            braking_system_overview_pixmap.width(), braking_system_overview_pixmap.height()
        )
        self.braking_system_overview_label.move(176, 250)
        self.braking_system_overview_label.show()

        self.fl_vel_label = QtWidgets.QLabel(self)
        self.fl_vel_label.setText(NOT_AVAILABLE)
        self.fl_vel_label.move(settings.FL_VEL_LABEL_X, settings.FL_VEL_LABEL_Y)
        self.fl_vel_label.show()

        fl_vel_label_secondary = QtWidgets.QLabel(self)
        fl_vel_label_secondary.setText('[km/h]')
        fl_vel_label_secondary.move(settings.FL_VEL_LABEL_X, settings.FL_VEL_LABEL_Y + 15)
        fl_vel_label_secondary.show()

        self.fr_vel_label = QtWidgets.QLabel(self)
        self.fr_vel_label.setText(NOT_AVAILABLE)
        self.fr_vel_label.move(settings.FR_VEL_LABEL_X, settings.FR_VEL_LABEL_Y)
        self.fr_vel_label.show()

        fr_vel_label_secondary = QtWidgets.QLabel(self)
        fr_vel_label_secondary.setText('[km/h]')
        fr_vel_label_secondary.move(settings.FR_VEL_LABEL_X, settings.FR_VEL_LABEL_Y + 15)
        fr_vel_label_secondary.show()

        self.rl_vel_label = QtWidgets.QLabel(self)
        self.rl_vel_label.setText(NOT_AVAILABLE)
        self.rl_vel_label.move(settings.RL_VEL_LABEL_X, settings.RL_VEL_LABEL_Y)
        self.rl_vel_label.show()

        rl_vel_label_secondary = QtWidgets.QLabel(self)
        rl_vel_label_secondary.setText('[km/h]')
        rl_vel_label_secondary.move(settings.RL_VEL_LABEL_X, settings.RL_VEL_LABEL_Y + 15)
        rl_vel_label_secondary.show()

        self.rr_vel_label = QtWidgets.QLabel(self)
        self.rr_vel_label.setText(NOT_AVAILABLE)
        self.rr_vel_label.move(settings.RR_VEL_LABEL_X, settings.RR_VEL_LABEL_Y)
        self.rr_vel_label.show()

        rr_vel_label_secondary = QtWidgets.QLabel(self)
        rr_vel_label_secondary.setText('[km/h]')
        rr_vel_label_secondary.move(settings.RR_VEL_LABEL_X, settings.RR_VEL_LABEL_Y + 15)
        rr_vel_label_secondary.show()

        self.fl_pres_label = QtWidgets.QLabel(self)
        self.fl_pres_label.setText(NOT_AVAILABLE)
        self.fl_pres_label.move(settings.FL_PRES_LABEL_X, settings.FL_PRES_LABEL_Y)
        self.fl_pres_label.show()

        fl_pres_label_secondary = QtWidgets.QLabel(self)
        fl_pres_label_secondary.setText('[bars]')
        fl_pres_label_secondary.move(settings.FL_PRES_LABEL_X, settings.FL_PRES_LABEL_Y + 15)
        fl_pres_label_secondary.show()

        self.fr_pres_label = QtWidgets.QLabel(self)
        self.fr_pres_label.setText(NOT_AVAILABLE)
        self.fr_pres_label.move(settings.FR_PRES_LABEL_X, settings.FR_PRES_LABEL_Y)
        self.fr_pres_label.show()

        fr_pres_label_secondary = QtWidgets.QLabel(self)
        fr_pres_label_secondary.setText('[bars]')
        fr_pres_label_secondary.move(settings.FR_PRES_LABEL_X, settings.FR_PRES_LABEL_Y + 15)
        fr_pres_label_secondary.show()

        self.rl_pres_label = QtWidgets.QLabel(self)
        self.rl_pres_label.setText(NOT_AVAILABLE)
        self.rl_pres_label.move(settings.RL_PRES_LABEL_X, settings.RL_PRES_LABEL_Y)
        self.rl_pres_label.show()

        rl_pres_label_secondary = QtWidgets.QLabel(self)
        rl_pres_label_secondary.setText('[bars]')
        rl_pres_label_secondary.move(settings.RL_PRES_LABEL_X, settings.RL_PRES_LABEL_Y + 15)
        rl_pres_label_secondary.show()

        self.rr_pres_label = QtWidgets.QLabel(self)
        self.rr_pres_label.setText(NOT_AVAILABLE)
        self.rr_pres_label.move(settings.RR_PRES_LABEL_X, settings.RR_PRES_LABEL_Y)
        self.rr_pres_label.show()

        rr_pres_label_secondary = QtWidgets.QLabel(self)
        rr_pres_label_secondary.setText('[bars]')
        rr_pres_label_secondary.move(settings.RR_PRES_LABEL_X, settings.RR_PRES_LABEL_Y + 15)
        rr_pres_label_secondary.show()

        self.fl_pres_pbar = QtWidgets.QProgressBar(self)
        self.fl_pres_pbar.setGeometry(50, 50, 20, 100)
        self.fl_pres_pbar.setOrientation(Qt.Vertical)
        self.fl_pres_pbar.setMinimum(settings.PRES_PBAR_MIN)
        self.fl_pres_pbar.setMaximum(settings.PRES_PBAR_MAX)
        self.fl_pres_pbar.setValue(settings.PRES_PBAR_MIN)
        self.fl_pres_pbar.move(settings.FL_PRES_PBAR_X, settings.FL_PRES_PBAR_Y)
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
        self.speed_gauge.set_MaxValue(200)
        self.speed_gauge.resize(200, 200)
        self.speed_gauge.move(540, 15)
        self.speed_gauge.show()

        simulation_progress_label_secondary = QtWidgets.QLabel(self)
        simulation_progress_label_secondary.setText('Simulation progress')
        simulation_progress_label_secondary.move(20, 545)
        simulation_progress_label_secondary.show()

        self.simulation_progress_pbar = QtWidgets.QProgressBar(self)
        self.simulation_progress_pbar.setGeometry(350, 10, 780, 10)
        self.simulation_progress_pbar.setOrientation(Qt.Horizontal)
        self.simulation_progress_pbar.setMinimum(0)
        self.simulation_progress_pbar.setMaximum(100)
        self.simulation_progress_pbar.setValue(0)
        self.simulation_progress_pbar.move(20, 575)
        self.simulation_progress_pbar.show()

    def load_and_start_simulation_profile(self):
        """

        :return:
        """
        LOGGER.info('Preparing profile...')
        target_speed = int(self.set_target_speed_slider.value())
        road_friction_coefficient = self.road_friction_coefficient_label.text()

        if target_speed % 10 == 0:
            formatted_target_speed = target_speed
        else:
            formatted_target_speed = (target_speed // 10 + 1) * 10

        if '/' in road_friction_coefficient:
            formatted_road_friction_coefficient = '38'
        else:
            formatted_road_friction_coefficient = road_friction_coefficient.replace('.', '')

        if formatted_road_friction_coefficient == '07':  # WARNING
            formatted_road_friction_coefficient = '06'

        if formatted_road_friction_coefficient == '08':  # WARNING
            formatted_road_friction_coefficient = '09'

        target_sim_profile = '{}_{}.json'.format(formatted_target_speed, formatted_road_friction_coefficient)

        profile = 'SPEED: {} -> {}\n'.format(target_speed, formatted_target_speed)
        profile += 'RFC: {} -> {}\n'.format(road_friction_coefficient, formatted_road_friction_coefficient)
        profile += 'SP: {}\n'.format(target_sim_profile)

        target_sim_profile_path = os.path.join(SIM_PROFILES_PATH, target_sim_profile)
        if not RELEASED:
            self.simulation_profile_label.setText('{}'.format(target_sim_profile_path))

        raw_time = int(str(now()).split('.')[1])

        skip_until_index = raw_time % 650

        self.target_speed = target_speed
        if target_speed % 10 == 0:
            sleep(4)
        self.load_simulation_profile(specific_file=target_sim_profile_path, skip_until_index=skip_until_index)

        profile += 'SKIP: {}\n'.format(skip_until_index)

        LOGGER.info(profile)
        self.start_simulation()

    def __update_target_speed__(self):
        """

        :return:
        """
        self.target_speed_label.setText('{}km/h'.format(self.set_target_speed_slider.value()))
        sleep(0.01)

    def __update_road_friction_coefficient__(self):
        """

        :return:
        """
        self.road_friction_coefficient_label.setText('{}'
                                                     .format(self.set_road_friction_coefficient_slider.value() / 10))

    def __update_road_friction_coefficient_split__(self):
        """

        :return:
        """
        if self.split_road_friction_coefficient_checkbox.isChecked():
            self.set_road_friction_coefficient_slider.setEnabled(False)
            self.road_friction_coefficient_label.setText('0.3/0.8')
        else:
            self.set_road_friction_coefficient_slider.setEnabled(True)
            self.road_friction_coefficient_label.\
                setText('{}'.format(self.set_road_friction_coefficient_slider.value() / 10))

    def update_time_base(self, value):
        self.simulation_time_base = float(value.replace('x', ''))
        LOGGER.info('Changed simulation time base to {}'.format(self.simulation_time_base))

    def on_thread_counter(self, index):
        self.simulation_index += self.simulation_index_growth

        self.simulation_progress = int((self.simulation_index * 100) / self.simulation_stamps)

        if self.simulation_progress != self.simulation_progress_old:
            # self.simulation_progress_label.setText('{}%'.format(self.simulation_progress))
            self.simulation_progress_old = self.simulation_progress
            self.simulation_progress_pbar.setValue(self.simulation_progress)

        if self.simulation_index > self.simulation_stamps - 1:
            self.simulation_index = self.simulation_stamps - 1
            self.simulation_thread.stop_sim_signal = True
            self.start_sim_profile_button.setEnabled(True)
            self.load_and_start_sim_profile_button.setEnabled(True)
            self.time_base_combo_box.setEnabled(True)
            self.load_sim_profile_button.setEnabled(True)
            self.stop_sim_profile_button.setEnabled(False)
            self.set_target_speed_slider.setEnabled(True)
            self.split_road_friction_coefficient_checkbox.setEnabled(True)
            if not self.split_road_friction_coefficient_checkbox.isChecked():
                self.set_road_friction_coefficient_slider.setEnabled(True)
            LOGGER.info('Emitted simulation stop signal!')
        else:
            pass
            self.__update_simulation_velocity__()
            self.__update_simulation_pressure__()
            self.__update_simulation_pressure_graphics__()
            self.data_viewer.speed_plotter.display_data(self.simulation_index)
            self.data_viewer.pressure_plotter.display_data(self.simulation_index)

    def start_simulation(self):
        if not self.simulation_profile:
            LOGGER.info('No simulation profile loaded!')
            return

        sampling_period = self.simulation_profile[SIGNAL_SAMPLING_PERIOD]
        fps, growth = __get_fps_growth__(sampling_period, self.simulation_time_base)

        self.simulation_period = 1 / fps
        self.simulation_index_growth = growth

        LOGGER.info('Simulation period: {}\nSimulation index growth: {}\nSimulation stamps: {}\n'
                    .format(self.simulation_period, self.simulation_index_growth, self.simulation_stamps))

        self.simulation_index = 0
        self.simulation_running = True
        self.simulation_progress = 0
        self.simulation_progress_old = -1

        self.simulation_thread = SimulationThread(period=self.simulation_period)
        self.simulation_thread.counted.connect(self.on_thread_counter)
        self.start_sim_profile_button.setEnabled(False)
        self.time_base_combo_box.setEnabled(False)
        self.load_sim_profile_button.setEnabled(False)
        self.stop_sim_profile_button.setEnabled(True)
        self.load_and_start_sim_profile_button.setEnabled(False)
        self.set_target_speed_slider.setEnabled(False)
        self.split_road_friction_coefficient_checkbox.setEnabled(False)
        self.set_road_friction_coefficient_slider.setEnabled(False)
        self.simulation_thread.start()

    def stop_sim(self):
        """

        :return:
        """
        self.stop_sim_signal = True
        self.fl_pres_pbar.setValue(self.fl_pres_pbar.value() + 1)

    def stop_simulation(self):
        """

        :return:
        """
        self.simulation_thread.stop_sim_signal = True
        self.start_sim_profile_button.setEnabled(True)
        self.load_and_start_sim_profile_button.setEnabled(True)
        self.time_base_combo_box.setEnabled(True)
        self.load_sim_profile_button.setEnabled(True)
        self.stop_sim_profile_button.setEnabled(False)
        self.split_road_friction_coefficient_checkbox.setEnabled(True)
        self.set_target_speed_slider.setEnabled(True)
        if not self.split_road_friction_coefficient_checkbox.isChecked():
            self.set_road_friction_coefficient_slider.setEnabled(True)
        sleep(.1)
        LOGGER.info('Forced stopped simulation!')

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
        self.set_target_speed_slider.setEnabled(False)
        self.split_road_friction_coefficient_checkbox.setEnabled(False)
        self.set_road_friction_coefficient_slider.setEnabled(False)

        sleep(.5)
        task_thread = threading.Thread(target=self.__fps_task__)

        task_thread.start()
        LOGGER.info('Started simulation!')
    
    def __update_simulation_velocity__(self):
        """
        
        :return: 
        """
        self.fl_vel_label.setText('{}'.format(self.fl_vel[self.simulation_index]))
        self.fr_vel_label.setText('{}'.format(self.fr_vel[self.simulation_index]))
        self.rl_vel_label.setText('{}'.format(self.rl_vel[self.simulation_index]))
        self.rr_vel_label.setText('{}'.format(self.rr_vel[self.simulation_index]))

        self.speed_gauge.update_value(self.abs_ref[self.simulation_index])
    
    def __update_simulation_pressure__(self):
        """
        
        :return: 
        """
        self.fl_pres_label.setText('{}'.format(self.fl_pres[self.simulation_index]))
        self.fr_pres_label.setText('{}'.format(self.fr_pres[self.simulation_index]))
        self.rl_pres_label.setText('{}'.format(self.rl_pres[self.simulation_index]))
        self.rr_pres_label.setText('{}'.format(self.rr_pres[self.simulation_index]))

    def __update_simulation_pressure_graphics__(self):
        """

        :return:
        """
        self.fl_pres_pbar.setValue(int(self.fl_pres[self.simulation_index]))
        self.fr_pres_pbar.setValue(int(self.fr_pres[self.simulation_index]))
        self.rl_pres_pbar.setValue(int(self.rl_pres[self.simulation_index]))
        self.rr_pres_pbar.setValue(int(self.rr_pres[self.simulation_index]))

    def __fps_task__(self):
        """

        :return:
        """
        self.__fps_task_started__ = True
        LOGGER.info('__fps_task__ started!')
        self.stop_sim_signal = False
        old_simulation_progress = -1
        while not self.__stop_fps_task__:
            sleep(self.simulation_period)
            if self.simulation_running:

                sim_progress = int((self.simulation_index * 100) / self.simulation_stamps)

                self.__update_simulation_velocity__()
                self.__update_simulation_pressure__()
                if self.simulation_index > 10:
                    if self.simulation_index % 55 == 0:
                        self.__update_simulation_pressure_graphics__()

                if sim_progress != old_simulation_progress:
                    self.simulation_progress_label.setText('{}%'.format(sim_progress))
                    old_simulation_progress = sim_progress

                if self.stop_sim_signal:
                    self.simulation_running = False
                    self.__stop_fps_task__ = True
                    self.start_sim_profile_button.setEnabled(True)
                    self.load_and_start_sim_profile_button.setEnabled(True)
                    self.split_road_friction_coefficient_checkbox.setEnabled(True)
                    if not self.split_road_friction_coefficient_checkbox.isChecked():
                        self.set_road_friction_coefficient_slider.setEnabled(True)
                    LOGGER.info('Stopped simulation!')

                self.simulation_index += self.simulation_index_growth
                
                if self.simulation_index >= self.simulation_stamps:
                    self.simulation_index = - 1
                    self.stop_sim_signal = True
                
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
            self.data_viewer.__prepare_for_closing__()
            self.data_viewer.close()
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
