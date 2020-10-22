import os
import sys
import numpy as np
import pyaudio
from librosa import lpc, load
import scipy.io.wavfile as wavfile
import scipy
from scipy.fftpack import rfft, fftfreq
from scipy.signal import lfilter, freqz
import matplotlib.pyplot as plt
import crepe
import praat_formants_python as pfp
from utils import get_vowel_intervals

CHUNK_SIZE = 1024


def playback(data, rate):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pa.get_format_from_width(data.dtype.itemsize),
                     channels=1,
                     rate=rate,
                     output=True)

    sound_length = len(data)

    for i in range(0, sound_length, CHUNK_SIZE):
        chunk_end = min(i + CHUNK_SIZE, sound_length)

        chunk = data[i:chunk_end]
        stream.write(chunk.tobytes())

    stream.stop_stream()
    stream.close()
    pa.terminate()


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

def get_formants(rate, audio, window, plot=False):
    total_length = len(audio)
    formants = []

    window_frames = window * rate
    sample_count = 0

    while True:
        start = int(sample_count * window_frames)
        end = int((sample_count + 1) * window_frames)
        sample_count += 1

        if start > total_length:
            break

        end = total_length if end > total_length else end

        clip = audio[start:end]

        N = len(clip)
        # apply window and high-pass filter
        window = np.hamming(N)
        processed = lfilter([1], [1., 0.63], clip * window)

        try:
            coeffs = lpc(processed, estimate_num_coefficients(rate))
        except FloatingPointError:
            continue

        roots = np.roots(coeffs)
        roots = [r for r in roots if np.imag(r) >= 0]

        angles = np.arctan2(np.imag(roots), np.real(roots))

        freqs = angles * (rate / (2 * np.pi))
        bandwidths = -1/2 * (rate / (2 * np.pi)) * np.log(np.abs(roots))


        # formants below 70Hz are too low to be part of human speech
        # formant bandwidths are usually < 100 and always < 200
        formants.append(sorted([freq for i, freq in enumerate(freqs) if freq > 50 and bandwidths[i] < 200]))
        print(formants[-1][0:4])

        if plot:
            plot_formants(formants, coeffs, clip, rate)

    return formants[0:3]

def plot_formants(formants, coeffs, clip, rate):
    print(formants[0:4])
    f, h = freqz([1], coeffs, 1000, fs=rate)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(f, np.log(np.abs(h)))
    ax.set_xlim(0, 5500)
    ax.set_ylim(0, 10)

    plot_fft(clip, ax, rate)
    plt.show()

def plot_fft(data, axis, rate):
    fft_out = rfft(data)

    freq = fftfreq(data.size, d=(1.0/rate))

    fft_abs = scipy.absolute(fft_out)

    log_fft = scipy.log10(scipy.absolute(fft_abs))

    axis.plot(freq, log_fft)

    return fft_out, freq


def smooth(x, window_len):
    s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]
    w = np.hanning(window_len)
    y = np.convolve(w/w.sum(), s, mode='valid')
    return y[int(window_len/2-1):-int(window_len/2)]

def find_fundamental(signal, rate):
    fft_out = rfft(signal)
    freq = fftfreq(signal.size, d=(1.0/rate))
    return freq[np.argmax(smooth(fft_out, 5))]


def do_pitch_extraction_fft(signal, rate, interval):
    interval_samples = int(rate * interval)
    t = 0
    freqs = []
    while t + interval_samples <= len(signal):
        sample = signal[t:t+interval_samples]
        N = len(sample)
        window = np.hamming(N)

        freqs.append(find_fundamental(sample * window, rate))
        t += interval_samples
    return freqs

def get_formants_praat(wavfile, start, stop):
    return pfp.formants_at_interval(wavfile, start, stop)

if __name__ == '__main__':
    audio_file = sys.argv[1]
    grid_dir = sys.argv[2]

    sound_dir = os.path.dirname(audio_file)
    audio_basename = os.path.basename(audio_file)

    grid_file = os.path.join(grid_dir, audio_basename[:-3] + 'TextGrid')
    vowel_intervals = get_vowel_intervals(grid_file)

    rate, data = wavfile.read(audio_file)

    for vowel in vowel_intervals:
        print(vowel)
        start = int(vowel.xmin * rate)
        stop = int(vowel.xmax * rate)

        clip = data[start:stop]
        playback(clip, rate)
        #get_formants(rate, clip, 50e-3, False)
        formants = get_formants_praat(os.path.join(os.getcwd(), audio_file),
                                      vowel.xmin, vowel.xmax)
        print("Formants")
        print(formants[:,1:])
        time, frequency, confidence, activation = crepe.predict(clip, rate, viterbi=True)
        print("Hz")
        print(frequency)
