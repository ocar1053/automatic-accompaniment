import pandas as pd
import pretty_midi
import os
from pathlib import Path
# relative path
relative_path = os.path.dirname(os.path.realpath(__file__))


def midi_note_to_pitch(midi_note) -> str:
    """
    Convert midi note to pitch
    param midi_note: int
    return: str
    """

    # Equal temperament
    pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note - 12) // 12 + 1
    pitch_class = midi_note % 12
    pitch_name = pitch_names[pitch_class]
    return f'{pitch_name}'


def get_midi_file(relative_path) -> list:
    """
    get the midi file path list
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

        chord_file = os.path.join(parent_path, 'POP909', file, file + '.mid')
        chord_file_list.append(chord_file)

    return chord_file_list


def data_preprocess(midi_data) -> pd.DataFrame:
    """
    Get melody dataframe from midi file
    param mid: MidiFile
    return: pd.DataFrame
    """

    # note event
    midi_data.instruments[0].notes

    # convert to pd
    melody = []

    for note in midi_data.instruments[0].notes:
        if note.velocity != 0:
            melody.append([float(note.start), midi_note_to_pitch(note.pitch)])
    melody_df = pd.DataFrame(melody, columns=['start', 'note'])

    return melody_df


def merge_all_df(file_list) -> pd.DataFrame:
    """
    merge all midi_df
    :param file_list: the midi file list
    :return all_df 
    """

    all_df = pd.DataFrame()

    for index, file in enumerate(file_list):

        mid = pretty_midi.PrettyMIDI(file)

        midi_df = data_preprocess(mid)

        midi_df['song_num'] = index
        all_df = pd.concat([all_df, midi_df])

    return all_df


def pipeline() -> pd.DataFrame:
    """
    pipeline
    """
    midi_file_list = get_midi_file(relative_path)
    all_df = merge_all_df(midi_file_list)

    all_df.to_csv('all_melody_df.csv', index=True, header=True)


if __name__ == "__main__":
    pipeline()
