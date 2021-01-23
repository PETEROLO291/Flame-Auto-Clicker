#!/usr/bin/env python

import PySimpleGUI as sg
import keyboard
import mouse
from time import sleep
from threading import Thread


# Made By PETEROLO 291©


sg.LOOK_AND_FEEL_TABLE['CustomDarkTheme'] = {'BACKGROUND': '#373737',
                                        'TEXT': '#FFFFFF',
                                        'INPUT': '#474747',
                                        'TEXT_INPUT': '#FFFFFF',
                                        'SCROLL': '#ff00d4',
                                        'BUTTON': ('white', '#474747'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 0, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        }


sg.theme("CustomDarkTheme")

# Variables

running = True
start_key = "F6"
stop_key = "F4"
click_but = "left"
clicking = False
delay = 0
repeat = 0
cb_marked = False
start_pressed = False
stop_pressed = False
threads_started = False
startable = True




# Try to oppen start key file, or create it in case doesnt exist
try:
    with open("start_key.txt", "r") as read_start_key:
        start_key = read_start_key.read()


except:
    with open("start_key.txt", "w+") as saved_start_key:
        saved_start_key.write("F6")
        saved_start_key.close()

# Try to oppen stop key file, or create it in case doesnt exist

try:
    with open("stop_key.txt", "r") as read_stop_key:
        stop_key = read_stop_key.read()

except:
    with open("stop_key.txt", "w+") as saved_stop_key:
        saved_stop_key.write("F4")
        saved_stop_key.close()




#··Window Elements··#


def key_popup(window):
    global start_key, stop_key, values
    
    sg.LOOK_AND_FEEL_TABLE['CustomDarkTheme'] = {'BACKGROUND': '#373737',
                                            'TEXT': '#FFFFFF',
                                            'INPUT': '#474747',
                                            'TEXT_INPUT': '#FFFFFF',
                                            'SCROLL': '#ff00d4',
                                            'BUTTON': ('white', '#474747'),
                                            'PROGRESS': ('#01826B', '#D0D0D0'),
                                            'BORDER': 0, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                            }


    sg.theme("CustomDarkTheme")

    layout = [  [sg.Text("Start Key", pad=((0, 13), None), font=("Arial", 13)), sg.Text("Stop Key", font=("Arial", 13))],
                [sg.Input(default_text=start_key ,size=(3, 1), font=("Arial", 15), pad=((0, 40), None), key="-K1-"), sg.Input(default_text=stop_key, size=(3, 1), font=("Arial", 15), key="-K2-")],
                [sg.Button("Save", size=(10, 1), pad=((0, 0), 8), font=("Arial", 11))]]


    pop = sg.Window('HotKeys', layout, size=(250, 110), element_justification="C", icon="flame_ico.ico", finalize=True)

    event, values = pop.read()

    if event == "Save":
        start_key = str(values["-K1-"])
        stop_key = str(values["-K2-"])

        window["-STAB-"].update(f"Start ({start_key.upper()})")
        window["-STOB-"].update(f"Start ({stop_key.upper()})")

    with open("start_key.txt", "w+") as save_start_key:
        save_start_key.write(start_key.upper())
        save_start_key.close()


    with open("stop_key.txt", "w+") as save_stop_key:
        save_stop_key.write(stop_key.upper())
        save_stop_key.close()

    

    pop.close()
    pop.write_event_value(event, None)


frame = [   [sg.Text("Click Interval (Seconds):", font=("Arial", 13), pad=((0, 75), None)), sg.Text("Repeat x Times:", font=("Arial", 13), pad=((0, 25), None))],
            [sg.Input(size=(30, 1), justification="l", default_text=0.1, key="-I1-"), sg.Input(size=(30, 1), justification="l", default_text=1000, key="-I2-")],
            [sg.InputOptionMenu(('Left Click', 'Right Click'), key="-IOM-", pad=((15, 100), 2)), sg.Checkbox('Click until stoped', key="-CB-")],
            [sg.Text("—" * 1000)],
            [sg.Button(f"Start ({start_key})", font=("Arial", 15), pad=(5, (0, 0)), key="-STAB-"), sg.Button(f"Stop ({stop_key})", font=("Arial", 15), pad=(5, (0, 0)), key="-STOB-")],
            [sg.Button("Change Hotkeys", font=("Arial", 12), pad=(None, (10, 0)), size=(13, 0))],
            [sg.Text("By PETEROLO 291", font=("Arial", 8), pad=(None, (10, 0)))]]


# Putting layout inside a frame is just to add a super small margin that i whanted to add
layout = [  [sg.Text("Flame Auto Clicker", justification='c', size=(100, 1), pad=(None, (10, 0)) , font=("Freestyle Script", 35))],
            [sg.Text("—" * 1000)],
            [sg.Frame(None, frame, element_justification='c', border_width=0)]]



# Window Config
window = sg.Window('Flame Auto Clicker', layout, size=(530, 310), finalize=True, icon="flame_ico.ico", keep_on_top=False, element_justification="c", margins=(0, 0))


window['-I1-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)
window['-I2-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)


# Backend


def click_loop():
    global clicking, delay, cb_marked, repeat

    while running:

        if cb_marked == False and clicking == True:

            sleep(0.05)

            while repeat != 1 and clicking == True:

                mouse.click(click_but)
                repeat = int(repeat) - 1
                clicking = True
                sleep(float(delay))

                if repeat == 1:
                    clicking = False



        if clicking == False:
            sleep(0.24)
            pass

        if clicking == True:
            mouse.click(click_but)
            sleep(float(delay))


st_click_loop = Thread(target=click_loop)



def detect_keys():
    global clicking, stop_pressed, start_pressed, repeat

    while running:
        sleep(0.05)
        try:
            if keyboard.is_pressed(start_key) or start_pressed == True and startable == True:
                clicking = True
                start_pressed = False

            elif keyboard.is_pressed(stop_key) or stop_pressed == True:
                repeat = 1
                clicking = False
                stop_pressed = False
        except:
            pass

start_k_check = Thread(target=detect_keys)




#···Main PySimpleGui event loop···#
while running:

    if threads_started == False:
        start_k_check.start()
        st_click_loop.start()
        threads_started = True


    event, values = window.read(timeout=250)

    if start_key == "" or stop_key == "":
        start_key = "F6"
        stop_key = "F4"
        window["-STAB-"].update(f"Start ({start_key.upper()})")
        window["-STOB-"].update(f"Start ({stop_key.upper()})")

    try:
        if delay == "" or repeat == "":
            window["-STAB-"].update(disabled=True)
            startable = False

        else:
            window["-STAB-"].update(disabled=False)
            startable = True

    except:
        pass

    if event == "Change Hotkeys":
        key_popup(window)



    try:
        if clicking == False:
            delay = values['-I1-']
            repeat = values['-I2-']

    except:
        pass
    
    # For some reason i have to read the input values 2 times to get them

    try:
        if clicking == False:
            delay = values['-I1-']
            repeat = values['-I2-']


        if delay == "":
            window['-I1-'].Widget.configure(highlightcolor='red', highlightbackground="red", insertbackground="White", highlightthickness=2)
        

        else:
            window['-I1-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)

        if repeat == "" and cb_marked == False:
            window['-I2-'].Widget.configure(highlightcolor='red', highlightbackground="red", insertbackground="White", highlightthickness=2)

        else:
            window['-I2-'].Widget.configure(highlightcolor='#FFFFFF', highlightbackground="#9C9C9C", insertbackground="White", highlightthickness=1)

    except:
        pass


    try:

        if values["-IOM-"] == "Left Click":
            click_but = "left"

        if values["-IOM-"] == "Right Click":
            click_but = "right"

        if values["-CB-"] == True:
            cb_marked = True

        if values["-CB-"] == False:
            cb_marked = False

        if event == "Start (F6)":
            start_pressed = True
        
        if event == "Stop (F4)":
            stop_pressed = True
    except:
        pass
    # Window closing event
    if event == sg.WINDOW_CLOSED or event == None:
        running = False

# Closing the window
window.close()