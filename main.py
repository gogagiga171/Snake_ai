import time
import random
import tensorflow
import pyray
import matplotlib.pyplot as plt
import numpy as np
from raylib import colors

#игра

class Snake:

    def __init__(self, _x, _y, _previous_part = 0):
        self.previous_part = _previous_part
        self.x = _x
        self.y = _y

    def addPart(self, _previous_part):
        self.previous_part = _previous_part

    def move(self, _x, _y):
        if self.previous_part:
            self.previous_part.move(self.x, self.y)
        self.x = _x
        self.y = _y



class Game:
    field = np.zeros([15, 15])
    snake = []

    def __init__(self):
        self.generateWalls()
        self.snake.append(Snake(8, 8))
        self.snake.append(Snake(7, 8))
        self.snake.append(Snake(6, 8))
        self.snake[0].addPart(self.snake[1])
        self.snake[1].addPart(self.snake[2])
        for s in self.snake:
            self.field[s.x][s.y] = 3
        self.field[self.snake[0].x, self.snake[0].y] = 4
        while not self.addApple():
            pass

    def generateWalls(self): #генерация стен
        if 1 not in self.field:
            for i in range(random.randint(2, 4)):

                width = random.randint(1, 5)
                orientation = random.choice(["vertical", "horizontal"])
                start_pos = [random.randint(1, 10-width), random.randint(1, 10)]

                if orientation == "vertical":

                    ph = start_pos[0]
                    start_pos[0] = start_pos[1]
                    start_pos[1] = ph

                    for j in range(width):
                        self.field[start_pos[0], start_pos[1]+j] = 1

                if orientation == "horizontal":

                    for j in range(width):
                        self.field[start_pos[0]+j, start_pos[1]] = 1

    def addApple(self):
        x = random.randint(0, 14)
        y = random.randint(0, 14)
        if self.field[x][y]==0:
            self.field[x][y]=2
            return True
        return False


    def move(self, _direction):
        if _direction == 1:
            new_x = self.snake[0].x - 1
            new_y = self.snake[0].y
        if _direction == 2:
            new_x = self.snake[0].x
            new_y = self.snake[0].y - 1
        if _direction == 3:
            new_x = self.snake[0].x + 1
            new_y = self.snake[0].y
        if _direction == 4:
            new_x = self.snake[0].x
            new_y = self.snake[0].y + 1

        if new_x == -1 or new_x == 15 or new_y == -1 or new_y == 15:
            return "lose"

        if self.field[new_x][new_y] == 1:
            return "lose"

        if self.field[new_x][new_y] == 3 or self.field[new_x][new_y] == 4:
            return "lose"

        if self.field[new_x][new_y] == 2:
            self.snake.append(Snake(self.snake[-1].x, self.snake[-1].y))
            self.snake[-2].addPart(self.snake[-1])

        self.snake[0].move(new_x, new_y)
        self.updateField()

        if 2 not in self.field:
            if 0 in self.field:
                self.addApple()
            else:
                return "win"

    def updateField(self):
        for i in range(15):
            for j in range(15):

                snake = 0
                for s in self.snake:
                    if s.x == i and s.y == j:
                        snake = 3
                        break
                if self.snake[0].x == i and self.snake[0].y == j:
                    snake = 4


                if self.field[i, j] != 3 and self.field[i, j] != 4 and snake != 0:
                    self.field[i, j] = snake

                elif (self.field[i, j] == 3 or self.field[i, j] == 4) and snake == 0:
                    self.field[i, j] = 0

    def draw(self):
        for i in range(15):
            for j in range(15):
                c = (177, 218, 99, 255)
                if self.field[i, j] == 1:
                    c = (55, 66, 7, 255)
                elif self.field[i, j] == 2:
                    c = (255, 66, 7, 255)
                elif self.field[i, j] == 3 or self.field[i, j] == 4:
                    c = (0, 99, 0, 255)
                pyray.draw_rectangle(i*20, j*20, 20, 20, c)