# https://pysdr.org/content/frequency_domain.html

import numpy as np
import matplotlib.pyplot as plt

freq = 0.5 # Hz
Fs = 2 # Hz
N = 100 # number of points to simulate, and our FFT size

t = np.arange(N) # because our sample rate is 1 Hz
s = np.sin(freq*2*np.pi*t)

# S = np.fft.fft(s)
S = np.fft.fftshift(np.fft.fft(s)) * np.hamming(N)
S_mag = np.abs(S)
# S_phase = np.angle(S)
f = np.arange(Fs/-2, Fs/2, Fs/N)
plt.figure(0)
plt.plot(f, S_mag,'.-')
plt.figure(1)
plt.plot(t, s,'.-')
plt.show()
