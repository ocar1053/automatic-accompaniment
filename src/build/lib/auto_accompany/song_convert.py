import os
from basic_pitch.inference import predict


def convert_to_midi(file_path, midi_path):
    """
    Converts a .mp3 or .wav file to a .midi file.
    :param file_path: the path to the .mp3 or .wav file
    :param midi_path: the path to the directory
    :return: None
    """

    model_output, midi_data, note_events = predict(file_path)

    midi_data.write(midi_path)
    print("success")


if __name__ == '__main__':
    convert_to_midi()
