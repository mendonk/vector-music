import numpy as np
from annoy import AnnoyIndex
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from mido import MidiFile, MidiTrack, Message
import random

class MidiGenerator:
    def __init__(self, midi_vectors_file, vector_length=128, seq_length=10):
        self.vector_length = vector_length
        self.seq_length = seq_length

        self.model = None
        self._load_data(midi_vectors_file)
        self._prepare_sequences()

    def _load_data(self, midi_vectors_file):
        t = AnnoyIndex(self.vector_length, 'angular')
        t.load(midi_vectors_file)
        num_items = t.get_n_items()
        self.data = [t.get_item_vector(i) for i in range(num_items)]

    def _prepare_sequences(self):
        X, y = [], []
        for i in range(len(self.data) - self.seq_length):
            X.append(self.data[i:i + self.seq_length])
            y.append(self.data[i + 1:i + 1 + self.seq_length])

        self.X = np.array(X)
        self.y = np.array(y)

    def define_model(self):
        self.model = Sequential()
        self.model.add(LSTM(256, input_shape=(self.seq_length, self.vector_length), return_sequences=True))
        self.model.add(LSTM(256, return_sequences=True))
        self.model.add(Dense(self.vector_length, activation='sigmoid'))

        self.model.compile(optimizer='adam', loss='mse')

    def train(self, epochs=100, batch_size=64, validation_split=0.2):
        if not self.model:
            self.define_model()

        self.model.fit(self.X, self.y, epochs=epochs, batch_size=batch_size, validation_split=validation_split)

    def generate_song(self, seed_sequence=None):
        if seed_sequence is None:
            seed_sequence = self.X[random.randint(0, len(self.X) - 1)]

        song = [vec for vec in seed_sequence]

        for i in range(self.seq_length - len(seed_sequence)):
            prediction = self.model.predict(np.array([song[-self.seq_length:]]))
            song.append(prediction[0][-1])

        return song

    from mido import Message

    def vectors_to_midi(self, vectors):
        midi_messages = []

        # Assuming no notes are active at the start
        previous_vector = [0] * len(vectors[0])

        for vector in vectors:
            for note, (prev, curr) in enumerate(zip(previous_vector, vector)):
                # If a note turns on
                if prev == 0 and curr == 1:
                    midi_messages.append(Message('note_on', note=note, velocity=64, time=0))
                # If a note turns off
                elif prev == 1 and curr == 0:
                    midi_messages.append(Message('note_off', note=note, time=0))

            previous_vector = vector

        # Ensure all notes are turned off at the end
        for note, is_active in enumerate(previous_vector):
            if is_active:
                midi_messages.append(Message('note_off', note=note, time=0))

        return midi_messages

    def save_as_midi(self, vectors, filename):
        midi_messages = self.vectors_to_midi(vectors)

        midi_song = MidiFile()
        track = MidiTrack()
        midi_song.tracks.append(track)

        for midi_message in midi_messages:
            track.append(midi_message)

        midi_song.save(filename)


# Example usage:
midi_vectors_file = 'midi_vectors.ann'
midi_gen = MidiGenerator('midi_vectors.ann')
midi_gen.train(epochs=10)  # Train for 10 epochs for demo purposes
song_vectors = midi_gen.generate_song()
midi_gen.save_as_midi(song_vectors, 'generated_song.mid')