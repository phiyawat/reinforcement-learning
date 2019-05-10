import time
from tkinter import Tk,Entry,Label,X,Canvas,Frame,Scale,Button,StringVar,OptionMenu,SUNKEN,HORIZONTAL,LEFT,BOTTOM,RIGHT,TOP,messagebox,simpledialog,filedialog
from PIL import Image,ImageTk
import numpy as np
import os

master = Tk()
master.wm_title("My Grid World")

result = messagebox.askyesno("Welcome to Grid World","Do you want to create a new map?")

grid = []
path = os.getcwd() + "/images/"

triangle_size = 0.3
text_offset = 17
cell_score_min = -0.2
cell_score_max = 0.2
Width = 70
actions = ["up", "left", "down", "right"]

if not result:
    filename = filedialog.askopenfilename(title = "Select map file")
    print(filename)
    if len(filename) == 0:
        messagebox.showwarning('Error', 'No map selected!')
        quit()
    ins = open(filename, "r")
    for line in ins:
        number_strings = line.split()
        numbers = [int(n) for n in number_strings]
        grid.append(numbers)
    (x, y) = (len(grid[0]), len(grid))
    board = Canvas(master, width=x*Width, height=y*Width)
else:
    x_str = simpledialog.askstring('Size', 'Enter grid size')
    if x_str == None:
        messagebox.showwarning('Error', 'No size found!')
        quit()
    x = int(x_str)
    (x, y) = (x, x)
    path = os.getcwd() + "/images/"
    wall_pic = ImageTk.PhotoImage(file=path+'wall.png')
    diamond_pic = ImageTk.PhotoImage(file=path+'diamond.png')
    ice_pic = ImageTk.PhotoImage(file=path+'ice.png')
    robot_pic = ImageTk.PhotoImage(file=path+'robot.png')
    board = Canvas(master, width=x*Width, height=y*Width)
    start_count = 0
    goal_count = 0
    for i in range(x):
        for j in range(y):
            board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="white", width=1)
    board.pack(side=LEFT)
    grid = [[0 for row in range(x)] for col in range(y)]
    item_grid = [[0 for row in grid[0]] for col in grid]
    var = StringVar(master)
    var.set("Select item")
    option = OptionMenu(master, var, "start", "walls", "goal", "pit")
    option.pack()

    robot = 0
    def create_item(event):
        global robot, start_count, goal_count
        x, y = int(event.x/75), int(event.y/75)
        if item_grid[y][x] == 0:
            if var.get() == "walls":
                item_grid[y][x] = board.create_image(x*Width+35, y*Width+35, image=wall_pic)
                grid[y][x] = 1
            elif var.get() == "start":
                item_grid[y][x] = board.create_image(x*Width+35, y*Width+35, image=robot_pic)
                grid[y][x] = 2
                start_count+=1
            elif var.get() == "goal":
                item_grid[y][x] = board.create_image(x*Width+35, y*Width+35, image=diamond_pic)
                grid[y][x] = 3
                goal_count+=1
            elif var.get() == "pit":
                item_grid[y][x] = board.create_image(x*Width+35, y*Width+35, image=ice_pic)
                grid[y][x] = 4

    board.bind('<Button-1>', create_item)

    Label(text="Note: Please close \nthis window after finished.",font = "Verdana 12").pack(side=BOTTOM)
    master.mainloop()
    master = Tk()
    board = Canvas(master, width=x*Width, height=y*Width)

    if start_count < 1:
        messagebox.showwarning('Error', 'No start found!')
        quit()
    elif goal_count <1:
        messagebox.showwarning('Error', 'No goal found!')
        quit()

print (x, y)
walls = []
start = ()
specials = []
pit = []

for i in range(y):
    for j in range(x):
        if grid[i][j] == 1:
            walls.append((j, i))
        if grid[i][j] == 2:
            start = (j, i)
        if grid[i][j] == 3:
            specials.append((j, i, "green", 1))
            goal = (j, i)
        if grid[i][j] == 4:
            specials.append((j, i, "red", -1))
            pit.append((j, i))


player = start
tri_objects = {}
text_objects = {}
flag = True
restart = False

path = os.getcwd() + "/images/"
wall_pic = ImageTk.PhotoImage(file=path+'wall.png')
diamond_pic = ImageTk.PhotoImage(file=path+'diamond.png')
ice_pic = ImageTk.PhotoImage(file=path+'ice.png')
robot_pic = ImageTk.PhotoImage(file=path+'robot.png')

def visualize_grid():
    global specials, walls, Width, x, y, player
    for i in range(x):
        for j in range(y):
            board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="white", width=1)
            temp = {}
            temp_val = {}
            tri_objects[(i,j)] = temp
            text_objects[(i,j)] = temp_val
    for (i, j, c, w) in specials:
        if w == -1:
            board.create_image(i*Width+35, j*Width+35, image=ice_pic)
        else:
            board.create_image(i*Width+35, j*Width+35, image=diamond_pic)
    for (i, j) in walls:
        board.create_image(i*Width+35, j*Width+35, image=wall_pic)
visualize_grid()

def move_bot(new_x, new_y):
    global player, x, y, score, walk_reward, robot, restart

    if (new_x >= 0) and (new_x < x) and (new_y >= 0) and (new_y < y) and not ((new_x, new_y) in walls):
        board.coords(robot, new_x*Width+35, new_y*Width+35)
        player = (new_x, new_y)


def restart_game():
    global player, score, robot, restart
    player = (0, y-1)
    score = 1
    restart = False
    board.coords(robot, start[0]*Width+35, start[1]*Width+35)


def showExpand(expanded_list, fgh_dict):
    expanded_list = expanded_list[1:]
    for e in expanded_list:
        board.create_rectangle(e[0]*Width, e[1]*Width, (e[0]+1)*Width, (e[1]+1)*Width, fill="yellow")
        board.create_text((e[0]+0.5)*Width, e[1]*Width+text_offset, text='f=' + str(format(fgh_dict[e]['f'], '.1f')), fill="black")
        board.create_text((e[0]+0.5)*Width, e[1]*Width+text_offset+20, text='g=' + str(fgh_dict[e]['g']), fill="black")
        board.create_text((e[0]+0.5)*Width, e[1]*Width+text_offset+40, text='h=' + str(format(fgh_dict[e]['h'], '.1f')), fill="black")
        time.sleep((w1.get() + 0.1)/ 100)
    for (i, j, c, w) in specials:
        if w == -1:
            board.create_image(i*Width+35, j*Width+35, image=ice_pic)
        else:
            board.create_image(i*Width+35, j*Width+35, image=diamond_pic)
robot = board.create_image(start[0]*Width+35, start[1]*Width+35, image=robot_pic)


def move():
    print("robot moving")
    global robot
    board.delete(robot)
    robot = board.create_image(player[0]*Width+35, player[1]*Width+35, image=robot_pic)

def noPath():
    nopath = Label(master, text="Opps! NO PATH EXISTS", fg="red", bg="yellow", font = "Verdana 14 bold")
    nopath.pack(side=BOTTOM)

board.pack(side=LEFT)
panel = Frame(master)
panel.pack(side=RIGHT)
Label(text="Controls\n", font = "Verdana 12 bold").pack()

q1frame = Frame(master)
q1frame.pack()
b1 = Button(text="Play / Pause")
def printName(event):
    global flag
    flag = not flag

b1.bind("<Button-1>", printName)
b1.pack()

q3frame = Frame(master)
q3frame.pack()
w1 = Scale(q3frame, from_=0, to=50, orient=HORIZONTAL)
w1.pack(side=LEFT)
Label(text="Speed").pack()

separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=2, pady=2)

Label(text="Q Learning Parameters\n",font = "Verdana 12 bold").pack()

qframe = Frame(master)
qframe.pack()
e = Entry(qframe, width=5)
e.pack(side=LEFT)
e.insert(0, "0.8")

discount = 0.8
def getDiscount(event):
    global discount
    discount = float(e.get())
    if discount > 1:
        discount = 1
    print("Q Learning Parameters : ",discount)
b3 = Button(qframe, text="Discount")
b3.bind("<Button-1>", getDiscount)
b3.pack(side=LEFT)

q4frame = Frame(master)
q4frame.pack()

def create_pit(event):
    x = int(e2.get())
    y = int(e3.get())
    item_grid[x][y] = board.create_image(y*Width+35, x*Width+35, image=ice_pic)
    grid[x][y] = 4
    pit.append((y, x))

e2 = Entry(q4frame, width=5)
e2.pack(side=LEFT)
e3 = Entry(q4frame, width=5)
e3.pack(side=LEFT)
b4 = Button(q4frame, text="add pit")
b4.bind("<Button-1>", create_pit)
b4.pack(pady=10)

def getNow():
    return discount

def begin():
    global flag
    master.mainloop()
    flag = None
    time.sleep(0.1)
