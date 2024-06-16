import os

def readConfig(config_filename):
    try:
        with open(config_filename, 'r') as file:
            lines = file.readlines()
    except:
        print('Could not load configiration...')
        exit()

    config = []
    t_thresh = 0
    v_thresh = 0
    for line in lines[10:]:
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if 'T-thresh' in stripped:
            t_thresh = int(stripped.split('=')[1])
        elif 'V-thresh' in stripped:
            v_thresh = int(stripped.split('=')[1])
        elif stripped:
            if stripped[0] in 'TxVo|':
                config.append(stripped)

    emcal_cfg = []
    top_hodo_cfg = []
    bottom_hodo_cfg = []
    current_section = 'top'
    
    for row in config:
        if current_section == 'top':
            top_hodo_cfg.append(row.split())
            current_section = 'emcal'
        elif current_section == 'emcal' and len(emcal_cfg)!=4:
            emcal_cfg.append(row.strip('|').split())
        else:
            bottom_hodo_cfg.append(row.split())

    allConfiguration= {
        'triggerThresh' : t_thresh,
        'vetoThresh' : v_thresh,
        'emcalCfg' : emcal_cfg,
        'topHodoCfg' : top_hodo_cfg[0],
        'bottomHodoCfg' : bottom_hodo_cfg[0],
        'topHodoEnabled' : not all(channel == 'x' for channel in top_hodo_cfg[0]), # true, unless all channels are 'x'
        'botHodoEnabled' : not all(channel == 'x' for channel in bottom_hodo_cfg[0])
    }

    if config_filename == '.previous_run.cfg':
        print(f'No config file provided.\n')
        print(f'Loading previous settings...\n')
    else:
        print(f'Loading {config_filename}...\n')
        os.system(f'cp {config_filename} .previous_run.cfg')
    print('Detector configuration:')
    for i in range(10,18):
        print(lines[i],end='')
    print('')
    print(f'Trigger threshold = {t_thresh}, Veto threshold = {v_thresh}')
    if allConfiguration['topHodoEnabled'] or allConfiguration['botHodoEnabled']:
        print('Hodoscope channels enabled in config. Expecting a run file with external trigger info.')
    else:
        print('Hodoscopes disabled in config. Expecting a self triggered run file.')
    print('')
    return allConfiguration