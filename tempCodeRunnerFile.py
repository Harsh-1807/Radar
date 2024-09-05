#def radar_scan_effect(center_x, center_y, radius, scan_angle, scan_speed, color=(0, 255, 255), alpha=100):
#     """
#     Draws an animated radar scan effect.
    
#     Args:
#         center_x (int): The x-coordinate of the radar center.
#         center_y (int): The y-coordinate of the radar center.
#         radius (int): The radius of the radar.
#         scan_angle (float): The current angle of the scan line (in radians).
#         scan_speed (float): The speed of the scan line (in radians per second).
#         color (tuple): The RGB color of the scan line (default: (0, 255, 255)).
#         alpha (int): The transparency of the scan line (default: 100).
#     """
#     # Draw the scan line
#     x1 = center_x + math.cos(scan_angle) * radius
#     y1 = center_y + math.sin(scan_angle) * radius
#     x2 = center_x + math.cos(scan_angle + math.pi) * radius
#     y2 = center_y + math.sin(scan_angle + math.pi) * radius
#     pygame.draw.line(screen, (*color, alpha), (x1, y1), (x2, y2), 4)

#     # Update the scan angle
#     scan_angle += scan_speed
#     if scan_angle > 2 * math.pi:
#         scan_angle -= 2 * math.pi

#     return scan_angle
