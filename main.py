import pygame
import random
import time
import os
import tkinter as tk
from tkinter import filedialog
from settings import *
from solver import resolucao

solving_started = False
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCORE_FILE_PATH = os.path.join(BASE_DIR, "high_score.txt")
CONFIGURACOES = os.path.join(BASE_DIR, "imgs", "configuracao.png")

ALGORITHMS = ["A*", "Busca Gulosa", "Largura"]
HEURISTICS = ["Manhattan", "Distância Euclidiana"]

def draw_text(surface, text, size, x, y, color, center=False, max_width=None):
    font = pygame.font.Font(None, size)
    if max_width:
        words = text.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] > max_width:
                lines.append(line)
                line = word + " "
            else:
                line = test_line
        lines.append(line)

        for i, l in enumerate(lines):
            text_surface = font.render(l.strip(), True, color)
            text_rect = text_surface.get_rect()
            if center:
                text_rect.center = (x, y + i * size)
            else:
                text_rect.topleft = (x, y + i * size)
            surface.blit(text_surface, text_rect)
    else:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_surface, text_rect)


class Button:
    def __init__(self, x, y, w, h, text, color, text_color, image=None, name=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.name = name 
        if image:
            loaded_image = pygame.image.load(image)
            self.image = pygame.transform.scale(loaded_image, (32, 32))  
        else:
            self.image = None

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        
        if self.image:
            img_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, img_rect)
        else:
            text_surface = draw_text(surface, self.text, 22, self.rect.centerx, self.rect.centery, self.text_color, center=True, max_width=self.rect.width - 10)


    def click(self, mx, my):
        return self.rect.collidepoint(mx, my)

    def update_text(self, new_text):
        self.text = new_text

    def is_hovered(self, mx, my):
        return self.rect.collidepoint(mx, my)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.shuffle_time = 0
        self.previous_choice = ""
        self.start_game = False
        self.start_timer = False
        self.elapsed_time = 0
        self.moves = 0
        self.selected_algorithm = "A*"
        self.selected_heuristic = "Manhattan"
        self.high_score = float(self.get_high_scores()[0])
        self.grid_offset_x = (WIDTH - (GAME_SIZE * TILESIZE)) // 2
        self.grid_offset_y = 100
        self.show_settings = False
        self.saved_solution = None
        self.message = ""
        self.message_time = 0
        self.loaded_image = None
        self.tile_images = None

    def run(self):
        self.new()
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.quit()

    def get_high_scores(self):
        if not os.path.exists(SCORE_FILE_PATH):
            with open(SCORE_FILE_PATH, "w") as f:
                f.write("0")
        with open(SCORE_FILE_PATH, "r") as f:
            scores = f.readlines()
            return [score.strip() for score in scores] or ["0"]

    def save_score(self):
        with open(SCORE_FILE_PATH, "w") as file:
            file.write(f"{self.high_score:.3f}\n")

    def create_game(self):
        grid = [[x + y * GAME_SIZE for x in range(1, GAME_SIZE + 1)] for y in range(GAME_SIZE)]
        grid[-1][-1] = 0
        return grid

    def shuffle_many(self, steps=100):
     for _ in range(steps):
        possible_moves = []
        for row, tiles in enumerate(self.tiles_grid):
            for col, tile in enumerate(tiles):
                if tile == 0:
                    if col < GAME_SIZE - 1: possible_moves.append("right")
                    if col > 0: possible_moves.append("left")
                    if row > 0: possible_moves.append("up")
                    if row < GAME_SIZE - 1: possible_moves.append("down")
                    break
            if possible_moves: break

        if self.previous_choice == "right": possible_moves = [move for move in possible_moves if move != "left"]
        elif self.previous_choice == "left": possible_moves = [move for move in possible_moves if move != "right"]
        elif self.previous_choice == "up": possible_moves = [move for move in possible_moves if move != "down"]
        elif self.previous_choice == "down": possible_moves = [move for move in possible_moves if move != "up"]

        choice = random.choice(possible_moves)
        self.previous_choice = choice
        row, col = [(r, c) for r in range(GAME_SIZE) for c in range(GAME_SIZE) if self.tiles_grid[r][c] == 0][0]
        if choice == "right":
            self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], self.tiles_grid[row][col]
        elif choice == "left":
            self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][col - 1], self.tiles_grid[row][col]
        elif choice == "up":
            self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][col], self.tiles_grid[row][col]
        elif choice == "down":
            self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][col], self.tiles_grid[row][col]


    def load_and_split_image(self, image_path):
        image = pygame.image.load(image_path).convert()
        image = pygame.transform.scale(image, (TILESIZE * GAME_SIZE, TILESIZE * GAME_SIZE))
        self.tile_images = []
    
        for row in range(GAME_SIZE):
            row_imgs = []
            for col in range(GAME_SIZE):
                sub_image = image.subsurface(pygame.Rect(col * TILESIZE, row * TILESIZE, TILESIZE, TILESIZE))
                row_imgs.append(sub_image)
            self.tile_images.append(row_imgs)

        self.loaded_image = True

    def draw_tiles(self):
        for row in range(GAME_SIZE):
            for col in range(GAME_SIZE):
                value = self.tiles_grid[row][col]
                x = self.grid_offset_x + col * TILESIZE
                y = self.grid_offset_y + row * TILESIZE
                rect = pygame.Rect(x, y, TILESIZE, TILESIZE)

                if value != 0:
                    pygame.draw.rect(self.screen, (173, 216, 230), rect, border_radius=8)
                    pygame.draw.rect(self.screen, COLOR2, rect, 2, border_radius=8)

                    if self.loaded_image:
                        img_row = (value - 1) // GAME_SIZE
                        img_col = (value - 1) % GAME_SIZE
                        image_part = self.tile_images[img_row][img_col]
                        self.screen.blit(image_part, rect)
                    else:
                        draw_text(self.screen, str(value), 36, rect.centerx, rect.centery, BLACK, center=True)
                else:
                    pygame.draw.rect(self.screen, WHITE, rect)

    def draw_settings_menu(self):
     menu_width = 400
     menu_height = 300 + (len(HEURISTICS) * 40 if self.selected_algorithm == "A*" else 0)
     menu_x = (WIDTH - menu_width) // 2
     menu_y = (HEIGHT - menu_height) // 2
     menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)

     self.settings_rect = menu_rect 

     pygame.draw.rect(self.screen, PINK, menu_rect, border_radius=10)
     pygame.draw.rect(self.screen, COLOR2, menu_rect, 2, border_radius=10)

     draw_text(self.screen, "Algoritmo:", 28, menu_rect.centerx, menu_rect.top + 40, BLACK, center=True)
     for idx, alg in enumerate(ALGORITHMS):
        color = (100, 100, 255) if self.selected_algorithm == alg else BLACK
        draw_text(self.screen, alg, 24, menu_rect.centerx, menu_rect.top + 80 + idx * 40, color, center=True)

     if self.selected_algorithm == "A*":
        draw_text(self.screen, "Heurística:", 28, menu_rect.centerx, menu_rect.top + 80 + len(ALGORITHMS) * 40 + 10, BLACK, center=True)
        for idx, heuristic in enumerate(HEURISTICS):
            color = (100, 100, 255) if self.selected_heuristic == heuristic else BLACK
            draw_text(self.screen, heuristic, 24, menu_rect.centerx, menu_rect.top + 80 + len(ALGORITHMS) * 40 + 50 + idx * 40, color, center=True)

     draw_text(self.screen, "Clique fora da caixa para fechar", 16, menu_rect.centerx, menu_rect.bottom - 30, (100, 100, 100), center=True)

    def new(self):
        self.tiles_grid = self.create_game()
        self.tiles_grid_completed = self.create_game()
        self.elapsed_time = 0
        self.moves = 0
        self.start_timer = False
        self.start_game = False
        start_y = 20
        button_height = 60
        spacing = 20

        button_width = (WIDTH - 80 - 5 * spacing) // 6

        total_buttons_width = 6 * button_width + 5 * spacing
        start_x = (WIDTH - total_buttons_width) // 2


        self.buttons_list = [
            Button(160 , HEIGHT - 150, button_width + 50, 50, "Imagem", PINK, BLACK, name="imagem"),
            Button(320, HEIGHT - 150, button_width + 50, 50, "Salvar Solução", COLOR2, BLACK, name="salvar_solucao"),
            Button(480, HEIGHT - 150, button_width + 50, 50, "Carregar Solução", COLOR3, BLACK, name="carregar_solucao"),
            Button(start_x, start_y, button_width, button_height, "Embaralhar", COLOR2, BLACK, name="embaralhar"),
            Button(start_x + button_width + spacing, start_y, button_width, button_height, "Reiniciar", COLOR3, BLACK, name="reiniciar"),
            Button(start_x + 2 * (button_width + spacing), start_y, button_width, button_height, "Resolver", BLUE, BLACK, name="resolver"),
            Button(50 + 3 * (button_width + spacing), 10, button_width * 2, button_height,
                   f"Algoritmo: {self.selected_algorithm}" +
                   (f" ({self.selected_heuristic})" if self.selected_algorithm == "A*" else ""), LIGHTBLUE, BLACK, name="algoritmo"),
            Button(80 + 5 * (button_width + spacing), start_y, 35, 50, "", LIGHTBLUE, BLACK, image=CONFIGURACOES, name="config")
        ]

    def update(self):
        if self.start_game:
            if self.tiles_grid == self.tiles_grid_completed:
                self.start_game = False
                if self.elapsed_time < self.high_score or self.high_score == 0:
                    self.high_score = self.elapsed_time
                    self.save_score()
            elif self.start_timer:
                self.elapsed_time += 1 / FPS

        if self.message and time.time() - self.message_time > 2:
            self.message = ""



    def animate_solution(self):
        path = resolucao(self.tiles_grid, self.selected_algorithm, self.selected_heuristic)
        if path:
            self.moves = 0
            self.elapsed_time = 0
            self.start_timer = True
            self.start_game = True
            start_time = time.time()

            for state in path[1:]:
                self.tiles_grid = state
                self.moves += 1
                self.elapsed_time = time.time() - start_time
                self.draw()
                pygame.time.delay(300)
            self.elapsed_time = time.time() - start_time
            self.start_timer = False

    def draw(self):
        self.screen.fill(LIGHTBLUE)
        self.draw_tiles()

        for button in self.buttons_list:
            button.draw(self.screen)

        if self.show_settings:
            self.draw_settings_menu()

        text_spacing = 220
        center_y = HEIGHT - 30

        draw_text(self.screen, f"Tempo: {self.elapsed_time:.2f}s", 24, WIDTH // 2 - text_spacing, center_y, BLACK, center=True)
        draw_text(self.screen, f"Movimentos: {self.moves}", 24, WIDTH // 2 + text_spacing, center_y, BLACK, center=True)

        if self.message:
            draw_text(self.screen, self.message, 24, WIDTH // 2, HEIGHT // 2, BLACK, center=True)

        pygame.display.update()



    def upload_image(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.load_and_split_image(file_path)

    def events(self):
     for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.playing = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Verifica se clicou fora da janela de configurações
            if self.show_settings and not self.settings_rect.collidepoint(mx, my):
                self.show_settings = False

            for button in self.buttons_list: 
                if button.name == "config" and button.click(mx, my):
                    self.show_settings = not self.show_settings
                    return  
                
                if button.name == "imagem" and button.click(mx, my):
                    self.upload_image()  # Abre a janela de upload de imagem
                    return 

            if self.show_settings:
                for idx, alg in enumerate(ALGORITHMS):
                    alg_rect_top = self.settings_rect.top + 80 + idx * 40
                    alg_rect_bottom = alg_rect_top + 24  
                    if alg_rect_top <= my <= alg_rect_bottom and self.settings_rect.left <= mx <= self.settings_rect.right:
                        self.selected_algorithm = alg
                        if alg != "A*":
                            self.selected_heuristic = None  # Reseta a heurística se não for A*
                            self.atualizar_texto_botao_algoritmo() 
                        return

                # Verifica cliques na heurística, se estiver visível
                if self.selected_algorithm == "A*":
                    for idx, heuristic in enumerate(HEURISTICS):
                        heuristic_rect_top = self.settings_rect.top + 80 + len(ALGORITHMS) * 40 + 50 + idx * 40
                        heuristic_rect_bottom = heuristic_rect_top + 24
                        if heuristic_rect_top <= my <= heuristic_rect_bottom and self.settings_rect.left <= mx <= self.settings_rect.right:
                            self.selected_heuristic = heuristic
                            self.atualizar_texto_botao_algoritmo()
                            return

            for button in self.buttons_list:
                if button.click(mx, my):
                    if button.text == "Embaralhar":
                        self.shuffle_many(30)
                        self.moves = 0
                        self.elapsed_time = 0
                        self.start_game = True
                        self.start_timer = False

                    elif button.text == "Reiniciar":
                        self.new()

                    elif button.text == "Resolver":
                        self.animate_solution()

                    elif button.text == "Salvar Solução":
                        self.saved_solution = self.tiles_grid
                        self.message = "Solução salva!"
                        self.message_time = time.time()

                    elif button.text == "Carregar Solução":
                        if self.saved_solution:
                            self.tiles_grid = self.saved_solution
                            self.start_game = False
                            self.moves = 0
                            self.elapsed_time = 0
                            self.start_timer = False
                            self.message = "Solução carregada!"
                            self.message_time = time.time()
    def atualizar_texto_botao_algoritmo(self):
     for button in self.buttons_list:
        if button.name == "algoritmo":
            novo_texto = f"Algoritmo: {self.selected_algorithm}"
            if self.selected_algorithm == "A*":
                novo_texto += f" ({self.selected_heuristic})"
            button.update_text(novo_texto)

if __name__ == '__main__':
    game = Game()
    game.run()