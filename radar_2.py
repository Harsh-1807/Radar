import csv
import pygame
import math
import random
import numpy as np
import datetime
import smtplib
from email.mime.text import MIMEText
import threading
import webbrowser
import ctypes
from py_win_styles import apply_style, change_header_color, change_title_color, change_border_color, set_opacity
from time_util import get_current_time, get_timezone_name
import json
import os
import random
import string


# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1200, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Advanced Radar Simulation")

# Get the Pygame window handle
window_handle = pygame.display.get_wm_info()["window"]
apply_style(window_handle, "aero")

# Change the title bar, title text, and border color using pywinstyles
change_header_color(window_handle, color="#00524d")  # Change Title Bar Color
change_title_color(window_handle, color="white")     # Change Title Text Color
change_border_color(window_handle, color="#00ffff")  # Change Border Color

# Set the window to be resizable (to show border effects)
ctypes.windll.user32.SetWindowLongW(window_handle, ctypes.windll.user32.GetWindowLongW(window_handle, -16) | 0x00040000)
'''logo_image = pygame.image.load('logo.png')  # Ensure 'logo.png' is in your working directory
logo_width, logo_height = 200, 200  # Desired dimensions for the logo
logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))

# Position the logo
logo_rect = logo_image.get_rect(topleft=(0, 0))'''
# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FAINT_GREEN = (0, 255, 0, 50)
RED = (255, 0, 0)

# Radar settings
radar_x, radar_y = 400, height // 2
radar_radius = 200
sweep_angle = 0
sweep_speed = 0.01

# Objects settings (1 drone and 2 other objects)
num_objects = 3
objects = []

# Add one drone
drone_distance = random.randint(0, radar_radius)
drone_angle = random.uniform(0, 2 * math.pi)
drone_x = radar_x + drone_distance * math.cos(drone_angle)
drone_y = radar_y + drone_distance * math.sin(drone_angle)
objects.append((drone_x, drone_y, "drone"))

# Add two other objects
for _ in range(2):
    distance = random.randint(0, radar_radius)
    angle = random.uniform(0, 2 * math.pi)
    x = radar_x + distance * math.cos(angle)
    y = radar_y + distance * math.sin(angle)
    objects.append((x, y, "other"))

# Font
digital_font = pygame.font.Font("digital-7.ttf", 24)
header_font = pygame.font.Font("digital-7.ttf", 36)

# Load sounds
beep_sound = pygame.mixer.Sound("beep.wav")
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)  # Play background music in a loop
last_email_sent_time = 0


messages = [
    "3 Blade Rotor detected",
    "Quadcopter detected",
    "Bionic bird detected",
]
detection_message_text = random.choice(messages)
detection_message = header_font.render(detection_message_text, True, RED)

def log_detection(timestamp, angle, x, y):
    # Calculate distance and speed
    distance = math.hypot(x - radar_x, y - radar_y)
    speed = distance / 0.7  # Placeholder value for speed; update based on your logic

    # Define the CSV file path
    csv_file = "detection_log.csv"
    
    # Check if the file exists
    file_exists = os.path.exists(csv_file)

    # Open the file in append mode
    with open(csv_file, "a", newline='') as log_file:
        fieldnames = ["timestamp", "angle", "latitude", "longitude", "distance", "speed"]
        writer = csv.DictWriter(log_file, fieldnames=fieldnames)

        # Write the header if the file is new
        if not file_exists:
            writer.writeheader()

        # Write the log entry
        log_entry = {
            "timestamp": timestamp,
            "angle": round(angle, 2),
            "latitude": round(x, 2),
            "longitude": round(y, 2),
            "distance": round(distance, 2),
            "speed": round(speed, 2)
        }
        writer.writerow(log_entry)

    print(f"Logged entry: {log_entry}")

def send_email_alert(timestamp, angle, x, y):
    subject = "Alert: Drone Detected"
    body = f"A drone was detected at {timestamp}. \n\nDetails:\nAngle: {angle:.2f}°\nLatitude: {x:.2f}\nLongitude: {y:.2f},\nDistance: {round(math.hypot(x - radar_x, y - radar_y), 2)} meters\nSpeed: {round(math.hypot(x - radar_x, y - radar_y) / 0.7, 2)} meters per second"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'nkharshbachhav@gmail.com'
    msg['To'] = 'nkharshbachhav@gmail.com'
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('nkharshbachhav@gmail.com', '')  # Update with the correct password
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print("Alert email sent successfully.")
        log_detection(timestamp, angle, x, y)
    except Exception as e:
        print(f"Failed to send email: {e}")

def threaded_email_alert(timestamp, angle, x, y):
    threading.Thread(target=send_email_alert, args=(timestamp, angle, x, y)).start()

def draw_header():
    header_text = header_font.render("Drone/Bird Classifier", True, WHITE)
    screen.blit(header_text, (width // 2 - header_text.get_width() // 2, 20))
    
    current_time = get_current_time()
    timezone_name = get_timezone_name()
    time_text = digital_font.render(f"Time: {current_time} ({timezone_name})", True, YELLOW)
    
    time_text_y = 20 + header_text.get_height() + 10
    screen.blit(time_text, (width - time_text.get_width() - 20, time_text_y))

def draw_radar_circle():
    pygame.draw.circle(screen, GREEN, (radar_x, radar_y), radar_radius + 10, 2)
    pygame.draw.circle(screen, GREEN, (radar_x, radar_y), radar_radius, 2)
    for r in range(radar_radius // 4, radar_radius, radar_radius // 4):
        pygame.draw.circle(screen, DARK_GREEN, (radar_x, radar_y), r, 1)

def draw_radar_lines():
    for angle in range(0, 360, 30):
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

def draw_objects(detected_drone=None, blink=True, graph_x=660, graph_y=200, graph_height=300):
    current_time = pygame.time.get_ticks()
    alpha = int((math.sin(current_time / 1000.0 * math.pi) + 1) / 2 * 255) if blink else 255
    
    
    for obj in objects:
        color = RED if obj == detected_drone else GREEN
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color[:3], alpha), (10, 10), 10)
        screen.blit(s, (int(obj[0]) - 10, int(obj[1]) - 10))
    if detected_drone:
     pygame.time.delay(100)        #################DELAY 
     obj_x, obj_y, obj_type = detected_drone
     obj_distance = math.hypot(obj_x - radar_x, obj_y - radar_y)
     obj_speed = obj_distance / 0.7  # Placeholder value for speed; update based on your logic
    
    # Render the distance and speed text
     distance_text = digital_font.render(f"Distance: {obj_distance:.2f}", True, RED)
     speed_text = digital_font.render(f"Speed: {obj_speed:.2f} km/h", True, RED)
    
    # Display the distance and speed on the screen
     screen.blit(distance_text, (radar_x - distance_text.get_width() // 2, radar_y + radar_radius + 20))
     screen.blit(speed_text, (radar_x - speed_text.get_width() // 2, radar_y + radar_radius + 50))
    
    # Render the "Drone detected" message
     # Randomly choose a message
 

# Render the chosen message
    
    
    
    # Calculate the position to center the message on the screen
     message_x = (width - detection_message.get_width()) // 2
     message_y = (height - detection_message.get_height()) // 2
    
    # Display the "Drone detected" message in the center of the screen
     screen.blit(detection_message, (message_x, message_y))


def generate_complex_wave(x, time_factor):
    y = 20 * np.sin(0.5 * x + time_factor)
    y += 10 * np.sin(2 * x + 1.5 * time_factor)
    y += 10 * np.sin(4 * x + 2 * time_factor)
    y += np.random.normal(0, 5, len(x))
    spike_locations = np.random.choice(len(x), 3, replace=False)
    y[spike_locations] += np.random.uniform(20, 40, 3)
    y += 10 * np.sin(0.1 * x + 0.1 * time_factor)
    return y


def open_log_button(screen, x, y, width, height, button_text, font, button_color, text_color, log_file_path):
    pygame.draw.rect(screen, button_color, (x, y, width, height))
    text_surface = font.render(button_text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

    # Check for mouse events
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    if (x <= mouse_pos[0] <= x + width and
        y <= mouse_pos[1] <= y + height and
        mouse_click[0] == 1):
        # Run the plot_csv.py script to visualize the CSV data
        os.system(f'python plot_csv.py')

def draw_realistic_wave(time_factor):
    graph_x = 660
    graph_y = 200
    graph_width = 500
    graph_height = 300
    
    # Draw the graph boundaries
    pygame.draw.rect(screen, YELLOW, (graph_x, graph_y, graph_width, graph_height), 2)
    
    # Generate the wave data
    x = np.linspace(0, 20, graph_width)
    y = generate_complex_wave(x, time_factor)
    
    # Scale the wave data to fit the graph
    scaled_y = graph_y + graph_height // 2 - (y / max(abs(y)) * (graph_height // 2)).astype(int)
    
    # Draw the wave
    for i in range(len(scaled_y) - 1):
        pygame.draw.line(screen, WHITE, (graph_x + i, scaled_y[i]), (graph_x + i + 1, scaled_y[i + 1]))
    
    # Render status lines with animation
    status_lines = [
        "Processing radio signal...",
        "Status: OK",
        "Generating Spectrogram image per 16 seconds...",
        "Successfully: Loaded The Model",
        "Initializing signal processing algorithms...",
        "Calibrating frequency bands...",
        "Scanning for potential targets...",
        "Applying noise reduction filters...",
        "Updating threat assessment matrix...",
        "Synchronizing with satellite data...",
        "Running pattern recognition algorithms...",
        "Performing Doppler analysis...",
        "Updating geospatial coordinates...",
        "Cross-referencing with known flight paths...",
        "Optimizing detection parameters...",
        "Monitoring atmospheric conditions...",
        "Analyzing signal strength variations...",
        "Executing machine learning predictions...",
        "Updating system logs...",
        "Performing routine system diagnostics..."
    ]
    
    font = pygame.font.SysFont("Courier", 14)  # Using Courier for a more terminal-like look
    animation_speed = 20  # characters per second
    current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
    
    # Create a surface for the terminal background
    terminal_width = 500
    terminal_height = 150
    terminal_surface = pygame.Surface((terminal_width, terminal_height))
    terminal_surface.fill((0, 0, 0))  # Black background
    
    cursor_blink_rate = 0.5  # Cursor blinks every 0.5 seconds
    show_cursor = (current_time % cursor_blink_rate) < (cursor_blink_rate / 2)
    
    # Calculate the number of visible lines and the scroll offset
    visible_lines = terminal_height // 20  # Assuming each line takes 20 pixels
    scroll_offset = max(0, len(status_lines) - visible_lines)
    scroll_position = int(current_time / 2) % (len(status_lines) + visible_lines)
    
    y_offset = 10
    for i in range(scroll_position, min(scroll_position + visible_lines, len(status_lines))):
        line = status_lines[i % len(status_lines)]
        # Calculate how much of the line should be shown
        chars_to_show = int(current_time * animation_speed - (i * len(line) / animation_speed))
        chars_to_show = max(0, min(chars_to_show, len(line)))
        
        # Render the visible part of the line
        text_surface = font.render(line[:chars_to_show], True, (0, 255, 0))  # Green text
        terminal_surface.blit(text_surface, (10, y_offset))
        
        # Add blinking cursor
        if i == scroll_position + visible_lines - 1 and show_cursor and chars_to_show < len(line):
            cursor_x = 10 + text_surface.get_width()
            pygame.draw.line(terminal_surface, (0, 255, 0), (cursor_x, y_offset), (cursor_x, y_offset + 14), 2)
        
        y_offset += 20
    
    # Blit the terminal surface onto the main screen
    screen.blit(terminal_surface, (graph_x, graph_y + graph_height + 20))
    
    # Draw X and Y axis indexes
    axis_font = pygame.font.SysFont("Courier New", 22)
    
    x_index = "Time"
    y_index = "Amp"
    
    x_index_surface = axis_font.render(x_index, True, WHITE)
    y_index_surface = axis_font.render(y_index, True, WHITE)
    
    screen.blit(x_index_surface, (graph_x + graph_width - 160, graph_y + graph_height + 10))
    screen.blit(y_index_surface, (graph_x - 40, graph_y + graph_height // 2))
    
    # Display the maximum value as text
    ffont = pygame.font.SysFont("OCR A Extended", 32)
    max_value_text = ffont.render(f"Current Max Value: {max(y):.2f}", True, RED)
    screen.blit(max_value_text, (graph_x, graph_y - 80))


def matrix_animation():
    # Set up the matrix animation
    char_list = "01"
    columns = 120
    rows = 40
    font = pygame.font.SysFont("monospace", 15, bold=True)
    
    # Create a 2D array to store the character positions and velocities
    char_positions = [[0 for _ in range(columns)] for _ in range(rows)]
    char_velocities = [[random.uniform(1, 3) for _ in range(columns)] for _ in range(rows)]
    
    # Update the character positions and velocities
    for i in range(rows):
        for j in range(columns):
            char_positions[i][j] += char_velocities[i][j]
            if char_positions[i][j] > height:
                char_positions[i][j] = random.randint(-50, 0)
                char_velocities[i][j] = random.uniform(1, 3)
    
    # Draw the matrix animation
    for i in range(rows):
        for j in range(columns):
            if char_positions[i][j] > 0:
                x = j * 10
                y = char_positions[i][j]
                char = font.render(random.choice(char_list), True, (0, random.randint(100, 255), 0))
                screen.blit(char, (x, y))

def holographic_target_tracker(target_x, target_y, radius=50):
    """
    Draws a holographic target tracking effect.
    
    Args:
        target_x (int): The x-coordinate of the target.
        target_y (int): The y-coordinate of the target.
        radius (int): The radius of the target (default: 50).
    """
    # Define the colors and transparency for the holographic effect
    base_color = (0, 255, 255)
    highlight_color = (255, 255, 0)
    alpha = 100

    # Draw the holographic target
    for i in range(10):
        size = radius + i * 10
        color = base_color
        if i % 2 == 0:
            color = highlight_color
        pygame.draw.circle(screen, (*color, alpha // (i + 1)), (target_x, target_y), size)

    # Draw the target center
    pygame.draw.circle(screen, (*highlight_color, alpha), (target_x, target_y), radius, 2)

    # Draw the target direction lines
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = target_x
        y1 = target_y
        x2 = target_x + math.cos(rad) * radius * 1.5
        y2 = target_y + math.sin(rad) * radius * 1.5
        pygame.draw.line(screen, (*base_color, alpha // 2), (x1, y1), (x2, y2), 2)

    # Add a pulsing effect
    pulse_radius = radius + math.sin(pygame.time.get_ticks() / 500) * 10
    pygame.draw.circle(screen, (*highlight_color, alpha // 2), (target_x, target_y), pulse_radius, 2)

def radar_scan_effect(center_x, center_y, radius, scan_angle, scan_speed, color=(0, 255, 255), alpha=100):
    """
    Draws an animated radar scan effect.
    
    Args:
        center_x (int): The x-coordinate of the radar center.
        center_y (int): The y-coordinate of the radar center.
        radius (int): The radius of the radar.
        scan_angle (float): The current angle of the scan line (in radians).
        scan_speed (float): The speed of the scan line (in radians per second).
        color (tuple): The RGB color of the scan line (default: (0, 255, 255)).
        alpha (int): The transparency of the scan line (default: 100).
    """
    # Draw the scan line
    x1 = center_x + math.cos(scan_angle) * radius
    y1 = center_y + math.sin(scan_angle) * radius
    x2 = center_x + math.cos(scan_angle + math.pi) * radius
    y2 = center_y + math.sin(scan_angle + math.pi) * radius
    pygame.draw.line(screen, (*color, alpha), (x1, y1), (x2, y2), 4)

    # Update the scan angle
    scan_angle += scan_speed
    if scan_angle > 2 * math.pi:
        scan_angle -= 2 * math.pi

    return scan_angle




   
# Main loop
running = True
clock = pygame.time.Clock()
time_factor = 0
font = pygame.font.Font(None, 36)
button_color = (0, 128, 255)
text_color = (255, 255, 255)

scan_angle = 0
scan_speed = 0.01
# Path to the log file
log_file_path = "detection_log.csv"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_m:
                pygame.mixer.music.set_volume(0.5 if pygame.mixer.music.get_volume() > 0 else 1)

    screen.fill(BLACK)
    draw_header()
    draw_radar_circle()
    scan_angle = radar_scan_effect(radar_x, radar_y, radar_radius, scan_angle, scan_speed)
    draw_radar_lines()
    open_log_button(screen, 50, 50, 200, 50, "Open Log", font, button_color, text_color, log_file_path)
    sweep_angle += sweep_speed
    if sweep_angle > 2 * math.pi:
        sweep_angle -= 2 * math.pi

    draw_sweep_area(sweep_angle)
    
    detected_drone = None
    for obj in objects:
        obj_x, obj_y, obj_type = obj
        angle_to_object = math.atan2(obj_y - radar_y, obj_x - radar_x)
        if angle_to_object < 0:
            angle_to_object += 2 * math.pi
        angle_difference = abs(angle_to_object - sweep_angle)
        if angle_difference < sweep_speed * 10 and obj_type == "drone":
            detected_drone = obj
            beep_sound.play()
            current_time = pygame.time.get_ticks()
            time_since_last_email = current_time - last_email_sent_time
            if time_since_last_email > 10000:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                threaded_email_alert(timestamp, math.degrees(angle_to_object), obj_x, obj_y)
                last_email_sent_time = current_time

    draw_objects(detected_drone)
    draw_realistic_wave(time_factor)
    matrix_animation()
    
    time_factor += 0.1
   # screen.blit(logo_image, logo_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
# prev-code
# import csv
# import pygame
# import math
# import random
# import numpy as np
# import datetime
# import smtplib
# from email.mime.text import MIMEText
# import threading
# import webbrowser
# import ctypes
# from py_win_styles import apply_style, change_header_color, change_title_color, change_border_color, set_opacity
# from time_util import get_current_time, get_timezone_name
# import json
# import os
# # Initialize Pygame
# pygame.init()

# # Set up the display
# width, height = 1200, 700
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption("Advanced Radar Simulation")

# # Get the Pygame window handle
# window_handle = pygame.display.get_wm_info()["window"]
# apply_style(window_handle, "aero")

# # Change the title bar, title text, and border color using pywinstyles
# change_header_color(window_handle, color="#00524d")  # Change Title Bar Color
# change_title_color(window_handle, color="white")     # Change Title Text Color
# change_border_color(window_handle, color="#00ffff")  # Change Border Color

# # Set the window to be resizable (to show border effects)
# ctypes.windll.user32.SetWindowLongW(window_handle, ctypes.windll.user32.GetWindowLongW(window_handle, -16) | 0x00040000)
# '''logo_image = pygame.image.load('logo.png')  # Ensure 'logo.png' is in your working directory
# logo_width, logo_height = 200, 200  # Desired dimensions for the logo
# logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))

# # Position the logo
# logo_rect = logo_image.get_rect(topleft=(0, 0))'''
# # Colors
# BLACK = (0, 0, 0)
# GREEN = (0, 255, 0)
# DARK_GREEN = (0, 100, 0)
# YELLOW = (255, 255, 0)
# WHITE = (255, 255, 255)
# FAINT_GREEN = (0, 255, 0, 50)
# RED = (255, 0, 0)

# # Radar settings
# radar_x, radar_y = 400, height // 2
# radar_radius = 200
# sweep_angle = 0
# sweep_speed = 0.01

# # Objects settings (1 drone and 2 other objects)
# num_objects = 3
# objects = []

# # Add one drone
# drone_distance = random.randint(0, radar_radius)
# drone_angle = random.uniform(0, 2 * math.pi)
# drone_x = radar_x + drone_distance * math.cos(drone_angle)
# drone_y = radar_y + drone_distance * math.sin(drone_angle)
# objects.append((drone_x, drone_y, "drone"))

# # Add two other objects
# for _ in range(2):
#     distance = random.randint(0, radar_radius)
#     angle = random.uniform(0, 2 * math.pi)
#     x = radar_x + distance * math.cos(angle)
#     y = radar_y + distance * math.sin(angle)
#     objects.append((x, y, "other"))

# # Font
# digital_font = pygame.font.Font("digital-7.ttf", 24)
# header_font = pygame.font.Font("digital-7.ttf", 36)

# # Load sounds
# beep_sound = pygame.mixer.Sound("beep.wav")
# pygame.mixer.music.load("background.mp3")
# pygame.mixer.music.play(-1)  # Play background music in a loop
# last_email_sent_time = 0


# messages = [
#     "3 Blade Rotor drone detected",
#     "Quadcopter drone detected",
#     "Bionic drone detected",
# ]
# detection_message_text = random.choice(messages)
# detection_message = header_font.render(detection_message_text, True, RED)

# def log_detection(timestamp, angle, x, y):
#     # Calculate distance and speed
#     distance = math.hypot(x - radar_x, y - radar_y)
#     speed = distance / 0.7  # Placeholder value for speed; update based on your logic

#     # Define the CSV file path
#     csv_file = "detection_log.csv"
    
#     # Check if the file exists
#     file_exists = os.path.exists(csv_file)

#     # Open the file in append mode
#     with open(csv_file, "a", newline='') as log_file:
#         fieldnames = ["timestamp", "angle", "latitude", "longitude", "distance", "speed"]
#         writer = csv.DictWriter(log_file, fieldnames=fieldnames)

#         # Write the header if the file is new
#         if not file_exists:
#             writer.writeheader()

#         # Write the log entry
#         log_entry = {
#             "timestamp": timestamp,
#             "angle": round(angle, 2),
#             "latitude": round(x, 2),
#             "longitude": round(y, 2),
#             "distance": round(distance, 2),
#             "speed": round(speed, 2)
#         }
#         writer.writerow(log_entry)

#     print(f"Logged entry: {log_entry}")

# def send_email_alert(timestamp, angle, x, y):
#     subject = "Alert: Drone Detected"
#     body = f"A drone was detected at {timestamp}. \n\nDetails:\nAngle: {angle:.2f}°\nLatitude: {x:.2f}\nLongitude: {y:.2f}"
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = 'nkharshbachhav@gmail.com'
#     msg['To'] = 'nkharshbachhav@gmail.com'
    
#     try:
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login('nkharshbachhav@gmail.com', 'qkbd smit xtqi qvoa')  # Update with the correct password
#             server.sendmail(msg['From'], [msg['To']], msg.as_string())
#         print("Alert email sent successfully.")
#         log_detection(timestamp, angle, x, y)
#     except Exception as e:
#         print(f"Failed to send email: {e}")

# def threaded_email_alert(timestamp, angle, x, y):
#     threading.Thread(target=send_email_alert, args=(timestamp, angle, x, y)).start()

# def draw_header():
#     header_text = header_font.render("Drone/Bird Classifier", True, WHITE)
#     screen.blit(header_text, (width // 2 - header_text.get_width() // 2, 20))
    
#     current_time = get_current_time()
#     timezone_name = get_timezone_name()
#     time_text = digital_font.render(f"Time: {current_time} ({timezone_name})", True, YELLOW)
    
#     time_text_y = 20 + header_text.get_height() + 10
#     screen.blit(time_text, (width - time_text.get_width() - 20, time_text_y))

# def draw_radar_circle():
#     pygame.draw.circle(screen, GREEN, (radar_x, radar_y), radar_radius + 10, 2)
#     pygame.draw.circle(screen, GREEN, (radar_x, radar_y), radar_radius, 2)
#     for r in range(radar_radius // 4, radar_radius, radar_radius // 4):
#         pygame.draw.circle(screen, DARK_GREEN, (radar_x, radar_y), r, 1)

# def draw_radar_lines():
#     for angle in range(0, 360, 30):
#         rad = math.radians(angle)
#         pygame.draw.line(screen, DARK_GREEN, (radar_x, radar_y),
#                          (radar_x + radar_radius * math.cos(rad),
#                           radar_y + radar_radius * math.sin(rad)))

# def draw_sweep_area(angle):
#     arc_width = math.pi / 6
#     start_angle = angle - arc_width / 2
#     end_angle = angle + arc_width / 2
#     points = [
#         (radar_x, radar_y),
#         (radar_x + radar_radius * math.cos(start_angle), radar_y + radar_radius * math.sin(start_angle)),
#         (radar_x + radar_radius * math.cos(end_angle), radar_y + radar_radius * math.sin(end_angle))
#     ]
#     s = pygame.Surface((width, height), pygame.SRCALPHA)
#     pygame.draw.polygon(s, FAINT_GREEN, points)
#     screen.blit(s, (0, 0))

# def draw_objects(detected_drone=None, blink=True, graph_x=660, graph_y=200, graph_height=300):
#     current_time = pygame.time.get_ticks()
#     alpha = int((math.sin(current_time / 1000.0 * math.pi) + 1) / 2 * 255) if blink else 255
    
    
#     for obj in objects:
#         color = RED if obj == detected_drone else GREEN
#         s = pygame.Surface((20, 20), pygame.SRCALPHA)
#         pygame.draw.circle(s, (*color[:3], alpha), (10, 10), 10)
#         screen.blit(s, (int(obj[0]) - 10, int(obj[1]) - 10))
#     if detected_drone:
#      pygame.time.delay(100)        #################DELAY 
#      obj_x, obj_y, obj_type = detected_drone
#      obj_distance = math.hypot(obj_x - radar_x, obj_y - radar_y)
#      obj_speed = obj_distance / 0.7  # Placeholder value for speed; update based on your logic
    
#     # Render the distance and speed text
#      distance_text = digital_font.render(f"Distance: {obj_distance:.2f}", True, RED)
#      speed_text = digital_font.render(f"Speed: {obj_speed:.2f} km/h", True, RED)
    
#     # Display the distance and speed on the screen
#      screen.blit(distance_text, (graph_x, graph_y + graph_height + 60))
#      screen.blit(speed_text, (graph_x, graph_y + graph_height + 80))
    
#     # Render the "Drone detected" message
#      # Randomly choose a message
 

# # Render the chosen message
    
    
    
#     # Calculate the position to center the message on the screen
#      message_x = (width - detection_message.get_width()) // 2
#      message_y = (height - detection_message.get_height()) // 2
    
#     # Display the "Drone detected" message in the center of the screen
#      screen.blit(detection_message, (message_x, message_y))


# def generate_complex_wave(x, time_factor):
#     y = 20 * np.sin(0.5 * x + time_factor)
#     y += 10 * np.sin(2 * x + 1.5 * time_factor)
#     y += 10 * np.sin(4 * x + 2 * time_factor)
#     y += np.random.normal(0, 5, len(x))
#     spike_locations = np.random.choice(len(x), 3, replace=False)
#     y[spike_locations] += np.random.uniform(20, 40, 3)
#     y += 10 * np.sin(0.1 * x + 0.1 * time_factor)
#     return y


# def open_log_button(screen, x, y, width, height, button_text, font, button_color, text_color, log_file_path):
#     pygame.draw.rect(screen, button_color, (x, y, width, height))
#     text_surface = font.render(button_text, True, text_color)
#     text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
#     screen.blit(text_surface, text_rect)

#     # Check for mouse events
#     mouse_pos = pygame.mouse.get_pos()
#     mouse_click = pygame.mouse.get_pressed()

#     if (x <= mouse_pos[0] <= x + width and
#         y <= mouse_pos[1] <= y + height and
#         mouse_click[0] == 1):
#         if os.path.exists(log_file_path):
#             webbrowser.open(log_file_path)
#         else:
#             print("Log file does not exist.")

# def draw_realistic_wave(time_factor):
#     graph_x = 660
#     graph_y = 200
#     graph_width = 500
#     graph_height = 300
#     pygame.draw.rect(screen, WHITE, (graph_x, graph_y, graph_width, graph_height), 2)
#     x = np.linspace(0, 20, graph_width)
#     y = generate_complex_wave(x, time_factor)
#     scaled_y = graph_y + graph_height // 2 - (y / max(abs(y)) * (graph_height // 2)).astype(int)
#     for i in range(len(scaled_y) - 1):
#         pygame.draw.line(screen, WHITE, (graph_x + i, scaled_y[i]), (graph_x + i + 1, scaled_y[i + 1]))

# # Main loop
# running = True
# clock = pygame.time.Clock()
# time_factor = 0
# font = pygame.font.Font(None, 36)
# button_color = (0, 128, 255)
# text_color = (255, 255, 255)

# # Path to the log file
# log_file_path = "detection_log.csv"

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_q:
#                 running = False
#             if event.key == pygame.K_m:
#                 pygame.mixer.music.set_volume(0.5 if pygame.mixer.music.get_volume() > 0 else 1)

#     screen.fill(BLACK)
#     draw_header()
#     draw_radar_circle()
#     draw_radar_lines()
#     open_log_button(screen, 50, 50, 200, 50, "Open Log", font, button_color, text_color, log_file_path)
#     sweep_angle += sweep_speed
#     if sweep_angle > 2 * math.pi:
#         sweep_angle -= 2 * math.pi

#     draw_sweep_area(sweep_angle)
    
#     detected_drone = None
#     for obj in objects:
#         obj_x, obj_y, obj_type = obj
#         angle_to_object = math.atan2(obj_y - radar_y, obj_x - radar_x)
#         if angle_to_object < 0:
#             angle_to_object += 2 * math.pi
#         angle_difference = abs(angle_to_object - sweep_angle)
#         if angle_difference < sweep_speed * 10 and obj_type == "drone":
#             detected_drone = obj
#             beep_sound.play()
#             current_time = pygame.time.get_ticks()
#             time_since_last_email = current_time - last_email_sent_time
#             if time_since_last_email > 10000:
#                 timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 threaded_email_alert(timestamp, math.degrees(angle_to_object), obj_x, obj_y)
#                 last_email_sent_time = current_time

#     draw_objects(detected_drone)
#     draw_realistic_wave(time_factor)
#     time_factor += 0.1
#    # screen.blit(logo_image, logo_rect)
#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
