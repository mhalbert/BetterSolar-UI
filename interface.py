import PySimpleGUI as sg
import os
from PIL import Image
import io
import base64

def preview_window():
    image = Image.open('/Users/melodyhalbert/Desktop/your_ouput/stitchmod.jpg')
    image.thumbnail((520, 300))
    bio = io.BytesIO()
    image.save(bio, format="jpeg")

    layout = [[sg.Image(image, key='-IMAGE-')]]
    window = sg.Window('Image Review', layout, size = (600,600))

    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED:
            break
    window.close()


def run_model():
    font = 'Arial 12'
    font_stats = 'Arial 12 bold'
    banner_color = '#4d4d73'
    background_color = '#ebecf5'

    clean = [sg.Text('Clean:', font=font,  background_color = background_color), sg.Text('69',  background_color = '#f0efbb', font=font_stats)]
    cracked = [sg.Text('Cracked:', font=font,  background_color = background_color), sg.Text('3',  background_color = '#f0efbb', font=font_stats)]
    highlighted = [sg.Text('Highlighted Cells:',  background_color = background_color, font=font), sg.Text('45, 52, 58',  background_color = '#f0efbb', font=font_stats)]

    layout = [
        [sg.Text('Results', size=(950,1), font = 'Sana 22', text_color = 'white', background_color = banner_color, justification = 'center')],
        [sg.Text('Summary Report', font='Arial 15 bold',  background_color = background_color)],
        [sg.Text('Time Submitted: 12:44:03 pm   Location: Orlando, Florida',font=font,  background_color = background_color)],
        [sg.Text('default: crack area above (0.05)', font = font, background_color = background_color)],
        [clean, cracked],
        [highlighted],
        [sg.Text('_'*500,font=font,pad=(10,10),  background_color = background_color)],
        [sg.Text('Preview', font='Arial 15 bold',  background_color = background_color)],
        [sg.Text('sort by: ',  background_color = background_color), sg.Checkbox('Clean',  background_color = background_color), sg.Checkbox('Cracked',  background_color = background_color)],
        [sg.Button('Preview')],
        [sg.Text('_'*500,font=font,pad=(10,10),  background_color = background_color)],
        [sg.Button('Save Results')],
        [sg.Button('Return to Home')] # add check for 'are you sure?'
    ]

    window = sg.Window('Results', layout, size=(500,500), background_color = '#ebecf5')
    saved = False
    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED:
            break
        if button == 'Review Results':
            preview_window()
        if button == 'Save Results':
            sg.Popup('Results Saved.')
            saved = True
        if button == 'Return to Home':
            if saved:
                break
            else:
                sg.Popup('Results not saved. Are you sure?')

    window.close()




def home_page():
    models=['5-class defect segmentation', 'Model A', 'Model B', 'Model C']
    header_font = 'Sathu 20 bold'
    font = 'Sathu 13'
    border_width = 5
    section_color = '#ebecf5'
    button_font='Menlo 12'
    banner_color = '#4d4d73'


    file_select_layout = [
        [sg.Text('Upload Files',  background_color = section_color, font=header_font)],
        [sg.Text('Folder:', font=font, pad=(10,10), background_color = section_color), sg.InputText(size=(40,1), enable_events=True,key='-FOLDER-'), sg.FolderBrowse(font=button_font, pad=(10,10), )],
        [sg.Text('File(s):', font = font, pad=(10,1), background_color = section_color)],
        [sg.Listbox(values=[], enable_events=True, font='Any 12', select_mode = 'multiple', size=(40,15), key="-FILES LIST-", pad=(10,1))], #sg.Text('Selected:', font=font, background_color = '#d1d8e0')],
        [sg.Checkbox('Select All', background_color = section_color, font=font, pad=(10,1))],
    ]

    model_select_layout = [
        [sg.Text('Processing Settings',  background_color = section_color, font=header_font)],
        [sg.Text('Select a model from the drop down menu.', background_color=section_color, font=font)],
        [sg.Combo(values=models, default_value=models[0], key='model', font=font, size=(20,1),
                  pad=((10,50),(10,10))),
                  sg.Checkbox('Cell Counts', font=font, background_color = section_color),
                  sg.Checkbox('Highlighted Cells',  font=font,background_color = section_color),
                  sg.Checkbox('Category 3', font=font, background_color = section_color)],
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
        #[sg.Text('*display modules directly here with a sequential flip through process*', pad = (20, None), font = font, background_color = section_color)],
        #[sg.Button('Previous', pad=(10,1)), sg.Button('Next', pad=(None,1))],
        [sg.Frame('', image_layout, size = (633,322), pad=(10,10), background_color = '#D8D8D8', element_justification='c'), sg.Column(input_button_layout, background_color=section_color)],
    ]
    output_display_layout = [
        [sg.Text('*either display here, or in popup window*', font = font)],
    ]

    file_select_col = sg.Column(file_select_layout, background_color=section_color, size=(400,400), element_justification='l')
    model_select_col = sg.Column(model_select_layout,  background_color=section_color, size=(1200,100), element_justification='l')
    input_display_col = sg.Column(input_display_layout, background_color = section_color, size = (800,400), element_justification='l')
    #output_display_col = sg.Column([[sg.Frame('Results', output_display_layout, border_width = border_width, font = header_font)]])

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

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
            # implement Quit function
        if event == 'Main Menu':
            break
        if event == '-FOLDER-':
            folder = values['-FOLDER-']
            try:
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and f.lower().endswith(('.png'))]

            window['-FILES LIST-'].update(fnames)
        if event == 'Run' or event == 'Run All':
            run_model()
        if event == '-FILES LIST-':
            continue
        if event == 'Select All':
            sg.Popup('TODO')
        if event == "Preview":
            filename = values["-FILES LIST-"]
            if not filename:
                sg.Popup('Select a file to preview.')
            elif os.path.exists('/Users/melodyhalbert/Desktop/testuifiles/'+filename[0]):
                image = Image.open('/Users/melodyhalbert/Desktop/testuifiles/'+filename[0])
                image.thumbnail((633, 322))
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                window["-IMAGE-"].update(data=bio.getvalue())
                window['FILENAME'].update(filename[0])

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

    image_layout = [
        [sg.Text('*Picture Here*')],
    ]

    font='Sathu 12'
    button_font='Menlo 12'
    banner_color = '#4d4d73'

    #heading font

    layout = [
        [sg.Text('Main Menu', font = 'Sathu 18', size=(700,1),pad=((0,0),(1,30)), text_color = 'white', background_color = banner_color, justification = 'center')],
        #[sg.Frame('',image_layout, size=(600,315), pad=(10,10))],
        [sg.Button('Launch', font=button_font, pad=(10,10))],
        [sg.Button('Help', font=button_font, pad=(10,10))],
        [sg.Button('Library', font=button_font, pad=(10,10))],

        [sg.Text('Better Solar, March 2022', size=(500,1), font = 'Sathu 12', text_color = 'white', background_color = banner_color, justification = 'center', pad=((1,1),(30,1)))],

    ]

    window = sg.Window("Welcome Page", layout, size=(700, 275), alpha_channel=1.0, grab_anywhere=True, element_justification='center')

    while True:
        button, values = window.read()
        if button == sg.WIN_CLOSED or button == 'Exit':     # If user closed window with X or if user clicked "Exit" button then exit
            break
        if button == 'Launch':
            window.Hide()
            home_page()
            window.UnHide()
        if button == 'Report Issues/Help':
            sg.Popup('Contact Info')
        if button == 'Library':
            sg.Popup('Previous work?')



if __name__ == "__main__":
    main()
