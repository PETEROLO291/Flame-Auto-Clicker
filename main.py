#!/usr/bin/env python

from tkinter import TclError
from time import sleep
from threading import Thread
from os import system
import PySimpleGUI as sg
from mouse import click, double_click
from keyboard import is_pressed


# Made By PETEROLO 291©


# Custop dark theme configuration
sg.theme_add_new('CustomDarkTheme', {'BACKGROUND': '#373737',
                                        'TEXT': '#FFFFFF',
                                        'INPUT': '#474747',
                                        'TEXT_INPUT': '#FFFFFF',
                                        'SCROLL': '#ff00d4',
                                        'BUTTON': ('white', '#474747'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 0, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        })


sg.theme("CustomDarkTheme")


# Variables

running = True
start_key = "F6"
stop_key = "F4"
global_key = ""
click_but = "left"
clicking = False
delay = float
repeat = 0
cb_marked = False
start_pressed = False
stop_pressed = False
threads_started = False
startable = True
on_top = False
looped = False
opacity = 1
slide_bar_val = 100
locked_opacity = None
error = False

# Try to oppen start key file, or create it in case doesnt exist
try:
    with open("start_key.txt", "r") as read_start_key:
        start_key = read_start_key.read()


except FileNotFoundError:
    with open("start_key.txt", "w") as saved_start_key:
        saved_start_key.write("F6")
        saved_start_key.close()

# Try to oppen stop key file, or create it in case doesnt exist

try:
    with open("stop_key.txt", "r") as read_stop_key:
        stop_key = read_stop_key.read()

except FileNotFoundError:
    with open("stop_key.txt", "w") as saved_stop_key:
        saved_stop_key.write("F4")
        saved_stop_key.close()

# Try to open opacity file, or create it in case doesn't exist
try:
    with open("opacity.txt", "r") as opacity:
        opacity = opacity.read()


except FileNotFoundError:
    with open("opacity.txt", "w") as create_opacity:
        create_opacity.write("1.0")
        create_opacity.close()


with open("opacity.txt", "r") as locked_opacity:
    locked_opacity = locked_opacity.read()


#··Window Elements··#

# Function to get the slider bar value
def new_opa():
    global opacity, slide_bar_val
    slide_bar_val = float(opacity) * 100

# Custop popup window to configure the Start and Stop keys
def key_popup(window):
    global start_key, stop_key, opacity, running, slide_bar_val, locked_opacity

    new_opa()

    sg.theme_add_new('CustomDarkTheme', {'BACKGROUND': '#373737',
                                            'TEXT': '#FFFFFF',
                                            'INPUT': '#474747',
                                            'TEXT_INPUT': '#FFFFFF',
                                            'SCROLL': '#515151',
                                            'BUTTON': ('white', '#474747'),
                                            'PROGRESS': ('#01826B', '#D0D0D0'),
                                            'BORDER': 0, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                            })


    # Set popup theme
    sg.theme("CustomDarkTheme")


    # Popup layout
    layout = [  [sg.Text("Start Key", pad=((0, 13), None), font=("Arial", 13)), sg.Text("Stop Key", font=("Arial", 13))],
                [sg.Input(default_text=start_key ,size=(3, 1), font=("Arial", 15), pad=((0, 42), None), key="-K1-"), sg.Input(default_text=stop_key, size=(3, 1), font=("Arial", 15), key="-K2-")],
                [sg.Text("—" * 25, pad=((0, 0), 0), font=("Arial", 13))],
                [sg.Text("Opacity", pad=((0, 0), 0), font=("Arial", 13))],
                [sg.Slider(range=(1,100), default_value=slide_bar_val, size=(20,15), orientation='horizontal', font=('Arial', 12), pad=(25, (0, 0)), key="-SLI-")],
                [sg.Text("—" * 25, pad=((0, 0), 8), font=("Arial", 13))],
                [sg.Button("Save", size=(10, 1), pad=((0, 0), 0), font=("Arial", 11))]]


    # Popup window construction
    pop = sg.Window('Settings', layout, size=(280, 219), element_justification="C", icon="ico.ico", finalize=True, keep_on_top=True)


    # Popup event reading
    event2, values2 = pop.read()

    # If Save button is pressed:
    if event2 != sg.WINDOW_CLOSED or event2 != None:
        opacity = int(values2["-SLI-"])
        opacity = opacity/100

    with open("opacity.txt", "w") as write_opacity:
        write_opacity.write(str(opacity))
        write_opacity.close()


    if event2 == "Save" and float(opacity) != float(locked_opacity):
        start_key = str(values2["-K1-"]) # Save the input values into a variable
        stop_key = str(values2["-K2-"])
        system("restart-link.vbs")
        running = False

    elif event2 != sg.WINDOW_CLOSED or event2 != None:
        start_key = str(values2["-K1-"]) # Save the input values into a variable
        stop_key = str(values2["-K2-"])


        window["-STAB-"].update(f"Start ({start_key.upper()})") # Edit start button text
        window["-STOB-"].update(f"Stop ({stop_key.upper()})") # Edit stop button text

    with open("start_key.txt", "w+") as save_start_key:
        save_start_key.write(start_key.upper()) # Save start key in txt file
        save_start_key.close()


    with open("stop_key.txt", "w+") as save_stop_key:
        save_stop_key.write(stop_key.upper()) # Save stop key in txt file
        save_stop_key.close()


    pop.write_event_value(event2, None)
    pop.close()


# Frame layout
frame = [   [sg.Text("Click Interval (milliseconds):", font=("Arial", 13), pad=((0, 70), None)), sg.Text("Repeat x Times:", font=("Arial", 13), pad=((0, 45), None))],
            [sg.Input(size=(24, 1), justification="c", default_text=100, tooltip="e.g: 0, 50, 100, 500, 1000...", key="-I1-", font=30), sg.Input(size=(24, 1), justification="c", default_text=1000, key="-I2-", font=30)],
            [sg.Checkbox(("Allways On Top"), pad=((20, 100), 2), key="-ONTOP-"), sg.Checkbox('Click until stoped', key="-CB-")],
            [sg.InputOptionMenu(('Left Click', 'Right Click'), default_value="Left Click", key="-BIOM-", pad=((15, 100), 2)), sg.InputOptionMenu(("Single Click", "Double Click"), default_value="Single Click", key="-CTIOM-")],
            [sg.Text("—" * 1000)],
            [sg.Button(f"Start ({start_key})", font=("Arial", 15), pad=(5, (0, 0)), key="-STAB-"), sg.Button(f"Stop ({stop_key})", font=("Arial", 15), pad=(5, (0, 0)), key="-STOB-")],
            [sg.Button("Settings", font=("Arial", 12), pad=(None, (10, 0)), size=(13, 0))]]


# Put layout inside a frame is just to add a super small margin that i whanted to add
layout = [  [sg.Text("Flame Auto Clicker", justification='c', size=(100, 1), pad=(None, (10, 0)) , font=("Arial", 25))],
            [sg.Text("—" * 1000)],
            [sg.Frame(None, frame, element_justification='c', border_width=0)]]



# Window Config
window = sg.Window('Flame Auto Clicker', layout, size=(505, 293), alpha_channel=opacity, finalize=True, icon="ico.ico", keep_on_top=False, element_justification="c", margins=(0, 0))


# Input details config
window['-I1-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)
window['-I2-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)


# ]---Backend---[



# Loop where the click events are created
def click_loop():
    global clicking, delay, cb_marked, repeat

    while running:


            if cb_marked == False and clicking == True:

                sleep(0.05)

                while repeat != 0 and clicking == True and running == True and values["-CTIOM-"] == "Single Click":

                    click(click_but)
                    repeat = int(repeat) - 1
                    sleep(float(delay))

                    if repeat == 1:
                        clicking = False

                while repeat != 0 and clicking == True and running == True and values["-CTIOM-"] == "Double Click":
                    
                    double_click(click_but)
                    repeat = int(repeat) - 1
                    sleep(float(delay))

                    if repeat == 1:
                        clicking = False


            elif cb_marked == True and clicking == True:

                sleep(0.05)

                while clicking == True and running == True and values["-CTIOM-"] == "Single Click":

                    click(click_but)
                    sleep(float(delay))


                while clicking == True and running == True and values["-CTIOM-"] == "Double Click":
                    
                    double_click(click_but)
                    sleep(float(delay))



            if clicking == False:
                sleep(0.24)
                pass






def detect_keys():
    global clicking, stop_pressed, start_pressed, repeat

    while running:
        sleep(0.05)
        if startable == True:
            try:
                if start_key != stop_key:
                    
                    if is_pressed(start_key) or start_pressed == True:
                        repeat = int(repeat) + 1
                        clicking = True
                        start_pressed = False
                        sleep(0.3)

                    elif is_pressed(stop_key) or stop_pressed == True:
                        repeat = 1
                        clicking = False
                        stop_pressed = False

                if start_key == stop_key:
                    global_key = start_key and stop_key

                    if start_pressed == True:
                        repeat = int(repeat) + 1
                        clicking = True
                        start_pressed = False
                        sleep(1)
                    
                    if stop_pressed == True:
                        clicking = False
                        stop_pressed = False
                        

                    if is_pressed(global_key) and clicking == False:
                        repeat = int(repeat) + 1
                        clicking = True
                        sleep(0.3)

                    if is_pressed(global_key) and clicking == True:
                        clicking = False
                        sleep(0.3)
            except:
                pass

# Creation of threads
start_k_check = Thread(target=detect_keys)
st_click_loop = Thread(target=click_loop)



#···Main PySimpleGui event loop···#
while running:
    # Start threads
    if threads_started == False:
        start_k_check.start()
        st_click_loop.start()
        threads_started = True

    event, values = window.read(timeout=100)


    try:
        if values["-ONTOP-"] == True:
            on_top = True
        elif values["-ONTOP-"] == False:
            on_top = False

        if on_top == True:
            window.TKroot.wm_attributes("-topmost", 1)
        elif on_top == False:
            window.TKroot.wm_attributes("-topmost", 0)

    except TypeError:
        pass

    if start_key == "" or stop_key == "":
        start_key = "F6"
        stop_key = "F4"
        window["-STAB-"].update(f"Start ({start_key.upper()})")
        window["-STOB-"].update(f"Start ({stop_key.upper()})")

    try:

        if looped == True: # Since fist in first loop "repeat" is 0 this conditional prevents this piece of code from running
            try:
                if "-" in str(repeat) or str(repeat) == "0" or " " in str(repeat) and str(repeat) and cb_marked == False and looped == True:
                    window['-I2-'].Widget.configure(highlightcolor='red', highlightbackground="red", insertbackground="White", highlightthickness=1)
                    window["-STAB-"].update(disabled=True)
                    startable = False

                if str(repeat) == "" and cb_marked == True:
                    window['-I2-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)
                    window["-STAB-"].update(disabled=False)
                    startable = True

                elif int(repeat) > 0:
                    window['-I2-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)
                    window["-STAB-"].update(disabled=False)
                    startable = True
                    error = False

            except ValueError:
                window['-I2-'].Widget.configure(highlightcolor='red', highlightbackground="red", insertbackground="White", highlightthickness=1)
                window["-STAB-"].update(disabled=True)
                startable = False
                error = True


            try:
                if "-" in str(delay) or " " in str(delay) and looped == True:
                    window['-I1-'].Widget.configure(highlightcolor='red', highlightbackground="red", insertbackground="White", highlightthickness=1)
                    window["-STAB-"].update(disabled=True)
                    startable = False

                elif float(delay) >= 0:
                    window['-I1-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)
                    startable = True
                    error = False

            except ValueError:
                window['-I1-'].Widget.configure(highlightcolor='red', highlightbackground="red", insertbackground="White", highlightthickness=1)
                window["-STAB-"].update(disabled=True)
                startable = False
                error = True


    except TclError:
        pass

    if event == "Settings":
        key_popup(window)



    try:
        if clicking == False:
            delay = values['-I1-']
            delay = float(delay) / 1000
            repeat = values['-I2-']
            

    except (TypeError, ValueError):

        startable = False
        error = True

    # For some reason i have to read the input values 2 times to get them

    try:
        if clicking == False:
            delay = float(values['-I1-'])
            delay = float(delay) / 1000
            repeat = values['-I2-']
            
    except (TypeError, ValueError):

        startable = False
        error = True


    try:

        # -BIOM- (Button Input Option Menu)
        if values["-BIOM-"] == "Left Click":
            click_but = "left"
        if values["-BIOM-"] == "Right Click":
            click_but = "right"
        if values["-CB-"] == True:
            cb_marked = True
        if values["-CB-"] == False:
            cb_marked = False
        if event == "-STAB-":
            start_pressed = True

        if event == "-STOB-":
            stop_pressed = True


    except TypeError:
        pass

    looped = True
    # Window closing event
    if event == sg.WINDOW_CLOSED or event == None:
        running = False
