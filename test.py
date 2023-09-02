from pathlib import Path
from basic_pitch.inference import predict
from auto_accompany.song_convert import convert_to_midi
from data_process.generatemusic import generate_music
import os
script_directory = Path(__file__).resolve().parent
vocal_file = script_directory / "upload_files" / "input.9.wav"
vocal_midi_output = os.path.join(script_directory, "midi", "wqeqweqwe.mid")
convert_to_midi(vocal_file, vocal_midi_output)


generate_music(vocal_file, vocal_midi_output)
