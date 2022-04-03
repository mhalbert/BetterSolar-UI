import pvimage as pvi
import cell_cropping
import glob2
import os
import cv2


image_folder = sorted(glob2.glob('Module_Images/*'))

# run through all modules, chop into cells
for pth in image_folder:
    if os.path.isdir(pth):
        mods = sorted(glob2.glob(pth + '/*'))
        for mod in mods:
            save_path = 'images/' + mod.split('/')[2].split('.')[0] + '/'
            os.makedirs(save_path, exist_ok=True)
            h, w = [int(i) for i in mod.split('/')[1].split('x')]
            try:
                n, f = pvi.pipelines.GetLensCorrectParams(mod)
                pvi.pipelines.FMpipeline(mod, save_path, n, f, w, h, savesmall=False)
            except ValueError:
                try:
                    # temporary, gets bad automatic split
                    if mod.split('/')[2].split('.')[0] == 'M0004C000cd0':
                        raise cv2.error
                    cell_cropping.CellCropComplete(mod, save_path, w, h, 'auto')
                except cv2.error:
                    cell_cropping.CellCropComplete(mod, save_path, w, h, 'manual')



