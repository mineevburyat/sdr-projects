from gnuradio import analog
analog_sig_source_x_0 = analog.sig_source_c(2000, analog.GR_SIN_WAVE, 1000, 1, 0, 0)
analog_sig_source_x_0.set_sampling_freq(4000)
print(analog_sig_source_x_0.start())