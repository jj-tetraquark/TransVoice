import os
import shutil
from pydub import AudioSegment

outdir = 'common_voice_en_wav'

with open('dev.tsv', 'r') as f:
    f.readline()
    i = 0
    for line in f:
        i += 1
        print('{}/{}'.format(i,13179))
        line = line.split('\t')
        path = line[1]
        sentence = line[2]
        gender = line[6]
        if gender == 'male' or gender == 'female':
            src = os.path.join('clips/', path)
            dest_stub = os.path.join(outdir, gender, path[:-3])
            dest = dest_stub + 'wav'
            print("{} -> {}".format(src, dest))

            if os.path.isfile(dest):
                print("skip!")
                continue

            try:
                sound = AudioSegment.from_mp3(src)
                sound.export(dest, format="wav")

                with open(dest_stub + 'lab', 'w') as labfile:
                    labfile.write(sentence)
            except:
                print("FAILED")
                with open(os.path.join(outdir, "failures.txt"), 'w+') as errfile:
                    errfile.write(src)
