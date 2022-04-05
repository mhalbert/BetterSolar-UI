import PySimpleGUI as sg
import os
from PIL import Image
import io
import base64
import time
import ntpath
# files
import glob2
import file_manager
import contactinfo_window
import save_results
from preprocessing import preprocessing
from process_cells import process_cells

# to do:
# provide in documentation of PNGs or GIFS limitation with PYSIMPLEGUI
# write helper function for image flip through, reusing code in two functions below
# add PASS FAIL CHECKBOX FUNCTIONALITY
# maybe have the default select file structure as Select All, to minimize clicking from user
# highlighting all contents of listbox is something that needs to be done via Tkinter
# TODO: check linux and windows comp.
# add model selection option and feed into process_cells
#update contact email
UP =    '▲'
RIGHT = '►'
DOWN =  '▼'
LEFT =  '◄'
# preview processed cells/modules
# TODO: give an output folder, flip through images
def preview_window(output_path,files, module):
    # design variables
    button_font='Menlo 12'
    text_color='#1a385c'
    SYMBOL_UP =    '▲'
    SYMBOL_DOWN =  '▼'

    #input_button_layout = [
    #    [sg.Button(SYMBOL_UP,pad=(5,5)), sg.Button(SYMBOL_DOWN,pad=(5,5))],
    #]

    # depends on multiple cells or single module viewing
    path = output_path #  TODO: temp for now, determine path based on output of model
    if module:
        bio=file_manager.display_output(path,files,module)
        filename=files
    else:
        bio=file_manager.display_output(path,files, module)
        filename=files


    data=bio.getvalue()

    image_layout = [
        [sg.Image(data,key='-IMAGE-')],
        [sg.Text(filename, size=(660,None), key = '-FILENAME-', font='Sathu 11 underline', text_color='#1a385c', justification='c')]
    ]

    layout = [
        [image_layout],
        #[input_button_layout],
    ]

    window = sg.Window('Image Review', layout, size = (660,400), element_justification='center')

    image_counter = 0
    num_files = 1
    if not isinstance(files, str):
        num_files = len(files)

    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED:
            break
        if button == SYMBOL_UP and num_files > 1:
            image_counter -=1
            if image_counter < 0:
                image_counter = num_files + image_counter
        if button == SYMBOL_DOWN and num_files > 1:
            image_counter += 1
            if image_counter >= num_files:
                image_counter -= num_files
        if num_files > 1:
            window['-FILENAME-'].update(files[image_counter])
            bio = file_manager.display_output(path,files[image_counter], False)
            window['-IMAGE-'].update(data=bio.getvalue())

    window.close()
    return


def results_window(module_names, model):
    # design variables
    font = 'Sathu 11'
    header_font = 'Sathu 15 underline'
    font_stats = 'Sathu 13 bold'
    banner_color = '#4d4d73'
    background_color = '#ebecf5'
    font_highlight = '#f0efbb'
    window_width=500
    window_height=600

    t = time.localtime()
    current_time=time.strftime("%H:%M:%S", t)
    output_path = 'demoout/'
    cells_path = 'cells/'
    defect_path = 'defect_percentages/'
    stitched_path = 'stitched/'

    folder_list = module_names
    #file_list = os.listdir(cells_path)
    #files = file_manager.get_filenames(cells,file_list)
    cells = []
    output_select_layout = [
        [sg.Combo(folder_list, enable_events=True, font='Arial 12', size=(30,6), key="-FOLDER LIST-", pad=(10,5))],
        [sg.Listbox(values=cells, enable_events=True, font='Arial 12', size=(30,6), key="-CELLS LIST-", pad=(10,5))],
    ]
    single_report_layout = [
        [sg.Text('Area Cracked (%):', font=font,  background_color = background_color),
            sg.Text('',  key = '-CRACKED-', background_color = background_color, font=font_stats)], # update value per module
        [sg.Text('Contact (%):',  background_color = background_color, font=font),
            sg.Text('',  key='-CONTACT-', background_color = background_color, font=font_stats)],
        [sg.Text('Interconnect (%):',  background_color = background_color, font=font),
            sg.Text('',  key='-INTERCONNECT-', background_color = background_color, font=font_stats)],
        [sg.Text('Corrosion (%):',  background_color = background_color, font=font),
            sg.Text('',  key='-CORROSION-', background_color = background_color, font=font_stats)],
    ]

    listbox_col = sg.Column(output_select_layout,background_color = background_color)
    info_col = sg.Column(single_report_layout, background_color = background_color)
    module_name = ''
    module_grade = {'rating': 'True'}

    layout = [
        [sg.Text('Results', size=(window_width,1), font = 'Sathu 22', text_color = 'white', background_color = banner_color, justification = 'center')],
        [sg.Text('Summary Report', font=header_font,  background_color = background_color)],
        [sg.Text('Time Submitted:\t' + current_time,font=font,  background_color = background_color)],
        [sg.Text('Selected Model:\t' + model, font = font, background_color = background_color)],
        [sg.Text('_'*window_width,font=font,pad=(None,5), background_color = background_color)],
        [sg.Text(module_name, background_color = background_color, font=font_stats, key='-NAME-' ),
            sg.Text('Grade', key='-GRADE-', font=font_stats, background_color = background_color)],
        [sg.Text('Select a module below to view results.',font=font,  background_color = background_color )],
        [listbox_col, info_col],
        [sg.Text('_'*window_width, font=font, pad=(None,5), background_color = background_color)],
        [sg.Text('Preview', font=header_font,  background_color = background_color)],
        [sg.Text('Select a module, or a cell above to preview.', font=font,  background_color = background_color)],
        [sg.Button('Module'), sg.Button('Selected Cell')],
        [sg.Text('_'*window_width,font=font,pad=(None,5),  background_color = background_color)],
        [sg.Button('Save Results')],
        [sg.Button('Return to Home')]
    ]

    window = sg.Window('Results', layout, size=(window_width,window_height), background_color = '#ebecf5')
    saved = False

    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED:
            break
        if button == '-FOLDER LIST-':
            cells = sorted(os.listdir(output_path + values['-FOLDER LIST-'] + '/'+ cells_path))
            window['-CELLS LIST-'].update(cells)
            window['-NAME-'].update('Module  ' + values['-FOLDER LIST-'] +': ')
            stats = (file_manager.get_json_stats(output_path,values['-FOLDER LIST-'],module=True))
            window['-GRADE-'].update('*FAIL*' if stats['rating'] == False else '*PASS*')
            window['-CRACKED-'].update(stats['crack'])
            window['-CONTACT-'].update(stats['contact'])
            window['-INTERCONNECT-'].update(stats['interconnect'])
            window['-CORROSION-'].update(stats['corrosion'])

        if button == 'Selected Cell':
            preview_window(output_path, values['-CELLS LIST-'][0] , False)
        if button == 'Module':
            preview_window(output_path, values['-FOLDER LIST-']  , True)
        if button == 'Save Results':
            try:
                saved = save_results.generate_report()
                sg.Popup('TODO', no_titlebar = True)
            except:
                sg.Popup('An issue occured, could not save results.')
        if button == 'Return to Home':
            if saved:
                break
            else:
                sg.Popup('Results not saved. Are you sure?')
                break
        if button == '-CELLS LIST-':            # list box item select
                # display stats by updating window!
                stats = file_manager.get_json_stats(output_path, values['-CELLS LIST-'][0], False)
                window['-CRACKED-'].update(stats['crack'])
                window['-CONTACT-'].update(stats['contact'])
                window['-INTERCONNECT-'].update(stats['interconnect'])
                window['-CORROSION-'].update(stats['corrosion'])
        # add PASS FAIL CHECKBOX FUNCTIONALITY

    window.close()
    return


def home_page():
    # design variables
    font = 'Sathu 13'
    button_font='Menlo 12'
    header_font = 'Sathu 20 bold'
    info_font = 'Sathu 11'
    listbox_font = 'Arial 12'
    section_color = '#f2f3fc'
    banner_color = '#4d4d73'
    border_width = 5
    window_width=1200
    window_height=750

    default_folder = 'demoinput'
    default_files = sorted(glob2.glob(default_folder+'/*'))
    file_list = []
    for files in default_files:
        file_list.append(files.split('/')[1])

    file_select_layout = [
        [sg.Text('Upload Files',  background_color = section_color, font=header_font)],
        [sg.Text('Upload a folder of module images here to process.',  background_color = section_color, font=font)],
        [sg.Text('Folder:', font = font, pad=(10,10), background_color = section_color), sg.InputText(size=(40,1), enable_events=True,key='-FOLDER-', default_text=default_folder), sg.FolderBrowse(font=button_font, pad=(10,10), )],
        [sg.Text('File(s):', font = font, pad=((10,1),(1,1)), background_color = section_color)], #sg.Text('Manually select from below or check "Select All."', font=info_font, background_color = section_color)],
        [sg.Listbox(file_list, enable_events = True, font = listbox_font, select_mode = 'multiple', size = (40,15), key = "-FILES LIST-", pad=(10,1))],
        [sg.Checkbox('Select All', enable_events = True, key = '-ALL-', default = False, background_color = section_color, font = font, pad = (10,1))],
    ]

    models = glob2.glob('models/*.pth')
    model_names = []
    for model in models:
        model_names.append(model.split('/')[1].split('.')[0])

    default_percentages = ['8','10','5','15']
    default_cells = ['2','5','2','8']
    grading_criteria_table = [
        [sg.Text('Crack', pad=((5,20),(1,5)), font=info_font, background_color = section_color),
            sg.Text('Contact', pad=((33,20),(1,5)), font=info_font, background_color = section_color),
            sg.Text('Interconnect', pad=((15,20),(1,5)), font=info_font, background_color = section_color),
            sg.Text('Corrosion', pad=((10,20),(1,1)), font=info_font, background_color = section_color),
       ],      # add a >100% check
        [sg.Input(default_text=default_percentages[0], justification='c', size=(5,None), pad=((1,11),(1,5)), key='-CRACK %-', font=info_font, background_color = section_color),
            sg.Text('%', font=info_font, background_color = section_color),
            sg.Input(default_text=default_percentages[1], justification='c',  size=(5,None),pad=((12,12),(1,5)), key='-CONTACT %-',  font=info_font,background_color = section_color),
            sg.Text('%', font=info_font, background_color = section_color),
            sg.Input(default_text=default_percentages[2], justification='c',  size=(5,None), pad=((11,12),(1,5)), key='-INTERCONNECT %-',  font=info_font,background_color = section_color),
            sg.Text('%', font=info_font, background_color = section_color),
            sg.Input(default_text=default_percentages[3], justification='c',  size=(5,None),pad=((11,12),(1,1)), key='-CORROSION %-',  font=info_font,background_color = section_color),
            sg.Text('%', font=info_font, background_color = section_color)],
        [sg.Input(default_text=default_cells[0], justification='c', size=(5,None),pad=((1,5),(1,5)), key='-CRACK #-', font=info_font, background_color = section_color),
            sg.Text('cells', font=info_font, background_color = section_color),
            sg.Input(default_text=default_cells[1], justification='c', size=(5,None),pad=((5,5),(1,5)), key='-CONTACT #-',  font=info_font,background_color = section_color),
            sg.Text('cells', font=info_font, background_color = section_color),
            sg.Input(default_text=default_cells[2], justification='c', size=(5,None),pad=((5,5),(1,5)), key='-INTERCONNECT #-',  font=info_font,background_color = section_color),
            sg.Text('cells', font=info_font, background_color = section_color),
            sg.Input(default_text=default_cells[3], justification='c', size=(5,None),pad=((5,5),(1,1)), key='-CORROSION #-',  font=info_font,background_color = section_color),
            sg.Text('cells', font=info_font, background_color = section_color),
        ],
    ]

    grading_criteria_layout = [
        [sg.Text('Module Grading Criteria:', pad=((1,1),(5,1)), font=font,background_color=section_color), sg.Text('minimum values resulting in a module grade of "FAIL"', pad=((1,1),(5,1)), font=info_font,background_color=section_color)],
        [sg.Frame('',grading_criteria_table, background_color=section_color, relief='flat')],
    ]
    defect_categories = 'Defect categories: Crack, Contact, Interconnect, Corrosion'
    model_layout = [
        [sg.Text('Processing Settings',  background_color = section_color, font=header_font)],
        [sg.Text('Select a model from the drop down menu.', background_color=section_color, font=info_font)],
        [sg.Combo(values=model_names, default_value=model_names[0], key='-MODEL-', tooltip=defect_categories, font=font, size=(20,1), pad=((10,50),(10,10)))],
    ]

    model_col = sg.Column(model_layout, background_color=section_color, size=(window_width/3,window_height/6))
    grading_col = sg.Column(grading_criteria_layout, background_color=section_color, size=(window_width*(2/3),window_height/6))
    processing_settings_layout = [
        [model_col, grading_col]
    ]


    frame = [[sg.Text('')]]
    SYMBOL_UP =  '▲'
    SYMBOL_DOWN =  '▼'

    input_button_layout = [
        [sg.Button(SYMBOL_UP,pad=(5,5), auto_size_button=True, tooltip='Previous'),
            sg.Button(SYMBOL_DOWN,pad=(5,5),auto_size_button=True, tooltip='Next')],
        [sg.Button('Preview',font=button_font, pad=(5,5))],
        #[sg.Checkbox('Preview All', enable_events = True, key = '-PREVIEW ALL-', default = False, background_color = section_color, font = 'Sathu 11', pad = (5,5))],

    ]
    image_layout = [[sg.Image(key='-IMAGE-')]]
    input_display_layout = [
        [sg.Text("Preview Files:", pad = (10,None), font=header_font, background_color = section_color)],
        [sg.Text('Click "preview" to begin. Use the arrow keys to flip through your selected files. Check "Select All" to preview all images.', pad = (10, None), font=info_font, background_color = section_color)],
        [sg.Frame('', image_layout, size = (633,322), pad=(10,10), background_color = '#D8D8D8', element_justification='c', relief='flat'),
                sg.Column(input_button_layout, background_color=section_color)],
        [sg.Text('', key = 'FILENAME', font='Sathu 11 underline', text_color='#1a385c', background_color=section_color)],
    ]

    file_select_col = sg.Column(file_select_layout, background_color=section_color, size=(window_width/3,window_height*0.56), element_justification='l')
    model_select_col = sg.Column(processing_settings_layout,  background_color=section_color, size=(window_width,window_height/6), element_justification='l')
    input_display_col = sg.Column(input_display_layout, background_color = section_color, size = (window_width*2/3,window_height*0.56), element_justification='l')

    layout = [
        [sg.Text('Home', size=(window_width,1), font = 'Sathu 22', text_color = 'white', background_color = banner_color, justification = 'center')],
        [file_select_col,input_display_col],
        [model_select_col],
        [sg.Text( '_' * window_width, font='Sathu 12 bold')],
        [sg.Button('Run', size=(5,1),font=button_font, pad=(5,10),  button_color = '#cf3f32'), sg.Button('View Previous Results',font=button_font, pad=(5,10))],
        [sg.Button('Back to Menu', font = button_font, pad=(5,1))],
        [sg.Text('', size=(window_width,1), font = 'Sathu 22', text_color = 'white', background_color = banner_color, justification = 'center', pad=((1,1),(10,1)))],
    ]

    window = sg.Window('Home', layout, size=(window_width,window_height))
    image_counter = 0
    prev = False
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Back to Menu':
            break
        if event == '-FOLDER-':
            folder = values['-FOLDER-']
            files = sorted(glob2.glob(folder + '/*'))
            file_list=[]
            for file in files:
                file_list.append(ntpath.basename(file))
            window['-FILES LIST-'].update(file_list)
        if event == 'Run':
            folder = values['-FOLDER-']
            if values['-ALL-'] == True:
                # files = file_manager.get_filenames(folder,file_list)
                files = sorted(glob2.glob(folder + '/*'))
            else:
                all_files = sorted(glob2.glob(folder + '/*'))
                files = []
                for value in values['-FILES LIST-']:
                    files.append([file for file in all_files if value in file][0])
                # files = values['-FILES LIST-']
            if not files:
                sg.Popup('Select files to begin.', font=font, no_titlebar=True)
            else:
                # preprocess modules in folder and store in /images/module_xx
                # print(ntpath.basename(folder))
                # print(files)
                image_paths = preprocessing(files)
                # create grading criteria list
                grading_criteria = [values['-CRACK %-'], values['-CRACK #-'],
                                    values['-CONTACT %-'], values['-CONTACT #-'],
                                    values['-INTERCONNECT %-'], values['-INTERCONNECT #-'],
                                    values['-CORROSION %-'], values['-CORROSION #-']]
                sg.popup_animated('popup.PNG','processing - please wait', text_color='white', font=font, background_color='#e8995d')
                # pass those to the processing algorithm
                output_mods = process_cells(image_paths, [int(x) for x in grading_criteria],
                                            model_name=values['-MODEL-']+'.pth')
                sg.popup_animated(None)
                # open results window with output paths.
                results_window(output_mods, values['-MODEL-'])
                prev=True
        if event == 'View Previous Results':
            if not prev:
                results_window(os.listdir('demoout'), values['-MODEL-'])
            else:
                results_window(output_mods, values['-MODEL-'])
        if event == "Preview":
            if values['-ALL-'] == True:
                folder = values['-FOLDER-']
                files = sorted(glob2.glob(folder + '/*'))
                file_list=[]
                for file in files:
                    file_list.append(ntpath.basename(file))
            else:
                file_list = values['-FILES LIST-']
            path = values['-FOLDER-'] + '/'
            if not file_list:
                sg.Popup('Select a file to preview.',font=font, no_titlebar=True)
            else:
                bio = file_manager.display(path,file_list[0])
                window["-IMAGE-"].update(data=bio.getvalue())
                window['FILENAME'].update(file_list[0])
        if event == SYMBOL_DOWN and (len(values['-FILES LIST-'])>1 or values['-ALL-'] == True):
            image_counter += 1
            path = values['-FOLDER-'] + '/'
            num_files=len(file_list)
            if image_counter >= num_files:
                image_counter -= num_files
            window['FILENAME'].update(file_list[image_counter])
            bio = file_manager.display(path,file_list[image_counter])
            window['-IMAGE-'].update(data=bio.getvalue())
        if event == SYMBOL_UP and (len(values['-FILES LIST-'])>1 or values['-ALL-'] == True):
            image_counter -= 1
            path = values['-FOLDER-'] + '/'
            num_files=len(file_list)
            if image_counter < 0:
                image_counter = num_files + image_counter
            window['FILENAME'].update(file_list[image_counter])
            bio = file_manager.display(path,file_list[image_counter])
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
        [sg.Button('Launch', font=button_font, pad=((1,1),(40,1)))],
        [sg.Button('Contact Us', font=button_font, pad=((1,1),(10,1)))],
        [sg.Text('Better Solar, 2022', size=(500,1), font = 'Sathu 12', text_color = 'white', background_color = banner_color, justification = 'center', pad=((1,1),(75,1)))],
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
        if button == 'Contact Us':
            contactinfo_window.window()

    window.close()

if __name__ == "__main__":
    main()
