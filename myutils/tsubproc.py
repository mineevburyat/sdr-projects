from subprocess import Popen, PIPE

out = Popen(['hackrf_sweep', '-1', '-w 200000'], stdout=PIPE)


NOISE = -50 # Noise floor
scan_analiz = {}

while out.poll() is None:
    line = out.stdout.readline().split(b', ')
    if len(line) > 0:
        ch_count = len(line) - 6
        powers = [float(item) for item in line[6:]]
        avg = sum(powers) / ch_count
        if avg > NOISE:
            for index, power in enumerate(powers):
                if power > NOISE:
                    freq = float(line[2]) + float(line[4]) * index
                    old_power = scan_analiz.get(freq)
                    if old_power and power > old_power:
                        scan_analiz[freq] = power
                    else:
                        scan_analiz[freq] = power

for freq, power in scan_analiz.items():
    print(freq/1e6, 'Mhz : ', power, 'dB')

                    
