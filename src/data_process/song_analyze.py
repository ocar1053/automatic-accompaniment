import librosa
import pretty_midi
from music21 import converter, pitch, scale
from pychord import Chord


def midi_note_to_pitch(midi_note: int) -> str:
    """
    Convert a MIDI note number to a musical note in the equal temperament system.

    Args:
        midi_note (int): The MIDI note number to be converted. Should be an integer from 0 to 127.

    Returns:
        A string representing the musical note corresponding to the input MIDI note. 
             For example, a midi_note of 69 returns 'A'.
    """

    # Equal temperament
    pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    pitch_class = midi_note % 12
    pitch_name = pitch_names[pitch_class]
    return f'{pitch_name}'


def get_beat_info(mp3Filanme: str) -> (float, list, float):
    """
    the function to get beat info: including tempo, time_section, start_time

    Args:
        mp3Filanme (str): the mp3 file name

    Returns:
        tempo (float): the tempo of the mp3
        time_section (list): the time section of the mp3
        start_time (float): the start time of the mp3
    """

    # Load the audio as a waveform `y`
    # Store the sampling rate as `sr`
    y, sr = librosa.load(mp3Filanme)

    # Run the default beat tracker
    vocal_tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # Convert the frame indices of beat events into timestamps
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # get A  element index multiple of 4 from 0 aka 4/4
    down_beat = beat_times[0::4]

    the_start_time = down_beat[0]

    # convert to time section group by 2 and the last elemnt cotinue to end
    time_section = []
    for i in range(0, len(down_beat)-1):
        time_section.append([down_beat[i], down_beat[i+1]])
    time_section.append([down_beat[-1], librosa.get_duration(y=y, sr=sr)])

    return vocal_tempo, time_section, the_start_time


def split_midi_to_measure(midi_file: str, time_section: list) -> list:
    """
    the function to split midi song into list of measure

    Args:
        midi_file (str): the midi file name
        time_section (list): the time section of the midi
    Returns:
        the list of note split by measure    
    """

    midi_data = pretty_midi.PrettyMIDI(midi_file)

    measure_list = []

    # accroding to time section to find the note events
    for i in range(0, len(time_section)):
        measure = []
        for note in midi_data.instruments[0].notes:
            if note.start >= time_section[i][0] and note.start < time_section[i][1]:
                measure.append(midi_note_to_pitch(note.pitch))
        measure_list.append(measure)

    return measure_list


def predict_key_of_song(midi_file: str) -> str:
    """
    the function to predict the key of the song

    Args:
        midi_file (str): the midi file name

    Returns:
        the key of the song
    """

    quality = ""

    # get the key of the song
    score = converter.parse(midi_file)
    key = score.analyze('key')

    # replace - with b, doing preprocessing for key signature
    adjust_key_tonic_name = key.tonic.name.replace('-', 'b')
    if key.mode == 'major':
        quality = 'maj'
    if key.mode == 'minor':
        quality = 'min'

    key_signature = adjust_key_tonic_name + ":" + quality

    return key_signature


def get_scale_tones(key: str, scale_type: str) -> list:
    """
    the function to get the scale tones of the key

    Args:
        key (str): the key of the song
        scale_type (str): the type of the scale

    Returns:
        the list containing the scale tones of the key    
    """
    tonic = key.upper()
    tonic_pitch = pitch.Pitch(tonic)

    if scale_type.lower() == 'major':
        scales = scale.MajorScale(tonic_pitch)
    elif scale_type.lower() == 'minor':
        scales = scale.MinorScale(tonic_pitch)
    else:
        raise ValueError('Invalid scale type')

    return scales.getPitches()


def get_scale_tones_enharmonic_equivalent(midi_file: str) -> list:
    """
    the function to get the  enharmonic scale tones of the key


    Args:
        midi_file (str): the midi file name

    Returns:
        the list containing the scale tones of the key    
    """

    # enharmonic equivalent dictionary
    enharmonic_equivalent = {'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb', 'F': 'E#',
                             'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#', 'E#': 'F'}

    score = converter.parse(midi_file)
    key = score.analyze('key')
    adjust_key_tonic_name = []

    # first get the orginal scale tones of the key
    scale_tones = get_scale_tones(key.tonic.name, key.mode)

    for pitch in scale_tones:
        # if pitch has - , replace it with b
        pitch = pitch.name.replace('-', 'b')
        # remove int
        pitch = pitch.replace('1', '')
        adjust_key_tonic_name.append(pitch)

    # Get the enharmonic equivalent, if yes append to the list
    for i in range(len(adjust_key_tonic_name)):
        if adjust_key_tonic_name[i] in enharmonic_equivalent:
            adjust_key_tonic_name.append(enharmonic_equivalent[adjust_key_tonic_name[i]])

    return adjust_key_tonic_name


def convert_to_note_name(chord_str) -> str:
    """
    the function to convert the chord name to adjust chord name

    Args:
        chord_str (str): the chord name

    Returns:
        the adjust chord name    
    """
    chord_parts = chord_str.split(':')
    chord_name = chord_parts[0]
    chord_type = chord_parts[1]

    if 'min' in chord_type:
        # replace min with m
        chord_type = chord_type.replace('min', 'm')

    # if last character is 6
    if chord_type[-1] == '6':
        chord_type = chord_type.replace('6', '')
    # if last character is not num
    if chord_type[-1].isdigit() == False:
        if "maj" in chord_type:
            chord_type = chord_type.replace('maj', '')
    return chord_name + chord_type


def get_each_chord_componetns(chord_sequence: list) -> list:
    """
    The function to get the chord components of each chord

    Args:
        chord_sequence (list): the list of chord sequence

    Returns:
        the list of chord components    

        Example:[['Bb', 'D', 'F'],
                ['Eb', 'G', 'Bb'],
                ['F', 'A', 'C'],
                ['Bb', 'D', 'F'],
                ['Eb', 'G', 'Bb'],
                ['Ab', 'C', 'Eb'],
                ['C#', 'E', 'G#'],
                ['F#', 'A', 'C#']]
    """

    chord_each_component = []
    for i in chord_sequence:

        c = Chord(convert_to_note_name(i))

        chord_each_component.append(c.components())

    return chord_each_component
