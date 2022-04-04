import pvimage as pvi
import cell_cropping
import glob2
import os
import cv2

def preprocessing(folder):
    image_folder = sorted(glob2.glob(folder+'/*'))
    print(image_folder)
    # run through all modules, chop into cells
    for image in image_folder:
        save_path = image.split('.')[0] + '/images/'
        print(save_path)
        os.makedirs(save_path, exist_ok=True)
        h, w = 6,10                                       # for demo purposes... TODO: figure out automating
        try:
            n, f = pvi.pipelines.GetLensCorrectParams(image)
            pvi.pipelines.FMpipeline(image, save_path, n, f, w, h, savesmall=False)
        except ValueError:
            try:
                # temporary, gets bad automatic split
                if image.split('/')[1].split('.')[0] == 'M0004C000cd0':
                    raise cv2.error
                cell_cropping.CellCropComplete(image, save_path, w, h, 'auto')
            except cv2.error:
                cell_cropping.CellCropComplete(image, save_path, w, h, 'manual')


