from PIL import Image
import PySimpleGUI as sg
import io
import os
import base64

def compatibility_check(filename):
    if filename.lower().endswith(('.png')):
        return True
    elif filename.lower().endswith(('.jpg')):
        return True
    else:
        return False

def get_filenames(folder,file_list):
    return [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and compatibility_check(f) ]

def display(path, file):
    image = Image.open(path+file)
    image.thumbnail((633, 322))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    return bio

def main():
    return
if __name__ == "__main__":
    main()
