from tkinter.colorchooser import askcolor
from tkinter import *
from PIL import ImageTk, Image
from collections import deque
from time import sleep
import threading
import math

class Paint(object):
    fullScreen = False
    DEFAULT_PEN_SIZE = 10.0
    DEFAULT_COLOR = 'white'

    def __init__(self):
        self.root = Tk()
        self.root.title('Paint')
        self.root.geometry('500x500')
        self.root.maxsize(1920,1200)
        self.root.minsize(500,300)
        self.root.bind("<F11>", self.toggleFullScreen)
        self.root.bind("<Escape>", self.toggleFullScreen)
        self.root.bind("<Control-a>", self.clear)
        self.configure = Toplevel()
        self.configure.title('Configure')
        self.configure.geometry('110x310')
        self.configure.maxsize(110,310)
        self.configure.minsize(110,310)

        self.c = Canvas(self.root, bg='black', width=1920, height=1200,relief=RIDGE,borderwidth=0)
        self.c.place(x=0,y=0)

        self.paint_tools = Frame(self.configure,width=100,height=300,relief=RIDGE,borderwidth=2)
        self.paint_tools.place(x=0,y=0)

        # self.pen_logo = ImageTk.PhotoImage(Image.open('pen.png'))
        # self.p = Label(self.paint_tools, text="pen",borderwidth=0,font=('verdana',10,'bold'))
        # self.p.place(x=5,y=11)
        # self.pen_button = Button(self.paint_tools,padx=6,image=self.pen_logo,borderwidth=2,command=self.use_pen)
        # self.pen_button.place(x=60,y=10)

        # self.brush_logo = ImageTk.PhotoImage(Image.open('brush.png'))
        # self.b = Label(self.paint_tools,borderwidth=0,text='brush',font=('verdana',10,'bold'))
        # self.b.place(x=5,y=40)
        # self.brush_button = Button(self.paint_tools,image = self.brush_logo,borderwidth=2,command=self.use_brush) 
        # self.brush_button.place(x=60,y=40)

        self.color_logo = ImageTk.PhotoImage(Image.open('color.png'))
        self.cl = Label(self.paint_tools, text='color',font=('verdana',10,'bold'))
        self.cl.place(x=5,y=11)
        self.color_button = Button(self.paint_tools,image = self.color_logo,borderwidth=2,command=self.choose_color)
        self.color_button.place(x=60,y=10)

        # self.eraser_logo = ImageTk.PhotoImage(Image.open('eraser.png'))
        # self.e = Label(self.paint_tools, text='eraser',font=('verdana',10,'bold'))
        # self.e.place(x=5,y=100)
        # self.eraser_button = Button(self.paint_tools,image = self.eraser_logo,borderwidth=2,command=self.use_eraser)
        # self.eraser_button.place(x=60,y=100)

        # self.pen_size = Label(self.paint_tools,text="Pen Size",font=('verdana',10,'bold'))
        # self.pen_size.place(x=15,y=250)
        # self.choose_size_button = Scale(self.paint_tools, from_=1, to=5, orient=VERTICAL)
        # self.choose_size_button.place(x=20,y=150)

        #colour, x-coordinate
        self.colours = [['red', 160], ['orange', 260], ['yellow', 360], ['green', 460], ['blue', 560], ['indigo', 660], ['violet', 760], ['antiquewhite', 860], ['brown', 960], ['gray', 1060], ['pink', 1160], ['purple', 1260], ['chocolate4', 1360], ['burlywood', 1460], ['aqua', 1560], ['cornflowerblue', 1660], ['darkolivegreen3', 1760], ['violetred1', 1860]] 
        for colour_data in self.colours:
            self.create_circle(colour_data[1], 40, 40, self.c, colour_data[0], "colour")

        self.c.create_rectangle(20, 100, 60, 700, fill="gray")

        self.c.create_rectangle(20, 0, 100, 80, fill="white", tags="colour_preview")
        self.c.create_text(60, 40, text="3", fill="black", font=("Helvetica", "40", "bold"), tags="size_text")

        # self.c.create_rectangle(0, 0, 140, 140, fill="white")
        # self.c.create_rectangle(1780, 0, 1920, 140, fill="white")
        # corner_left = ImageTk.PhotoImage(file='aruco_marker.png')
        # self.c.create_image(20, 20, image=corner_left, anchor=NW)
        # corner_right = ImageTk.PhotoImage(file='aruco_marker2.png')
        # self.c.create_image(1800, 20, image=corner_right, anchor=NW)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = 6
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.circle_bool = False
        self.pointer_bool = False
        self.size_bool = False
        self.empty_count = 21
        self.offset_x = 0
        self.offset_y = -25
        self.thickness = 10
        self.palm_size_max = 115
        self.palm_size_prev = deque(maxlen=10)
        self.reset()
        a = threading.Thread(target=self.paint, args=())
        a.start()
        
        # self.c.bind('<B1-Motion>', self.paint)
        # self.c.bind('<ButtonRelease-1>', self.reset)

    # def use_pen(self):
    #     self.activate_button(self.pen_button)

    # def use_brush(self):
    #     self.activate_button(self.brush_button)

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    # def use_eraser(self):
    #     self.activate_button(self.eraser_button, eraser_mode=True)

    # def activate_button(self, some_button, eraser_mode=False):
    #     self.active_button.config(relief=RAISED)
    #     some_button.config(relief=SUNKEN)
    #     self.active_button = some_button
    #     self.eraser_on = eraser_mode

    def create_circle(self, x, y, r, canvas, fill, tags): #center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return canvas.create_oval(x0, y0, x1, y1, fill=fill, tags=tags)
    
    def reset(self):
        self.old_x, self.old_y = None, None

    def toggleFullScreen(self, event):
        if self.fullScreen:
            self.deactivateFullscreen()
        else:
            self.activateFullscreen()

    def activateFullscreen(self):
        self.fullScreen = True

        # Store geometry for reset
        self.geometry = self.root.geometry()

        # Hides borders and make truly fullscreen
        self.root.overrideredirect(True)

        # Maximize window (Windows only). Optionally set screen geometry if you have it
        self.root.state("zoomed")

    def deactivateFullscreen(self):
        self.fullScreen = False
        self.root.state("normal")
        self.root.geometry(self.geometry)
        self.root.overrideredirect(False)

    def clear(self, event):
        self.c.delete("line")
        self.reset()

    def calculate_distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def paint(self):
        while True:
            sleep(0.01)
            file = open("memory.txt", "r")
            coord = file.read().splitlines()
            if len(coord) >= 2:      #sometimes coord is ['']

                for i in range(len(coord)):        
                    coord[i] = int(coord[i])
                
                self.empty_count = 0
                x = coord[0] + self.offset_x
                y = coord[1] + self.offset_y
                palm_size_new = math.sqrt((coord[2] - coord[4])**2 + (coord[3] - coord[5])**2) #distance between middle knuckle and bottom of palm
                self.palm_size_prev.append(palm_size_new)
                if len(self.palm_size_prev) == 10:
                    palm_size_av = sum(self.palm_size_prev)/10
                else:
                    palm_size_av = palm_size_new

                touching_wall = True if palm_size_av < self.palm_size_max else False
                point = False if self.calculate_distance((coord[0], coord[1]), (coord[6], coord[7])) < 70 and self.calculate_distance((coord[0], coord[1]), (coord[16], coord[17])) > 50 else True      #distance between middle and index finger
                triple = True if self.calculate_distance((coord[0], coord[1]), (coord[14], coord[15])) < 60 else False    #distance between index and ring finger
                # print(z, point, math.sqrt((coord[0] - coord[6])**2 + (coord[1] - coord[7])**2))
                x_palm = (coord[2] + coord[4])/2 + self.offset_x
                y_palm = (coord[3] + coord[5])/2 + self.offset_y
                palm_size_radius = palm_size_av//0.7    #radius of palm
                finger_list = [ 
                                [coord[i] + self.offset_x - self.thickness, 
                                 coord[i+1] + self.offset_y - self.thickness,
                                 coord[i+2] + self.offset_x + self.thickness, 
                                 coord[i+3] + self.offset_y + self.thickness] for i in range(6, 14, 4)
                               ]
            else:
                if self.empty_count < 30:
                    self.empty_count += 1
                if self.empty_count > 20:
                    x = None
                    y = None
                    x_palm = None
                    y_palm = None
                    finger_list = None
            file.close()

            # draw line
            if self.old_x and self.old_y and x and y and touching_wall and point and not triple:
                if self.calculate_distance((x,y),(self.old_x, self.old_y)) < 100:
                    paint_color = self.color
                    # self.line_width = self.choose_size_button.get() * 3 + 3
                    self.c.create_line(self.old_x, self.old_y, x, y,
                                    width=self.line_width, fill=paint_color,
                                    capstyle=ROUND, smooth=TRUE, splinesteps=36, tags="line")   
            elif self.old_x and touching_wall and not point and x and y and not triple:
                if y < 90:
                    for colour_data in self.colours:
                        if self.calculate_distance((colour_data[1], 40), (x, y)) < 50:
                            self.color = colour_data[0]
                            break
                    self.c.itemconfig("colour_preview", fill=self.color)
                
                elif x < 70 and 100 < y < 700:
                    self.size_bool = not self.size_bool
                    size = math.ceil((700-y)/20)
                    self.c.itemconfig("size_text", text=str(size))
                    self.line_width = size * 2
                    if self.size_bool:
                        self.c.create_rectangle(20, 700-size*20, 60, 700, fill="blue", tags="size1")
                        self.c.delete("size2")
                    else:
                        self.c.create_rectangle(20, 700-size*20, 60, 700, fill="blue", tags="size2")
                        self.c.delete("size1")
            elif self.old_x and x and y and touching_wall and not point and triple:  #erase
                if self.calculate_distance((x,y),(self.old_x, self.old_y)) < 100:
                    self.c.create_line(self.old_x, self.old_y, x, y,
                                    width=self.line_width * 2, fill="black",
                                    capstyle=ROUND, smooth=TRUE, splinesteps=36, tags="line")   



            self.old_x = x
            self.old_y = y

            #draw shadow to cover hand
            if x_palm:
                self.circle_bool = not self.circle_bool
                if self.circle_bool:
                    self.create_circle(x_palm, y_palm, palm_size_radius, self.c, "black", "shadow1")
                    for i in range(len(finger_list)):
                        self.c.create_rectangle(finger_list[i][0], finger_list[i][1], finger_list[i][2]+30, finger_list[i][3], fill="black", tags="shadow1")    
                    self.c.delete("shadow2")
                else:
                    self.create_circle(x_palm, y_palm, palm_size_radius, self.c, "black", "shadow2")
                    for i in range(len(finger_list)):
                        self.c.create_rectangle(finger_list[i][0], finger_list[i][1], finger_list[i][2]+30, finger_list[i][3], fill="black", tags="shadow2")
                    self.c.delete("shadow1")
            else:
                self.c.delete("shadow1")
                self.c.delete("shadow2")

            #indicate pointer finger position
            if x:
                self.pointer_bool = not self.pointer_bool
                if self.pointer_bool:
                    self.create_circle(x, y, self.line_width//1.8 if self.line_width >= 7 else 7, self.c, "red" if point or triple and touching_wall else "green", "pointer1") 
                    self.c.delete("pointer2")
                else:
                    self.create_circle(x, y, self.line_width//1.8 if self.line_width >= 7 else 7, self.c, "red" if point or triple and touching_wall else "green", "pointer2") 
                    self.c.delete("pointer1")
            else:
                self.c.delete("pointer1")
                self.c.delete("pointer2")


if __name__ == '__main__':
    Paint()

