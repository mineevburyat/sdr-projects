from __future__ import print_function
import SoapySDR

soapy_device = "hackrf"
device = SoapySDR.Device(dict(driver = soapy_device))

channels = list(range(device.getNumChannels(SoapySDR.SOAPY_SDR_RX)))
print("Channels:", channels)

ch = channels[0]

sample_rates = device.listSampleRates(SoapySDR.SOAPY_SDR_RX, ch)
print("Sample rates:\n", sample_rates)

bandwidths = list(map(lambda r: int(r.maximum()), device.getBandwidthRange(SoapySDR.SOAPY_SDR_RX, ch)))
print("Bandwidths:\n", bandwidths)

print("Gain controls:")
for gain in device.listGains(SoapySDR.SOAPY_SDR_RX, ch):
    print("  %s: %s" % (gain, device.getGainRange(SoapySDR.SOAPY_SDR_RX, ch, gain)))
    
frequencies = device.listFrequencies(SoapySDR.SOAPY_SDR_RX, ch)
print("Frequencies names:", frequencies)

frequency_name = frequencies[0]
print("Frequency channel name:", frequency_name)

print("Frequency range:", device.getFrequencyRange(SoapySDR.SOAPY_SDR_RX, ch, frequency_name)[0])