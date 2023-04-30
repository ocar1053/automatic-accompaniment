from auto_accompany.song_convert import convert_to_midi
import os

# test convert_to_midi


def test_convert_to_midi():
    """
    Tests the convert_to_midi function.
    """
    # generate relative path
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path_vocal = os.path.join(dir_path, 'vocal',
                                   'sarah_and_me_voice.mp3')
    # convert to midi

    # check if file exists
    assert convert_to_midi(file_path_vocal, dir_path)
    # remove file
