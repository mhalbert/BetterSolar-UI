import pvimage as pvi
import cell_cropping
from pvimage import process
import os
import cv2


def preprocessing(images):
    # image_folder = sorted(glob2.glob(folder+'/*'))
    new_paths = []
    # run through all modules, chop into cells
    for image in images:
        save_path = os.path.join('images', os.path.basename(image).split('.')[0])
        new_paths.append(save_path)
        # skip if path has already been created
        if os.path.isdir(save_path):
            continue

        print(save_path)
        os.makedirs(save_path, exist_ok=True)
        h, w = 6, 10                                       # for demo purposes... TODO: figure out automating
        try:
            n, f = pvi.pipelines.GetLensCorrectParams(image)
            FMpipeline(image, save_path, n, f, w, h, savesmall=False)
        except ValueError:
            try:
                # temporary, gets bad automatic split
                # if image.split('/')[1].split('.')[0] == 'M0004C000cd0':
                #     raise cv2.error
                cell_cropping.CellCropComplete(image, save_path, w, h, 'auto')
            except cv2.error:
                cell_cropping.CellCropComplete(image, save_path, w, h, 'manual')

    return new_paths


# modified pv image code
"""
Created on Thu Jan 30 10:29:52 2020

@author: jlbraid
"""
def FMpipeline(imagepath, savepath, n=None, f=None, numCols=None, numRows=None, savesmall=False, imgtype=''):
    """Performs full-size module image processing steps, including
        lens correction, planar indexing, and cell extraction, if desired.

        Lens correction is performed if n and f are provided.
        n and f can be found with the GetLensCorrectParams function.
        Cells are extracted if numCols and numRows are provided.

    Args:
        imagepath (str): path to a raw image
        savepath (str): folder path for saving output
        numCols (int): number of cells across in module image
        numRows (int): number of cells down in module image
        savesmall (bool): Save a smaller .jpg version of the planar indexed
            image with True. Default is False.
        imgtype (str):  'UVF' UV Fluorescence Image
                        'gradient' for unequal intensity across the image
                        'lowcon' low contrast between cell and background
                            or PL images without background subtraction
    Returns:

    """
    img = cv2.imread(imagepath)
    if (n is not None) and (f is not None):
        img = process.lensCorrect(img, n, f)
    planarindexed = process.PlanarIndex(img, imgtype)
    file_name = os.path.split(imagepath)[1]
    image_name = os.path.join(savepath, file_name)
    cv2.imwrite(image_name.replace('.jpg', '_module.jpg'), planarindexed)
    if savesmall == True:
        dims = planarindexed.shape
        y = int(dims[0] / 3)
        x = int(dims[1] / 3)
        jpg_name = os.path.splitext(image_name)[0] + '.jpg'
        cv2.imwrite(jpg_name, cv2.resize(planarindexed, (x, y)))
    if (numCols is not None) and (numRows is not None):
        cellarrays = process.CellExtract(planarindexed, numCols, numRows)
        for i in range(len(cellarrays)):
            out = cellarrays[i]
            file_name, ext = os.path.splitext(os.path.split(imagepath)[1])
            image_name = os.path.join(savepath, os.path.splitext(file_name)[0] + '_' + '{:02}'.format(i + 1) + ext)
            cv2.imwrite(image_name, out)
    return True

