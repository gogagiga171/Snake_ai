import time
import random
import tensorflow
import pyray
import matplotlib.pyplot as plt
#from tf_agents import dqn_agent
import numpy as np
import tf_keras as keras
from collections import deque


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
    apple = [0, 0]

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
        self.last_dist = self.calc_dist()


    def newGame(self):
        self.field = np.zeros([15, 15])
        self.snake = []
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
            self.apple=[x, y]
            return True
        return False

    def calc_dist(self):
        return (abs(self.snake[0].x - self.apple[0])+abs(self.snake[0].y - self.apple[1]))**0.5


    def move(self, _direction):
        if _direction == 1:
            new_x = self.snake[0].x + 1
            new_y = self.snake[0].y
        if _direction == 2:
            new_x = self.snake[0].x
            new_y = self.snake[0].y - 1
        if _direction == 3:
            new_x = self.snake[0].x - 1
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

        while 2 not in self.field:
            if 0 in self.field:
                self.addApple()
                return "ate_apple"
            else:
                return "win"

        if self.calc_dist() < self.last_dist:
            self.last_dist = self.calc_dist()
            return "nearer"
        if self.calc_dist() > self.last_dist:
            self.last_dist = self.calc_dist()
            return "further"

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

    def prepareData(self):
        data = np.zeros(15**2)
        for i in range(15):
            for j in range(15):
                data[j*15+i] = self.field[i][j]
        return np.expand_dims(data, axis=0)


GAMMA = 0.99
ALPHA = 0.001
MEMORY_SIZE = 10000
BATCH_SIZE = 64
EPSILON_START = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995


def build_model(input_shape, output_shape):
    model = keras.Sequential([
        keras.layers.Dense(24, activation='relu', input_shape=input_shape),
        keras.layers.Dense(24, activation='relu'),
        keras.layers.Dense(output_shape, activation='linear')
    ])
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=ALPHA), loss='mse')
    return model


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.epsilon = EPSILON_START
        self.model = build_model((state_size,), action_size)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])

    def replay(self):
        if len(self.memory) < BATCH_SIZE:
            return
        minibatch = random.sample(self.memory, BATCH_SIZE)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += GAMMA * np.amax(self.model.predict(next_state, verbose=0))
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > EPSILON_MIN:
            self.epsilon *= EPSILON_DECAY


def main():
    pyray.init_window(300, 300, "Snake_ai")
    agent = DQNAgent(15**2, 4)
    g = Game()
    EPISODES = 500

    for e in range(EPISODES):
        g.newGame()
        total_reward = 0
        res = "none"
        state = g.prepareData()
        for time in range(500):
            pyray.clear_background((0, 0, 0, 0))
            g.draw()
            pyray.draw_fps(10, 10)
            pyray.end_drawing()
            action = agent.act(state)
            res = g.move(action+1)
            next_state = g.prepareData()
            if res == "lose":
                reward = -2
            if res == "ate_apple":
                reward = 2
            if res == "win":
                reward = 5
            if res == "nearer":
                reward = 0.1
            if res == "further":
                reward = -0.1
            done = res == "win" or res == "lose"
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            if done:
                print(f"Episode: {e + 1}/{EPISODES}, Score: {total_reward}, Epsilon: {agent.epsilon:.2f}")
                break
            agent.replay()

if __name__=="__main__":
    main()