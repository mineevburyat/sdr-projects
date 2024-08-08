from subprocess import Popen, PIPE, DEVNULL, STDOUT
from time import sleep, mktime, strptime
from datetime import datetime
import numpy as np
from myutils.frange import FreqRange, FreqRanges


freq_range = FreqRanges((125, 150),
                       (420, 450),
                       (800, 900),
                       (1200, 1300),
                       (2300, 2500)
)

# product
process = Popen(['hackrf_sweep', '-w 1000000', '-a 1'], stdout=PIPE)
# debug
# out = Popen(['hackrf_sweep', '-f 200:6000', '-1'], stdout=PIPE)


run_str = ['|', '/', '-', '\\']
indx = 0
print('start hackrf_sweep.....')

SNR = 20 # dB превышение уровня шума
scan_analiz = {} # 
history = {}
count_freq = 0
count_find = 0
min_power = 0
max_power = -100
try:
    while process.poll() is None:
        print(f'\r{run_str[indx]} {count_find} ({count_freq})', end='')
        line = process.stdout.readline().strip().split(b', ')
        if len(line) > 6:
            ch_count = len(line) - 6
            powers = np.array([float(item) for item in line[6:]])
            avg = powers.mean()
            min_power = min(min_power, np.min(powers))
            max_power = max(max_power, np.max(powers))
            for index, power in enumerate(powers):
                freq = float(line[2]) + float(line[4]) * index
                if freq_range.inranges(freq * 1e6):
                    if power > avg + SNR:
                        old_power = scan_analiz.get(freq)
                        if old_power and power > old_power:
                            scan_analiz[freq] = power
                        else:
                            scan_analiz[freq] = power
                            count_freq += 1
                        count_find += 1
        
        indx = (indx + 1) % len(run_str)
        if scan_analiz:
            for freq, power in dict(sorted(scan_analiz.items())):
                print(f"{freq} - {power}")
except KeyboardInterrupt:
    sleep(1)
    print('\nstop hackrf.')
    
for freq, power in scan_analiz.items():
    print(freq/1e6, 'Mhz : ', power, 'dB')

# for freq, t_line in history.items():
#     print(freq/1e6, 'Mhz: ')
#     for stamp in t_line:
#         t_value = datetime.fromtimestamp(stamp[0])
#         print('\t', t_value.strftime("%Y-%m-%d %H:%M:%S"), ': ', stamp[1])
