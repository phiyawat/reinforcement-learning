import numpy as np
import math as math
import World
import threading
import time
import random

# grid = [[0, 0, 0, 0],
#         [0, -99, 0, 0],
#         [0, 0, 0, 0],
#         [0, 0, 0, 0]]
grid = World.grid
actions = World.actions #   ["up", "left", "down", "right"]
policy_sign = ["^", "<", "v", ">"]
states = []

# start = World.start # (0, World.y - 1)
current = World.start
walls = World.walls
goal = World.goal   #   (World.specials[1][0], World.specials[1][1])
pit = World.pit #   [(World.specials[0][0], World.specials[0][1])]

Q = {}
discount = World.discount
alpha = 1
score = 1
move_reward = -1
goal_reward = 1
pit_reward = -1
move_pass = 0.8
move_fail = 0.1
move_action = [-1, 0, 1]
epsilon = 0.1
episodes = 10000
steps = 300


def init():
    for i in range(World.x):
        for j in range(World.y):
            if (i, j) in walls:   
                continue
            states.append((i, j))


    for state in states:
        temp = {}
        for action in actions:
            if state == goal:
                temp[action] = goal_reward
            elif state in pit:
                temp[action] = pit_reward
            else:
                temp[action] = 0.1
        Q[state] = temp

def move(action):
    global current, score
    s = current
    (curr_x, curr_y) = current

    if action == actions[1]:
        current = (curr_x-1 if curr_x-1 >= 0 else curr_x, curr_y)
    elif action == actions[3]:
        current = (curr_x+1 if curr_x+1 < World.x else curr_x, curr_y)
    elif action == actions[0]:
        current = (curr_x, curr_y-1 if curr_y-1 >= 0 else curr_y)
    elif action == actions[2]:
        current = (curr_x, curr_y+1 if curr_y+1 < World.y else curr_y)

    if current in walls:
        current = s
    elif current == goal:
        World.restart = True
    elif current in pit:
        World.restart = True

    World.move_bot(current[0], current[1])
    r = move_reward

    score += r
    s2 = current
    return s, action, r, s2

def main():
    global alpha, discount, current, score, epsilon, episodes
    iter = 1
    init()

    while iter != episodes:
        if World.flag is None:
            quit()
        if World.flag is True:
            continue

        (s, a, reward, s2) = move(actions[2])
        print(reward)

        iter += 1

        if World.restart is True:
            current = World.start
            World.move_bot(current[0], current[1])
            World.restart = False
            World.restart_game()
            alpha = pow(iter, -0.1)
            score = 1

        time.sleep((World.w1.get() + 0.1)/ 100)
        discount = World.discount


t = threading.Thread(target=main)
t.daemon = True
t.start()
World.begin()
