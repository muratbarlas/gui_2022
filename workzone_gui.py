#packages
# pascal-voc-writer         0.1.4
# Pillow                    7.2.0
# scikit-image              0.17.2
# opencv-python             3.4.2.16
# imutils                   0.5.3
# pygame                    1.9.6
# numpy                     1.18.5


#version 7
from pascal_voc_writer import Writer
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from skimage.util import random_noise
import os
import cv2
import imutils
import numpy as np
import pygame
import glob
from csv import writer


window = tk.Tk()
window.title("Create Annotation Files")
window.configure(background="white")
WIDTH, HEIGHT = 1200, 600
topx, topy, botx, boty = 0, 0, 0, 0
rect_id = None
window.geometry('%sx%s' % (WIDTH, HEIGHT))
class_type = tk.StringVar()
file_path_master = None
save_directory = None
path_for_augmented_image = None

selected_object = None
curr_box_selection = None
curr_annotation_list = {}
master_w = None
master_w = None
mylabel = None
canvas = None



#####
canvas = tk.Canvas(window, width=704, height=480, borderwidth=0, highlightthickness=0)
canvas.configure(bg="snow3")
canvas.create_text(352,170,  width = 700, font = ('Arial',20), fill="black",
                   text="First select your image set folder by clicking 'Image  set' and then  select a save folder directory for your annotations.")

canvas.create_text(330, 300, width = 700, font = ('Arial, 20'), fill="black", text = "Warning: You can't select your root folder as the save directory.")
canvas.place(relx=0.25, rely=0.05, anchor="nw")


file_list = []
tracker = 0
annotated_list = []
writer_list = {}

#labels
anno_added_label = tk.Label(window,text="Object was added to the annotation", bg = "white")

enlarged_label = tk.Label(window,text="Enlarged image file was saved ", bg = "white")
rotation_label = tk.Label(window,text="Rotated image file was saved", bg = "white")
gamma_label = tk.Label(window,text="Gamma corrected image file was saved", bg = "white")
noise_label = tk.Label(window,text="Image file with added noise was saved", bg = "white")
key_label = tk.Label(window,text="You may use the arrow keys to navigate the directory", bg = "white")
annotated_label = tk.Label(window,text="This image has already been annotated", bg = "white")
saved_label = tk.Label(window,text="Annotation file has been saved", bg = "white")

progress = tk.Label(window, text=str(len(annotated_list)) + '/' + str(len(file_list)) + " images have been annotated")


def resize(input_path): #acts as resize not enlarge
    global enlarged_label
    img = cv2.imread(input_path) #here
    img_size = Image.open(input_path)
    w, h = img_size.size
    if (w > 704 and h >480):
        dim = (704, 480)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        cv2.imwrite(input_path, resized)

def select_save_directory():
    global save_directory
    save_directory = askdirectory(title='Select Folder')


def select_file_dir():
    global file_list, path_for_augmented_image, canvas
    key_label.place(relx=0.5, rely=0.95, anchor='center')
    path = askdirectory(title='Select Folder')# shows dialog box and return the path
    path_for_augmented_image = path
    for file in sorted(os.listdir(path)):
        file_list.append(path + "/" + file)

    file_list.pop(0)  #mac only
    canvas.destroy()
    select_area(file_list[0])



def next_im(event=None):
    global file_list, tracker, annotated_list, progress
    progress.pack_forget()
    progress = tk.Label(window, text=str(len(annotated_list)) + '/' + str(len(file_list)) + " images have been annotated")
    progress.pack()
    anno_added_label.place_forget()
    enlarged_label.pack_forget()
    rotation_label.place_forget()
    gamma_label.place_forget()
    noise_label.place_forget()
    saved_label.place_forget()
    annotated_label.place_forget()
    curr_annotation_list.clear()
    if tracker + 1 < len(file_list):
        tracker = tracker + 1
        select_area(file_list[tracker])
        if file_list[tracker] in annotated_list:

            annotated_label.place(relx=0.5, rely=0.95, anchor='center')
def prev_im(event=None):
    global file_list, tracker, annotated_list
    anno_added_label.place_forget()
    enlarged_label.pack_forget()
    rotation_label.place_forget()
    saved_label.place_forget()
    gamma_label.place_forget()
    noise_label.place_forget()
    annotated_label.place_forget()
    curr_annotation_list.clear()
    if tracker > 0:
        tracker = tracker - 1
        select_area(file_list[tracker])
        if file_list[tracker] in annotated_list:
            annotated_label.place(relx=0.5, rely=0.95, anchor='center')

def add_noise():
    global file_list, tracker
    #print(file_list)
    #print(tracker)
    key_label.place_forget()
    im = Image.open(file_path_master)
    # convert PIL Image to ndarray
    im_arr = np.asarray(im)
    # random_noise() method will convert image in [0, 255] to [0, 1.0],
    # inherently it use np.random.normal() to create normal distribution
    # and adds the generated noised back to image
    noise_img = random_noise(im_arr, mode='gaussian', var=0.05 ** 2)
    noise_img = (255 * noise_img).astype(np.uint8)
    new_img = Image.fromarray(noise_img)
    new_img = new_img.save(path_for_augmented_image +"/" + os.path.basename(file_path_master).split(".")[0]+"NOISE.jpg")
    select_area(
        given_file=path_for_augmented_image+'/' + os.path.basename(file_path_master).split(".")[
            0] + "NOISE.jpg")
    tracker = tracker + 1
    file_list.insert(tracker,  path_for_augmented_image+'/' + os.path.basename(file_path_master).split(".")[0]+".jpg")
    annotated_label.place_forget()
    rotation_label.place_forget()
    gamma_label.place_forget()
    enlarged_label.place_forget()
    saved_label.place_forget()
    noise_label.place(relx=0.5, rely=0.95, anchor='center')


def rotate():
    global rotation_label
    rotate_win = tk.Toplevel()
    rotate_win.title("Rotate")
    rot_val_entry = tk.Entry(rotate_win)
    rot_val_entry.pack()
    to_save = None

    def perform_rotate():
        nonlocal to_save
        image = cv2.imread(file_path_master) #here
        rotated = imutils.rotate_bound(image, int(rot_val_entry.get()))
        to_save = rotated
        cv2.imshow("Rotated image", rotated) #here

    def save_rotation():
        nonlocal rotate_win
        global tracker
        key_label.place_forget()
        cv2.imwrite(path_for_augmented_image+"/" + os.path.basename(file_path_master).split(".")[0]+"ROTATED.jpg", to_save)
        resize(path_for_augmented_image+"/"  + os.path.basename(file_path_master).split(".")[0]+"ROTATED.jpg")




        select_area(given_file=path_for_augmented_image+"/"  + os.path.basename(file_path_master).split(".")[0]+"ROTATED.jpg")
        tracker = tracker + 1
        file_list.insert(tracker,path_for_augmented_image+"/"  + os.path.basename(file_path_master).split(".")[0] + ".jpg")

        annotated_label.place_forget()
        noise_label.place_forget()
        enlarged_label.place_forget()
        gamma_label.place_forget()
        saved_label.place_forget()
        rotation_label.place(relx=0.5, rely=0.95, anchor='center')
        rotate_win.destroy()
        cv2.destroyAllWindows()


    tk.Button(rotate_win, text="View rotation", command=perform_rotate, anchor="w").pack()
    tk.Button(rotate_win, text="Save rotation image", command=save_rotation, anchor="w").pack()

def gamma_coorection():
    global gamma_label
    gamma_win = tk.Toplevel()
    gamma_win.title("Gamma Correction")
    gamma_entry = tk.Entry(gamma_win)
    gamma_entry.pack()
    gamma_to_save = None
    key_label.place_forget()
    def perform_gamma():
        nonlocal gamma_to_save
        lookUpTable = np.empty((1, 256), np.uint8)  #gamma corrected image
        gamma = float(gamma_entry.get())
        image = cv2.imread(file_path_master)
        for i in range(256):
            lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
        gamma_to_save = cv2.LUT(image, lookUpTable)
        cv2.imshow("Gamma Correction Result", gamma_to_save)
    def save_gamma():
        global tracker
        nonlocal gamma_win
        cv2.imwrite(path_for_augmented_image+"/"  + os.path.basename(file_path_master).split(".")[0]+"GAMMA_CORRECTION.jpg", gamma_to_save)
        select_area(given_file=path_for_augmented_image+"/"  + os.path.basename(file_path_master).split(".")[
                0] + "GAMMA_CORRECTION.jpg")

        tracker = tracker + 1
        file_list.insert(tracker, path_for_augmented_image+"/"  + os.path.basename(file_path_master).split(".")[0] + ".jpg")
        annotated_label.place_forget()
        rotation_label.place_forget()
        noise_label.place_forget()
        enlarged_label.place_forget()
        saved_label.place_forget()
        gamma_label.place(relx=0.5, rely=0.95, anchor='center')
        gamma_win.destroy()
        cv2.destroyAllWindows()
    tk.Button(gamma_win, text="View gamma correction", command=perform_gamma, anchor="w").pack()
    tk.Button(gamma_win, text="Save new image", command=save_gamma, anchor="w").pack()

def enlarge():
    global enlarged_label, tracker, file_path_master
    img_size = Image.open(file_path_master)
    w, h = img_size.size
    if (w < 704 and h < 480):
        key_label.place_forget()
        img = cv2.imread(file_path_master)
        dim = (704, 480)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        cv2.imwrite(path_for_augmented_image+'/' + os.path.basename(file_path_master).split(".")[0] + "_ENLARGED.jpg", resized)
        select_area(given_file=path_for_augmented_image + '/' + os.path.basename(file_path_master).split(".")[0] + "_ENLARGED.jpg")
        tracker = tracker + 1
        file_list.insert(tracker, path_for_augmented_image + "/" + os.path.basename(file_path_master).split(".")[0] + ".jpg")
        noise_label.place_forget()
        annotated_label.place_forget()
        rotation_label.place_forget()
        gamma_label.place_forget()
        saved_label.place_forget()
        enlarged_label.place(relx=0.5, rely=0.95, anchor='center')


    else:
        error_win1 = tk.Toplevel()
        error_win1.title("Make point selections")
        img = ImageTk.PhotoImage(Image.open('warning2.png'))
        error_win1.geometry('%sx%s' % (500, 300))
        canvas = tk.Canvas(error_win1, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)
        canvas.pack()
        canvas.img = img  # Keep reference in case this code is put into a function.
        canvas.create_image(0, 0, image=img, anchor='nw')  # tk.NW
        error_message = tk.Message(error_win1, text="Image size reached threshold", width=500)
        error_message.config(font=('Arial', 20))
        error_message.pack()
        error_message2 = tk.Message(error_win1, text="The size of this image already reached the maximum size supported by this GUI",
                                    width=500)
        error_message2.config(font=('Arial', 10))
        error_message2.pack()
        def close_wind1():
            error_win1.destroy()
        done_button1 = tk.Button(error_win1, text="Close", command=close_wind1, anchor="w")
        done_button1.pack()

def get_points():
    point_win = tk.Toplevel()
    point_win.title("Make point selections")

    img = ImageTk.PhotoImage(Image.open(file_list[tracker]))
    point_win.geometry('%sx%s' % (img.width(), img.height()+30))
    canvas = tk.Canvas(point_win, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)

    canvas.pack()
    canvas.img = img  # Keep reference in case this code is put into a function.
    canvas.create_image(0, 0, image=img, anchor=tk.NW)

    point_dict = {}
    def get_mouse_pos(event):
        nonlocal point_dict
        x_pos, y_pos = event.x, event.y
        if (y_pos>=0 and y_pos <= img.height()):
            canvas.create_oval(x_pos+5, y_pos+5, x_pos-5, y_pos-5, fill="#FFFF00", outline="#FFFF00")
            if file_list[tracker] not in point_dict:
                point_dict[file_list[tracker]] = [(x_pos, y_pos)]
            else:
                point_dict[file_list[tracker]].append((x_pos, y_pos))


    def add_row():
        nonlocal point_dict, point_win
        point_dict[file_list[tracker]].pop() #deletes the final wrong point from  the dict that gets added when pressing done
        point_win.destroy()


        with open("parking_points.csv", 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            for key, val in point_dict.items():
                csv_writer.writerow([key, val])






    done_button = tk.Button(point_win, text="Done", command=add_row, anchor="w")

    done_button.pack()
    point_win.bind('<Button-1>', get_mouse_pos)


def open_pdf():
    #os.startfile("guide.pdf") #windows only
    os.system("open /Users/muratbarlas/Desktop/project_trial/guide.pdf") #for mac


def delete_box():
    global curr_box_selection, mylabel, curr_annotation_list
    if len(curr_annotation_list) > 0:
        anno_added_label.place_forget()
        list_boxes = list(curr_annotation_list.values())
        canvas.delete(list_boxes[-1])
        canvas.delete(mylabel)
        curr_annotation_list.popitem()


def create_annotation():
    global curr_annotation_list, file_path_master,master_w, master_h, writer_list
    anno_added_label.place_forget()
    if file_path_master not in annotated_list:
        annotation = Writer(file_path_master, master_w, master_h)
        writer_list[file_path_master] = annotation
    else:

        annotation = writer_list.get(file_path_master)

    for elem in curr_annotation_list.keys():
        annotation.addObject(elem[0], elem[1], elem[2], elem[3], elem[4])
        annotation.save(save_directory+"/" + os.path.basename(file_path_master).split(".")[0] + ".xml")

    curr_annotation_list.clear()

    saved_label.place(relx=0.5, rely=0.95, anchor='center')

    if file_path_master not in annotated_list:
        annotated_list.append(file_path_master)

def select_area(given_file = None):
    global file_path_master, canvas, anno_added_label, saved_label, rotation_label, enlarged_label, gamma_label, noise_label, annotated_list, master_w, master_h
    curr_annotation_list.clear()
    if given_file == None:
        canvas.destroy()
        file_path  = filedialog.askopenfilename()
        file_path_master = file_path
    elif given_file is not None:
        canvas.destroy()
        file_path  = given_file
        file_path_master = file_path

    img_size = Image.open(file_path)
    w, h = img_size.size

    master_w = w
    master_h = h

    img = ImageTk.PhotoImage(Image.open(file_path))
    global rect_id

    def get_mouse_posn(event):
        anno_added_label.place_forget()
        enlarged_label.place_forget()
        rotation_label.place_forget()
        gamma_label.place_forget()
        noise_label.place_forget()
        key_label.place_forget()
        saved_label.place_forget()
        global topy, topx, x_begin, y_begin
        topx, topy = event.x, event.y


    def update_sel_rect(event):
        global rect_id
        global topy, topx, botx, boty
        botx, boty = event.x, event.y
        canvas.coords(rect_id, topx, topy, botx, boty)  #Update selection rect


    def add_selection():
        global save_directory, selected_object,  mylabel #,curr_box_selection
        #selected_object = None

        if class_type.get() == "":
            pygame.mixer.init()
            pygame.mixer.music.load("error_sound.mp3")
            pygame.mixer.music.play(loops = 0)
            error_win1 = tk.Toplevel()
            error_win1.title("Make point selections")
            img1 = ImageTk.PhotoImage(Image.open('warning2.png'))
            error_win1.geometry('%sx%s' % (500, 300))
            canvas1 = tk.Canvas(error_win1, width=img1.width(), height=img1.height(), borderwidth=0, highlightthickness=0)
            canvas1.pack()
            canvas1.img = img1  # Keep reference in case this code is put into a function.
            canvas1.create_image(0, 0, image=img1, anchor='nw')  # tk.NW
            error_message1 = tk.Message(error_win1, text="Object class type not selected", width=500)
            error_message1.config(font=('Arial', 20))
            error_message1.pack()
            error_message2_2 = tk.Message(error_win1, text="Please select an object class type on the left and proceed", width=500)
            error_message2_2.config(font=('Arial', 10))
            error_message2_2.pack()

            def close_wind1():
                error_win1.destroy()

            done_button1 = tk.Button(error_win1, text="Close", command=close_wind1, anchor="w")
            done_button1.pack()

        if save_directory  == None:
            pygame.mixer.init()
            pygame.mixer.music.load("error_sound.mp3")
            pygame.mixer.music.play(loops=0)

            error_win = tk.Toplevel()
            error_win.title("Make point selections")
            img = ImageTk.PhotoImage(Image.open('warning2.png'))
            error_win.geometry('%sx%s' % (500, 300))
            canvas2 = tk.Canvas(error_win, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)
            canvas2.pack()
            canvas2.img = img  # Keep reference in case this code is put into a function.
            canvas2.create_image(0, 0, image=img, anchor='nw') #tk.NW
            error_message = tk.Message(error_win, text="Save directory isn't defined", width =500)
            error_message.config(font = ('Arial', 20))
            error_message.pack()
            error_message2 = tk.Message(error_win, text="Please select a save directory and proceed", width=500)
            error_message2.config(font=('Arial', 10))
            error_message2.pack()

            def close_wind():
                error_win.destroy()
                print('here')

            done_button = tk.Button(error_win, text="Close", command=close_wind, anchor="w")
            done_button.pack()

        else:
            if class_type.get() == "Traffic cones and drums":
                selected_object ="Traffic cones and drums"
                color = "yellow"
            elif class_type.get() == "Barrier & Barricades":
                selected_object ="Barrier & Barricades"
                color = "turquoise1"
            elif class_type.get() == "Delineator and Channelizer":
                selected_object ="Delineator and Channelizer"
                color = "orange"
            elif class_type.get() == "Work zone/Safety signs":
                selected_object ="Work zone/Safety signs"
                color = "springgreen"
            elif class_type.get() == "Safety Flags":
                selected_object ="Safety Flags"
                color = "green"
            elif class_type.get() == "Barrier Tapes":
                selected_object ="Barrier Tapes"
                color = "purple"
            elif class_type.get() == "Road Plates and Trench Covers":
                selected_object ="Road Plates and Trench Covers"
                color = "deep pink"
            elif class_type.get() == "Vent":
                selected_object = "Vent"
                color = "blue"
            elif class_type.get() == "Manhole Guard Rail":
                selected_object ="Manhole Guard Rail"
                color = "maroon"
            elif class_type.get() == "Workers":
                selected_object ="Workers"
                color = "indian red"
            elif class_type.get() == "Construction Vehicles":
                selected_object = "Construction Vehicles"
                color = "dark olive green"

            xmin = min(topx, botx)
            xmax = max(topx, botx)
            ymin = min(topy, boty)
            ymax = max(topy, boty)


            if ymin < 0:
                ymin = 0

            if ymax > h:
                ymax = h

            if xmin < 0:
                xmin = 0

            if xmax > w:
                xmax = w


            #annotation.addObject(selected_object, xmin, ymin, xmax, ymax)
            #annotation.save(save_directory+"/" + os.path.basename(file_path).split(".")[0] + ".xml")
            box_selection = canvas.create_rectangle(topx, topy, botx, boty, width=w_rect, fill='', outline=color)
            curr_annotation_list[selected_object, xmin, ymin, xmax, ymax] = box_selection
            #mylabel = canvas.create_text((topx+9, topy-7), font = ('Arial', font_size), text=selected_object, fill = color)
            #if file_path not in annotated_list:
                #annotated_list.append(file_path)

            anno_added_label.place(relx=0.5, rely=0.95, anchor='center')



    def destroy_canvas():
        canvas.destroy()
        anno_added_label.place_forget()
        saved_label.place(relx=0.5, rely=0.95, anchor='center')


    canvas = tk.Canvas(window, width=img.width(), height=img.height(), borderwidth=0, highlightthickness=0)

    if (w > 704/2 and h > 480/2): #allign it to left if image is large
        canvas.place(relx=0.27, rely=0.05, anchor="nw")
        w_rect = 3
        font_size =13

    else: #center it if image is small
        canvas.place(relx=0.35, rely=0.05, anchor="nw")
        w_rect = 1.5
        font_size = 8

    canvas.img = img  # Keep reference in case this code is put into a function.
    canvas.create_image(0, 0, image=img, anchor=tk.NW)

    done_button = tk.Button(text="Done", command = create_annotation, bg = 'peach puff', fg = 'black', anchor="e")
    done_button_window = canvas.create_window(5, 1, anchor="nw", window=done_button)

    '''''''''
    done_button = tk.Button(text="Done", command=destroy_canvas, anchor="w")
    done_button.configure(width=6, activebackground="#33B5E5", relief="flat")
    #done_button_window = canvas.create_window(0, 1, anchor="nw", window=done_button)
    done_button_window = canvas.create_window(w-60, 1, anchor="nw", window=done_button)
    '''''

    add_selectionButton = tk.Button(text="Add selection", command=add_selection, bg = 'peach puff', fg = 'black', anchor="e")
    add_selectionButton_window = canvas.create_window(w-95, 1, anchor="nw", window=add_selectionButton)

    # Create selection rectangle
    rect_id = canvas.create_rectangle(topx, topy, topx, topy, width=w_rect, fill='', outline='red')
    canvas.bind('<Button-1>', get_mouse_posn)
    canvas.bind('<B1-Motion>', update_sel_rect)



def clear_selection():
    global file_path_master
    os.remove(save_directory+"/" + os.path.basename(file_path_master).split(".")[0] + ".xml")
    select_area(file_list[tracker])
    annotated_label.place_forget()
    rotation_label.place_forget()
    gamma_label.place_forget()
    enlarged_label.place_forget()
    noise_label.place_forget()

#buttons
file_but = tk.Button(window, text='Image Set', wraplength=100, height=4, width=10, command=select_file_dir)
file_but.place(relx=0.875, rely=0.22, anchor="w")

save_directory_button = tk.Button(window, text='Select save directory', wraplength=100, height=4, width=10, command=select_save_directory)
save_directory_button.place(relx=0.875, rely=0.35, anchor="w")

rotate_button = tk.Button(window, text='Rotate', height=4, width=10, command=rotate)
rotate_button.place(relx=0.875, rely=0.48, anchor="w")

gamma_button=tk.Button(window, text='Apply gamma correction', wraplength=100, height=4, width=10, command=gamma_coorection)
gamma_button.place(relx=0.875, rely=0.61, anchor="w")
noise_button = tk.Button(window, text='Add noise', wraplength=100, height =4,width=10, command=add_noise)
noise_button.place(relx=0.875, rely=0.74, anchor="w")

enlarge_button=tk.Button(window, text='Enlarge', wraplength=100, height=4, width=10, command=enlarge)
enlarge_button.place(relx=0.875, rely=0.87, anchor="w")




guide_button = tk.Button(window, text='User Guide', wraplength=100, height =2,width=10, command=open_pdf)
guide_button.place(relx = 0.04, rely = 0.68, anchor='w')

points_button = tk.Button(window, text='Select Parking Points', wraplength=100, height =2,width=10, command=get_points)
points_button.place(relx=0.04, rely=0.75, anchor="w")

undo_button = tk.Button(window, text='Undo', wraplength=80, height =2,width=10, command = delete_box)
undo_button.place(relx = 0.04, rely = 0.82, anchor='w')

left_arrow_im = tk.PhotoImage(file = "left.png")
right_arrow_im = tk.PhotoImage(file = "right.png")

prev_button = tk.Button(window,  text='Prev', image= left_arrow_im, command=prev_im)
next_button = tk.Button(window,  text='Next', image = right_arrow_im, command=next_im)

prev_button.config(bg="snow3", activebackground="snow3")


prev_button.place(relx = 0.89, rely = 0.12, anchor = "sw")
next_button.place(relx = 0.92, rely = 0.12, anchor = "sw")

#radiobutton text font
boldFont = tkFont.Font(size = 15, weight = "bold")
logo_im = tk.PhotoImage(file = "logo2.png")
logo =  tk.Button(window,  text='Prev', image= logo_im)
logo.place(relx = 0.01, rely = 0.93, anchor='w')

#radiobuttons
tk.Label(window, text="Object class types:", bg="white").place(relx=0.0, rely =0.045, anchor='nw')
tk.Radiobutton(window, text="Traffic cones and drums", font = boldFont, bg="white", variable =class_type,value ="Traffic cones and drums").place(relx=0.0, rely =0.08, anchor='nw')
tk.Radiobutton(window, text="Barrier & Barricades", font = boldFont, bg= "white", variable=class_type, value="Barrier & Barricades").place(relx=0.0, rely =0.13, anchor='nw')
tk.Radiobutton(window, text="Delineator and Channelizer", font = boldFont, bg= "white", variable=class_type, value="Delineator and Channelizer").place(relx=0.0, rely =0.18, anchor='nw')
tk.Radiobutton(window, text="Work zone/Safety signs", font = boldFont, bg= "white", variable=class_type, value="Work zone/Safety signs").place(relx=0.0, rely =0.23, anchor='nw')
tk.Radiobutton(window, text="Safety Flags", font = boldFont, bg= "white",variable=class_type, value="Safety Flags").place(relx=0.0, rely =0.28, anchor='nw')
tk.Radiobutton(window, text="Barrier Tapes", font = boldFont, bg= "white", variable=class_type, value="Barrier Tapes").place(relx=0.0, rely =0.33, anchor='nw')
tk.Radiobutton(window, text="Road Plates and Trench Covers", font = boldFont, bg= "white", variable=class_type, value="Road Plates and Trench Covers").place(relx=0.0, rely =0.38, anchor='nw')
tk.Radiobutton(window, text="Manhole Guard Rail", font = boldFont, bg= "white",variable=class_type, value="Manhole Guard Rail").place(relx=0.0, rely =0.43, anchor='nw')
tk.Radiobutton(window, text="Workers", font = boldFont, bg= "white",variable=class_type, value="Workers").place(relx=0.0, rely =0.48, anchor='nw')
tk.Radiobutton(window, text="Construction Vehicles", font = boldFont, bg= "white",variable=class_type, value="Construction Vehicles").place(relx=0.0, rely =0.53, anchor='nw') #missing color
tk.Radiobutton(window, text="Vent", font = boldFont, bg= "white",variable=class_type, value="Vent").place(relx=0.0, rely =0.58, anchor='nw') #missing color



boldFont2 = tkFont.Font(size = 20, weight = "bold")
cones = tk.Label(window, bg = "white", fg = "yellow", text = "•", font=boldFont2).place(relx=0.2, rely=0.08)
barrier = tk.Label(window, bg = "white", fg = "turquoise1", text = "•", font=boldFont2).place(relx=0.2, rely=0.13)
delineator = tk.Label(window, bg = "white", fg = "orange", text = "•", font=boldFont2).place(relx=0.2, rely=0.18)
wzsign = tk.Label(window, bg = "white", fg = "springgreen" , text = "•", font=boldFont2).place(relx=0.2, rely=0.23)
flags = tk.Label(window, bg = "white", fg = "green", text = "•", font=boldFont2).place(relx=0.2, rely=0.28)
tapes = tk.Label(window, bg = "white", fg = "purple", text = "•", font=boldFont2).place(relx=0.2, rely=0.33)
plates = tk.Label(window, bg = "white", fg = "deep pink", text = "•", font=boldFont2).place(relx=0.22, rely=0.38)
manholeguard = tk.Label(window, bg = "white", fg = "maroon", text = "•", font=boldFont2).place(relx=0.2, rely=0.43)
workers = tk.Label(window, bg = "white", fg = "indian red", text = "•", font=boldFont2).place(relx=0.2, rely=0.48)
cvehicle = tk.Label(window, bg = "white", fg = "dark olive green", text = "•", font=boldFont2).place(relx=0.2, rely=0.53)
vent = tk.Label(window, bg = "white", fg = "blue", text = "•", font=boldFont2).place(relx=0.2, rely=0.58)


#arrow keys
window.bind("<Left>", prev_im)
window.bind("<Right>", next_im)


window.mainloop()