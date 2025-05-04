import pygame

class ChessTooltip:
    def __init__(self, position=(200, 150), size=(400, 200)):
        self.font = pygame.font.SysFont("Arial", 15)
        self.title_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.show_tooltip = False
        self.tooltip_text = ""
        self.tooltip_rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.tooltip_close_rect = pygame.Rect(position[0] + size[0] - 30, position[1] + 10, 20, 20)
        
        # For dragging
        self.is_dragging = False
        self.drag_offset = (0, 0)
        
        # Store screen dimensions for boundary checking
        self.screen_dimensions = (800, 670)  # Default, will be updated on first draw

    def show(self, text):
        self.tooltip_text = text
        self.show_tooltip = True

    def hide(self):
        self.show_tooltip = False

    def handle_event(self, event):
        if not self.show_tooltip:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if close button clicked
            if self.tooltip_close_rect.collidepoint(event.pos):
                self.hide()
                return
                
            # Check if window is being dragged
            if self.tooltip_rect.collidepoint(event.pos):
                self.is_dragging = True
                self.drag_offset = (self.tooltip_rect.x - event.pos[0], 
                                   self.tooltip_rect.y - event.pos[1])
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            # Move tooltip with mouse
            new_x = event.pos[0] + self.drag_offset[0]
            new_y = event.pos[1] + self.drag_offset[1]
            
            # Apply boundary constraints
            new_x = max(10, min(new_x, self.screen_dimensions[0] - self.tooltip_rect.width - 10))
            new_y = max(10, min(new_y, self.screen_dimensions[1] - self.tooltip_rect.height - 10))
            
            self.tooltip_rect.x = new_x
            self.tooltip_rect.y = new_y
            self.tooltip_close_rect.x = new_x + self.tooltip_rect.width - 30
            self.tooltip_close_rect.y = new_y + 10

    def draw(self, screen):
        if self.show_tooltip:
            # Update screen dimensions (in case of window resize)
            self.screen_dimensions = screen.get_size()
            
            # Make sure tooltip is within screen boundaries
            if self.tooltip_rect.right > self.screen_dimensions[0]:
                self.tooltip_rect.x = self.screen_dimensions[0] - self.tooltip_rect.width - 10
                self.tooltip_close_rect.x = self.tooltip_rect.x + self.tooltip_rect.width - 30
            if self.tooltip_rect.bottom > self.screen_dimensions[1]:
                self.tooltip_rect.y = self.screen_dimensions[1] - self.tooltip_rect.height - 10
                self.tooltip_close_rect.y = self.tooltip_rect.y + 10
            
            # Semi-transparent background
            bg_surface = pygame.Surface((self.tooltip_rect.width, self.tooltip_rect.height), pygame.SRCALPHA)
            bg_surface.fill((50, 50, 50, 230))  # RGBA - semi-transparent
            screen.blit(bg_surface, (self.tooltip_rect.x, self.tooltip_rect.y))
            
            # Border
            pygame.draw.rect(screen, (200, 200, 200), self.tooltip_rect, 2, border_radius=10)
            
            # Title bar
            title_bar_rect = pygame.Rect(self.tooltip_rect.x, self.tooltip_rect.y, 
                                         self.tooltip_rect.width, 30)
            pygame.draw.rect(screen, (30, 30, 80), title_bar_rect, border_radius=10)
            
            # Title
            title_text = self.title_font.render("Chess Hint", True, (255, 255, 255))
            screen.blit(title_text, (self.tooltip_rect.x + 10, self.tooltip_rect.y + 5))
            
            # Close "X" button
            pygame.draw.rect(screen, (200, 50, 50), self.tooltip_close_rect, border_radius=5)
            x_text = self.font.render('X', True, (255, 255, 255))
            screen.blit(x_text, (self.tooltip_close_rect.x + 5, self.tooltip_close_rect.y + 2))

            # Wrap and render the tooltip text
            wrapped_lines = []
            words = self.tooltip_text.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if self.font.size(test_line)[0] < self.tooltip_rect.width - 40:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word + " "
            wrapped_lines.append(line)

            for idx, l in enumerate(wrapped_lines):
                text_surf = self.font.render(l.strip(), True, (255, 255, 255))
                screen.blit(text_surf, (self.tooltip_rect.x + 20, 
                                        self.tooltip_rect.y + 40 + idx * 20)) 