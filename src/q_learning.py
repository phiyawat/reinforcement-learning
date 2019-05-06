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
print(grid)
actions = World.actions #   ["up", "left", "down", "right"]
policy_sign = ["^", "<", "v", ">"]
states = []

# start = World.start # (0, World.y - 1)
current = World.start
walls = World.walls
goal = World.goal   #   (World.specials[1][0], World.specials[1][1])
pit = World.pit #   [(World.specials[0][0], World.specials[0][1])]

Q = {}
alpha = 1
score = 1
move_reward = -0.1
goal_reward = 1
pit_reward = -1
move_pass = 0.8
move_fail = 0.1
move_action = [-1, 0, 1]
epsilon = 0.1
episodes = 100000
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
                temp[action] = 0
        Q[state] = temp

def move(action):
    global current, score
    s = current
    (curr_x, curr_y) = current
    r = 0
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
        r = goal_reward
        World.restart = True
    elif current in pit:
        r = pit_reward
        World.restart = True

    World.move_bot(current[0], current[1])

    s2 = current
    return s, action, r, s2

def agent(s,Q):
   a = ['up','left','down','right']
   if Q[s][a[0]] == 0 and Q[s][a[1]] == 0 and Q[s][a[2]] == 0 and Q[s][a[3]] == 0:
       action = np.random.randint(0,4)
       return action
   else:
       max2 = 0
       for i in range(4):
           if Q[s][a[i]] > max2:
               max2 = Q[s][a[i]]
               action = i
       if max2 == 0:
           while(True):
               action = np.random.randint(0,4)
               if Q[s][a[action]] >= 0:
                   break
       return action

def Q_Learning(path,count,reward):    
    path = np.array(path)
   # print("Path: ",path)
    for i in range(path.shape[0]):
        if i+1 < path.shape[0]:
            state = path[i][0]
            action = path[i][1]
            nextState = path[i+1][0]
            nextAction = path[i+1][1]
            alpha = 1/count
            discountRate = World.getNow()
            # print(path)
            
            Q[state][actions[action]] = Q[state][actions[action]] + (alpha* reward * ( (discountRate *Q[nextState][actions[nextAction]]) - Q[state][actions[action]] ))
    print("*************************"+"Round: "+str(count)+"***************************************")
    print("Q",count," ",Q)
    print("********************************************************************************")

def main():
    global alpha, discount, current, score, epsilon, episodes,grid
    iter = 1
    init()
    path = []
    count = 0
    count2 = 0
   
 
   # print(Q)
    while iter != episodes:
        if World.flag is None:
            quit()
        if World.flag is True:
            continue
        
        myaction = agent(current,Q)
        path.append([current,myaction])
        (s, a, reward, s2) = move(actions[myaction])
        if reward == 1:
            count += 1
            path.append([current,myaction])
            Q_Learning(path,count,reward)
            path = []
        elif reward == -1:
            count2 += 1
            # print('punished!!',count2)
            # print(Q)
            Q_Learning(path,count2,-1)
            #Q[current][actions[myaction]] = -1
            path = []


        iter += 1

        if World.restart is True:
            current = World.start
            World.move_bot(current[0], current[1])
            World.restart = False
            World.restart_game()
            alpha = pow(iter, -0.1)
            score = 1

        time.sleep((World.w1.get() + 0.1)/ 100)


t = threading.Thread(target=main)
t.daemon = True
t.start()
World.begin()
