import os
import sys
import crepe
import praat_formants_python as pfp
import scipy.io.wavfile as wavfile
from utils import get_vowel_intervals

if __name__ == '__main__':
    audio_dir = sys.argv[1]
    grid_dir = sys.argv[2]

    audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith('wav')]

    outfile = open(os.path.join(grid_dir, 'metadata.csv'), 'a+')
    outfile.write('filename, time, phoneme, f0, f1, f2, f3\n')

    count = 0
    for audio_file in audio_files:
        count += 1
        print ("{}/{} Processing {}".format(count, len(audio_files), audio_file))
        audio_basename = os.path.basename(audio_file)
        grid_file = os.path.join(grid_dir, audio_basename[:-3] + 'TextGrid')

        if not os.path.exists(grid_file):
            print("No gridfile, SKIP!")
            continue

        vowel_intervals = get_vowel_intervals(grid_file)
        rate, data = wavfile.read(audio_file)

        for vowel in vowel_intervals:
            start = int(vowel.xmin * rate)
            stop = int(vowel.xmax * rate)

            formants = pfp.formants_at_interval(
                            os.path.join(os.getcwd(), audio_file),
                            vowel.xmin, vowel.xmax)

            clip = data[start:stop]
            time, frequency, confidence, activation = crepe.predict(clip, rate, viterbi=True)

            for i in range(len(formants)):
                outfile.write("{filename}, {time}, {phoneme}, {f0}, {f1}, {f2}, {f3}\n".format(
                                filename=audio_basename,
                                time=formants[i, 0],
                                phoneme=vowel.text.rstrip('0123'),
                                f0=frequency[i + 1] if i + 1 < len(frequency) else '',
                                f1=formants[i,1],
                                f2=formants[i,2],
                                f3=formants[i,3]))
