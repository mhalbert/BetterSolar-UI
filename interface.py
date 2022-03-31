import PySimpleGUI as sg
import os
from PIL import Image
import io
import base64
import image_viewer
import time
# to do:
# provide in documentation of PNGs or GIFS limitation with PYSIMPLEGUI
# write helper function for image flip through, reusing code in two functions below
# add PASS FAIL CHECKBOX FUNCTIONALITY
# maybe have the default select file structure as Select All, to minimize clicking from user
# highlighting all contents of listbox is something that needs to be done via Tkinter

# preview processed cells/modules
# TODO: give an output folder, flip through images
def preview_window(files):
    # design variables
    button_font='Menlo 12'
    text_color='#1a385c'

    SYMBOL_UP =    '▲'
    SYMBOL_DOWN =  '▼'

    input_button_layout = [
        [sg.Button(SYMBOL_UP,pad=(5,5)), sg.Button(SYMBOL_DOWN,pad=(5,5))],
    ]

    path = 'testuifiles/'   #  temp for now, determine path based on output of model
    bio=image_viewer.display(path,files[0])
    data=bio.getvalue()

    image_layout = [
        [sg.Image(data,key='-IMAGE-')],
        [sg.Text(files[0], size=(660,None), key = '-FILENAME-', font='Sathu 11 underline', text_color='#1a385c', justification='c')]
    ]

    layout = [
        [image_layout],
        [input_button_layout],
    ]

    window = sg.Window('Image Review', layout, size = (660,400), element_justification='center')

    image_counter = 0
    num_files = len(files)

    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED:
            break
        if button == SYMBOL_UP:
            image_counter -=1
            if image_counter < 0:
                image_counter = num_files + image_counter
        if button == SYMBOL_DOWN:
            image_counter += 1
            if image_counter >= num_files:
                image_counter -= num_files
        window['-FILENAME-'].update(files[image_counter])
        bio = image_viewer.display(path,files[image_counter])
        window['-IMAGE-'].update(data=bio.getvalue())

    window.close()
    return


def results_window(files,model):
    # design variables
    font = 'Arial 12'
    font_stats = 'Arial 12 bold'
    banner_color = '#4d4d73'
    background_color = '#ebecf5'
    font_highlight = '#f0efbb'

    t = time.localtime()
    current_time=time.strftime("%H:%M:%S", t)

    # TO DO: link to model ouput
    modules = files
    output_select_layout = [
        [sg.Listbox(values=modules, enable_events=True, font=font, size=(20,6), key="-FILES LIST-", pad=(10,5))],
    ]
    single_report_layout = [
        [sg.Text('Clean:', font=font,  background_color = background_color),
                sg.Text('',  key = '-CLEAN-', background_color = background_color, font=font_stats), # update value per module
                sg.Text('Cracked:', font=font,  background_color = background_color),
                sg.Text('',  key = '-CRACKED-', background_color = background_color, font=font_stats)], # update value per module
        [sg.Text('Highlighted Cells:',  background_color = background_color, font=font), sg.Text('',  key='-HIGHLIGHTED CELLS-', background_color = background_color, font=font_stats)],
        [sg.Text('Module Grade: ', background_color = background_color, font=font_stats), sg.Text('', key='-GRADE-', font=font_stats, background_color = background_color)],
    ]


    listbox_col = sg.Column(output_select_layout,background_color = background_color)
    info_col = sg.Column(single_report_layout, background_color = background_color)

    layout = [
        [sg.Text('Results', size=(950,1), font = 'Sana 22', text_color = 'white', background_color = banner_color, justification = 'center')],
        [sg.Text('Summary Report', font='Arial 15 bold',  background_color = background_color)],
        [sg.Text('Time Submitted:\t' + current_time,font=font,  background_color = background_color)],
        [sg.Text('Selected Model:\t' + model, font = font, background_color = background_color)],
        [sg.Text('_'*500,font=font,pad=(8,8),  background_color = background_color)],
        [sg.Text('Select a module below to view results.',font=font,  background_color = background_color )],
        [listbox_col, info_col],
        [sg.Text('_'*500,font=font,pad=(8,8),  background_color = background_color)],
        [sg.Text('Preview All Images', font='Arial 15 bold',  background_color = background_color)],
        [sg.Text('sort by: ',  background_color = background_color), sg.Checkbox('Pass',  background_color = background_color), sg.Checkbox('Fail',  background_color = background_color)],
        [sg.Button('Preview')],
        [sg.Text('_'*500,font=font,pad=(8,8),  background_color = background_color)],
        [sg.Button('Save Results')],
        [sg.Button('Return to Home')] # add check for 'are you sure?'
    ]

    window = sg.Window('Results', layout, size=(500,500), background_color = '#ebecf5')
    saved = False
    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED:
            break
        if button == 'Preview':
            preview_window(files)
        if button == 'Save Results':
            sg.Popup('Results Saved.')
            saved = True
        if button == 'Return to Home':
            if saved:
                break
            else:
                sg.Popup('Results not saved. Are you sure?')
                break
        # add PASS FAIL CHECKBOX FUNCTIONALITY

    window.close()
    return



def home_page():
    models=['5-class defect segmentation', 'Model A', 'Model B', 'Model C']
    # design variables
    header_font = 'Sathu 20 bold'
    font = 'Sathu 13'
    border_width = 5
    section_color = '#f2f3fc'
    button_font='Menlo 12'
    banner_color = '#4d4d73'


    file_select_layout = [
        [sg.Text('Upload Files',  background_color = section_color, font=header_font)],
        [sg.Text('Folder:', font = font, pad=(10,10), background_color = section_color), sg.InputText(size=(40,1), enable_events=True,key='-FOLDER-'), sg.FolderBrowse(font=button_font, pad=(10,10), )],
        [sg.Text('File(s):', font = font, pad=((10,1),(1,1)), background_color = section_color),
                 sg.Text('Manually select from below or check "Select All."', font='Sathu 11', background_color = section_color)],
        [sg.Listbox(values = [], enable_events = True, font = 'Any 12', select_mode = 'multiple', size = (40,15), key = "-FILES LIST-", pad=(10,1))],
        [sg.Checkbox('Select All', enable_events = True, key = '-ALL-', default = False, background_color = section_color, font = font, pad = (10,1))],
    ]

    model_select_layout = [
        [sg.Text('Processing Settings',  background_color = section_color, font=header_font)],
        [sg.Text('Select a model from the drop down menu.', background_color=section_color, font='Sathu 11')],
        [sg.Combo(values=models, default_value=models[0], key='-MODEL-', font=font, size=(20,1),
                  pad=((10,50),(10,10))),
                  sg.Text('Report Statistics:', font=font,background_color=section_color),
                  sg.Checkbox('Cell Counts', font=font, background_color = section_color),
                  sg.Checkbox('Highlighted Cells',  font=font,background_color = section_color)],
        [sg.Text(' '*109,background_color=section_color),sg.Text('Sort by:',font=font,background_color=section_color), sg.Checkbox('Total Defect Area',font=font,background_color=section_color), sg.Checkbox('Total Number of Defected Cells',font=font,background_color=section_color)],
    ]

    frame = [[sg.Text('')]]
    SYMBOL_UP =    '▲'
    SYMBOL_DOWN =  '▼'

    image_layout = [[sg.Image(key='-IMAGE-')]]

    input_button_layout = [
        [sg.Text('', key = 'FILENAME', font='Sathu 11 underline', text_color='#1a385c', background_color=section_color)],
        [sg.Button(SYMBOL_UP,pad=(5,5)), sg.Button(SYMBOL_DOWN,pad=(5,5))],
        [sg.Button('Preview',font=button_font, pad=(5,5))],
    ]
    input_display_layout = [
        [sg.Text("Preview Files:", pad = (10,None), font=header_font, background_color = section_color)],
        [sg.Text('Click "preview" to begin. Use the arrow keys to flip through your selected files.', pad = (10, None), font='Sathu 11', background_color = section_color)],
        [sg.Frame('', image_layout, size = (633,322), pad=(10,10), background_color = '#D8D8D8', element_justification='c'),
                sg.Column(input_button_layout, background_color=section_color)],
    ]
    output_display_layout = [
        [sg.Text('*either display here, or in popup window*', font = font)],
    ]

    file_select_col = sg.Column(file_select_layout, background_color=section_color, size=(400,400), element_justification='l')
    model_select_col = sg.Column(model_select_layout,  background_color=section_color, size=(1200,125), element_justification='l')
    input_display_col = sg.Column(input_display_layout, background_color = section_color, size = (800,400), element_justification='l')

    layout = [
        [sg.Text('Home', size=(1200,1), font = 'Sathu 22', text_color = 'white', background_color = banner_color, justification = 'center')],
        [file_select_col,input_display_col],
        [model_select_col],
        [sg.Text( '_' * 950, font='Sathu 12 bold')],
        [sg.Button('Run', size=(5,1),font=button_font, pad=(5,10),  button_color = '#cf3f32')], #sg.Button('Run All', pad=(10,10), font='Arial 12 bold',  button_color = '#cf3f32')],
        [sg.Button('Back to Menu', font = button_font, pad=(5,1))],
        [sg.Text('', size=(1200,1), font = 'Sathu 22', text_color = 'white', background_color = banner_color, justification = 'center', pad=(5,10))],
    ]
    window = sg.Window('Home', layout, size=(1200,720))
    image_counter = 0
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
            # implement Quit function
        if event == 'Back to Menu':
            break
        if event == '-FOLDER-':
            folder = values['-FOLDER-']
            try:
                file_list = os.listdir(folder)
            except:
                file_list = []
            fnames = [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and f.lower().endswith(('.png'))]     # png requirement?
            window['-FILES LIST-'].update(fnames)
        if event == 'Run':
            if values['-ALL-'] == True:
                folder = values['-FOLDER-']
                files = [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and f.lower().endswith(('.png'))]
            else:
                files = values['-FILES LIST-']
            if not files:
                sg.Popup('Select files to begin.', font=font, no_titlebar=True)
            else:
                results_window(files,values['-MODEL-'])
        if event == "Preview":
            if values['-ALL-'] == True:
                folder = values['-FOLDER-']
                files = [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and f.lower().endswith(('.png'))]
            else:
                files = values['-FILES LIST-']
            path = values['-FOLDER-'] + '/'
            if not files:
                sg.Popup('Select a file to preview.')
            else:
                bio = image_viewer.display(path,files[0])
                window["-IMAGE-"].update(data=bio.getvalue())
                window['FILENAME'].update(files[0])
        if event == SYMBOL_DOWN and (len(values['-FILES LIST-'])>1 or values['-ALL-'] == True):
            image_counter += 1
            if values['-ALL-'] == True:
                folder = values['-FOLDER-']
                files = [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and f.lower().endswith(('.png'))]
            else:
                files = values['-FILES LIST-']
            path = values['-FOLDER-'] + '/'
            num_files=len(files)
            if image_counter >= num_files:
                image_counter -= num_files
            window['FILENAME'].update(files[image_counter])
            bio = image_viewer.display(path,files[image_counter])
            window['-IMAGE-'].update(data=bio.getvalue())
        if event == SYMBOL_UP and (len(values['-FILES LIST-'])>1 or values['-ALL-'] == True):
            image_counter -= 1
            if values['-ALL-'] == True:
                folder = values['-FOLDER-']
                files = [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and f.lower().endswith(('.png'))]
            else:
                files = values['-FILES LIST-']
            path = values['-FOLDER-'] + '/'
            num_files=len(files)
            if image_counter < 0:
                image_counter = num_files + image_counter
            window['FILENAME'].update(files[image_counter])
            bio = image_viewer.display(path,files[image_counter])
            window['-IMAGE-'].update(data=bio.getvalue())



    window.close()
    return

def main():
    #print(sg.Text.fonts_installed_list())

    my_new_theme = {'BACKGROUND': '#e4e4f0',
                    'TEXT': '#000000',
                    'INPUT': '#D8D8D8',
                    'TEXT_INPUT': '#000000',
                    'SCROLL': '#D8D8D8',
                    'BUTTON': ('white', '#82CA9C'),
                    'PROGRESS': ('#01826B', '#D0D0D0'),
                    'BORDER': 1,
                    'SLIDER_DEPTH': 0,
                    'PROGRESS_DEPTH': 0}

    sg.theme_add_new('MainTheme', my_new_theme)
    sg.theme('MainTheme')

    font='Sathu 12'
    button_font='Menlo 12'
    banner_color = '#4d4d73'

    layout = [
        [sg.Text('Main Menu', font = 'Sathu 18', size=(700,1),pad=((0,0),(1,30)), text_color = 'white', background_color = banner_color, justification = 'center')],
        #[sg.Frame('',image_layout, size=(600,315), pad=(10,10))],
        [sg.Button('Launch', font=button_font, pad=(10,10))],
        [sg.Button('Help', font=button_font, pad=(10,10))],
        [sg.Button('Contact', font=button_font, pad=(10,10))],
        [sg.Text('Better Solar, 2022', size=(500,1), font = 'Sathu 12', text_color = 'white', background_color = banner_color, justification = 'center', pad=((1,1),(30,1)))],
    ]

    window = sg.Window("Better Solar", layout, size=(700, 275), alpha_channel=1.0, grab_anywhere=True, element_justification='center')

    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED or button == 'Exit':     # If user closed window with X or if user clicked "Exit" button then exit
            break
        if button == 'Launch':
            window.Hide()
            home_page()
            window.UnHide()
        if button == 'Help':
            sg.Popup('Contact Info')
        if button == 'Contact':
            sg.Popup('Previous work?')


if __name__ == "__main__":
    main()
