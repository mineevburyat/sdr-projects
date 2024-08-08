# https://www.cs.princeton.edu/courses/archive/spring19/cos463/labs/Lab1_preview.html


import SoapySDR
import SoapyHackRF
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
import time
import numpy as np
import matplotlib.pyplot as plt

class Radio:
    def __init__(self, driver="hackrf", freq=90e6, 
                 sampl_rate=8e6):
        self.rx_stream = None
        self.driver = driver
        self.center_freq = freq
        self.sampl_rate = sampl_rate
        self.sdr = SoapySDR.Device(dict(driver=driver))
        self.set_sample_rate(self.sampl_rate)
        self.set_center_frequency(self.center_freq)

    def set_sample_rate(self, sample_rate_hz):
        self.sdr.setSampleRate(SOAPY_SDR_RX, 0, sample_rate_hz)

    def set_center_frequency(self, freq_hz):
        self.sdr.setFrequency(SOAPY_SDR_RX, 0, freq_hz)

    def start_receive(self):
        self.rx_stream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
        self.sdr.activateStream(self.rx_stream)

    def stop_receive(self):
        self.sdr.deactivateStream(self.rx_stream)
        self.sdr.closeStream(self.rx_stream)
        self.rx_stream = None

    def grab_samples(self, rx_buff):
        if self.rx_stream is None:
            raise RuntimeError("Need to start receiving before grabbing samples")

        if len(rx_buff) > self.get_buffer_size():
            raise RuntimeError("Number of samples cannot be more than the buffer size")

        resp = self.sdr.readStream(self.rx_stream, [rx_buff], numElems=len(rx_buff))
        print(resp)
        if resp.ret != len(rx_buff):
            raise RuntimeError('Receive failed: {}'.format(SoapySDR.errToStr(resp.ret)))

    def get_buffer_size(self):
        return 131072
    
    def get_stream(self):
        return self.rx_stream



device1 = Radio()
buffer = np.empty([device1.get_buffer_size()], dtype=np.complex64)
device1.get_stream()
device1.start_receive()
# time.sleep(0)
device1.grab_samples(buffer)
device1.stop_receive()

plt.plot(np.real(buffer));
plt.show()
# spectr = np.fft.fft(buffer)
# spectr_power = 10 * np.log10(np.abs(np.fft.fft(buffer) ** 2))
# fig = plt.figure();
# plt.plot(spectr_power);
# plt.show()
# plt.magnitude_spectrum(spectr, Fs=device1.sampl_rate, Fc=device1.center_freq)
# plt.show()