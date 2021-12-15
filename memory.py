"""
The Memory game has appeared in many different contexts, either as a computer game or as a card game that uses a partial
 or full deck of playing cards. The player tries to find two matching tiles by selecting tiles from a rectangular grid.
 This game also appeared as a popular American TV show called Concentration. We will create a single person game that
 tracks the score of the player as the time taken to complete the game, where a lower score is better. Multiple players
 can take turns playing the game and compete by comparing their scores.

"""

import pygame
import random


def main():
    pygame.init()
    pygame.display.set_mode((500, 400))
    pygame.display.set_caption('Memory')
    w_surface = pygame.display.get_surface()
    game = Game(w_surface)
    game.play()
    pygame.quit()


class Game:
    def __init__(self, surface):
        self.surface = surface
        self.bg_color = pygame.Color('black')
        self.fg_color = pygame.Color('white')

        self.FPS = 60
        self.game_Clock = pygame.time.Clock()
        self.close_clicked = False
        self.continue_game = True
        self.click = False  # The check procedure will active only when user click their mouse.

        self.score = 0

        self.board_size = 4

        self.images = []  # All 16 images.
        self.board = []  # The 4x4 board.
        self.record = []  # Store previous data in order to compare.

        # The coordinates of the image.
        self.x = 0
        self.y = 0

        self.question = pygame.image.load('image0.bmp')

        # Add eight images to the images list, double it, and shuffle it.
        for i in range(1, 9):
            self.images.append(pygame.image.load('image' + str(i) + '.bmp'))
        self.images += self.images
        random.shuffle(self.images)

        self.create_board()

    def play(self):
        while not self.close_clicked:
            self.handle_events()
            self.draw()
            if self.continue_game:
                self.update()
                self.decide_continue()
            self.game_Clock.tick(self.FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_clicked = True
            elif event.type == pygame.MOUSEBUTTONUP and self.continue_game:
                self.x, self.y = event.pos  # Get mouse position.
                self.click = True

    def get_location(self):
        # It convert the mouse location into corresponding position in the board.

        target = [self.y // 100, self.x // 100]
        return target

    def draw(self):
        self.surface.fill(self.bg_color)
        self.draw_score()

        # Draw all 16 tiles in the board.
        for i in self.board:
            for j in i:
                j.draw()

        pygame.display.update()

    def draw_score(self):
        font = pygame.font.SysFont('Times New Roman', 50)
        text_box = font.render(str(self.score), True, self.fg_color, None)
        location = (self.surface.get_width() - text_box.get_width(), 0)
        self.surface.blit(text_box, location)

    def update(self):
        self.score = pygame.time.get_ticks() // 1000  # Update the score according to game time.
        target = self.get_location()
        if self.click:
            # Check if the clicked position is inside the board and that tile can be turned.
            if (-1 < target[0] < 4 and -1 < target[1] < 4) and not self.board[target[0]][target[1]].get_final():
                self.record.append(target)  # Add target to the input history.
                self.board[target[0]][target[1]].change()  # Turn the corresponding tile.
                # Check if the input history is longer than one, otherwise it can't be compared with the previous data.
                if len(self.record) > 1:
                    # Check if this time and last time's images are identical.
                    if not self.board[self.record[-1][0]][self.record[-1][1]].check_same(self.board[self.record[-2][0]][self.record[-2][1]]):
                        self.surface.blit(self.board[self.record[-1][0]][self.record[-1][1]].get_image(), (self.board[self.record[-1][0]][self.record[-1][1]].get_pos()))
                        pygame.display.update()
                        pygame.time.wait(500)  # After the image turn, wait for 0.5 seconds.
                        # Turn those different images back to question mark.
                        self.board[self.record[-1][0]][self.record[-1][1]].change_back()
                        self.board[self.record[-2][0]][self.record[-2][1]].change_back()
                    self.record = []  # Clear input history.
            self.click = False

    def decide_continue(self):
        # Check if 16 tiles have turned forever.

        counter = 0
        for i in self.board:
            for j in i:
                if j.get_final():
                    counter += 1
        if counter == 16:
            self.continue_game = False

    def create_board(self):
        # The 4x4 board contains 16 different tile objects.

        counter = 0
        width = (self.surface.get_width() - 100) // self.board_size  # The screen is 500x400.
        height = self.surface.get_height() // self.board_size
        for row_index in range(0, self.board_size):
            row = []
            for col_index in range(0, self.board_size):
                x = col_index * width
                y = row_index * height
                tile = Tile(x, y, self.surface, self.images[counter])
                row.append(tile)
                counter += 1
            self.board.append(row)


class Tile:
    def __init__(self, x, y, surface, image):
        self.x = x
        self.y = y
        self.surface = surface
        self.image = image
        self.side = False  # Decide it is image side or question side. False = ?. True = image.
        self.final = False  # Decide whether the tile is turned forever.
        self.last_time = pygame.image  # It record which image the tile currently is.

        self.question = pygame.image.load('image0.bmp')

    def __eq__(self, other):
        # Newly defined equal method.

        return self.num == other.num

    def draw(self):
        # Draw the image based on which side the tile is on and update the last_time variable.

        if not self.side:
            self.surface.blit(self.question, (self.x, self.y))
            self.last_time = self.question
        elif self.side:
            self.surface.blit(self.image, (self.x, self.y))
            self.last_time = self.image

    def change(self):
        # Turn the tile.

        # It can only be turned when the tile haven't be turned forever.
        if not self.final:
            if not self.side:
                self.side = True
            elif self.side:
                self.side = False
            self.final = True  # After each turn, assume the tile is turned forever.

    def change_back(self):
        # This method is used when two images are not same. Set those two variables to False, we can manipulate this
        # tile again.

        self.side = False
        self.final = False

    def get_last_time(self):
        # Return the current image of the tile.

        return self.last_time

    def get_final(self):
        # Return whether it is turned forever.

        return self.final

    def get_image(self):
        # Return what image this tile contains.

        return self.image

    def get_pos(self):
        # Return the position of the tile.

        return self.x, self.y

    def check_same(self, other_tile):
        # Check if this tile is same with other tile based on images.

        return self.image == other_tile.get_last_time()


main()
