import numpy as np
from scipy.fftpack import fft
import pygame
from pydub import AudioSegment
from pydub.utils import which
import os
from dotenv import load_dotenv

load_dotenv()
song_path = os.getenv("songPath")

ffmpeg_path = "C:\\Users\\ZPAYCI21\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe"
ffprobe_path = "C:\\Users\\ZPAYCI21\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffprobe.exe"

AudioSegment.ffmpeg = which(ffmpeg_path)
AudioSegment.ffprobe = which(ffprobe_path)

song = AudioSegment.from_mp3(song_path)
samples = np.array(song.get_array_of_samples())
sample_rate = song.frame_rate

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

pygame.mixer.init()
pygame.mixer.music.load(song_path)
pygame.mixer.music.play()

def normalize_frequency(freq_data):
    """ Normalize frequency data using percentile-based scaling for better contrast. """
    freq_data = np.abs(freq_data)
    freq_data = np.power(freq_data, 1.3)

    min_val = np.percentile(freq_data, 10)
    max_val = np.percentile(freq_data, 95)

    freq_data = (freq_data - min_val) / (max_val - min_val)
    freq_data = np.clip(freq_data, 0, 1) * 255

    return freq_data

def freq_to_rgb(freq_data):
    freq_data = normalize_frequency(freq_data)

    low_freqs = np.mean(freq_data[:100])
    mid_freqs = np.mean(freq_data[100:500])
    high_freqs = np.mean(freq_data[500:])

    total_energy = low_freqs + mid_freqs + high_freqs
    if total_energy == 0:
        return (0, 0, 0)

    red = (low_freqs / total_energy) * 255
    green = (mid_freqs / total_energy) * 255
    blue = (high_freqs / total_energy) * 255

    return (int(red), int(green), int(blue))

for i in range(0, len(samples), 2048):
    sample_chunk = samples[i:i + 2048]
    fft_data = fft(sample_chunk)
    freq_data = np.abs(fft_data)

    rgb_color = freq_to_rgb(freq_data)

    screen.fill(rgb_color)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            pygame.quit()
            exit()

    clock.tick(30)

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)