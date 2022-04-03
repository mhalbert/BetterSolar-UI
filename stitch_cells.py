from PIL import Image
from matplotlib import pyplot as plt


def merge_images(file1, file2, side=0):
    """Merge two images into one, displayed side by side
    :param file1: path to first image file
    :param file2: path to second image file
    :return: the merged Image object
    """
    image1 = Image.open(file1) if isinstance(file1, str) else file1
    image2 = Image.open(file2) if isinstance(file2, str) else file2

    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = width1 + width2 if side == 1 else max(width1, width2)
    result_height = max(height1, height2) if side == 1 else height1 + height2

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width1, 0) if side == 1 else (0, height1))
    return result


def stitch_cells(cells, height, width):
    rebuild = 1
    height_arr = []
    old_col = Image.new("1", (0, 0))
    old_row = Image.new("1", (0, 0))
    for w in range(width):
        for h in range(height):
            height_arr.append([i for i in cells if '_' + f"{(width*h + w + 1):02d}" in i][0])
        for h in range(height - 1):
            if h == 0:
                col = merge_images(height_arr[h], height_arr[h + 1], side=0)
            else:
                col = merge_images(col, height_arr[h + 1], side=0)

            # plt.imshow(merge_images(old_col, col, side=1))
            # plt.axis('off')
            # plt.savefig(f'data/newout/cascade/rebuild{rebuild:02d}.jpg', bbox_inches='tight', transparent=True,
            #             pad_inches=0)
            # plt.clf()
            # plt.show()
            # plt.imsave(f'data/newout/cascade/rebuild{rebuild:02d}.jpg', merge_images(old_col, col, side=1),
            #            cmap=None)
            rebuild += 1
        height_arr = []
        if w != 0:
            old_col = merge_images(old_col, col, side=1)
        else:
            old_col = col

    for h in range(height):
        for w in range(width):
            height_arr.append([i for i in cells if '_' + f"{(width*h + w + 1):02d}" in i][0])
        for w in range(width - 1):
            if w == 0:
                row = merge_images(height_arr[w], height_arr[w + 1], side=1)
            else:
                row = merge_images(row, height_arr[w + 1], side=1)
        height_arr = []
        if h != 0:
            old_row = merge_images(old_row, row, side=0)
        else:
            old_row = row

    old_col.save(cells[0].replace('cells', 'stitched').replace('_01.jpg', '_col.jpg'))
    old_row.save(cells[0].replace('cells', 'stitched').replace('_01.jpg', '_row.jpg'))
