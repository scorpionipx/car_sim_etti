import logging


from car_sim_etti import APP_SLUG


LOGGER = logging.getLogger(APP_SLUG)

NOT_AVAILABLE = 'N/A'

SIGNAL_FL_VEL = 'fl_vel'
SIGNAL_FR_VEL = 'fr_vel'
SIGNAL_RL_VEL = 'rl_vel'
SIGNAL_RR_VEL = 'rr_vel'

SIGNAL_FL_PRES = 'fl_pres'
SIGNAL_FR_PRES = 'fr_pres'
SIGNAL_RL_PRES = 'rl_pres'
SIGNAL_RR_PRES = 'rr_pres'


def sim_profile_valid(profile):
    """sim_profile_valid

        Check if specified simulation profile is valid.
    :param profile: simulation profile
    :type profile: dict
    :return: validation result
    :rtype: bool
    """
    validation = True

    fl_vel = profile.get(SIGNAL_FL_VEL, None)
    if fl_vel is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_FL_VEL))
        validation = False

    fr_vel = profile.get(SIGNAL_FR_VEL, None)
    if fr_vel is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_FR_VEL))
        validation = False

    rl_vel = profile.get(SIGNAL_RL_VEL, None)
    if rl_vel is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_RL_VEL))
        validation = False

    rr_vel = profile.get(SIGNAL_RR_VEL, None)
    if rr_vel is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_RR_VEL))
        validation = False

    fl_pres = profile.get(SIGNAL_FL_PRES, None)
    if fl_pres is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_FL_PRES))
        validation = False

    fr_pres = profile.get(SIGNAL_FR_PRES, None)
    if fr_pres is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_FR_PRES))
        validation = False

    rl_pres = profile.get(SIGNAL_RL_PRES, None)
    if rl_pres is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_RL_PRES))
        validation = False

    rr_pres = profile.get(SIGNAL_RR_PRES, None)
    if rr_pres is None:
        LOGGER.error('Signal <{}> not defined within simulation profile!'.format(SIGNAL_RR_PRES))
        validation = False

    if len(fl_vel) == len(fr_vel) == len(rl_vel) == len(rr_vel):
        pass
    else:
        error = 'Simulation signals length miss match!\n'
        error += '{}: {} entries\n'.format(SIGNAL_FL_VEL, len(fl_vel))
        error += '{}: {} entries\n'.format(SIGNAL_FR_VEL, len(fr_vel))
        error += '{}: {} entries\n'.format(SIGNAL_RL_VEL, len(rl_vel))
        error += '{}: {} entries\n'.format(SIGNAL_RR_VEL, len(rr_vel))

        LOGGER.error(error)
        validation = False

    return validation


