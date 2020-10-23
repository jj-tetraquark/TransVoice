import os
import numpy as np
import matplotlib.pyplot as plt
import pickle as pkl


def pitch_analysis(pitches):
    pitches = [p for p in pitches if not np.isnan(p)]
    return np.mean(pitches), np.std(pitches)


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def extract_column(column_name, data):
    headings = data[0]
    column = data[1:, np.where(headings == column_name)].flatten()
    dtype = np.float if is_number(column[0]) else np.str
    try:
        return column.astype(dtype)
    except ValueError:
        column[np.where(column == '')] = 'NaN'
        return column.astype(dtype)


def extract_columns_all_phonemes(column_name, data_by_phoneme):
    return np.array([x for phoneme in data_by_phoneme.values()
                     for x in extract_column(column_name, phoneme)])


def split_data_by_phoneme(data):
    phonemes = extract_column('phoneme', data)
    return {phoneme: np.vstack([data[0], data[1:][phonemes == phoneme, :]])
            for phoneme in set(phonemes)}


def load_from_pkl_if_exists_else_csv(pkl_file, csv_file):
    if os.path.exists(pkl_file):
        print("Loading from {}".format(pkl_file))
        try:
            with open(pkl_file, 'rb') as f:
                data_by_phoneme = pkl.load(f)
                return data_by_phoneme
        except:
            print("Couldn't load from {}".format(pkl_file))

    print("Loading from {}".format(csv_file))
    data = np.genfromtxt(csv_file, delimiter=',', dtype='str')
    data = np.char.strip(data, ' ')
    data_by_phoneme = split_data_by_phoneme(data)

    with open(pkl_file, 'wb') as f:
        pkl.dump(data_by_phoneme, f)

    return data_by_phoneme



def load_data():
    male_data_by_phoneme = load_from_pkl_if_exists_else_csv(
                                'male_data_by_phoneme.pkl',
                                'male_data.csv')

    female_data_by_phoneme = load_from_pkl_if_exists_else_csv(
                                'female_data_by_phoneme.pkl',
                                'female_data.csv')

    return male_data_by_phoneme, female_data_by_phoneme


if __name__ == '__main__':
    print("Loading...")
    male_data_by_phoneme, female_data_by_phoneme = load_data()

    fig, ax = plt.subplots(1, 2)

    ax[0].set_title('Female')
    ax[0].set_xlabel('F2')
    ax[0].set_ylabel('F1')
    ax[0].set_ylim(1500, 0)
    ax[0].set_xlim(4000, 300)

    ax[1].set_title('Male')
    ax[1].set_xlabel('F2')
    ax[1].set_ylabel('F1')
    ax[1].set_ylim(1500, 0)
    ax[1].set_xlim(4000, 300)

    female_median = [[], []]
    male_median = [[], []]

    for phoneme, phoneme_data_female in female_data_by_phoneme.items():
        phoneme_data_male = male_data_by_phoneme[phoneme]

        female_f1 = extract_column('f1', phoneme_data_female)
        female_f2 = extract_column('f2', phoneme_data_female)

        male_f1 = extract_column('f1', phoneme_data_male)
        male_f2 = extract_column('f2', phoneme_data_male)

        ax[0].scatter(female_f2, female_f1, s=0.05, label=phoneme)
        ax[1].scatter(male_f2, male_f1, s=0.05, label=phoneme)

        female_median_f1 = np.median(female_f1)
        female_median_f2 = np.median(female_f2)
        print("{} Female median F1:{} F2:{}".format(phoneme, female_median_f1, female_median_f2))

        female_median[0].append(female_median_f1)
        female_median[1].append(female_median_f2)

        male_median_f1 = np.median(male_f1)
        male_median_f2 = np.median(male_f2)
        print("{} Male median F1:{} F2:{}".format(phoneme, male_median_f1, male_median_f2))

        male_median[0].append(male_median_f1)
        male_median[1].append(male_median_f2)


    print(female_median)

    print(male_median)

    ax[0].scatter(female_median[1], female_median[0])
    ax[1].scatter(male_median[1], male_median[0])

    ax[0].legend(loc='best', markerscale=20)
    ax[1].legend(loc='best', markerscale=20)
    plt.show()
