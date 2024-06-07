import pygame
import numpy as np
import time

# Initialize pygame mixer
pygame.mixer.init()

# Define note frequencies (in Hz)
NOTE_FREQUENCIES = {
    'C4': 261.63,
    'D4': 293.66,
    'E4': 329.63,
    'F4': 349.23,
    'G4': 392.00,
    'A4': 440.00,
    'B4': 493.88,
    'C5': 523.25
}

# Function to generate a tone
def generate_tone(frequency, duration_ms):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n_samples, False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Convert waveform to 16-bit PCM format and create a stereo buffer
    waveform_integers = np.int16(waveform * 32767)
    stereo_waveform = np.column_stack((waveform_integers, waveform_integers))

    sound = pygame.sndarray.make_sound(stereo_waveform)
    return sound

# Define the melody (notes and durations in milliseconds)
zelda_chest_melody = [
    ('C4', 300),
    ('D4', 300),
    ('E4', 300),
    ('F4', 300),
    ('G4', 300)
]

# Play each note in the melody
for note, duration in zelda_chest_melody:
    frequency = NOTE_FREQUENCIES[note]
    tone = generate_tone(frequency, duration)
    tone.play()
    pygame.time.delay(duration)
    time.sleep(0.1)  # Short pause between notes
