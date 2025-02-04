import numpy as np
from scipy.fftpack import fft
import pygame
from pydub import AudioSegment
from pydub.utils import which
import os
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
song_path = os.getenv("songPath")

# Set FFmpeg paths
ffmpeg_path = "C:\\Users\\ZPAYCI21\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe"
ffprobe_path = "C:\\Users\\ZPAYCI21\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffprobe.exe"

AudioSegment.ffmpeg = which(ffmpeg_path)
AudioSegment.ffprobe = which(ffprobe_path)

# Load and process audio
song = AudioSegment.from_mp3(song_path)
samples = np.array(song.get_array_of_samples(), dtype=np.float32)
sample_rate = song.frame_rate

# Normalize samples (for better visualization)
samples /= np.max(np.abs(samples))

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 🎵 Start playing the song
pygame.mixer.init()
pygame.mixer.music.load(song_path)
pygame.mixer.music.play()

def normalize_frequency(freq_data):
    """ Normalize frequency data dynamically to avoid dominant red. """
    freq_data = np.abs(freq_data) ** 1.2  # Reduce extreme values
    min_val, max_val = np.percentile(freq_data, 5), np.percentile(freq_data, 90)
    freq_data = np.clip((freq_data - min_val) / (max_val - min_val), 0, 1) * 255
    return freq_data

def freq_to_rgb(freq_data):
    """ Improved color mapping for vibrant and varied colors """
    freq_data = normalize_frequency(freq_data)

    bass = np.mean(freq_data[:80])  # Bass (Red)
    mids = np.mean(freq_data[80:500])  # Mids (Green)
    highs = np.mean(freq_data[500:])  # Highs (Blue)

    # Normalize all values
    total = bass + mids + highs
    if total == 0:
        return (0, 0, 0)

    red = int((bass / total) * 255)
    green = int((mids / total) * 255)
    blue = int((highs / total) * 255)

    return (red, green, blue)

class Particle:
    """ Sparkling effect around the waves """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.life = random.randint(10, 30)
        self.velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.size *= 0.95  # Shrink over time
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), max(1, int(self.size)))

particles = []

def draw_waveform(sample_chunk, color):
    """ Draw a vibrant, colored waveform with a sparkling effect """
    screen.fill((0, 0, 0))  # Black background
    num_points = len(sample_chunk)
    x_step = WIDTH / num_points  # Spacing between points
    center_y = HEIGHT // 2

    points = []
    for i in range(num_points):
        x = int(i * x_step)
        y = int(center_y + sample_chunk[i] * (HEIGHT // 3))
        points.append((x, y))

        # Add some sparkle effect (random chance)
        if random.random() < 0.02:
            particles.append(Particle(x, y, color))

    # Draw the waveform using connected lines
    pygame.draw.lines(screen, color, False, points, 2)

    # Draw the particles
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.life <= 0:
            particles.remove(particle)

    pygame.display.flip()

# 🎨 Main visualization loop
for i in range(0, len(samples), 2048):
    sample_chunk = samples[i:i + 2048]
    fft_data = fft(sample_chunk)
    freq_data = np.abs(fft_data)

    color = freq_to_rgb(freq_data)
    draw_waveform(sample_chunk, color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            pygame.quit()
            exit()

    clock.tick(30)

# Keep running until song ends
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)
