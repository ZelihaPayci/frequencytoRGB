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
    freq_data = np.abs(freq_data) ** 1.2
    min_val, max_val = np.percentile(freq_data, 5), np.percentile(freq_data, 90)
    freq_data = np.clip((freq_data - min_val) / (max_val - min_val), 0, 1) * 255
    return freq_data

def freq_to_rgb(freq_data):
    freq_data = normalize_frequency(freq_data)

    bass = np.mean(freq_data[:80])
    mids = np.mean(freq_data[80:500])
    highs = np.mean(freq_data[500:])

    total = bass + mids + highs
    if total == 0:
        return (0, 0, 0)

    red = int((bass / total) * 255)
    green = int((mids / total) * 255)
    blue = int((highs / total) * 255)

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
