import pygame


class Button:
    def __init__(self, text, width, height, pos, screen):
        self.top_rect = pygame.Rect((pos[0] - width/2, pos[1] - height/2), (width, height))
        self.top_color = '#475F77'
        self.screen = screen
        self.width = width
        self.height = height

        self.text_surface = pygame.font.Font(None, 25).render(text, True, '#FFFFFF')
        self.text_rect = self.text_surface.get_rect(center=self.top_rect.center)

    def draw(self):
        pygame.draw.rect(self.screen, self.top_color, self.top_rect, border_radius=12)
        self.screen.blit(self.text_surface, self.text_rect)

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                self.top_color = '#D74B4B'
                return True
        else:
            self.top_color = '#475F77'

        return False
