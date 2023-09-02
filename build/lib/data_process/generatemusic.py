from hmmlearn import hmm
import numpy as np
from data_process.hmm_model_generate import hmm_pipeline
from music21 import *
from midi2audio import FluidSynth
from data_process.song_analyze import get_each_chord_componetns
from pydub import AudioSegment


class ChordGenerator:
    """
    The Class to generate the chord sequence

    Attributes:
        model (hmm.CategoricalHMM): the hmm model
        measure_list_vector (list): the list of measure vector
        chord_list (list): the trimmed chord list

    Methods:
        generate: generate the chord sequence        


    Examples usage:
        insatnce = ChordGenerator(model, measure_list_vector, chord_list)
        chord_progression =  insatnce.generate()
    """

    def __init__(self, model, measure_list_vector, chord_list):
        """
        Args:
            model (hmm.CategoricalHMM): The HMM model.
            measure_list_vector (list): The list of measure vector.
            chord_list (list): The trimmed chord list.
        """
        self.model = model
        self.measure_list_vector = measure_list_vector
        self.chord_list = chord_list

    def generate(self) -> list:
        """
        Generate the chord sequenc according to the measure list vector

        Returns: chord_progression (list): the chord sequence

        """
        observations_variable = self.measure_list_vector

        # given the observation, predict the state

        user_sing_action = np.array(
            [[i for i in range(len(observations_variable))]])
        logprob, chord_sequence = self.model.decode(
            user_sing_action.transpose(), algorithm="viterbi")

        print("logprob", logprob)
        print("chord_sequence", chord_sequence)

        # convert chord_sequence to chord name
        chord_sequence_name = []
        for i in chord_sequence:
            chord_sequence_name.append(self.chord_list[i])

        return chord_sequence_name


class Accompaniment:
    """
    A class to represent a musical accompaniment. 

    Attributes:
        instrument (str): The instrument for the accompaniment. 

        bpm (float): The beats per minute of the accompaniment.
        main_stream (stream.Stream): The music21 stream object for the accompaniment. 

    Methods:
        generate(chords): Generate the accompaniment given the chords.
    """

    def __init__(self, bpm, chord_sequence=None):
        """
        Constructs all the necessary attributes for the accompaniment object.

        Args:
            instrument (str): The instrument for the accompaniment.
            bpm (float): The beats per minute of the accompaniment.
            main_stream (stream.Stream): The music21 stream object for the accompaniment. 
        """

        self.bpm = bpm
        self.main_stream = stream.Stream()
        self.chord_sequence = chord_sequence

    def generate(self, chords):
        pass


class PianoAccompanimentMode1(Accompaniment):
    """
    A class to represent a piano accompaniment in mode 1.

    This class inherits from the Accompaniment class and overrides its methods 
    to provide functionality specific to a piano accompaniment in mode 1.

    Attributes:
        bpm (float): The beats per minute of the accompaniment.
        chord_sequence (list): The chord sequence for the accompaniment.
    Methods:
        generate(chords): Generate the piano accompaniment in mode 1 given the chords.
    """

    def __init__(self, bpm, chord_sequence):
        """
        Constructs all the necessary attributes for the piano accompaniment in mode 1 object.

        Args:
            bpm (float): The beats per minute of the accompaniment.
            chord_sequence (list): The chord sequence for the accompaniment.
        """

        super().__init__(bpm, chord_sequence)

        self.left_hand = stream.Part()
        self.right_hand = stream.Part()
        self.left_hand.insert(0, instrument.Piano())
        self.right_hand.insert(0, instrument.Piano())
        self.chord_sequence = get_each_chord_componetns(chord_sequence)

    def generate(self):
        """
        Generate the piano accompaniment in mode 1 given the chords.

        Returns:
            main_stream (stream.Stream): The music21 stream object for the piano accompaniment in mode 1.
        """

        for chord_notes in self.chord_sequence:
            root_note_str = chord_notes[0]
            third_note_str = chord_notes[1]
            fifth_note_str = chord_notes[2]

            # left hand

            root_note = note.Note(root_note_str+'3')
            root_note.duration.type = 'whole'

            self.left_hand.append(root_note)

            # right hand
            for i in range(4):

                right_notes = chord.Chord(
                    [root_note_str+'4', third_note_str+'4', fifth_note_str+'4'])
                right_notes.duration.type = 'quarter'

                self.right_hand.append(right_notes)

        self.main_stream.insert(0, self.left_hand)
        self.main_stream.insert(0, self.right_hand)
        self.main_stream.insert(0, tempo.MetronomeMark(int(self.bpm)))

        return self.main_stream


class PianoAccompanimentMode2(Accompaniment):
    def __init__(self, bpm, chord_sequence):
        """
        Constructs all the necessary attributes for the piano accompaniment in mode 1 object.

        Args:
            bpm (float): The beats per minute of the accompaniment.
            chord_sequence (list): The chord sequence for the accompaniment.
        """

        super().__init__(bpm, chord_sequence)

        self.left_hand = stream.Part()
        self.right_hand = stream.Part()
        self.left_hand.insert(0, instrument.Piano())
        self.right_hand.insert(0, instrument.Piano())
        self.chord_sequence = get_each_chord_componetns(chord_sequence)

    def generate(self):

        for chord_notes in self.chord_sequence:
            root_note_str = chord_notes[0]
            third_note_str = chord_notes[1]
            fifth_note_str = chord_notes[2]

            # left hand

            root_note = note.Note(root_note_str+'3')
            root_note.duration.type = 'whole'

            self.left_hand.append(root_note)

            # right hand
            for i in range(4):
                if i % 2 == 0:
                    right_notes = chord.Chord(
                        [third_note_str+'4', fifth_note_str+'4'])
                    right_notes.duration.type = 'quarter'
                    self.right_hand.append(right_notes)
                else:
                    r_note = note.Note(root_note_str+'4')
                    r_note.duration.type = 'quarter'

                    self.right_hand.append(r_note)

        self.main_stream.insert(0, self.left_hand)
        self.main_stream.insert(0, self.right_hand)
        self.main_stream.insert(0, tempo.MetronomeMark(int(self.bpm)))

        return self.main_stream


class DrumAccompanimentMode1(Accompaniment):

    """
    A class to represent a drum accompaniment in mode 1.
    This class inherits from the Accompaniment class and overrides its methods 
    to provide functionality specific to a drum accompaniment in mode 1.

    Attributes:
        bpm (float): The beats per minute of the accompaniment.

    Methods:
        generate(chords): Generate the drum accompaniment in mode 1 given the chords.

    """

    def __init__(self, bpm, chord_sequence):
        """
        Constructs all the necessary attributes for the drum accompaniment in mode 1 object.

        Args:
            bpm(float): The beats per minute of the accompaniment.
        """
        super().__init__(bpm, chord_sequence)
        self.main_stream = stream.Stream()
        self.num_measures = len(chord_sequence)
        self.bpm = bpm

    def generate(self):
        """
        Generate the drum accompaniment in mode 1 given the chords.

        Returns:
            main_stream (stream.Stream): The music21 stream object for the drum accompaniment in mode 1.
        """
        pattern = [
            (36, 36),  # Bass Drum + Closed Hi-hat
            (38, 42),  # Snare Drum + Closed Hi-hat
            (36, 36),  # Bass Drum + Closed Hi-hat
            (38, 42)   # Snare Drum + Closed Hi-hat
        ]

        # Create the drum track
        for _ in range(self.num_measures):
            for p in pattern:
                for midi_pitch in p:
                    n = note.Note()
                    n.pitch.midi = midi_pitch
                    n.duration = duration.Duration(1/2)
                    self.main_stream.append(n)
        self.main_stream.insert(0, tempo.MetronomeMark(int(self.bpm)))
        return self.main_stream


class DrumAccompanimentMode2(Accompaniment):
    def __init__(self):

        pass

    def generate(self, chords):
        # 用特定于鼓和模式2的方式生成伴奏
        pass


class MIDIFile:

    """
    The class to write a MIDI file.

    Attributes:
        filename (str): The filename of the MIDI file.
        main_stream (stream.Stream): The music21 stream object for the accompaniment.
    """

    def __init__(self, filename, main_stream):
        """
        Constructs all the necessary attributes for the MIDI file object.

        Args:
            filename (str): The filename of the MIDI file.
        """
        self.filename = filename
        self.main_stream = main_stream

    def write(self):
        """
        The fucntion to Write the MIDI file.

        Returns: 
            None
        """

        self.main_stream.write('midi', fp=self.filename)
        print("MIDI file generated successfully!")
        return None


class WAVFile:

    """
    The class to convert a midi file to a WAV file.

    Attributes:
        SoundFont (str): The SoundFont file.
        filename_midi (str): The filename of the midi file.
        filename_wav (str): The filename of the WAV file.

    """

    def __init__(self,  SoundFont, filename_midi, filename_wav):
        """
        Constructs all the necessary attributes for the WAV file object.
        """
        self.SoundFont = SoundFont
        self.filename_midi = filename_midi
        self.filename_wav = filename_wav

    def convert_and_write(self):
        """
        The fucntion to convert a midi file to a WAV file.

        Returns:
            None
        """

        fs = FluidSynth(self.SoundFont)
        fs.midi_to_audio(self.filename_midi, self.filename_wav)
        print("WAV file generated successfully!")

        return None


class Mixer:
    """
    The class to mix the vocal, piano and drum.

    Please mix the instruments fist, then mix instruments with vocal.

    Attributes:

        voice (str): AudioSegmente of the vocal file.
        piano (str): AudioSegment of the piano file.
        drum (str): AudioSegment of the drum file.
        min_length (float): The minimum length of the three files.

    """

    def __init__(self, vocal_file, piano_file, drum_file, vocal_start_time_in_ms):
        """
        Constructs all the necessary attributes for the mixer object.

        Args:
            vocal_file (str): The filename of the vocal file.
            piano_file (str): The filename of the piano file.
            drum_file (str): The filename of the drum file.
            vocal_start_time_in_ms (float): The start time of the vocal file in ms.

        """

        self.voice = AudioSegment.from_mp3(
            vocal_file)[vocal_start_time_in_ms * 1000:]
        self.piano = AudioSegment.from_wav(piano_file)
        self.drum = AudioSegment.from_wav(drum_file)
        self.min_length = min(len(self.voice), len(self.piano), len(self.drum))

        self.voice = self.voice[:self.min_length]
        self.piano = self.piano[:self.min_length]
        self.drum = self.drum[:self.min_length]

    def mix_instruments(self):
        """
        the function to mix the piano and drum.


        Returns:
           AudioSegment of the mixed file. (Instrumental)
        """

        # adjust volume
        self.piano = self.piano - 5
        self.drum = self.drum + 5
        # Ensure both are stereo
        if self.piano.channels == 1:
            self.piano = self.piano.set_channels(2)

        if self.drum.channels == 1:
            self.drum = self.drum.set_channels(2)

        # Mix them together
        mixed = self.drum.overlay(self.piano)

        # Output the result
        print("mixing instruments successfully!")
        return mixed

    def mix_vocal_instrumental(self, intrument_mixed):
        """
        the function to mix the vocal and instrumental.

        Args:
            intrument_mixed (AudioSegment): AudioSegment of the instrumental file.
        Returns:
              None
        """
        # adjust the volume
        self.voice = self.voice - 5

        # set to stereo
        if self.voice.channels == 1:
            self.voice = self.voice.set_channels(2)

        # overlay the vocal
        mixed = intrument_mixed.overlay(self.voice)

        # Output the result
        print("mixing vocal and instrumental successfully!")

        # export the file

        mixed.export(
            "C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\api\\uploaded_files\\combined.wav", format="wav")

        return None


def generate_music(vocal_file, vocal_midi_file):
    # file adress

    midi_piano_file = 'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\api\\midi\\piano.mid'
    midi_drum_file = 'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\api\\midi\\drum.mid'
    wav_piano_file = "C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\api\\wav\\piano.wav"
    wav_drum_file = "C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\api\\wav\\drum.wav"
    model, vocal_tempo, the_start_time, chord_list, split_notes_list = hmm_pipeline(
        vocal_file, vocal_midi_file)

    # generate the chord sequence
    my_chord_generator = ChordGenerator(model, split_notes_list, chord_list)
    chord_sequence = my_chord_generator.generate()

    # generate the piano accompaniment
    my_piano_accompaniment = PianoAccompanimentMode1(
        vocal_tempo, chord_sequence)
    piano_accompaniment = my_piano_accompaniment.generate()

    # generate the drum accompaniment
    my_drum_accompaniment = DrumAccompanimentMode1(vocal_tempo, chord_sequence)
    drum_accompaniment = my_drum_accompaniment.generate()

    # write the MIDI file
    piano_midi_file = MIDIFile(midi_piano_file, piano_accompaniment)
    piano_midi_file.write()

    drum_midi_file = MIDIFile(midi_drum_file, drum_accompaniment)
    drum_midi_file.write()

    # convert the MIDI file to WAV file
    piano_wav_file = WAVFile(
        'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\data_process\\soundfont\\Nice-Steinway-v3.9.sf2', midi_piano_file, wav_piano_file)
    piano_wav_file.convert_and_write()

    drum_wav_file = WAVFile(
        'C:\\Users\\Hsieh\\Documents\\nccucs\\specialTopic\\special_topic\\src\\data_process\\soundfont\\Ultimate Acoustic Session Kit.sf2', midi_drum_file, wav_drum_file)
    drum_wav_file.convert_and_write()

    # mix
    my_mixer = Mixer(vocal_file,
                     wav_piano_file, wav_drum_file, the_start_time)
    my_mixer.mix_vocal_instrumental(my_mixer.mix_instruments())
