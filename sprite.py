import pygame
import tkinter as tk
from tkinter import filedialog
from settings import WHITE, BLACK

# Função para selecionar imagem usando uma janela do sistema
def selecionar_imagem():
    root = tk.Tk()
    root.withdraw()
    caminho_imagem = filedialog.askopenfilename(
        filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")]
    )
    return caminho_imagem

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text, color, text_color, image=None):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.text_color = text_color
        self.image_icon = image

        self.font = pygame.font.Font(None, 30)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.render_text()

    def render_image(self):
        if self.image_icon:
            icon = pygame.image.load(self.image_icon).convert_alpha()
            icon = pygame.transform.scale(icon, (self.width, self.height))
            self.image.blit(icon, (0, 0))

    def render_text(self):
        self.image.fill((0, 0, 0, 0))  
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height), border_radius=10)

        if self.image_icon:
            self.render_image()

        if not self.text:
            return

        lines = self.wrap_text(self.text, self.width - 20)
        y_offset = (self.height - len(lines) * self.font.get_height()) // 2

        for line in lines:
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.width // 2, y_offset + self.font.get_height() // 2))
            self.image.blit(text_surface, text_rect)
            y_offset += self.font.get_height()

    def wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_surface = self.font.render(test_line, True, self.text_color)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def click(self, mouse_x, mouse_y):
        return self.rect.collidepoint(mouse_x, mouse_y)

    def update_text(self, new_text):
        self.text = new_text
        self.render_text()

class UIElement(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.Font(None, 30)
        self.image = self.font.render(self.text, True, BLACK)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# --- Botão de "Inserir Imagem" ---

upload_image_button = Button(
    x=50,
    y=500,
    width=200,
    height=50,
    text="Inserir Imagem",
    color=(255, 182, 193),  
    text_color=BLACK,
)
