import os
from basic_pitch.inference import predict


# generate relative path
dir_path = os.path.dirname(os.path.abspath(__file__))
file_path_vocal = os.path.join(dir_path, 'audio\\vocal',
                               'sarah_and_me_voice.mp3')
# convert mp3 or wav to midi


def convert_to_midi(file_path=file_path_vocal, dir_path=dir_path):
    """
    Converts a .mp3 or .wav file to a .midi file.
    :param file_path: the path to the .mp3 or .wav file
    :param dir_path: the path to the directory
    :return: None
    """
    # convert to midi
    midi_path = os.path.join(dir_path, 'midi', 'midi_output.mid')

    model_output, midi_data, note_events = predict(file_path)

    midi_data.write(midi_path)


if __name__ == '__main__':
    convert_to_midi()
