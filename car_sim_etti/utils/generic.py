import logging
import os.path as py_path


from car_sim_etti import APP_SLUG


LOGGER = logging.getLogger(APP_SLUG)


CURRENT_DIR = py_path.dirname(__file__)
STATIC_DIR = py_path.join(py_path.dirname(CURRENT_DIR), 'static')
IMAGES_DIR = py_path.join(STATIC_DIR, 'images')

NOT_AVAILABLE = 'N/A'

SIGNAL_ABS_REF = 'abs_ref'

SIGNAL_FL_VEL = 'fl_vel'
SIGNAL_FR_VEL = 'fr_vel'
SIGNAL_RL_VEL = 'rl_vel'
SIGNAL_RR_VEL = 'rr_vel'

SIGNAL_FL_PRES = 'fl_pres'
SIGNAL_FR_PRES = 'fr_pres'
SIGNAL_RL_PRES = 'rl_pres'
SIGNAL_RR_PRES = 'rr_pres'

SIGNAL_SAMPLING_PERIOD = 'sampling_period'

ALLOWED_SAMPLING_PERIODS = (0.001, 0.01, 0.1, 1, 2)
FPS = {0.001: 24, 0.001: 24, 0.001: 24, 0.001: 24, 0.001: 24, 0.001: 24}

BRAKING_SYSTEM_OVERVIEW_IMG = py_path.join(IMAGES_DIR, 'braking_system_overview.png')


def sim_profile_valid(profile):
    """sim_profile_valid

        Check if specified simulation profile is valid.
    :param profile: simulation profile
    :type profile: dict
    :return: validation result
    :rtype: bool
    """
    validation = True

    sampling_period = profile.get(SIGNAL_SAMPLING_PERIOD, None)
    if sampling_period is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(SIGNAL_SAMPLING_PERIOD)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(sampling_period, int) and not isinstance(sampling_period, float):
            error = 'Signal <{}> type int or float expected! Got {} instead!'\
                .format(SIGNAL_SAMPLING_PERIOD, type(sampling_period))
            LOGGER.error(error)
            validation = False
        else:
            if sampling_period not in ALLOWED_SAMPLING_PERIODS:
                error = 'Signal <{}> value [{}] not allowed! Supported values are: {}!'\
                    .format(SIGNAL_SAMPLING_PERIOD, ALLOWED_SAMPLING_PERIODS, sampling_period)
                LOGGER.error(error)
                validation = False

    signal_name = SIGNAL_ABS_REF
    abs_ref = profile.get(signal_name, None)
    signal = abs_ref
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_FL_VEL
    fl_vel = profile.get(signal_name, None)
    signal = fl_vel
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_FR_VEL
    fr_vel = profile.get(signal_name, None)
    signal = fr_vel
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_RL_VEL
    rl_vel = profile.get(signal_name, None)
    signal = rl_vel
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_RR_VEL
    rr_vel = profile.get(signal_name, None)
    signal = rr_vel
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_FL_PRES
    fl_pres = profile.get(signal_name, None)
    signal = fl_pres
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_FR_PRES
    fr_pres = profile.get(signal_name, None)
    signal = fr_pres
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_RL_PRES
    rl_pres = profile.get(signal_name, None)
    signal = rl_pres
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    signal_name = SIGNAL_RR_PRES
    rr_pres = profile.get(signal_name, None)
    signal = rr_pres
    if signal is None:
        error = 'Signal <{}> not defined within simulation profile!'.format(signal_name)
        LOGGER.error(error)
        validation = False
    else:
        if not isinstance(signal, list):
            error = 'Signal <{}> type list expected! Got {} instead!'\
                .format(signal_name, type(signal))
            LOGGER.error(error)
            validation = False
        else:
            for index, value in enumerate(signal):
                if not isinstance(value, int) and not isinstance(value, float):
                    error = 'Signal <{}> value type int or float expected! Got {} at index {}!'\
                        .format(signal_name, type(value), index)
                    LOGGER.error(error)
                    validation = False
                else:
                    if value < 0:
                        error = 'Signal <{}> value expected to be greater than 0! Got {} instead at index {}!'\
                            .format(signal_name, value, index)
                        LOGGER.error(error)
                        validation = False

    if not validation:
        return False

    if len(fl_vel) == len(fr_vel) == len(rl_vel) == len(rr_vel) == len(fl_pres) == len(fr_pres) == len(rl_pres) \
            == len(rr_pres) == len(abs_ref):
        pass
    else:
        error = 'Simulation signals length miss match!\n'
        error += '{}: {} entries\n'.format(SIGNAL_ABS_REF, len(abs_ref))
        error += '{}: {} entries\n'.format(SIGNAL_FL_VEL, len(fl_vel))
        error += '{}: {} entries\n'.format(SIGNAL_FR_VEL, len(fr_vel))
        error += '{}: {} entries\n'.format(SIGNAL_RL_VEL, len(rl_vel))
        error += '{}: {} entries\n'.format(SIGNAL_RR_VEL, len(rr_vel))
        error += '{}: {} entries\n'.format(SIGNAL_FL_PRES, len(fl_pres))
        error += '{}: {} entries\n'.format(SIGNAL_FR_PRES, len(fr_pres))
        error += '{}: {} entries\n'.format(SIGNAL_RL_PRES, len(rl_pres))
        error += '{}: {} entries\n'.format(SIGNAL_RR_PRES, len(rr_pres))

        LOGGER.error(error)
        validation = False

    return validation


def __get_fps_growth__(sampling_period, time_base):
    """__get_fps__

        Get fps according to specified sampling period for a smooth as possible simulation.
    :param sampling_period: sampling period in seconds
    :type sampling_period: int or float
    :return: specific fps
    :rtype: float
    """
    fps = 25
    growth = 1

    if sampling_period == 0.01:
        if time_base == 1:
            fps = 25
            growth = 4
        elif time_base == 0.5:
            fps = 25
            growth = 2
        elif time_base == 0.25:
            fps = 25
            growth = 1
        elif time_base == 0.10:
            fps = 12.5
            growth = 1

    return fps, growth


if __name__ == '__main__':
    LOGGER.info('{}'.format(BRAKING_SYSTEM_OVERVIEW_IMG))
