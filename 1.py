from __future__ import print_function
import SoapySDR

# Enumerate devices
print("SDR devices:")
for d in SoapySDR.Device.enumerate(''):
    print(d)
print()