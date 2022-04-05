import PySimpleGUI as sg

def window():
    font='Sathu 12'
    button_font='Menlo 12'
    banner_color = '#4d4d73'

    layout = [
        [sg.Text('Questions? Contact us: ', font=font, pad=((0,0),(50,0)))],
        [sg.InputText('contact@bettersolargroup.com', size=(300,1), justification='c', use_readonly_for_disable=True, disabled=True, key='-IN-', font='Sathu 12 underline', text_color='#1a385c')]
    ]
    window = sg.Window('Contact', layout, size = (300,300), element_justification='c', finalize=True)
    window['-IN-'].Widget.config(readonlybackground=sg.theme_background_color())
    window['-IN-'].Widget.config(borderwidth=0)
    window.read()
    window.close()
    return

def main():
    window()


if __name__ == "__main__":
    main()
