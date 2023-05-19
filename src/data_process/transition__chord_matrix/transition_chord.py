import pandas as pd
import numpy as np
import os
from pathlib import Path
# relative path
relative_path = os.path.dirname(os.path.realpath(__file__))


def get_chord_file(relative_path) -> list:
    """
    get the chord file path list
    :param relative: the relative path
    :return: chord_file_list
    """

    chord_file_list = []

    # get the file in the upper folder POP909
    parent_path = Path(relative_path).parent
    file_list = os.listdir(os.path.join(parent_path, 'POP909'))

    # remove file that fileName is not number
    for file in file_list:
        if not file.isdigit():
            file_list.remove(file)

    for file in file_list:

        chord_file = os.path.join(parent_path, 'POP909', file, 'chord_midi.txt')
        chord_file_list.append(chord_file)

    return chord_file_list


def data_preprocess(chord_df) -> pd.DataFrame:
    """
    data preprocess to remove empty chord and add start_chord and end_chord
    :param chord_df: the chord DataFrame
    :return: chord_df
    """

    # remove the empty chord
    chord_df = chord_df[chord_df['chord'] != 'N']

    start_chord = pd.Series({'start_time': 0, 'end_time': chord_df['start_time'].iloc[0], 'chord': 'start_chord'})
    end_chord = pd.Series({'start_time': chord_df['end_time'].iloc[-1], 'end_time': chord_df['end_time'].iloc[-1]+1, 'chord': 'end_chord'})

    chord_df = pd.concat([pd.DataFrame(start_chord).T, chord_df], ignore_index=True)

    chord_df = pd.concat([chord_df, pd.DataFrame(end_chord).T], ignore_index=True)

    # simplfy the chord by change remove chord after '/' and remove chord after '(')
    chord_df['chord'] = chord_df['chord'].apply(lambda x: x.split('/')[0])
    chord_df['chord'] = chord_df['chord'].apply(lambda x: x.split('(')[0])
    return chord_df


def merge_all_df(file_list) -> pd.DataFrame:
    """
    merge all chord_df
    :param file_list: the chord file list
    :return: all_df
    """

    all_df = pd.DataFrame()

    for index, file in enumerate(file_list):

        chord_df = pd.read_csv(file, sep='\t', header=None, names=['start_time', 'end_time', 'chord'])

        chord_df = data_preprocess(chord_df)
        chord_df['song_num'] = index

        all_df = pd.concat([all_df, chord_df])

    all_df.to_csv('all_chord.csv', index=True, header=True)
    return all_df


def get_transition_chord_normalize_each_time(all_df) -> pd.DataFrame:
    """
    get the transition chord but normalize_each_time
    :param all_df: pd.dataframe
    :return: transitions matirx
    """

    # get row  chord == 'end_chord'
    end_time_list = all_df[all_df['chord'] == 'end_chord']['end_time'].tolist()

    # calculate the how many chord in each song_num
    chord_amount_each_song = all_df.groupby('song_num')
    chord_amount_each_song = chord_amount_each_song.size().tolist()

    chord_list = all_df['chord'].unique()
    chord_list.sort()

    transitions = pd.DataFrame(np.zeros((len(chord_list), len(chord_list))), index=chord_list, columns=chord_list)

    # create transition matrix
    for i in range(len(all_df)-1):
        scale_value = all_df['song_num'].iloc[i]
        transitions.loc[all_df['chord'].iloc[i], all_df['chord'].iloc[i+1]] += 1/chord_amount_each_song[scale_value]

    transitions = transitions.apply(lambda x: x/x.sum(), axis=1)

    transitions = transitions.applymap(lambda x: '{:.2%}'.format(x))

    # save as csv
    transitions.to_csv('transition_chord_normalize_each_time.csv', index=True, header=True)

    return transitions


def get_transition_chord(all_df) -> pd.DataFrame:
    """
    get the transition chord
    :param all_df: the all_df
    :return: transitions
    """

    chord_list = all_df['chord'].unique()
    chord_list.sort()

    transitions = pd.DataFrame(np.zeros((len(chord_list), len(chord_list))), index=chord_list, columns=chord_list)

    # get the transition matrix
    for i in range(len(all_df)-1):
        transitions.loc[all_df['chord'].iloc[i], all_df['chord'].iloc[i+1]] += 1

    transitions = transitions.drop(['start_chord', 'end_chord'], axis=0)
    transitions = transitions.drop(['start_chord', 'end_chord'], axis=1)

    transitions = transitions.apply(lambda x: x/x.sum(), axis=1)

    transitions = transitions.applymap(lambda x: '{:.2%}'.format(x))

    # save as csv
    transitions.to_csv('transition_chord.csv', index=True, header=True)
    return transitions


def pipeline() -> pd.DataFrame:
    """
    pipeline process
    :return: chord_transition_matrix
    """

    chord_file_list = get_chord_file(relative_path)
    all_df = merge_all_df(chord_file_list)
    get_transition_chord_normalize_each_time(all_df)
    return get_transition_chord(all_df)


if __name__ == "__main__":
    chord_transition_matrix = pipeline()
