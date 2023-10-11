import pandas as pd
import numpy as np
import os
from pathlib import Path
# relative path
relative_path = os.path.dirname(os.path.realpath(__file__))


def get_chord_file(relative_path) -> list:
    print(relative_path)
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

        chord_file = os.path.join(
            parent_path, 'POP909', file, 'chord_midi.txt')
        chord_file_list.append(chord_file)

    return chord_file_list


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

    transitions = pd.DataFrame(np.zeros(
        (len(chord_list), len(chord_list))), index=chord_list, columns=chord_list)

    # create transition matrix
    for i in range(len(all_df)-1):
        scale_value = all_df['song_num'].iloc[i]
        transitions.loc[all_df['chord'].iloc[i], all_df['chord'].iloc[i+1]
                        ] += 1/chord_amount_each_song[scale_value]

    transitions = transitions.apply(lambda x: x/x.sum(), axis=1)

    transitions = transitions.applymap(lambda x: '{:.2%}'.format(x))

    # save as csv
    file_path = os.path.join(
        relative_path, 'csv_file\\transition_chord_normalize_each_time.csv')
    transitions.to_csv(file_path, index=True, header=True)

    return transitions


def get_transition_chord(all_df) -> pd.DataFrame:
    """
    get the transition chord
    :param all_df: the all_df
    :return: transitions
    """

    chord_list = all_df['chord'].unique()
    chord_list.sort()

    transitions = pd.DataFrame(np.zeros(
        (len(chord_list), len(chord_list))), index=chord_list, columns=chord_list)

    # get the transition matrix
    for i in range(len(all_df)-1):
        transitions.loc[all_df['chord'].iloc[i],
                        all_df['chord'].iloc[i+1]] += 1

    transitions = transitions.drop(['start_chord', 'end_chord'], axis=0)
    transitions = transitions.drop(['start_chord', 'end_chord'], axis=1)

    transitions = transitions.apply(lambda x: x/x.sum(), axis=1)

    transitions = transitions.applymap(lambda x: '{:.2%}'.format(x))

    file_path = os.path.join(relative_path, 'csv_file\\transition_chord.csv')
    # save as csv
    transitions.to_csv(file_path, index=True, header=True)
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
