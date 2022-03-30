from PIL import Image
import PySimpleGUI as sg
import io
import base64

def display(path, file):
    image = Image.open(path+file)
    image.thumbnail((633, 322))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    return bio


def main(path, file):
    display(path, file)

if __name__ == "__main__":
    main()
