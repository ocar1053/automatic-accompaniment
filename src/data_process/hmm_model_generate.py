import pandas as pd
from pychord import Chord
from song_analyze import convert_to_note_name, get_beat_info, get_scale_tones_enharmonic_equivalent, predict_key_of_song, split_midi_to_measure
from scipy.special import softmax
from hmmlearn import hmm
import numpy as np


def get_the_chord_list(chord_file: str) -> list:
    """
    the function to get the chord list from the chord dataset

    Args:
        chord_file (str): the chord file name

    Returns:
        the chord list
    """

    chord = pd.read_csv(chord_file)
    chord_list = chord['chord'].unique()
    chord_list.sort()

    # remove the last two chord
    chord_list = list(chord_list[:len(chord_list)-2])

    return chord_list


def trim_the_chord(chord_list: list, adjust_key_tonic_name: list) -> (list, int):
    """
    this stage is to check chord's component is in the scale or not
    if not, remove it

    Args:
        chord_list (list): the chord list
        adjust_key_tonic_name (list): the adjust key tonic name with enharmonic equivalent

    Returns:
        chord_list (list) the trim chord list  
        chord_len (int) the length of chord list  
    """

    for i in chord_list:

        c = Chord(convert_to_note_name(i))

        # if chord's component is not in the scale, add to chord_list
        if c.components() not in adjust_key_tonic_name:
            chord_list.remove(i)

    return chord_list, len(chord_list)


def preprocess_melody_observation_matrix(melody_file: str, chord_list: list) -> pd.DataFrame:
    """
    read the melody_observation_matrix and preprocess for emission probability 
    in hmm model

    Args:
        melody_file (str): the melody observation matrix file name
        chord_list (list): the chord list
    Returns: 
        the melody observation matrix
    """
    # read all_pitch_sorted.csv as dataframe
    df_pitch = pd.read_csv(melody_file)

    # preprocess dataframe
    df_pitch.rename(columns={'Unnamed: 0': 'chord'}, inplace=True)
    # remove row with chord = 'start_chord' ro 'end_chord'

    df_pitch = df_pitch[df_pitch['chord'] != 'start_chord']
    df_pitch = df_pitch[df_pitch['chord'] != 'end_chord']

    # reset index
    df_pitch.reset_index(drop=True, inplace=True)
    # sort by chord column
    df_pitch.sort_values(by=['chord'], inplace=True)

    """Since certain notes are very unlikely to appear when certain
    chords are playing, many combinations of notes and chords
    will have no observed data. We add a few “imaginary”
    instances of every note observed for a short duration over
    every chord"""

    # add 1 to column except 'chord' column
    df_pitch.iloc[:, 1:] = df_pitch.iloc[:, 1:].apply(lambda x: x + 1)

    # remove the row with chord not in chord_list
    df_pitch = df_pitch[df_pitch['chord'].isin(chord_list)]

    return df_pitch


def caculate_emission_probability(split_notes_list: list, df_pitch: pd.DataFrame) -> list:
    """
    the function to caculate the emission probability

    Args:
        split_notes_list (list): the list of notes already split 
        by the measure

    Returns:
        emission matrix probability as loglikelihood_list

    """

    pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # create 12 dim vector for each measure
    measure_list_vector = []
    loglikelihood_list = []
    for measure in split_notes_list:
        temp_list = []
        for pitch in pitch_names:
            temp_list.append(measure.count(pitch)/len(measure) + 1e-10)
        measure_list_vector.append(temp_list)

    """
    taking the dot product of the
    observation vector x with the log of the appropriate row of
    the melody observation matrix; this yields the loglikelihood for this chord. For each measure in the recorded
    voice track, MySong stores a list containing all 60 of these
    observation probabilities. 
    """

    for measure_vector in measure_list_vector:
        temp_list = []

        for i in range(len(df_pitch)):
            temp_list.append(np.dot(measure_vector, np.log2(df_pitch.iloc[i, 1:].to_numpy().astype(float))))
        loglikelihood_list.append(temp_list)

    return loglikelihood_list


def generate_emission_matrix(loglikelihood_list: list) -> np.array:
    """
    the function to generate the emission matrix

    emission matrix sample
    [
        [0.7, 0.3]
        [0.2, 0.8]
    ]

    matrix[0][0] stands for the probability about if chord is a, the probability of 
    measure is 1 is 0.7, measure is 2 is 0.2
    Args:
        loglikelihood_list (list): the list of loglikelihood

    Returns:
        the emission matrix
    """

    loglikelihood_list_matrix = np.array(loglikelihood_list)

    emission_matrix = loglikelihood_list_matrix.transpose()

    # normalize emission matrix each row to 1 ues softmax

    for i in range(len(emission_matrix)):
        emission_matrix[i] = softmax(emission_matrix[i])

    # convert nan to 0
    emission_matrix = np.nan_to_num(emission_matrix)

    # convert emission matrix to numpy array
    emission_matrix = np.array(emission_matrix)

    return emission_matrix


def generate_transition_matrix(transition__chord_matrix_file: str, chord_list: list) -> np.array:
    """
    the function to generate the transition matrix

    Args:
        transition__chord_matrix_file (str): the transition chord matrix file name
        chord_list (list): the trimmed chord list
    Returns:
        the transition matrix
    """

    transition_matrix = pd.read_csv(transition__chord_matrix_file)
    # preprocess dataframe
    transition_matrix.rename(columns={'Unnamed: 0': 'chord'}, inplace=True)
    # remove the row with chord not in chord_list
    transition_matrix = transition_matrix[transition_matrix['chord'].isin(chord_list)]
    # remove the column's name not in chord_list but remain the column "chord"
    transition_matrix = transition_matrix[transition_matrix.columns.intersection(chord_list)]

    # remove the % in each element
    transition_matrix = transition_matrix.apply(lambda x: x.str.replace('%', ''))

    # convert to numpy array
    transition_matrix = np.array(transition_matrix)

    # normalize transition matrix each row to 1
    for i in range(len(transition_matrix)):
        transition_matrix[i] = transition_matrix[i].astype(float)
        transition_matrix[i] = transition_matrix[i]/sum(transition_matrix[i])

    # change dtype to float
    transition_matrix = transition_matrix.astype(float)

    return transition_matrix


def ensemble_hmm_model(transition_matrix: np.array, emission_matrix: np.array, chord_list: list) -> hmm.CategoricalHMM:
    """
    the function to ensemble the hmm model

    Args:
        transition_matrix (np.array): the transition matrix
        emission_matrix (np.array): the emission matrix
        chord_list (list): the trimmed chord list
        measure_list_vector (list): the list of measure vector
    Returns:
        the ensembled hmm model
    """

    states = chord_list
    n_states = len(states)

    # observation that is note vector

    start_probability = np.full(n_states, 1/n_states)
    transition_probability = transition_matrix
    emission_probability = emission_matrix

    model = hmm.CategoricalHMM(n_components=n_states, verbose=True, n_iter=1000)
    model.startprob_ = start_probability
    model.transmat_ = transition_probability
    model.emissionprob_ = emission_probability

    return model


def hmm_pipeline() -> (hmm.CategoricalHMM, float, float, list, list):
    """
    the pipeline to generate the hmm model

    Returns:
        model(hmm.CategoricalHMM) the ensembled hmm model
        vocal_tempo(float) the vocal tempo
        start_time(float) the start time of the vocal time
        chord_list(list) the trimmed chord list
        split_notes_list(list) the list of notes already split by the measure
    """

    transition__chord_matrix_file = "C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\data_process\\transition__chord_matrix\\csv_file\\transition_chord.csv"
    melody_observation_matrix_file = 'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\data_process\\melody observation matrix\\csv_file\\all_pitch.csv'
    original_chord_list = get_the_chord_list(
        'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\data_process\\transition__chord_matrix\\csv_file\\all_chord.csv')
    vocal_file = 'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\auto_accompany\\audio\\vocal\\input.9.mp3'
    vocal_midi_file = 'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\auto_accompany\\midi\\midi_output_voice.mid'

    # 1. get the vocal tempo, time section, start time
    vocal_tempo, time_section, the_start_time = get_beat_info(vocal_file)

    # 2. split the vocal melody to measure
    split_notes_list = split_midi_to_measure(vocal_midi_file, time_section)

    # 3. get enharmonic scale
    enharmonic_scale_tonic_name = get_scale_tones_enharmonic_equivalent(vocal_midi_file)

    # 4. get the trimmed chord list
    chord_list, chord_len = trim_the_chord(original_chord_list, enharmonic_scale_tonic_name)

    # 5. get the melody observation matrix
    df_pitch = preprocess_melody_observation_matrix(melody_observation_matrix_file, chord_list)

    # 6. caculate the emission probability
    loglikelihood_list = caculate_emission_probability(split_notes_list, df_pitch)

    # 7. generate the emission matrix
    emission_matrix = generate_emission_matrix(loglikelihood_list)

    # 8. generate the transition matrix
    transition_matrix = generate_transition_matrix(transition__chord_matrix_file, chord_list)

    # 9. ensemble the hmm model
    model = ensemble_hmm_model(transition_matrix, emission_matrix, chord_list)

    return model, vocal_tempo, the_start_time, chord_list, split_notes_list
