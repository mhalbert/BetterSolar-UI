from PIL import Image
import PySimpleGUI as sg
import io
import os
import base64
import json
import ntpath

# os.path.split or os.path.basename doesn't work on Linux or Windows.. so,
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_json_stats(output_path, filename, module):
    if module:
        path = output_path + (ntpath.splitext(filename))[0] + '/defect_percentages/' + (ntpath.splitext(filename))[0] + '.json'
    else:
        path = output_path + ((ntpath.splitext(filename)[0]).split('_',1))[0] + '/defect_percentages/' + ntpath.splitext(filename)[0] +'.json'

    f = open(path)
    stats = json.loads(f.read())
    return stats

def compatibility_check(filename):
    if filename.lower().endswith(('.png')):
        return True
    elif filename.lower().endswith(('.jpg')):
        return True
    else:
        return False

def get_filenames(folder,file_list):
    return [ f for f in file_list if os.path.isfile(os.path.join(folder,f)) and compatibility_check(f) ]

def display_output(path, file, module):
    if module:
        module_path = path + file + '/stitched/' + file + '_col.jpg'
        image = Image.open(module_path)
    else:
        cells_path = path + (file.split('_',1))[0] + '/cells/' + file
        image = Image.open(cells_path)

    image.thumbnail((633, 322))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    return bio


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
