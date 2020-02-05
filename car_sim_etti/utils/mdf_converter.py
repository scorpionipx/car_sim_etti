import json
import os
from asammdf.mdf import MDF


def convert_mdf_to_sim_profile(mdf_file, rename):
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
    file_handler = open(r'D:\masu\{}.json'.format(rename), 'w+')
    # file_handler = open(r'D:\{}.json'.format(file_name.lower().replace('.mdf', '')), 'w+')
    file_handler.write(json.dumps(sim_profile, indent=3))
    file_handler.close()


if __name__ == '__main__':
    # rename files
    # ==================================================================================================================
    path = r'C:\Users\ScorpionIPX\Desktop\meas_ipx'
    json_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json')]
    # for json_file in json_files:
    #     print(json_file)

    speeds = [50, 60, 70, 80, 90, 100, 110, 120, 130]
    us = ['03', '04', '05', '06', '07', '08', '09', '38']

    index = 0
    for u in us:
        for s in speeds:
            rename = '{}_{}.json'.format(s, u)
            old = json_files[index]
            new = os.path.join(path, rename)
            print('{} - > {}'.format(old, new))
            index += 1
            # os.rename(old, new)
    # ==================================================================================================================

    # path = r'C:\Users\ScorpionIPX\Desktop\meas_ipx'
    # mdf_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json')]
    # files = []
    # for mdf_file in mdf_files:
    #     files.append(mdf_file)
    # speeds = [50, 60, 70, 80, 90, 100, 110, 120, 130]
    # us = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 3.8]
    # file_index = 0
    # for speed in speeds:
    #     for u in us:
    #         renaming = '{}_{}'.format(speed, u)
    #         print(file_index, renaming)
    #         file_index += 1
    #         mdf_file = files[file_index]
    #         # convert_mdf_to_sim_profile(mdf_file, rename=renaming)
    #         # print(mdf_file)

    path = r'C:\Users\ScorpionIPX\Desktop\meas_ipx'
    json_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json')]
    print('{} files'.format(len(json_files)))
    # for file in json_files:
    #     print(file)

    for file in json_files:
        # if '07' in file:
        #     continue
        # if '08' in file:
        #     continue
        file_handler = open(file, 'r')
        content = file_handler.read()
        file_handler.close()
        signals = json.loads(content)
        speeds = signals['abs_ref']
        max_speed = max(signals['abs_ref'])
        file_name = os.path.basename(file)
        diff = int(file_name[:file_name.find('_')]) - max_speed
        warning = 'WARNING! ' * 3 + '\n' if abs(diff) > 2 else 'OK'
        lenu = len(speeds)
        print('{} -> max speed: {}km/h diff: {} len: {} {}'
              .format(file.split('\\')[-1], max_speed, diff, lenu, warning))



