import sys
import os
import numpy as np
from scipy.signal import lfilter, freqz
import scipy.io.wavfile as wavfile
from librosa import lpc, load
import matplotlib.pyplot as plt
from audiolazy import lazy_lpc


def find_fundamental(signal, rate):
    fft_out = rfft(signal)
    freq = fftfreq(signal.size, d=(1.0/rate))
    return freq[np.argmax(fft_out)]

# When estimating formants it is essential to select the number of coefficients correctly
# Theoretically, the maximum frequence that can be represented in an audio
# signal is *half* the sample rate (known as the Nyquist frequency).
# The absolute minimum number of filter coefficients there should be is twice
# the number of formants
# We estimate there is roughly one formant per 1000Hz for the frequency range
# and then +2 for saftey
def estimate_num_coefficients(rate):
    max_freq = rate/2
    formants = max_freq/1000
    return int(formants * 2)



def get_formants(rate, data):
    N = len(data)

    # apply window and high-pass filter
    window = np.hamming(N)
    processed = lfilter([1], [1., 0.63], data * window)

    coeffs = lpc(processed, estimate_num_coefficients(rate))
    #coeffs = lazy_lpc.lpc.autocor(processed, estimate_num_coefficients(rate)).numerator

    roots = np.roots(coeffs)
    roots = [r for r in roots if np.imag(r) >= 0]

    angles = np.arctan2(np.imag(roots), np.real(roots))

    freqs = angles * (rate / (2 * np.pi))
    bandwidths = -1/2 * (rate / (2 * np.pi)) * np.log(np.abs(roots))

    #print(freqs)
    #print(bandwidths)

    # formants below 70Hz are too low to be part of human speech
    # formant bandwidths are usually < 100 and always < 200
    formants = sorted([freq for i, freq in enumerate(freqs) if freq > 50 and bandwidths[i] < 200])
    #print(formants[0:3])

    f, h = freqz([1], coeffs, 1000, fs=rate)
    plt.plot(f, np.log(np.abs(h)))
    plt.xlim(0,4000)
    plt.show()
    return formants[0:3]



if __name__ == '__main__':
    file_path = sys.argv[1]

    if (os.path.isdir(file_path)):
        files = [os.path.join(file_path, f) for f in os.listdir(file_path) if f.endswith('.wav')]
        for f in files:
            rate, data = wavfile.read(f)
            formants = get_formants(rate, data)
            print("{} : {}".format(f, formants))

    else:
        rate, data = wavfile.read(file_path)
        #data, rate = load(file_path)
        print(get_formants(rate, data))

        #lpc = lpc_spectrum(data)

