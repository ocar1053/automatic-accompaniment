import os
import sounddevice as sd
from scipy.io.wavfile import write
from . import dir_path
# generate relative path

file_path_vocal = os.path.join(dir_path, 'audio\\vocal', 'output.wav')


def record_song(file_path=file_path_vocal) -> None:
    """
    Records a song and saves it as a .wav file.
    :param file_path: the path to save the .wav file
    :return: None
    """
    fs = 44100  # Sample rate
    seconds = 10  # Duration of recording

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)

    sd.wait()  # Wait until recording is finished

    write(file_path, fs, myrecording)  # Save as WAV file
