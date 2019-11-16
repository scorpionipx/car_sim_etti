import json
import os
from asammdf.mdf import MDF


def convert_mdf_to_sim_profile(mdf_file):
    """convert_mdf_to_sim_profile

    :param mdf_file:
    :return:
    """
    target_signals = [
        ('ABSRef', 'abs_ref'),
        ('VEL_FL', 'fl_vel'),
        ('VEL_FR', 'fr_vel'),
        ('VEL_RL', 'rl_vel'),
        ('VEL_RR', 'rr_vel'),

        ('MkcPmPress_FL_fast_00', 'fl_pres'),
        ('MkcPmPress_FR_fast_00', 'fr_pres'),
        ('MkcPmPress_RL_fast_00', 'rl_pres'),
        ('MkcPmPress_RR_fast_00', 'rr_pres'),
    ]
    x = MDF(mdf_file)

    sim_profile = {'sampling_period': 0.01}

    for target_signal in target_signals:
        signal = next(x.iter_get(target_signal[0], ))
        samples = signal.samples
        reforged_samples = []
        for sample in samples:
            if sample == 0.12:
                sample = 0
                reforged_samples.append(round(sample, 2))
            else:
                reforged_samples.append(round(sample, 2))

        sim_profile[target_signal[1]] = list(reforged_samples)

    file_name = os.path.basename(mdf_file)
    file_handler = open(r'D:\{}.json'.format(file_name.lower().replace('.mdf', '')), 'w+')
    file_handler.write(json.dumps(sim_profile, indent=3))
    file_handler.close()


if __name__ == '__main__':
    MDF_FILE = r"C:\Users\ScorpionIPX\Desktop\IoanaABS\ABS_03_100.mdf"
    convert_mdf_to_sim_profile(MDF_FILE)
    MDF_FILE = r"C:\Users\ScorpionIPX\Desktop\IoanaABS\ABS_04_100.mdf"
    convert_mdf_to_sim_profile(MDF_FILE)
    MDF_FILE = r"C:\Users\ScorpionIPX\Desktop\IoanaABS\ABS_05_100.mdf"
    convert_mdf_to_sim_profile(MDF_FILE)
    MDF_FILE = r"C:\Users\ScorpionIPX\Desktop\IoanaABS\ABS_06_100.mdf"
    convert_mdf_to_sim_profile(MDF_FILE)
    MDF_FILE = r"C:\Users\ScorpionIPX\Desktop\IoanaABS\ABS_07_100.mdf"
    convert_mdf_to_sim_profile(MDF_FILE)
    MDF_FILE = r"C:\Users\ScorpionIPX\Desktop\IoanaABS\ABS_08_100.mdf"
    convert_mdf_to_sim_profile(MDF_FILE)


