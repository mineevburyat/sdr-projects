from __future__ import print_function
import SoapySDR
import numpy as np
import struct
import sys
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def sdr_init():
    soapy_device = "hackrf"
    device = SoapySDR.Device({"driver": soapy_device})

    channels = list(range(device.getNumChannels(SoapySDR.SOAPY_SDR_RX)))
    print("Channels:", channels)

    ch = channels[0]

    sample_rates = device.listSampleRates(SoapySDR.SOAPY_SDR_RX, ch)
    print("Sample rates:\n", sample_rates)

    print("Gain controls:")
    for gain in device.listGains(SoapySDR.SOAPY_SDR_RX, ch):
        print("  %s: %s" % (gain, device.getGainRange(SoapySDR.SOAPY_SDR_RX, ch, gain)))

    frequencies = device.listFrequencies(SoapySDR.SOAPY_SDR_RX, ch)
    print("Frequencies names:", frequencies)

    frequency_name = frequencies[0]
    print("Frequency channel name:", frequency_name)

    print("Frequency range:", device.getFrequencyRange(SoapySDR.SOAPY_SDR_RX, ch, frequency_name)[0])

    print()
    return device

def scan_freq(device, frequency, sample_rate, fft_size=1024):
    channel = 0  # Always for RTL-SDR
    num_rows = 300
    device.setFrequency(SoapySDR.SOAPY_SDR_RX, channel, frequency)
    device.setSampleRate(SoapySDR.SOAPY_SDR_RX, channel, sample_rate)
    stream = device.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    buffer = np.array([0] * fft_size , np.complex64)
    device.activateStream(stream)
    sonogram = np.zeros((num_rows, fft_size))
    
    for i in range(num_rows):
        d_info = device.readStream(stream, [buffer], len(buffer))
        print(d_info, end=' ')
        if d_info.ret > 0:
            spectr = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(buffer)))**2)
            sonogram[i,:] = spectr
            print(spectr.mean())
    
    # print(sonogram[0,:])
    
    extent = [(frequency + sample_rate/-2)/1e6,
            (frequency + sample_rate/2)/1e6,
            len(buffer)/sample_rate, 0]
    plt.imshow(sonogram, aspect='auto', extent=extent)
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("Time [s]")
    plt.show()
    # i = 0
    # if d_info.ret > 0:
    #     spectr = 10*np.log10(np.abs(np.fft.fftshift(np.fft.fft(buffer)))**2)
        # spectr = np.fft.fftshift(np.fft.fft(buffer)) 
        # S_mag = np.abs(spectr)
        # zero_dc_left = S_mag[S_mag.size // 2 - 1]
        # zero_dc_right = S_mag[S_mag.size // 2 + 1]
        # mean_zero = (zero_dc_left + zero_dc_right) / 2
        # S_mag[S_mag.size // 2] = mean_zero
        # mean = spectr.mean()
    # device.deactivateStream(stream)
    # device.closeStream(stream)
    # freq = np.arange(frequency + sample_rate/-2, frequency + sample_rate/2, sample_rate/fft_size)
    # plt.plot(freq, spectr)
    # plt.show()
    # return np.column_stack([S_mag, freq])



if __name__ == "__main__":
    print("App started")

    device = sdr_init()
    scan_freq(device, 2.4e9, 20000000, fft_size=1024)
    