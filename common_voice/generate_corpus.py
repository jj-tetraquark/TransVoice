import os
import sys


if __name__ == '__main__':
    labfiles = [f for f in os.listdir(sys.argv[1]) if f.endswith('lab')]

    corpus = set()
    for labfile in labfiles:
        path = os.path.join(sys.argv[1], labfile)
        with open(path) as f:
            txt = f.read()
            words = txt.split(' ')
            for word in words:
                word = word.rstrip().replace('"', '').replace('.','').replace(',','').lower()
                corpus.add(word.lower())

    with open('corpus.txt', "a+") as outfile:
        outfile.write('\n'.join(corpus))
