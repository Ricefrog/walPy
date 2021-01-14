#! /usr/bin/python

import os
import sys
import time
import PIL.Image
import PIL.ImageTk
from collections import defaultdict
import tkinter as tk
from tkinter import *
from tkinter import font as tkFont

tolerance = 20

def replace_color(source, replacement, image):
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if is_similar(pixels[i, j], source):
                pixels[i, j] = replacement
    return image

def apply_color_map(original, replacement, color_map, image):
    pixels = image.load()
    for coords in color_map[original]:
        #print('coords:', coords)
        i, j = coords
        pixels[i, j] = replacement
        #image.putpixel((i, j), replacement)
    print('Applied color map')
    #image.show()
    return image

def rgb_to_hex(rgb):
    output = []
    for i in range(3):
        temp = hex(rgb[i])[2:]
        if len(temp) < 2:
            temp = '0' + temp
        output.append(temp)
    return output[0] + output[1] + output[2]

def hex_to_rgb(hex_code):
    hex_code = hex_code[1:]
    return (int(hex_code[:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16))

def inverted(rgb):
    return (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])

def is_similar(col_1, col_2):
    if (abs(col_1[0] - col_2[0]) < tolerance
            and abs(col_1[1] - col_2[1]) < tolerance
            and abs(col_1[2] - col_2[2]) < tolerance):
        return True
    return False

def merge_similar_colors(color_dict):
    new_color_dict = defaultdict(int)

    for key, val in color_dict.items():
        similar = False
        for col in new_color_dict.keys():
            if is_similar(key, col):
                similar = True
                new_color_dict[col] += val
                break
        if not similar:
            new_color_dict[key] += val
    return new_color_dict

def merge_color_map(color_map):
    new_color_map = defaultdict(lambda: [])

    for key, val in color_map.items():
        similar = False
        for col in new_color_map.keys():
            if is_similar(key, col):
                similar = True
                new_color_map[col] += val
                break
        if not similar:
            new_color_map[key] = val
    return new_color_map

def similarity_index(col_1, col_2):
    col_1 = hex_to_rgb(col_1)
    #print('col_1:', col_1)
    #print('col_2:', col_2)
    return sum([abs(col_1[s] - col_2[s]) for s in range(3)])

def get_nearest_match(palette, pixel):
    closest = (0, similarity_index(palette[0], pixel))

    for i in range(1, len(palette)):
        cur = similarity_index(palette[i], pixel)
        if cur < closest[1]:
            closest = (i, cur)
    return hex_to_rgb(palette[closest[0]])

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def automatch(palette, image):
    start = time.perf_counter()
    palette = palette[1:]
    pixels = image.load()
    count = 0
    width, height = image.size
    total = width * height

    for i in range(width):
        for j in range(height):
            pixels[i, j] = get_nearest_match(palette, pixels[i, j])
            count += 1
            progress(count, total, status='Automatching')
    print('Automatch complete')
    print(f'Took {(time.perf_counter() - start):.2f} seconds.')
    return image

def lazy_automatch(palette, color_map, image):
    print('Lazy automatching...')
    start = time.perf_counter()
    palette = palette[1:]

    for key, coords in color_map.items():
        for coord in coords:
            image.putpixel(coord, get_nearest_match(palette, key))
    print('Lazy automatching complete')
    print(f'Took {time.perf_counter() - start}:.2f seconds.')
    return image


#original_image_path = './images/crazyFrog_1.jpg'
#original_image_path = './images/catSkirt.jpg'
original_image_path = './images/Asuka_98.jpg'
#original_image_path = './images/medieval1.jpg'
#original_image_path = './images/aesCar.png'
#original_image_path = './images/grassSky.jpg'
#original_image_path = './images/lum.png'
#original_image_path = './images/aesfield.jpg'
#original_image_path = './images/pimpPepe.jpg'

new_image_path = './images/newImage.' + original_image_path[-3:]
print('new_image_path', new_image_path)
infile = PIL.Image.open(original_image_path)

width, height = infile.size

if os.path.exists(new_image_path):
    os.remove(new_image_path)
    print('removed newImage.jpg')

print('width:', width)
print('height:', height)

pixels = infile.load()
unique_colors = defaultdict(int)
color_map = defaultdict(lambda: [])

for i in range(width):
    for j in range(height):
        unique_colors[pixels[i, j]] += 1
        color_map[pixels[i, j]].append((i, j))

print('number of unique colors before merge:', len(unique_colors.keys()))

# sort unique colors by count
unique_colors = {k: v for k, v in sorted(unique_colors.items(), 
                 key=lambda item: item[1], reverse=True)}
color_map = {k: v for k, v in sorted(color_map.items(), 
                 key=lambda item: len(item[1]), reverse=True)}

unique_colors = merge_similar_colors(unique_colors)
color_map = merge_color_map(color_map)

if len(unique_colors.keys()) >= 10:
    number_of_top_colors = 10
else:
    number_of_top_colors = len(unique_colors.keys())

print('number of unique colors after merge:', len(unique_colors.keys()))
top_colors = [list(unique_colors.keys())[s] for s in range(number_of_top_colors)]

print('Top colors:')
for col in top_colors:
    print(f'Color: {col}, {rgb_to_hex(col)}, Count: {unique_colors[col]}')
    #print(f'color_map count: {len(color_map[col])}')

infile.save(new_image_path)

root = tk.Tk()
root.geometry("800x800")
root['padx'] = 50
myFont = tkFont.Font(family='Roboto', size='14', weight='bold')
buttonFont = tkFont.Font(family='Roboto', size='12', weight='bold')

class walPyGUI:
    def __init__(self, master):
        self.master = master
        self.image_frame = tk.Frame(self.master)
        self.image_frame['borderwidth'] = 2
        self.image_frame['relief'] = 'sunken'
        self.image_frame['pady'] = 50

        self.original_path = original_image_path
        self.altered_path = new_image_path
        self.original_img = PIL.Image.open(self.original_path)
        self.original_img = self.original_img.resize((600, 600), 
                                                      PIL.Image.ANTIALIAS) 
        self.alt_img = PIL.Image.open(self.altered_path)
        self.alt_img = self.alt_img.resize((600, 600), PIL.Image.ANTIALIAS) 

        self.f_original_img = PIL.ImageTk.PhotoImage(self.original_img)
        self.f_alt_img = PIL.ImageTk.PhotoImage(self.alt_img)

        self.orig_panel = tk.Label(self.image_frame, 
                                   image = self.f_original_img)
        self.orig_panel.pack(side='left', padx='50')
        self.alt = tk.Label(self.image_frame, image = self.f_alt_img)
        self.alt.pack(side='right', padx='50')
        self.image_frame.pack(side='bottom')

        self.palette = ['unchanged', 
         "#684c31",
         "#ff8a3a",
         "#aecab8", 
         "#ffc878",
         "#67a0ce",
         "#ff8a3a",
         "#83a7b4",
         "#fefff1",
         "#6e5346",
         "#e35b00",
         "#5cab96",
         "#e3cd7b",
         "#0f548b",
         "#06afc7",
         "#f0f1ce",
         "#fadadd"
         ]

        self.palette_frame = tk.Frame(self.master)
        for i in range(1, len(self.palette)):
            temp_label = tk.Label(self.palette_frame,
                                  font=myFont,
                                  text=self.palette[i],
                                  fg=self.palette[i])
            temp_label.pack(side='left')
        self.palette_frame.pack(side='right')

        self.color_subframes = []
        self.colors_frame = tk.Frame(self.master)
        self.colors_frame['borderwidth'] = 2
        self.colors_frame['relief'] = 'sunken'
        self.colors_frame['padx'] = 50
        self.create_color_widgets();
        self.colors_frame.pack(side='left')

        self.reset_button = tk.Button(self.image_frame,
                                     text='Reset',
                                     command=self.reset)
        self.reset_button.pack()
        self.automatch()

    def create_color_widgets(self):
        for i in range(number_of_top_colors):
            z = i
            subframe = tk.Frame(self.colors_frame)
            subframe['padx'] = 10
            color_label = tk.Label(subframe, 
                    text=f'{(unique_colors[top_colors[i]] /(width * height) * 100):.2f}%: {top_colors[i]}',
                                   font=myFont,
                                   fg=f'#{rgb_to_hex(top_colors[i])}')
            apply_color_button = tk.Button(subframe, 
                                   text='Apply color',
                                   font=buttonFont,
                                   fg=f'#{rgb_to_hex(inverted((top_colors[i])))}',
                                   bg=f'#{rgb_to_hex(top_colors[i])}',
                                   padx=10)

            variable = tk.StringVar()
            variable.set(self.palette[0])

            palette_dropdown = tk.OptionMenu(subframe, 
                                             variable, 
                                             *self.palette,
                    command=lambda a, i=i, r=apply_color_button: self.color_change(a, i, r))
            color_label.grid(column=0, row=0, padx=10)
            palette_dropdown.grid(column=1, row=0, padx=10)
            apply_color_button.grid(column=2, row=0, padx=10)
            self.color_subframes.append(subframe)
            subframe.pack()

    def color_change(self, target_color, i, button):
        if target_color == 'unchanged':
            target_color = top_colors[i]
        else:
            target_color = hex_to_rgb(target_color)
        source_color = top_colors[i]
        print('\ntarget_color:', target_color)
        print('source_color:', source_color)
        button['bg'] = f'#{rgb_to_hex(target_color)}'
        button['fg'] = f'#{rgb_to_hex(inverted((target_color)))}'
        button['command'] = lambda a=target_color, b=source_color: self.apply_color(a, b)

    def apply_color(self, target_color, source_color):
        new_altered_image = PIL.Image.open(self.altered_path)
        new_altered_image = apply_color_map(source_color,
                                            target_color,
                                            color_map,
                                            new_altered_image
                                            )
        os.remove(new_image_path)
        new_altered_image.save(new_image_path)

        self.alt_img = PIL.Image.open(self.altered_path)
        self.alt_img = self.alt_img.resize((600, 600), PIL.Image.ANTIALIAS) 
        self.f_alt_img = PIL.ImageTk.PhotoImage(self.alt_img)
        self.alt.config(image=self.f_alt_img)
        self.alt.image = self.f_alt_img

    def automatch(self):
        matched_image =  PIL.Image.open(self.original_path)
        matched_image = automatch(self.palette[3:6], matched_image)
        #matched_image = automatch(self.palette, matched_image)
        #matched_image = lazy_automatch(self.palette, color_map, matched_image)

        os.remove(new_image_path)
        matched_image.save(new_image_path)

        self.alt_img = PIL.Image.open(self.altered_path)
        self.alt_img = self.alt_img.resize((600, 600), PIL.Image.ANTIALIAS) 
        self.f_alt_img = PIL.ImageTk.PhotoImage(self.alt_img)
        self.alt.config(image=self.f_alt_img)
        self.alt.image = self.f_alt_img


    def reset(self):
        new_altered_image = PIL.Image.open(self.original_path)

        os.remove(new_image_path)
        new_altered_image.save(new_image_path)

        self.alt_img = PIL.Image.open(self.altered_path)
        self.alt_img = self.alt_img.resize((600, 600), PIL.Image.ANTIALIAS) 
        self.f_alt_img = PIL.ImageTk.PhotoImage(self.alt_img)
        self.alt.config(image=self.f_alt_img)
        self.alt.image = self.f_alt_img


walPyGui = walPyGUI(root)
root.mainloop()
