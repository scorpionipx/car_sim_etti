import os.path as py_path


CURRENT_DIR = py_path.dirname(__file__)
STATIC_DIR = py_path.join(CURRENT_DIR, 'static')
IMAGES_DIR = py_path.join(STATIC_DIR, 'images')

WINDOWS_ICON_PATH = py_path.join(IMAGES_DIR, 'icon.ico')

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = 'CarSimIPX ETTI'

MIN_FPS = 24
MAX_FPS = 36


FR_VEL_LABEL_X = 250
FR_VEL_LABEL_Y = 380
FL_VEL_LABEL_X = 250
FL_VEL_LABEL_Y = 525
RR_VEL_LABEL_X = 535
RR_VEL_LABEL_Y = 370
RL_VEL_LABEL_X = 535
RL_VEL_LABEL_Y = 505

FR_PRES_LABEL_X = 180
FR_PRES_LABEL_Y = 280
FL_PRES_LABEL_X = 180
FL_PRES_LABEL_Y = 425
RR_PRES_LABEL_X = 670
RR_PRES_LABEL_Y = 280
RL_PRES_LABEL_X = 670
RL_PRES_LABEL_Y = 425

FR_PRES_PBAR_X = 150
FR_PRES_PBAR_Y = 280
FL_PRES_PBAR_X = 150
FL_PRES_PBAR_Y = 425
RR_PRES_PBAR_X = 640
RR_PRES_PBAR_Y = 280
RL_PRES_PBAR_X = 640
RL_PRES_PBAR_Y = 425

PRES_PBAR_MIN = 0
PRES_PBAR_MAX = 250


NOB_TO_N = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3}


def build_spi_command(cmd_id, data):
    """build_spi_command
        Build SPI command.
    :param cmd_id: command's ID in range [0, 31]
    :type cmd_id: int
    :param data: list of 8 bits data to be sent, maximum 1024 bytes
    :type data: list of int
    :return: None
    """
    number_of_data_bytes = len(data)

    if number_of_data_bytes <= 7:
        extend = 0
        n = NOB_TO_N[number_of_data_bytes + 1]
        data_0_byte = False
        frame_length = 1 << n
    else:
        number_of_data_bytes += 1
        extend = 1
        n = (number_of_data_bytes & 0b1100000000) >> 8
        data_0_byte = number_of_data_bytes & 0xFF
        data_frame_length = number_of_data_bytes + 1
        frame_length = data_frame_length + 1

    header_byte = (cmd_id << 3) | (extend << 2) | n

    spi_data = [header_byte]

    if data_0_byte:
        spi_data.append(data_0_byte)

    spi_data.extend(data)
    if extend == 0:
        while len(spi_data) < frame_length:
            spi_data.append(0)  # dummy byte

    return spi_data


if __name__ == '__main__':
    cmd = build_spi_command(cmd_id=5, data=[0x01, 0x02, 0x03, 0x01, 0x02, 0x03, 0x01, 0x02, 0x03])
    for b in cmd:
        print('0b{n:08b}'.format(n=b))
