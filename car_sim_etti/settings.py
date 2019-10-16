import os.path as py_path


CURRENT_DIR = py_path.dirname(__file__)
STATIC_DIR = py_path.join(CURRENT_DIR, 'static')
IMAGES_DIR = py_path.join(STATIC_DIR, 'images')

WINDOWS_ICON_PATH = py_path.join(IMAGES_DIR, 'icon.ico')

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = 'CarSim ETTI - ScorpionIPX'
