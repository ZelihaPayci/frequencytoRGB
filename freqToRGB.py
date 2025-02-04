import numpy as np
from scipy.fftpack import fft
import pygame
from pydub import AudioSegment
from pydub.utils import which
import os
import random
from dotenv import load_dotenv
from particle import Particle

load_dotenv()
song_path = os.getenv("songPath")

ffmpeg_path = os.getenv("ffmpeg_path")
ffprobe_path = os.getenv("ffprobe_path")

AudioSegment.ffmpeg = which(ffmpeg_path)
AudioSegment.ffprobe = which(ffprobe_path)

song = AudioSegment.from_mp3(song_path)
samples = np.array(song.get_array_of_samples(), dtype=np.float32)
sample_rate = song.frame_rate

samples /= np.max(np.abs(samples))

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.mixer.init()
pygame.mixer.music.load(song_path)
pygame.mixer.music.play()

is_paused = False
current_position = 0


def normalize_frequency(freq_data):
    """Normalize the frequency data to the range of 0-255 for better visualization."""
    freq_data = np.nan_to_num(freq_data, nan=0, posinf=0, neginf=0)

    # Apply a logarithmic scale to better capture the lower frequencies
    freq_data = np.abs(freq_data) ** 0.8  # Stretch frequencies for better color mapping

    # Normalize based on the max value
    max_val = np.max(freq_data)
    min_val = np.min(freq_data)

    # Avoid division by zero and scale to 0-255 range
    if max_val - min_val > 0:
        freq_data = (freq_data - min_val) / (max_val - min_val) * 255
    else:
        freq_data = np.zeros_like(freq_data)

    return freq_data


def freq_to_rgb(freq_data):
    """Convert frequency data to RGB color based on bass, mids, and highs."""
    freq_data = normalize_frequency(freq_data)

    if np.all(freq_data == 0):  # In case all frequencies are zero, return black
        return (0, 0, 0)

    # Define frequency bands for bass, mids, and highs
    bass = np.mean(freq_data[:150])  # Low frequencies (bass up to 150 Hz)
    mids = np.mean(freq_data[150:1000])  # Mid frequencies (from 150 Hz to 1 kHz)
    highs = np.mean(freq_data[1000:])  # High frequencies (from 1 kHz upwards)

    # We can use a threshold for each range to prevent one band from dominating
    total = bass + mids + highs
    if total == 0:
        return (0, 0, 0)  # If all frequencies are zero, return black

    # Calculate the RGB components, based on their respective frequency ranges
    red = int((bass / total) * 255)
    green = int((mids / total) * 255)
    blue = int((highs / total) * 255)

    # To add more dynamic range, let's tweak how we calculate these components:
    # We will apply a scaling to `highs` for better balance across frequency bands.
    blue = int(min(max(blue * 1.2, 0), 255))  # Increase blue intensity for high frequencies

    # Ensure that the values are bounded between 0 and 255
    red = min(max(red, 0), 255)
    green = min(max(green, 0), 255)
    blue = min(max(blue, 0), 255)

    return (red, green, blue)

particles = []

def draw_waveform(sample_chunk, color):
    screen.fill((0, 0, 0))
    num_points = len(sample_chunk)
    x_step = WIDTH / num_points
    center_y = HEIGHT // 2

    points = []
    for i in range(num_points):
        x = int(i * x_step)
        y = int(center_y + sample_chunk[i] * (HEIGHT // 3))
        points.append((x, y))

        if random.random() < 0.02:
            particles.append(Particle(x, y, color))

    pygame.draw.lines(screen, color, False, points, 2)

    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.life <= 0:
            particles.remove(particle)

    pygame.display.flip()

running = True
while running:
    for i in range(current_position, len(samples), 2048):
        sample_chunk = samples[i:i + 2048]
        fft_data = fft(sample_chunk)
        freq_data = np.abs(fft_data)

        color = freq_to_rgb(freq_data)
        draw_waveform(sample_chunk, color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                running = False
                pygame.quit()
                exit()

        if not pygame.mixer.music.get_busy():
            running = False
            break

        clock.tick(30)

    if pygame.mixer.music.get_busy():
        current_position = pygame.mixer.music.get_pos() / 1000

    pygame.time.Clock().tick(10)

pygame.quit()