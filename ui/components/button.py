import pygame


class ImageButton:
    def __init__(self, center_x, center_y, normal_image_path, hover_image_path, scale=None):
        self.normal_image = pygame.image.load(normal_image_path).convert_alpha()
        self.hover_image = pygame.image.load(hover_image_path).convert_alpha()

        if scale is not None:
            self.normal_image = pygame.transform.scale(self.normal_image, scale)
            self.hover_image = pygame.transform.scale(self.hover_image, scale)

        self.image = self.normal_image
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def draw(self, screen, alpha=255):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            image = self.hover_image.copy()
        else:
            image = self.normal_image.copy()

        image.set_alpha(alpha)
        screen.blit(image, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            return self.rect.collidepoint(mouse_pos)

        return False