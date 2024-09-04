import pygame
import math
import random
import numpy as np
import datetime
import pytz
from opensimplex import OpenSimplex

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1600, 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Advanced Radar Simulation v2.0")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FAINT_GREEN = (0, 255, 0, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Radar settings
radar_x, radar_y = 400, height // 2
radar_radius = 300
sweep_angle = 0
sweep_speed = 0.03

# Objects settings (1 drone and 4 other objects)
num_objects = 5
objects = []

# Add one drone
drone_distance = random.randint(0, radar_radius)
drone_angle = random.uniform(0, 2 * math.pi)
drone_x = radar_x + drone_distance * math.cos(drone_angle)
drone_y = radar_y + drone_distance * math.sin(drone_angle)
objects.append((drone_x, drone_y, "drone"))

# Add four other objects
for _ in range(4):
    distance = random.randint(0, radar_radius)
    angle = random.uniform(0, 2 * math.pi)
    x = radar_x + distance * math.cos(angle)
    y = radar_y + distance * math.sin(angle)
    objects.append((x, y, "other"))

# Font
digital_font = pygame.font.Font("digital-7.ttf", 24)
header_font = pygame.font.Font("digital-7.ttf", 36)

# Load sound
beep_sound = pygame.mixer.Sound("beep.wav")

# Initialize OpenSimplex noise
noise = OpenSimplex(seed=random.randint(0, 10000))

def draw_header():
    header_text = header_font.render("Advanced Drone/Bird Classifier System", True, WHITE)
    screen.blit(header_text, (width // 2 - header_text.get_width() // 2, 20))

def draw_radar_circle():
    pygame.draw.circle(screen, GREEN, (radar_x, radar_y), radar_radius + 10, 2)
    pygame.draw.circle(screen, GREEN, (radar_x, radar_y), radar_radius, 2)
    for r in range(radar_radius // 6, radar_radius, radar_radius // 6):
        pygame.draw.circle(screen, DARK_GREEN, (radar_x, radar_y), r, 1)
    
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

    # Render timezone and time text
    timezone_text = digital_font.render("Timezone: IST", True, WHITE)
    time_text = digital_font.render(f"Time: {current_time}", True, WHITE)
    
    screen.blit(timezone_text, (radar_x - radar_radius - 200, radar_y - radar_radius - 30))
    screen.blit(time_text, (radar_x - radar_radius - 200, radar_y - radar_radius - 10))

def draw_radar_lines():
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        pygame.draw.line(screen, DARK_GREEN, (radar_x, radar_y), 
                         (radar_x + radar_radius * math.cos(rad),
                          radar_y + radar_radius * math.sin(rad)))

def draw_sweep_area(angle):
    arc_width = math.pi / 6
    start_angle = angle - arc_width / 2
    end_angle = angle + arc_width / 2
    
    points = [
        (radar_x, radar_y),
        (radar_x + radar_radius * math.cos(start_angle), radar_y + radar_radius * math.sin(start_angle)),
        (radar_x + radar_radius * math.cos(end_angle), radar_y + radar_radius * math.sin(end_angle))
    ]
    
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.polygon(s, FAINT_GREEN, points)
    screen.blit(s, (0, 0))

def draw_objects(detected_drone=None, blink=True):
    current_time = pygame.time.get_ticks()
    
    if blink:
        alpha = int((math.sin(current_time / 1000.0 * math.pi) + 1) / 2 * 255)
    else:
        alpha = 255
    
    for obj in objects:
        color = RED if obj == detected_drone else GREEN
        
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color[:3], alpha), (10, 10), 10)
        
        screen.blit(s, (int(obj[0]) - 10, int(obj[1]) - 10))

def generate_complex_wave(x, time_factor):
    y = 20 * np.sin(0.5 * x + time_factor)
    y += 10 * np.sin(2 * x + 1.5 * time_factor)
    y += 10 * np.sin(4 * x + 2 * time_factor)
    y += np.random.normal(0, 5, len(x))
    spike_locations = np.random.choice(len(x), 3, replace=False)
    y[spike_locations] += np.random.uniform(20, 40, 3)
    y += 10 * np.sin(0.1 * x + 0.1 * time_factor)
    
    return y

def draw_realistic_wave(time_factor):
    graph_x = 860
    graph_y = 200
    graph_width = 700
    graph_height = 300

    pygame.draw.rect(screen, DARK_GREEN, (graph_x, graph_y, graph_width, graph_height), 2)

    x = np.linspace(0, 20, graph_width)
    y = generate_complex_wave(x, time_factor)
    y_scaled = (y - y.min()) / (y.max() - y.min()) * graph_height
    y_scaled = graph_height - y_scaled + graph_y

    points = [(graph_x + i, int(y_scaled[i])) for i in range(graph_width)]
    pygame.draw.lines(screen, WHITE, False, points, 2)

    max_amplitude = (y.max() - y.min()) / 2
    amp_text = digital_font.render(f"Max Amplitude: {max_amplitude:.2f}", True, GREEN)
    screen.blit(amp_text, (graph_x, graph_y + graph_height + 10))
    
    status_lines = [
        "Processing radio signal...",
        "Status: OK",
        "Generating Spectrogram image per 16 seconds...",
        "Successful: Given to Model",
        "AI Analysis: In Progress",
        "Threat Assessment: Low"
    ]

    for i, line in enumerate(status_lines):
        status_text = digital_font.render(line, True, FAINT_GREEN)
        screen.blit(status_text, (graph_x, graph_y + graph_height + 40 + i * 20))

def draw_info():
    info_text = digital_font.render(f"Angle: {int(math.degrees(sweep_angle))}°", True, GREEN)
    screen.blit(info_text, (10, 10))

    drone_detected = False
    detection_angle = 0
    detected_drone = None
    for obj in objects:
        distance = math.sqrt((obj[0] - radar_x) ** 2 + (obj[1] - radar_y) ** 2)
        if distance <= radar_radius:
            relative_angle = math.atan2(obj[1] - radar_y, obj[0] - radar_x)
            if abs(relative_angle - sweep_angle) % (2 * math.pi) <= math.pi / 6:
                if obj[2] == "drone":
                    drone_detected = True
                    detection_angle = math.degrees(relative_angle)
                    detected_drone = obj
                break

    if drone_detected:
        detection_text = digital_font.render(f"Drone Detected! Angle: {int(detection_angle)}°", True, YELLOW)
        popup_x = width // 2 - detection_text.get_width() // 2
        popup_y = height // 2 - detection_text.get_height() // 2
        screen.blit(detection_text, (popup_x, popup_y))
        
        pygame.time.delay(200)
        beep_sound.play()

        log_drone_detection(datetime.datetime.now(), detection_angle, detected_drone[0], detected_drone[1])

    return detected_drone, not drone_detected

def log_drone_detection(timestamp, angle, x, y):
    try:
        with open("drone_detection_log.txt", "a") as log_file:
            log_file.write(f"{timestamp}, Angle: {angle:.2f}°, Latitude: {x:.2f}, Longitude: {y:.2f}\n")
    except IOError as e:
        print(f"Error logging drone detection: {e}")

def draw_complex_interface():
    pygame.draw.rect(screen, GREEN, (810, 150, 760, 500), 2)
    draw_realistic_wave(time_factor=pygame.time.get_ticks() / 1000.0)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    draw_header()
    draw_radar_circle()
    draw_radar_lines()
    draw_sweep_area(sweep_angle)
    detected_drone, blink = draw_info()
    draw_objects(detected_drone, blink)
    draw_complex_interface()
    pygame.display.flip()

    sweep_angle += sweep_speed
    sweep_angle %= 2 * math.pi

    pygame.time.Clock().tick(60)

pygame.quit()
