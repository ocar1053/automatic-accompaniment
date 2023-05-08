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
    # create a list to store the file name
    chord_file_list = []

    # get the file in the upper folder POP909
    parent_path = Path(relative_path).parent
    file_list = os.listdir(os.path.join(parent_path, 'POP909'))

    # remove file that fileName is not number
    for file in file_list:
        if not file.isdigit():
            file_list.remove(file)

    file_list.pop()

    for file in file_list:

        # get the chord file path
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

    # create 'start_chord' and 'end_chord'
    start_chord = pd.Series({'start_time': 0, 'end_time': chord_df['start_time'].iloc[0], 'chord': 'start_chord'})
    end_chord = pd.Series({'start_time': chord_df['end_time'].iloc[-1], 'end_time': chord_df['end_time'].iloc[-1]+1, 'chord': 'end_chord'})

    # add 'start_chord' to the DataFrame first row
    chord_df = pd.concat([pd.DataFrame(start_chord).T, chord_df], ignore_index=True)

    # add 'end_chord' to the DataFrame last row
    chord_df = pd.concat([chord_df, pd.DataFrame(end_chord).T], ignore_index=True)

    return chord_df


def merge_all_df(file_list) -> pd.DataFrame:
    """
    merge all chord_df
    :param file_list: the chord file list
    :return: all_df
    """

    # create a empty DataFrame to store all chord_df
    all_df = pd.DataFrame()

    for file in file_list:
        # read the chord file
        chord_df = pd.read_csv(file, sep='\t', header=None, names=['start_time', 'end_time', 'chord'])
        # data preprocess
        chord_df = data_preprocess(chord_df)
        # merge  chord_df
        all_df = pd.concat([all_df, chord_df])

    return all_df


def get_transition_chord(all_df) -> pd.DataFrame:
    """
    get the transition chord
    :param all_df: the all_df
    :return: transitions
    """

    all_df["chord"] = pd.Categorical(all_df["chord"])

    # generate the transition matrix
    transitions = pd.crosstab(all_df["chord"], all_df["chord"].shift(-1), normalize="index")
    transitions = transitions.fillna(0)

    # convert value to %
    transitions = transitions.applymap(lambda x: '{:.2%}'.format(x))

    return transitions


def pipeline() -> pd.DataFrame:
    """
    pipeline process
    :return: chord_transition_matrix
    """

    chord_file_list = get_chord_file(relative_path)
    all_df = merge_all_df(chord_file_list)
    return get_transition_chord(all_df)


if __name__ == "__main__":
    chord_transition_matrix = pipeline()
    chord_transition_matrix.to_csv('transition_chord.csv', index=True, header=True)
