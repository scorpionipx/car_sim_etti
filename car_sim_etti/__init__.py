import logging
import os
import sys

from time import gmtime, strftime

from .version import __version__


APP_NAME = 'CarSim ETTI'
APP_SLUG = 'car_sim_etti'


STATION = os.environ['COMPUTERNAME']
USER = os.getlogin()

CURRENT_DIR = os.path.dirname(__file__)
if getattr(sys, 'frozen', False):
    CURRENT_DIR = os.path.dirname(sys.executable)

LOG_DIR = os.path.join(CURRENT_DIR, '{}_logs'.format(APP_SLUG))

try:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
except Exception as err:
    print(err)


logger = logging.getLogger(APP_SLUG)

log_formatter = logging.Formatter('%(asctime)s: %(message)s', '%d-%b-%Y %H:%M:%S')
log_file_name = '{}_{}.log'.format(APP_SLUG, strftime("%Y_%m_%d_%H_%M_%S", gmtime()))
log_file = os.path.join(LOG_DIR, log_file_name)

file_output = logging.FileHandler(log_file)
file_output.setFormatter(log_formatter)
file_output.setLevel(logging.INFO)
logger.addHandler(file_output)

console = logging.StreamHandler()
console.setFormatter(log_formatter)
logger.addHandler(console)

logger.setLevel(logging.DEBUG)

logger.info('{} v {}'.format(APP_NAME, __version__))
logger.info('Log file: {}'.format(log_file))
logger.info('STATION: {}'.format(STATION))
logger.info('USER: {}'.format(USER))
