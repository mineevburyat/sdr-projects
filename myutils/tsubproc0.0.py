from subprocess import Popen, PIPE, DEVNULL, SubprocessError
from time import sleep, mktime, strptime
from datetime import datetime
from tempfile import TemporaryFile

f = TemporaryFile()

noise_proc = Popen(['hackrf_sweep', '-1', '-f 400:457', '-w 100000'], stdout=PIPE, stderr=f)
min_power = []
max_power = []
avg_power = []
result = {}


while noise_proc.poll() is None:
    line = noise_proc.stdout.readline().split(b', ')
    print(f.read().decode("utf-8"))
    if len(line) > 2:
        ch_count = len(line) - 6
        powers = [float(item) for item in line[6:]]
        freq = float(line[2]) + (float(line[3]) - float(line[2])) // 2
        freq1 = float(line[2])
        freq2 = float(line[3])
        avg = sum(powers) / ch_count
        p_max = max(powers)
        p_min = min(powers)
        avg_power.append(avg)
        min_power.append(p_min)
        max_power.append(p_max)
        result[freq1] = (p_min, p_max, avg)

for freq, item in result.items():
    print(freq, '-', item)

# print(min_power)
# print(max_power)
# try:

#     while process.stderr:
#         print(process.stderr.readline())
#     while process.poll() is None:

#         print('\r',run_str[indx], count, end='')
#         # print(process.stderr.readline())
#         line = process.stdout.readline().split(b', ')
#         if len(line) > 2:
#             ch_count = len(line) - 6
#             if ch_count == 0:
#                 print(line)
#             powers = [float(item) for item in line[6:]]
#             avg = sum(powers) / ch_count
#             if avg > NOISE:
#                 # print(len(line),line)
#                 t = mktime(strptime(line[0].decode() + ', ' + line[1].decode(),
#                                             "%Y-%m-%d, %H:%M:%S.%f"))
#                 for index, power in enumerate(powers):
#                     if power > NOISE:
#                         freq = float(line[2]) + float(line[4]) * index
#                         old_power = scan_analiz.get(freq)
#                         if old_power and power > old_power:
#                             scan_analiz[freq] = power
#                             history[freq].append((t, power))
#                         else:
#                             scan_analiz[freq] = power
#                             history[freq] = [(t, power)]
#                         count += 1
#         indx = (indx + 1) % len(run_str)
# except KeyboardInterrupt:
#     sleep(1)
#     print('\nstop hackrf.')
# # for freq, power in scan_analiz.items():
# #     print(freq/1e6, 'Mhz : ', power, 'dB')

# for freq, t_line in history.items():
#     print(freq/1e6, 'Mhz: ')
#     for stamp in t_line:
#         t_value = datetime.fromtimestamp(stamp[0])
#         print('\t', t_value.strftime("%Y-%m-%d %H:%M:%S"), ': ', stamp[1])

                    