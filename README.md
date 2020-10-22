# Trans Voice Research

This is a repo containing research code and things for my trans voice project.
This readme serves as a reminder to myself and as a quick-start for anyone hoping
to understand what is going on in my head and this mess of code.

## Dataset

Included in the repository are csvs of the auto-extracted formants from the dev
subset of the common-voice dataset. This was created like so:

1. Convert all the dev files to wav and sort them in to male and female directories 
(`common-voice/convert_to_wav.py`). This also creates `.lab` files for the forced aligner.
2. Perform forced alignment on these wav files using a prebuilt copy of the [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/introduction.html).
I used the standard english pretrained model and the lexicon `montreal-force-aligner/lexicon2.txt`
3. Using the [`praat_formants_python`](https://github.com/mwv/praat_formants_python) and [Praat](https://www.fon.hum.uva.nl/praat/), 
auto extract the first 4 formants from 10ms slices of the sections of audio that correspond
with vowels (`common-voice/generate_dataset.py`)

The raw data is not included in this repo as it's fucking huge, just running `ls` on 
the directory takes minutes to complete. Even the dev subset
is like 2GB converted to wav. If you want to use it you'll need to download it from
[The common voice project](https://commonvoice.mozilla.org/en/datasets)


