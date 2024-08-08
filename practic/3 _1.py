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
    device.setFrequency(SoapySDR.SOAPY_SDR_RX, channel, frequency)
    device.setSampleRate(SoapySDR.SOAPY_SDR_RX, channel, sample_rate)
    stream = device.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    buffer = np.array([0]*fft_size, np.complex64)
    device.activateStream(stream)
    d_info = device.readStream(stream, [buffer], len(buffer))
    i = 0
    while i < 1:
        print(d_info.ret)
        if d_info.ret > 0:
            spectr = np.fft.fftshift(np.fft.fft(buffer)) 
            S_mag = np.abs(spectr)
            zero_dc_left = S_mag[S_mag.size // 2 - 1]
            zero_dc_right = S_mag[S_mag.size // 2 + 1]
            mean_zero = (zero_dc_left + zero_dc_right) / 2
            S_mag[S_mag.size // 2] = mean_zero
            mean = S_mag.mean()
            S_mag = S_mag - 2 * mean
            S_mag = np.where(S_mag > mean, S_mag, 0)
            i += 1
    device.deactivateStream(stream)
    device.closeStream(stream)
    freq = np.arange(frequency + sample_rate/-2, frequency + sample_rate/2, sample_rate/fft_size)
    return np.column_stack([S_mag, freq])

def plot_time(device, frequency, sample_rate, gain, blocks_count, fft_size=1024):
    channel = 0  # Always for RTL-SDR
    device.setFrequency(SoapySDR.SOAPY_SDR_RX, channel, frequency)
    device.setSampleRate(SoapySDR.SOAPY_SDR_RX, channel, sample_rate)
    stream = device.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    device.activateStream(stream)
    block_size = device.getStreamMTU(stream)
    buffer = np.array([0]*fft_size, np.complex64)
    d_info = device.readStream(stream, [buffer], len(buffer))
    print('info:', d_info, d_info.ret)
    i = 1
    while i < blocks_count:
        if d_info.ret > 0:
            f = np.arange(frequency + sample_rate/-2, frequency + sample_rate/2, sample_rate/fft_size)
            plt.plot(f, buffer.real,'.-')
            plt.plot(f, buffer.imag, '.-')
            plt.show()
            i += 1
    device.deactivateStream(stream)
    device.closeStream(stream)

def sdr_record(device, frequency, sample_rate, gain, blocks_count, fft_size=1024):
    print("Frequency:", frequency)
    print("Sample rate:", sample_rate)
    print("Gain:", gain)
    
    channel = 0  # Always for RTL-SDR
    
    device.setFrequency(SoapySDR.SOAPY_SDR_RX, channel, frequency)
    device.setSampleRate(SoapySDR.SOAPY_SDR_RX, channel, sample_rate)

    stream = device.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    device.activateStream(stream)

    block_size = device.getStreamMTU(stream)
    print("Block size:", block_size)
    # print("Data format:", data_format)
    print()

    buffer = np.array([0]*fft_size, np.complex64)
    d_info = device.readStream(stream, [buffer], len(buffer))
    print('info:', d_info, d_info.ret)
    plt.ion()
    i = 0
    while i < blocks_count:
        print(d_info.ret)
        if d_info.ret > 0:
            spectr = np.fft.fftshift(np.fft.fft(buffer)) 
            S_mag = np.abs(spectr)
            # print(S_mag[fft_size // 2 - 3: fft_size // 2 + 4])
            zero_dc_left = S_mag[S_mag.size // 2 - 1]
            zero_dc_right = S_mag[S_mag.size // 2 + 1]
            mean_zero = (zero_dc_left + zero_dc_right) / 2
            # print(zero_dc_right, zero_dc_left, S_mag[fft_size // 2 - 1], mean_zero)
            S_mag[S_mag.size // 2] = mean_zero
            f = np.arange(frequency + sample_rate/-2, frequency + sample_rate/2, sample_rate/fft_size)
            # f = np.arange(0,fft_size)
            mean = np.mean(S_mag)
            S_mag = S_mag - 2 * mean
            S_mag = np.where(S_mag > mean, S_mag, 0)
            # piks = S_mag[S_mag > mean]
            # print(piks)
            # print('mean:', np.mean(S_mag))
            # print('max:', np.max(S_mag))
            # print('min:', np.min(S_mag))
            plt.plot(f, S_mag,'.-')
            # !!! Следующие два вызова требуются для обновления графика
            plt.draw()
            plt.gcf().canvas.flush_events()
            # Задержка перед следующим обновлением
            time.sleep(0.02)
            
        d_info = device.readStream(stream, [buffer], len(buffer))
        i += 1
    plt.ioff()
    # plt.bar(f, S_mag)
    plt.show()
    device.deactivateStream(stream)
    device.closeStream(stream)

if __name__ == "__main__":
    print("App started")

    device = sdr_init()

    t_start = time.time()
    plot_time(device, frequency=100000000, sample_rate=20000000, gain=14, blocks_count=2, fft_size=2048)
    # sdr_record(device, frequency=100000000, sample_rate=20000000, gain=0, blocks_count=10, fft_size=2048)

    # samp_f = 10e6
    # freq_ranges = [(70e6, 100e6), (390e6, 440e6)]
    # result = None
    # for freq_range in freq_ranges:
    #     start_freq, stop_freq = freq_range
    #     center_freq = start_freq + samp_f / 2
    #     while center_freq <= stop_freq:
    #         print(center_freq)
    #         if result is None:
    #             result = scan_freq(device, center_freq, samp_f)
    #         else:
    #             result = np.concatenate([result, scan_freq(device, center_freq, samp_f)])
    #         center_freq = center_freq + samp_f
            
    # print(result)