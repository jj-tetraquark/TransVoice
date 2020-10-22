import textgrids

ARPAbet_vowels = [
    'AA',
    'AE',
    'AH',
    'AO',
    'AW',
    'AY',
    'EH',
    'ER',
    'EY',
    'IH',
    'IY',
    'OW',
    'OY',
    'UH',
    'UW'
]


def get_vowel_intervals(textgrid_file):
    grid = textgrids.TextGrid(textgrid_file)
    vowels = [p for p in grid['phones'] if p.text.rstrip('0123') in ARPAbet_vowels]
    return vowels
