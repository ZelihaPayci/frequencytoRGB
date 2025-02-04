import numpy as np
from scipy.fftpack import fft
import pygame
from pydub import AudioSegment
from pydub.utils import which

ffmpeg_path = "C:\\Users\\ZPAYCI21\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe"
ffprobe_path = "C:\\Users\\ZPAYCI21\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffprobe.exe"

AudioSegment.ffmpeg = which(ffmpeg_path)
AudioSegment.ffprobe = which(ffprobe_path)

song = AudioSegment.from_mp3("")
samples = np.array(song.get_array_of_samples())
sample_rate = song.frame_rate

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

def freq_to_rgb(freq_data):
    freq_data = np.clip(freq_data, 0, np.max(freq_data))

    red = np.mean(freq_data[:50]) * 0.3
    green = np.mean(freq_data[50:200]) * 0.2
    blue = np.mean(freq_data[200:]) * 0.5

    red = np.clip(red, 0, 255)
    green = np.clip(green, 0, 255)
    blue = np.clip(blue, 0, 255)

    print(f"Red: {red}, Green: {green}, Blue: {blue}")

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
            pygame.quit()
            exit()

    clock.tick(30)
