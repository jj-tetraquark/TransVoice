import os
from pydub import AudioSegment
from pydub.playback import play

class Getch:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


if __name__ == '__main__':
    getch = Getch()

    female_audio_files = [f for f in os.listdir('common_voice_en_wav/female') if f.endswith('wav')]
    total = len(female_audio_files)
    i = 0
    for audio_file in female_audio_files:
        i += 1
        print("{}/{} - {}".format(i, total, audio_file))
        path = os.path.join('common_voice_en_wav/female', audio_file)
        labfile = path[:-3] + "lab"

        while True:
            clip = AudioSegment.from_file(path, 'wav')
            play(clip)
            print('(K)eep, (D)iscard, (R)eplay, (M)ove to male')
            cmd = getch()
            cmd = cmd.lower()
            if cmd == 'k':
                print("all good")
                break
            elif cmd == 'd':
                print("DESTROY")
                os.remove(path)
                os.remove(labfile)
            elif cmd == 'r':
                print("replaying...")
                continue
            elif cmd == 'm':
                print("that's a man...")
                malepath = os.path.join('common_voice_en_wav/male', audio_file)
                os.rename(path, malepath)
            else:
                print("not understood")
