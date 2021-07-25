from tkinter import Canvas, Label, Tk, StringVar, Button, LEFT
from tkinter import messagebox
from tkinter import * 
from turtle import *
import turtle
from PIL import ImageTk
from PIL import Image
from random import choice, randint
from random import randrange
from os import system
from freegames import square, vector
import os
import random
import time

turn = 1;
flag=1;

def my_text(text):
    system("say {}".format(text))

def fallingbox():
    class GameCanvas(Canvas):
        def clean_line(self, boxes_to_delete):
            for box in boxes_to_delete:
                self.delete(box)
            self.update()

        def drop_boxes(self, boxes_to_drop):
            for box in boxes_to_drop:
                self.move(box, 0, fllbx.BOX_SIZE)
            self.update()

        def completed_lines(self, y_coords):
            cleaned_lines = 0
            y_coords = sorted(y_coords)
            for y in y_coords:
                if sum(1 for box in self.find_withtag('game') if self.coords(box)[3] == y) == \
                ((fllbx.GAME_WIDTH - 20) // fllbx.BOX_SIZE):
                    self.clean_line([box
                                    for box in self.find_withtag('game')
                                    if self.coords(box)[3] == y])

                    self.drop_boxes([box
                                    for box in self.find_withtag('game')
                                    if self.coords(box)[3] < y])
                    cleaned_lines += 1
            return cleaned_lines

        def game_board(self):
            board = [[0] * ((fllbx.GAME_WIDTH - 20) // fllbx.BOX_SIZE)\
                    for _ in range(fllbx.GAME_HEIGHT // fllbx.BOX_SIZE)]
            for box in self.find_withtag('game'):
                x, y, _, _ = self.coords(box)
                board[int(y // fllbx.BOX_SIZE)][int(x // fllbx.BOX_SIZE)] = 1
            return board
        def boxes(self):
            return self.find_withtag('game') == self.find_withtag(fill="blue")

    class Shape():
        def __init__(self, coords = None):
            if not coords:
                self.__coords = choice(fllbx.SHAPES)
            else:
                self.__coords = coords

        @property
        def coords(self):
            return self.__coords

        def rotate(self):  
            self.__coords = self.__rotate()

        def rotate_directions(self):
            rotated = self.__rotate()
            directions = [(rotated[i][0] - self.__coords[i][0],
                        rotated[i][1] - self.__coords[i][1]) for i in range(len(self.__coords))]

            return directions

        @property
        def matrix(self):
            return [[1 if (j, i) in self.__coords else 0 \
                    for j in range(max(self.__coords, key=lambda x: x[0])[0] + 1)] \
                    for i in range(max(self.__coords, key=lambda x: x[1])[1] + 1)]

        def drop(self, board, offset):
            off_x, off_y = offset
            last_level = len(board) - len(self.matrix) + 1
            for level in range(off_y, last_level):
                for i in range(len(self.matrix)):
                    for j in range(len(self.matrix[0])):
                        if board[level+i][off_x+j] == 1 and self.matrix[i][j] == 1:
                            return level - 1
            return last_level - 1  

        def __rotate(self):
            max_x = max(self.__coords, key=lambda x:x[0])[0]
            new_original = (max_x, 0)

            rotated = [(new_original[0] - coord[1],
                        new_original[1] + coord[0]) for coord in self.__coords]

            min_x = min(rotated, key=lambda x:x[0])[0]
            min_y = min(rotated, key=lambda x:x[1])[1]
            return [(coord[0] - min_x, coord[1] - min_y) for coord in rotated]

    class Piece():
        def __init__(self, canvas, start_point, shape = None):
            self.__shape = shape
            if not shape:
                self.__shape = Shape()
            self.canvas = canvas
            self.boxes = self.__create_boxes(start_point)

        @property
        def shape(self):
            return self.__shape

        def move(self, direction):
            if all(self.__can_move(self.canvas.coords(box), direction) for box in self.boxes):
                x, y = direction
                for box in self.boxes:
                    self.canvas.move(box,
                                    x * fllbx.BOX_SIZE,
                                    y * fllbx.BOX_SIZE)
                return True
            return False

        def rotate(self):
            directions = self.__shape.rotate_directions()
            if all(self.__can_move(self.canvas.coords(self.boxes[i]), directions[i]) for i in range(len(self.boxes))):
                self.__shape.rotate()
                for i in range(len(self.boxes)):
                    x, y = directions[i]
                    self.canvas.move(self.boxes[i],
                                    x * fllbx.BOX_SIZE,
                                    y * fllbx.BOX_SIZE)

        @property
        def offset(self):
            return (min(int(self.canvas.coords(box)[0]) // fllbx.BOX_SIZE for box in self.boxes),
                    min(int(self.canvas.coords(box)[1]) // fllbx.BOX_SIZE for box in self.boxes))

        def predict_movement(self, board):
            level = self.__shape.drop(board, self.offset)
            min_y = min([self.canvas.coords(box)[1] for box in self.boxes])
            return (0, level - (min_y // fllbx.BOX_SIZE))

        def predict_drop(self, board):
            level = self.__shape.drop(board, self.offset)
            self.remove_predicts()

            min_y = min([self.canvas.coords(box)[1] for box in self.boxes])
            for box in self.boxes:
                x1, y1, x2, y2 = self.canvas.coords(box)
                box = self.canvas.create_rectangle(x1, level * fllbx.BOX_SIZE + (y1 - min_y), x2, (level + 1) * fllbx.BOX_SIZE + (y1 - min_y),
                                                fill="yellow", tags = "predict")

        def remove_predicts(self):
            for i in self.canvas.find_withtag('predict'):
                self.canvas.delete(i) 
            self.canvas.update()

        def __create_boxes(self, start_point):
            boxes = []
            off_x, off_y = start_point
            for coord in self.__shape.coords:
                x, y = coord
                box = self.canvas.create_rectangle(x * fllbx.BOX_SIZE + off_x, y * fllbx.BOX_SIZE + off_y, x * fllbx.BOX_SIZE + fllbx.BOX_SIZE + off_x,
                                                y * fllbx.BOX_SIZE + fllbx.BOX_SIZE + off_y, fill="blue", tags="game")
                boxes += [box]

            return boxes

        def __can_move(self, box_coords, new_pos):
            x, y = new_pos
            x = x * fllbx.BOX_SIZE
            y = y * fllbx.BOX_SIZE
            x_left, y_up, x_right, y_down = box_coords

            overlap = set(self.canvas.find_overlapping((x_left + x_right) / 2 + x, 
                                                    (y_up + y_down) / 2 + y, 
                                                    (x_left + x_right) / 2 + x,
                                                    (y_up + y_down) / 2 + y))
            other_items = set(self.canvas.find_withtag('game')) - set(self.boxes)

            if y_down + y > fllbx.GAME_HEIGHT or \
            x_left + x < 0 or \
            x_right + x > fllbx.GAME_WIDTH or \
            overlap & other_items:
                return False
            return True        

    class fllbx():
        SHAPES = ([(0, 0), (1, 0), (0, 1), (1, 1)], 
                [(0, 0), (1, 0), (2, 0), (3, 0)],  
                [(2, 0), (0, 1), (1, 1), (2, 1)],   
                [(0, 0), (0, 1), (1, 1), (2, 1)],   
                [(0, 1), (1, 1), (1, 0), (2, 0)], 
                [(0, 0), (1, 0), (1, 1), (2, 1)],     
                [(1, 0), (0, 1), (1, 1), (2, 1)])  

        BOX_SIZE = 20

        GAME_WIDTH = 300
        GAME_HEIGHT = 500
        GAME_START_POINT = GAME_WIDTH / 2 / BOX_SIZE * BOX_SIZE - BOX_SIZE

        def __init__(self, predictable = False):
            self._level = 1
            self._score = 0
            self._blockcount = 0
            self.speed = 500
            self.predictable = predictable

            self.root = Tk()
            self.root.geometry("500x550") 
            self.root.title('Falling Box')
            self.root.bind("<Key>", self.game_control)
            self.__game_canvas()
            self.__level_score_label()
            self.__next_piece_canvas()

        def game_control(self, event):
            if event.char in ["a", "A", "\uf702"]:
                self.current_piece.move((-1, 0))
                self.update_predict()
            elif event.char in ["d", "D", "\uf703"]:
                self.current_piece.move((1, 0))
                self.update_predict()
            elif event.char in ["s", "S", "\uf701"]:
                self.hard_drop()
            elif event.char in ["w", "W", "\uf700"]:
                self.current_piece.rotate()
                self.update_predict()

        def new_game(self):
            self.level = 1
            self.score = 0
            self.blockcount = 0
            self.speed = 500

            self.canvas.delete("all")
            self.next_canvas.delete("all")

            self.__draw_canvas_frame()
            self.__draw_next_canvas_frame()

            self.current_piece = None
            self.next_piece = None        

            self.game_board = [[0] * ((fllbx.GAME_WIDTH - 20) // fllbx.BOX_SIZE)\
                            for _ in range(fllbx.GAME_HEIGHT // fllbx.BOX_SIZE)]

            self.update_piece()

        def update_piece(self):
            if not self.next_piece:
                self.next_piece = Piece(self.next_canvas, (20,20))

            self.current_piece = Piece(self.canvas, (fllbx.GAME_START_POINT, 0), self.next_piece.shape)
            self.next_canvas.delete("all")
            self.__draw_next_canvas_frame()
            self.next_piece = Piece(self.next_canvas, (20,20))
            self.update_predict()

        def start(self):
            self.new_game()
            self.root.after(self.speed, None)
            self.drop()
            self.root.mainloop()

        def drop(self):
            if not self.current_piece.move((0,1)):
                self.current_piece.remove_predicts()
                self.completed_lines()
                self.game_board = self.canvas.game_board()
                self.update_piece()

                if self.is_game_over():
                    return
                else:
                    self._blockcount += 1
                    self.score += 1

            self.root.after(self.speed, self.drop)

        def hard_drop(self):
            self.current_piece.move(self.current_piece.predict_movement(self.game_board))

        def update_predict(self):
            if self.predictable:
                self.current_piece.predict_drop(self.game_board)

        def update_status(self):
            self.status_var.set(f"Level: {self.level}, Score: {self.score}")
            self.status.update()

        def is_game_over(self):
            if not self.current_piece.move((0,1)):

                self.play_again_btn = Button(self.root, text="Play Again", command=self.play_again)
                self.quit_btn = Button(self.root, text="Quit", command=self.quit) 
                self.play_again_btn.place(x = fllbx.GAME_WIDTH + 10, y = 200, width=100, height=25)
                self.quit_btn.place(x = fllbx.GAME_WIDTH + 10, y = 300, width=100, height=25)
                return True
            return False

        def play_again(self):
            self.play_again_btn.destroy()
            self.quit_btn.destroy()
            my_text("Good Luck for this turn")
            self.start()

        def quit(self):
            my_text("Thanks For Playing, I hope You Like it !!")
            self.root.destroy()

        def completed_lines(self):
            y_coords = [self.canvas.coords(box)[3] for box in self.current_piece.boxes]
            completed_line = self.canvas.completed_lines(y_coords)
            if completed_line == 1:
                self.score += 400
            elif completed_line == 2:
                self.score += 1000
            elif completed_line == 3:
                self.score += 3000
            elif completed_line >= 4:
                self.score += 12000

        def __game_canvas(self):
            self.canvas = GameCanvas(self.root, width = fllbx.GAME_WIDTH, height = fllbx.GAME_HEIGHT)
            self.canvas.pack(padx=5 , pady=10, side=LEFT)



        def __level_score_label(self):
            self.status_var = StringVar()        
            self.status = Label(self.root,  textvariable=self.status_var, font=("Helvetica", 10, "bold"))
            self.status.pack()

        def __next_piece_canvas(self):
            self.next_canvas = Canvas(self.root,
                                    width = 100,
                                    height = 100)
            self.next_canvas.pack(padx=5 , pady=10)

        def __draw_canvas_frame(self):
            self.canvas.create_line(10, 0, 10, self.GAME_HEIGHT, fill = "red", tags = "line")
            self.canvas.create_line(self.GAME_WIDTH-10, 0, self.GAME_WIDTH-10, self.GAME_HEIGHT, fill = "red", tags = "line")
            self.canvas.create_line(10, self.GAME_HEIGHT, self.GAME_WIDTH-10, self.GAME_HEIGHT, fill = "red", tags = "line")

        def __draw_next_canvas_frame(self):
            self.next_canvas.create_rectangle(10, 10, 90, 90, tags="frame")

        def __get_level(self):
            return self._level

        def __set_level(self, level):
            self.speed = 500 - (level - 1) * 25
            self._level = level
            self.update_status()

        def __get_score(self):
            return self._score

        def __set_score(self, score):
            self._score = score
            self.update_status()

        def __get_blockcount(self):
            return self._blockcount

        def __set_blockcount(self, blockcount):
            self.level = blockcount // 5 + 1
            self._blockcount = blockcount

        level = property(__get_level, __set_level)
        score = property(__get_score, __set_score)
        blockcount = property(__get_blockcount, __set_blockcount)

    if __name__ == '__main__':
        game = fllbx(predictable = True)
        game.start()

def bounceball():
        class Ball:
                def __init__(self, canvas, paddle, color):
                        self.canvas = canvas
                        self.paddle = paddle

                        self.id = canvas.create_oval(10, 10, 25, 25, fill=color)

                        starts = [-3, -2, -1, 1, 2, 3]
                        
                        random.shuffle(starts)

                        self.x = starts[0]
                        self.y = -3
                        self.canvas_height = canvas.winfo_height()
                        self.canvas_width = canvas.winfo_width()

                        self.is_hitting_bottom = False

                        canvas.move(self.id, 245, 100)

                def draw(self):
        
                        self.canvas.move(self.id, self.x, self.y)

                        pos = self.canvas.coords(self.id)

                        if pos[1] <= 0:
                                self.y = 1

                        if pos[3] >= self.canvas_height:
                                #self.y = -1
                                self.is_hitting_bottom = True

                        if self.hit_top_paddle(pos) == True:
                                self.y = -3

                        if self.hit_bottom_paddle(pos) == True:
                                self.y = 1

                        if pos[0] <= 0:
                                self.x = 3

                        if pos[2] >= self.canvas_width:
                                self.x = -3

                def hit_top_paddle(self, pos):
                        
                        paddle_pos = self.canvas.coords(self.paddle.id)
                        
                        if pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2]:
                                if pos[3] >= paddle_pos[1] and pos[3] <= paddle_pos[3]:
                                        return True
                        return False

                def hit_bottom_paddle(self, pos):
                
                        paddle_pos = self.canvas.coords(self.paddle.id)
                        
                        if pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2]:
                                if pos[1] >= paddle_pos[1] and pos[1] <= paddle_pos[3]:
                                        return True
                        return False

        class Paddle:

                def __init__(self, canvas, color):
                        
                        self.canvas = canvas
                        self.id = canvas.create_rectangle(0, 0, 100, 10, fill=color)

                        self.x = 0
                        self.canvas_width = canvas.winfo_width()

                        canvas.move(self.id, 200, 300)

                        canvas.bind_all('<KeyPress-Left>', self.move_left)
                        canvas.bind_all('<KeyPress-Right>', self.move_right)

                def draw(self):
                
                        self.canvas.move(self.id, self.x, 0)

                        pos = self.canvas.coords(self.id)

                        if pos[0] <= 0:
                                self.x = 0

                        if pos[2] >= self.canvas_width:
                                self.x = 0

                def move_left(self, event):
                        self.x = -2

                def move_right(self, event):
                        self.x = 2

                

        tk = Tk()
        tk.title('Bounce Ball')
        canvas = Canvas(tk, width=550, height=400, bd=0, highlightthickness=0)
        canvas.pack()
        tk.update()

        paddle = Paddle(canvas, 'black')
        ball = Ball(canvas, paddle, 'yellow')

        grndscore = 0
        
        while 1:
            if ball.is_hitting_bottom == False:
                    ball.draw()
                    paddle.draw()
            else:
                break

            tk.update_idletasks()
            tk.update()
            time.sleep(0.0000001)
        my_text("Thanks for playing")

def snakeg():
    food = vector(0, 0)
    snake = [vector(10, 0)]
    aim = vector(0, -10)

    def change(x, y):
        "Change snake direction."
        aim.x = x
        aim.y = y

    def inside(head):
        "Return True if head inside boundaries."
        return -200 < head.x < 190 and -200 < head.y < 190

    def move():
        head = snake[-1].copy()
        head.move(aim)

        if not inside(head) or head in snake:
            square(head.x, head.y, 9, 'red')
            update()
            my_text("Your Score is ,")
            my_text(len(snake))
            my_text("Thanks for playing, I hope you like it.")
            return

        snake.append(head)

        if head == food:
            my_text(len(snake))
            food.x = randrange(-15, 15) * 10
            food.y = randrange(-15, 15) * 10
        else:
            snake.pop(0)

        clear()

        for body in snake:
            square(body.x, body.y, 9, 'black')

        square(food.x, food.y, 9, 'green')
        update()
        ontimer(move, 100)

    setup(420, 420, 370, 0)
    hideturtle()
    tracer(False)
    listen()
    onkey(lambda: change(10, 0), 'Right')
    onkey(lambda: change(-10, 0), 'Left')
    onkey(lambda: change(0, 10), 'Up')
    onkey(lambda: change(0, -10), 'Down')
    turtle.title("Snake Game")
    move()
    exitonclick()

def tictactoe():
    
    window=Tk()

    window.title("Tic Tac Toe")
    window.geometry("400x300")

    lbl=Label(window,text="Tic-tac-toe Game",font=('Helvetica','15'))
    lbl.grid(row=0,column=0)
    lbl=Label(window,text="Player 1: X",font=('Helvetica','10'))
    lbl.grid(row=1,column=0)
    lbl=Label(window,text="Player 2: O",font=('Helvetica','10'))
    lbl.grid(row=2,column=0)


    def clicked1():
        global turn
        if btn1["text"]==" ": 
            if turn==1:
                turn =2;
                btn1["text"]="X"
            elif turn==2:
                turn=1;
                btn1["text"]="O"
        check();

    def clicked2():
        global turn
        if btn2["text"]==" ":
            if turn==1:
                turn =2;
                btn2["text"]="X"
            elif turn==2:
                turn=1; 
                btn2["text"]="O"
        check();

    def clicked3():
        global turn
        if btn3["text"]==" ":
            if turn==1:
                turn =2;
                btn3["text"]="X"
            elif turn==2:
                turn=1;
                btn3["text"]="O"
        check();

    def clicked4():
        global turn
        if btn4["text"]==" ":
            if turn==1:
                turn =2;
                btn4["text"]="X"
            elif turn==2:
                turn=1;
                btn4["text"]="O"
        check();

    def clicked5():
        global turn
        if btn5["text"]==" ":
            if turn==1:
                turn =2;
                btn5["text"]="X"
            elif turn==2:
                turn=1;
                btn5["text"]="O"
        check();

    def clicked6():
        global turn
        if btn6["text"]==" ":
            if turn==1:
                turn =2;
                btn6["text"]="X"
            elif turn==2:
                turn=1;
                btn6["text"]="O"
        check();

    def clicked7():
        global turn
        if btn7["text"]==" ":
            if turn==1:
                turn =2;
                btn7["text"]="X"
            elif turn==2:
                turn=1;
                btn7["text"]="O"
        check();

    def clicked8():
        global turn
        if btn8["text"]==" ":
            if turn==1:
                turn =2;
                btn8["text"]="X"
            elif turn==2:
                turn=1;
                btn8["text"]="O"
        check();

    def clicked9():
        global turn
        if btn9["text"]==" ":
            if turn==1:
                turn =2;
                btn9["text"]="X"
            elif turn==2:
                turn=1;
                btn9["text"]="O"
        check();

    def check():
        global flag;
        b1 = btn1["text"];
        b2 = btn2["text"];
        b3 = btn3["text"];
        b4 = btn4["text"];
        b5 = btn5["text"];
        b6 = btn6["text"];
        b7 = btn7["text"];
        b8 = btn8["text"];
        b9 = btn9["text"];
        flag = flag+1;
        if b1==b2 and b1==b3 and b1=="O" or b1==b2 and b1==b3 and b1=="X":
            win(btn1["text"])
        if b4==b5 and b4==b6 and b4=="O" or b4==b5 and b4==b6 and b4=="X":
            win(btn4["text"]);
        if b7==b8 and b7==b9 and b7=="O" or b7==b8 and b7==b9 and b7=="X":
            win(btn7["text"]);
        if b1==b4 and b1==b7 and b1=="O" or b1==b4 and b1==b7 and b1=="X":
            win(btn1["text"]);
        if b2==b5 and b2==b8 and b2=="O" or b2==b5 and b2==b8 and b2=="X":
            win(btn2["text"]);
        if b3==b6 and b3==b9 and b3=="O" or b3==b6 and b3==b9 and b3=="X":
            win(btn3["text"]);
        if b1==b5 and b1==b9 and b1=="O" or b1==b5 and b1==b9 and b1=="X":
            win(btn1["text"]);
        if b7==b5 and b7==b3 and b7=="O" or b7==b5 and b7==b3 and b7=="X":
            win(btn7["text"]);
        if flag ==10:
            messagebox.showinfo("Tie", "Match Tied!!!  Try again :)")
            window.destroy()
    def win(player):
        ans = player + " wins ";
        messagebox.showinfo("Congratulations", ans)
        window.destroy()

    btn1 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked1)
    btn1.grid(column=1, row=1)
    btn2 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked2)
    btn2.grid(column=2, row=1)
    btn3 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked3)
    btn3.grid(column=3, row=1)
    btn4 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked4)
    btn4.grid(column=1, row=2)
    btn5 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked5)
    btn5.grid(column=2, row=2)
    btn6 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked6)
    btn6.grid(column=3, row=2)
    btn7 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked7)
    btn7.grid(column=1, row=3)
    btn8 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked8)
    btn8.grid(column=2, row=3)
    btn9 = Button(window, text=" ",bg="yellow", fg="Black",width=3,height=1,font=('Helvetica','20'),command=clicked9)
    btn9.grid(column=3, row=3)
    window.mainloop()
    

def speak():
    my_text("Welcome to Frolic Oration")

class surukiyajaye:
    
    def __init__(self, root):
        
        self.root = root
        self.root.title("FROLIC ORATION")
        self.root.geometry("1200x600")

        self.root.resizable(False, False)
        self.bg = ImageTk.PhotoImage(Image.open("abs1.jpg"))
        self.bg_image = Label(self.root, image = self.bg).place(x = 0, y = 0, relwidth = 1, relheight = 1)

        title = Label(self.root, text = "FROLIC ORATION", font = ("charter", 50, "bold"), fg = "#FF0000").place(x = 390, y = 125)

        speak()

        g1button = Button(self.root, cursor = "hand2", text = "BOUNCE BALL", command = bounceball, font = ("charter", 15, "bold"), fg = "#d77337", bg = "white").place(x = 200, y = 470, width = 180, height = 40)

        g2button = Button(self.root, cursor = "hand2", text = "FALLING BOX", command = fallingbox, font = ("charter", 15, "bold"), fg = "#d77337", bg = "white").place(x = 400, y = 470, width = 180, height = 40)

        g3button = Button(self.root, cursor = "hand2", text = "TIC TAC TOE", command = tictactoe, font = ("charter", 15, "bold"), fg = "#d77337", bg = "white").place(x = 600, y = 470, width = 180, height = 40)

        g4button = Button(self.root, cursor = "hand2", text = "SNAKE", command = snakeg, font = ("charter", 15, "bold"), fg = "#d77337", bg = "white").place(x = 800, y = 470, width = 180, height = 40)




root = Tk() 

obj = surukiyajaye(root)

'''
  
n = input()
n = int(n)
if n==1 :
    fallingbox()
if n==2 :
    os.system('python Bouncegame.py')
if n==3 :
    os.system('python tictactoe.py')
if n==4 :
    os.system('python snakegame.py')

'''
    
root.mainloop() 
