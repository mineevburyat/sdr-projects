from __future__ import print_function
import SoapySDR
import numpy as np
import struct
import sys
import time
import datetime


def wait_for_start(dt):
    # Wait for the start
    while True:
        now = datetime.datetime.now()
        diff = int((dt - now).total_seconds())
        print("{:02d}:{:02d}:{:02d}: Recording will be started after {}m {:02d}s...".format(now.hour, now.minute, now.second, int(diff / 60), diff % 60))
        time.sleep(5)
        if diff <= 1:
            break


def sdr_enumerate():
    # Enumerate SDR devices
    print("SDR devices:")
    for d in SoapySDR.Device.enumerate(''):
        print(d)
    print()


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


def sdr_record(device, frequency, sample_rate, gain, blocks_count):
    print("Frequency:", frequency)
    print("Sample rate:", sample_rate)
    print("Gain:", gain)

    channel = 0  # Always for RTL-SDR
    device.setFrequency(SoapySDR.SOAPY_SDR_RX, channel, "RF", frequency)
    device.setGain(SoapySDR.SOAPY_SDR_RX, channel, "TUNER", gain)
    device.setGainMode(SoapySDR.SOAPY_SDR_RX, channel, False)
    device.setSampleRate(SoapySDR.SOAPY_SDR_RX, channel, sample_rate)

    data_format = SoapySDR.SOAPY_SDR_CS8 # if 'rtlsdr' in soapy_device or 'hackrf' in soapy_device else SoapySDR.SOAPY_SDR_CS16
    stream = device.setupStream(SoapySDR.SOAPY_SDR_RX, data_format, [channel], {})
    device.activateStream(stream)

    block_size = device.getStreamMTU(stream)
    print("Block size:", block_size)
    print("Data format:", data_format)
    print()

    # IQ: 2 digits ver variable
    buffer_format = np.int8
    buffer_size = 2 * block_size # I + Q samples
    buffer = np.empty(buffer_size, buffer_format)

    # Number of blocks to save
    block, max_blocks = 0, blocks_count

    # Save to file
    file_name = "HDSDR_%s_%dkHz_RF.wav" % (datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%SZ"), frequency/1000)
    print("Saving file:", file_name)
    with open(file_name, "wb") as wav:
        # Wav data info
        bits_per_sample = 16
        channels_num, samples_num = 2, int(max_blocks * block_size)
        subchunk_size = 16  # always 16 for PCM
        subchunk2_size = int(samples_num * channels_num * bits_per_sample / 8)
        block_alignment = int(channels_num * bits_per_sample / 8)

        # Write RIFF header
        wav.write('RIFF'.encode('utf-8'))
        wav.write(struct.pack('<i', 4 + (8 + subchunk_size) + (8 + subchunk2_size)))  # Size of the overall file
        wav.write('WAVE'.encode('utf-8'))
        # Write fmt subchunk
        wav.write('fmt '.encode('utf-8'))  # chunk type
        wav.write(struct.pack('<i', subchunk_size))  # subchunk data size (16 for PCM)
        wav.write(struct.pack('<h', 1))  # compression type 1 - PCM
        wav.write(struct.pack('<h', channels_num))  # channels
        wav.write(struct.pack('<i', int(sample_rate)))  # sample rate
        wav.write(struct.pack('<i', int(sample_rate * bits_per_sample * channels_num/ 8)))  # byte rate
        wav.write(struct.pack('<h', block_alignment))  # block alignment
        wav.write(struct.pack('<h', bits_per_sample))  # sample depth
        # Write data subchunk
        wav.write('data'.encode('utf-8'))
        wav.write(struct.pack('<i', subchunk2_size))
        while True:
            d_info = device.readStream(stream, [buffer], buffer_size)
            if d_info.ret > 0:
                data = buffer[0:2*d_info.ret]
                fileData = data
                if data_format == SoapySDR.SOAPY_SDR_CS8:
                   fileData = data.astype('int16')
                wav.write(fileData)
                print("Block %d saved: %d bytes" % (block, 2*d_info.ret))
                block += 1
                if block > max_blocks:
                    break

    device.deactivateStream(stream)
    device.closeStream(stream)

if __name__ == "__main__":
    print("App started")

    # Forecast for active NOAA satellites
    # NOAA 15: 137.620, https://www.n2yo.com/passes/?s=25338
    # NOAA 18: 137.9125, https://www.n2yo.com/passes/?s=28654
    # NOAA 19: 137.100, https://www.n2yo.com/passes/?s=33591
    # Wait for the start: 18-May 21:49 21:49:
    # wait_for_start(datetime.datetime(2019, 5, 18, 21, 49, 0))

    device = sdr_init()

    t_start = time.time()

    sdr_record(device, frequency=88800000, sample_rate=250000, gain=35, blocks_count=210)

    print("Recording complete, time = %ds" % int(time.time() - t_start))
    print()