import math

import numpy as np
import pygame
import sys

class ForestFireSimulation:
    def __init__(self, size=(50, 50), density=0.6, ignition_probability=0.1, initial_image_path=None,
                 initial_fire=None):
        self.size = size
        self.density = density
        self.ignition_probability = ignition_probability
        self.initial_fire = initial_fire
        self.humidity = 9
        self.wind_horizontal = 0.5
        self.wind_vertical = 0.5
        self.size_wall = 0
        self.which_drop = 0
        self.time = 0
        self.fire_fight = 0  #gaszenie
        if initial_image_path:
            self.load_initial_image(initial_image_path)
        else:
            self.grid = np.random.choice([1, 3], size=self.size, p=[density, 1 - density])

        if initial_fire:
            for i, j in initial_fire:
                self.grid[i, j] = 2
        else:
            self.grid = np.random.choice([2, 3], size=self.size, p=[density, 1 - density])
        pygame.init()
        self.screen_size = (self.size[1] * 5, self.size[0] * 8)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()

        # Inicjalizacja wartości suwaka wilgotności
        self.humidity_slider_rect = pygame.Rect(400, 560, 200, 10)
        self.humidity_value = self.humidity
        self.humidity_dragging = False

        # Inicjalizacja wartości suwaka wiatru poziomego
        self.wind_horizontal_slider_rect = pygame.Rect(400, 440, 200, 10)
        self.wind_horizontal_value = self.wind_horizontal
        self.wind_horizontal_dragging = False

        # Inicjalizacja wartości suwaka wiatru pionowego
        self.wind_vertical_slider_rect = pygame.Rect(400, 500, 200, 10)
        self.wind_vertical_value = self.wind_vertical
        self.wind_vertical_dragging = False

        # Inicjalizacja czcionki do wyświetlania tekstu
        self.font = pygame.font.Font(None, 36)

        # Inicjalizacja przycisków Wall i Helicopter
        self.wall_button_rect = pygame.Rect(40, 440, 100, 50)
        self.helicopter_button_rect = pygame.Rect(190, 440, 150, 50)

        # Inicjalizacja przycisku restart
        self.restart_button_rect = pygame.Rect(40, 530, 100, 50)

    def load_initial_image(self, image_path):
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (self.size[1] * 5, self.size[0] * 5))
        self.grid = np.zeros(self.size, dtype=int)
        self.color_grid = np.zeros(self.size + (3,), dtype=int)

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                r, g, b, _ = image.get_at((j * 5, i * 5))
                if r == 0 and g == 0 and b == 255:
                    self.grid[i, j] = 1
                elif r == 255 and g == 0 and b == 0:
                    self.grid[i, j] = 2
                elif r == 139 and g == 69 and b == 19:
                    self.grid[i, j] = 5
                elif r == 0 and g == 255 and b == 0:
                    self.grid[i, j] = 3
                elif r == 66 and g == 40 and b == 14:
                    self.grid[i, j] = 7
                elif r == 224 and g == 255 and b == 255:
                    self.grid[i, j] = 6
                self.color_grid[i, j] = (r, g, b)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.humidity_slider_rect.collidepoint(event.pos):
                    self.humidity_dragging = True
                elif self.wind_horizontal_slider_rect.collidepoint(event.pos):
                    self.wind_horizontal_dragging = True
                elif self.wind_vertical_slider_rect.collidepoint(event.pos):
                    self.wind_vertical_dragging = True
                elif self.wall_button_rect.collidepoint(event.pos):
                    self.fire_fight = 1  # Ustawienie trybu Wall
                elif self.helicopter_button_rect.collidepoint(event.pos):
                    self.fire_fight = 2  # Ustawienie trybu Helicopter
                elif self.restart_button_rect.collidepoint(event.pos):
                    self.restart_simulation()  # Dodano obsługę przycisku restart
            elif event.type == pygame.MOUSEBUTTONUP:
                self.humidity_dragging = False
                self.wind_horizontal_dragging = False
                self.wind_vertical_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.humidity_dragging:
                    # Dostosuj wilgotność na podstawie pozycji myszki
                    mouse_x, _ = event.pos
                    slider_x = mouse_x - self.humidity_slider_rect.width / 2
                    slider_x = max(self.humidity_slider_rect.x,
                                   min(slider_x, self.humidity_slider_rect.x + self.humidity_slider_rect.width - 1))
                    self.humidity_value = (slider_x - self.humidity_slider_rect.x) / self.humidity_slider_rect.width * (
                                10.0 - 0.5) + 0.5
                    self.humidity = self.humidity_value
                elif self.wind_horizontal_dragging:
                    # Dostosuj wiatr poziomy na podstawie pozycji myszki
                    mouse_x, _ = event.pos
                    slider_x = mouse_x - self.wind_horizontal_slider_rect.width / 2
                    slider_x = max(self.wind_horizontal_slider_rect.x, min(slider_x, self.wind_horizontal_slider_rect.x + self.wind_horizontal_slider_rect.width - 1))
                    self.wind_horizontal_value = (slider_x - self.wind_horizontal_slider_rect.x) / self.wind_horizontal_slider_rect.width
                elif self.wind_vertical_dragging:
                    # Dostosuj wiatr pionowy na podstawie pozycji myszki
                    mouse_x, _ = event.pos
                    slider_x = mouse_x - self.wind_vertical_slider_rect.width / 2
                    slider_x = max(self.wind_vertical_slider_rect.x, min(slider_x,
                                                                         self.wind_vertical_slider_rect.x + self.wind_vertical_slider_rect.width - 1))
                    self.wind_vertical_value = (
                                                    slider_x - self.wind_vertical_slider_rect.x) / self.wind_vertical_slider_rect.width

    def restart_simulation(self):
        # Tworzenie nowej instancji symulacji
        initial_fire = [(20, 80)]
        new_simulation = ForestFireSimulation(size=(80, 130), ignition_probability=0.7, initial_image_path='colored_image.png',
                                             initial_fire=initial_fire)

        # Uruchamianie nowej instancji symulacji
        new_simulation.visualize()

    def draw_restart_button(self):
        # Rysowanie przycisku restart
        pygame.draw.rect(self.screen, (255,0,0), self.restart_button_rect)
        text = self.font.render("Restart", True, (0,0,0))
        text_rect = text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(text, text_rect)

    def draw_buttons(self):
        # Rysowanie przycisku Wall
        pygame.draw.rect(self.screen, (255,255,255), self.wall_button_rect)
        text = self.font.render("Wall", True, (0,0,0))
        text_rect = text.get_rect(center=self.wall_button_rect.center)
        self.screen.blit(text, text_rect)

        # Rysowanie przycisku Helicopter
        pygame.draw.rect(self.screen, (255,255,255), self.helicopter_button_rect)
        text = self.font.render("Helicopter", True, (0,0,0))
        text_rect = text.get_rect(center=self.helicopter_button_rect.center)
        self.screen.blit(text, text_rect)
    def update(self):
        new_grid = np.copy(self.grid)
        for i in range(0, self.size[0]):
            for j in range(0, self.size[1]):
                if self.grid[i, j] == 2 and (np.random.random() < self.ignition_probability):
                    new_grid[i, j] = 5

        for i in range(1, self.size[0] - 1):
            for j in range(1, self.size[1] - 1):
                if self.grid[i, j] == 5:
                    neighbors = [[i + 1, j,np.random.random() > self.wind_vertical_value], [i - 1, j,np.random.random() < self.wind_vertical_value], [i, j + 1,np.random.random() > self.wind_horizontal_value], [i, j - 1,np.random.random() < self.wind_horizontal_value]]
                    for element in neighbors:
                        if self.grid[element[0], element[1]] == 3 and element[2]:
                            new_grid[element[0], element[1]] = 2
        self.grid = np.copy(new_grid)

    def extinguish_wall(self):
        new_grid = np.copy(self.grid)
        if initial_fire:
            for i, j in initial_fire:
                #math.ceil(self.time/math.sqrt(2)) - optymalizacja przy użyciu pitagorasa
                wall = [[i + 3 + math.ceil(self.time/math.sqrt(2)) - k, j - k] for k in range(0, self.size_wall)] + \
                       [[i - 3 - math.ceil(self.time/math.sqrt(2)) + k, j + k] for k in range(0, self.size_wall)] + \
                       [[i - k, j + 3 + math.ceil(self.time/math.sqrt(2)) - k] for k in range(0, self.size_wall)] + \
                       [[i + k, j - 3 - math.ceil(self.time/math.sqrt(2)) + k] for k in range(0, self.size_wall)]
                wall += [[i + 3 + math.ceil(self.time/math.sqrt(2)) - k, j + k] for k in range(0, self.size_wall)] + \
                       [[i - 3 - math.ceil(self.time/math.sqrt(2)) + k, j - k] for k in range(0, self.size_wall)] + \
                       [[i + k, j + 3 + math.ceil(self.time/math.sqrt(2)) - k] for k in range(0, self.size_wall)] + \
                       [[i - k, j - 3 - math.ceil(self.time/math.sqrt(2)) + k] for k in range(0, self.size_wall)]
        for element in wall:
            if element[0] >= 0 and element[1] >= 0: #zabezpieczenie przed wychodzeniem za ramke
                if self.grid[element[0], element[1]] == 3:
                    new_grid[element[0], element[1]] = 7
        if self.size_wall < math.ceil(2 + self.time/2):
            self.size_wall += 1
        self.grid = np.copy(new_grid)

    def extinguish_helicopter(self):
        new_grid = np.copy(self.grid)
        u_can_throw = 0
        if initial_fire:
            for i, j in initial_fire:
                distance = 7 + math.ceil(self.time/math.sqrt(2))
                water_bombs = [[i + distance, j],
                               [i + math.ceil(distance/2), j + math.ceil(distance/2)],
                               [i, j + distance],
                               [i - math.ceil(distance/2), j + math.ceil(distance/2)],
                               [i - distance, j],
                               [i - math.ceil(distance/2), j - math.ceil(distance/2)],
                               [i, j - distance],
                               [i + math.ceil(distance/2), j - math.ceil(distance/2)]]

            for i in range(0, self.size[0]):
                for j in range(0, self.size[1]):
                    if self.grid[i, j] == 2:
                        u_can_throw = 1
            if u_can_throw == 1:
                for i in range(self.which_drop):
                    if water_bombs[i][0] >= 0 and water_bombs[i][1] >= 0:  # zabezpieczenie przed wychodzeniem za ramke
                        if self.grid[water_bombs[i][0], water_bombs[i][1]] == 3:
                            new_grid[water_bombs[i][0], water_bombs[i][1]] = 6
                for i in range(1, self.size[0] - 1):
                    for j in range(1, self.size[1] - 1):
                        if self.grid[i, j] == 6:
                            neighbors = [[i + 1, j], [i - 1, j], [i, j + 1], [i, j - 1]]
                            for element in neighbors:
                                if element[0] >= 0 and element[1] >= 0:  # zabezpieczenie przed wychodzeniem za ramke
                                    if self.grid[element[0], element[1]] == 3 or self.grid[element[0], element[1]] == 2:
                                        new_grid[element[0], element[1]] = 6

        if self.which_drop < 8:
            self.which_drop += 1
        self.grid = np.copy(new_grid)

    def draw_sliders(self):
        # Rysowanie suwaka wilgotności
        pygame.draw.rect(self.screen, (255, 255, 255), self.humidity_slider_rect)
        slider_pos = (
            int(self.humidity_slider_rect.x + (self.humidity_value - 0.5) / (
                        10.0 - 0.5) * self.humidity_slider_rect.width),
            self.humidity_slider_rect.y + self.humidity_slider_rect.height // 2
        )
        pygame.draw.circle(self.screen, (255, 0, 0), slider_pos, 10)

        # Wyświetlanie napisu "Wilgotność"
        text = self.font.render("Humidity", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (self.humidity_slider_rect.x, self.humidity_slider_rect.y - 30)
        self.screen.blit(text, text_rect)

        # Rysowanie suwaka wiatru poziomego
        pygame.draw.rect(self.screen, (255, 255, 255), self.wind_horizontal_slider_rect)
        wind_horizontal_slider_pos = (
            int(self.wind_horizontal_slider_rect.x + self.wind_horizontal_value * self.wind_horizontal_slider_rect.width),
            self.wind_horizontal_slider_rect.y + self.wind_horizontal_slider_rect.height // 2
        )
        pygame.draw.circle(self.screen, (255, 0, 0), wind_horizontal_slider_pos, 10)

        # Wyświetlanie napisu "Wiatr Poziomy"
        wind_horizontal_text = self.font.render("Horizontal wind", True, (255, 255, 255))
        wind_horizontal_text_rect = wind_horizontal_text.get_rect()
        wind_horizontal_text_rect.topleft = (
        self.wind_horizontal_slider_rect.x, self.wind_horizontal_slider_rect.y - 30)
        self.screen.blit(wind_horizontal_text, wind_horizontal_text_rect)

        # Rysowanie suwaka wiatru pionowego
        pygame.draw.rect(self.screen, (255, 255, 255), self.wind_vertical_slider_rect)
        wind_vertical_slider_pos = (
            int(self.wind_vertical_slider_rect.x + self.wind_vertical_value * self.wind_vertical_slider_rect.width),
            self.wind_vertical_slider_rect.y + self.wind_vertical_slider_rect.height // 2
        )
        pygame.draw.circle(self.screen, (255, 0, 0), wind_vertical_slider_pos, 10)

        # Wyświetlanie napisu "Wiatr Pionowy"
        wind_vertical_text = self.font.render("Veritcal wind", True, (255, 255, 255))
        wind_vertical_text_rect = wind_vertical_text.get_rect()
        wind_vertical_text_rect.topleft = (self.wind_vertical_slider_rect.x, self.wind_vertical_slider_rect.y - 30)
        self.screen.blit(wind_vertical_text, wind_vertical_text_rect)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.draw_sliders()
        self.draw_buttons()
        self.draw_restart_button()

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.grid[i, j] == 1:
                    color = (0, 0, 255)
                elif self.grid[i, j] == 2:
                    color = (255, 0, 0)
                elif self.grid[i, j] == 5:
                    color = (139, 69, 19)
                elif self.grid[i, j] == 3:
                    color = (0, 255, 0)
                elif self.grid[i, j] == 7:
                    color = (60, 40, 14)
                elif self.grid[i, j] == 6:
                    color = (224, 255, 255)
                else:
                    color = self.color_grid[i, j]

                pygame.draw.rect(self.screen, color, (j * 5, i * 5, 4, 4))

    def visualize(self):
        while True:
            self.handle_events()
            self.update()
            if self.fire_fight == 1:  # Jeżeli wybrano tryb Wall
                self.extinguish_wall()
            if self.fire_fight == 2:  # Jeżeli wybrano tryb Helicopter
                self.extinguish_helicopter()
            if self.fire_fight == 0:
                self.time += 1
            self.draw()
            pygame.display.flip()
            self.clock.tick(11-self.humidity)

# Example usage:
if __name__ == "__main__":
    initial_fire = [(20,80)]
    forest_fire = ForestFireSimulation(size=(80, 130), ignition_probability=0.7, initial_image_path='colored_image.png',
                                       initial_fire=initial_fire)
    forest_fire.visualize()
