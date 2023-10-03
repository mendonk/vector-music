import mido
from mido import MidiFile
import numpy as np
from annoy import AnnoyIndex
import os
import glob

class MidiVectorizer:
    def __init__(self):
        pass

    def midi_to_vector(self, midifile):
        notes = [0] * 128  # For 128 possible MIDI note values
        mid = MidiFile(midifile)
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'note_on':
                    notes[msg.note] += 1
        return np.array(notes)


class VectorDatabase:
    def __init__(self, dim=128, metric='angular'):
        self.dim = dim
        self.metric = metric
        self.db = AnnoyIndex(dim, metric)

    def add_vector(self, vector, index):
        self.db.add_item(index, vector)

    def build(self, trees=10):
        self.db.build(trees)

    def save(self, filename):
        self.db.save(filename)

    def load(self, filename):
        self.db.load(filename)

    def get_similar_indices(self, vector, n=5):
        return self.db.get_nns_by_vector(vector, n)


class MidiDatabase:
    def __init__(self, midi_files):
        self.midi_files = glob.glob(os.path.join("Pop_Music_Midi", "*.midi"))
        self.vectorizer = MidiVectorizer()
        self.database = VectorDatabase()

    def build_database(self):
        for i, midi_file in enumerate(self.midi_files):
            v = self.vectorizer.midi_to_vector(midi_file)
            self.database.add_vector(v, i)
        self.database.build()

    def save_database(self, filename):
        self.database.save(filename)

    def load_database(self, filename):
        self.database.load(filename)

    def get_similar_midis(self, seed_midi, n=5):
        seed_vector = self.vectorizer.midi_to_vector(seed_midi)
        indices = self.database.get_similar_indices(seed_vector, n)
        return [self.midi_files[i] for i in indices]


# Usage example
midi_files = glob.glob(os.path.join("Pop_Music_Midi", "*.midi"))
db = MidiDatabase(midi_files)
db.build_database()
db.save_database('midi_vectors.ann')
# similar_midis = db.get_similar_midis("Pop_Music_Midi/Clocks - Intro.midi")
