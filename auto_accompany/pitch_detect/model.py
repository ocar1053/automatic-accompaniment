import os
import pretty_midi
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

# generate relative path
dir_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(dir_path, '..\\audio\\vocal',
                         'sarah_and_me_voice.mp3')
midi_path = os.path.join(dir_path, 'midi_output.mid')

model_output, midi_data, note_events = predict(file_path)

midi_data.write(midi_path)
