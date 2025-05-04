import pygame
import sys

pygame.init()

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Dashboard")

# Fonts and colors
font = pygame.font.SysFont("Arial", 30, bold=True)
title_font = pygame.font.SysFont("Arial", 48, bold=True)
button_color = (220, 220, 250)
hover_color = (180, 180, 255)
text_color = (30, 30, 30)
bg_color_start = (245, 245, 255)  # Top of the gradient
bg_color_end = (200, 200, 255)    # Bottom of the gradient

# Game buttons (Updated width and centered position)
button_width = 250
button_height = 50
button_spacing = 20  # Spacing between buttons vertically
buttons = [
    {"name": "Chess", "rect": pygame.Rect((screen_width - button_width) // 2, 150 + button_height + button_spacing, button_width, button_height), "action": None}
]

def draw_gradient_background():
    """Create a vertical gradient background."""
    for y in range(screen_height):
        color = (
            int(bg_color_start[0] + (bg_color_end[0] - bg_color_start[0]) * y / screen_height),
            int(bg_color_start[1] + (bg_color_end[1] - bg_color_start[1]) * y / screen_height),
            int(bg_color_start[2] + (bg_color_end[2] - bg_color_start[2]) * y / screen_height)
        )
        pygame.draw.line(screen, color, (0, y), (screen_width, y))

def draw_rounded_rect(surface, color, rect, radius=15):
    """Draw a rounded rectangle."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_dashboard():
    screen.fill((0, 0, 0, 0))  # Transparent background to layer the gradient behind the buttons
    draw_gradient_background()

    # Title
    title_text = title_font.render("Game Dashboard", True, text_color)
    screen.blit(title_text, ((screen_width - title_text.get_width()) // 2, 40))

    # Draw buttons
    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        # Add hover effect
        if btn["rect"].collidepoint(mouse_pos):
            draw_rounded_rect(screen, hover_color, btn["rect"])
        else:
            draw_rounded_rect(screen, button_color, btn["rect"])

        # Text for button
        text = font.render(btn["name"], True, text_color)
        screen.blit(
            text,
            (
                btn["rect"].x + (btn["rect"].width - text.get_width()) // 2,
                btn["rect"].y + (btn["rect"].height - text.get_height()) // 2,
            ),
        )

    pygame.display.flip()

def dashboard_loop():
    while True:
        draw_dashboard()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn["rect"].collidepoint(event.pos):
                        if btn["name"] == "Chess":
                            from chess.main import run
                            run()

        pygame.time.delay(100)

if __name__ == "__main__":
    dashboard_loop()
