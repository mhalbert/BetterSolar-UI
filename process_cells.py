import json
import matplotlib
import numpy as np
import glob2
import torch
import torchvision
from torchvision.models.segmentation.deeplabv3 import DeepLabHead
from torchvision import transforms as t
from matplotlib import pyplot as plt
from PIL import Image
import os
import stitch_cells


# editable parameters, set up to fit local file structure
##################################################
image_path = 'images/'                # folder where images are
model_path = 'models/'                # folder where model is stored
model_name = 'model_97.pth'           # trained model name
save_path = 'demoout/'                # location to save figures
defect_dir = 'defect_percentages/'    # location to save defect percentage jsons
##################################################
################ model parameters ################
pre_model = 'deeplabv3_resnet50'      # backbone model was trained on
num_classes = 5                       # number of classes model trained on
threshold = .52                       # threshold for defect interpretation
aux_loss = True                       # loss type model trained with
##################################################

# PRELIMINARY MODEL SETUP
# softmax layer for defect interpretation
softmax = torch.nn.Softmax(dim=0)

# this section loads in the weights of an already trained model
model = torchvision.models.segmentation.__dict__[pre_model](aux_loss=aux_loss,
                                                            pretrained=True)

# changes last layer for output of appropriate class number
if pre_model == 'deeplabv3_resnet50' or pre_model == 'deeplabv3_resnet101':
    model.classifier = DeepLabHead(2048, num_classes)
else:
    num_ftrs_aux = model.aux_classifier[4].in_channels
    num_ftrs = model.classifier[4].in_channels
    model.aux_classifier[4] = torch.nn.Conv2d(num_ftrs_aux, num_classes, kernel_size=1)
    model.classifier[4] = torch.nn.Conv2d(num_ftrs, num_classes, kernel_size=1)

# model = model.cuda()
checkpoint = torch.load(model_path+model_name, map_location='cpu')
model.load_state_dict(checkpoint['model'])
model.eval()

# transforms to put images through the model
trans = t.Compose([t.ToTensor(), t.Normalize(mean=.5, std=.2)])

# create custom colormap for image visualizations [Black, Red, Blue, Purple, Orange]
cmaplist = [(0.001462, 0.000466, 0.013866, 1.0),
            (0.8941176470588236, 0.10196078431372549, 0.10980392156862745, 1.0),
            (0.21568627450980393, 0.49411764705882355, 0.7215686274509804, 1.0),
            (0.596078431372549, 0.3058823529411765, 0.6392156862745098, 1.0),
            (1.0, 0.4980392156862745, 0.0, 1.0)]

# create the new map
cmap = matplotlib.colors.LinearSegmentedColormap.from_list('Custom', cmaplist, len(cmaplist))


def process_cells(image_paths):
    cnt = 0
    os.makedirs(save_path, exist_ok=True)
    all_modules = []
    for mod in image_paths:
        # this time, only care about folders, not module images
        if not os.path.isdir(mod):
            print('There should only be module folders here. Images in this directory will not be processed.')
            continue

        cnt += 1
        cells = sorted(glob2.glob(mod + '/*'))

        # create necessary paths
        module_name = mod.split('/')[-2].split('.')[0]
        module_path = save_path + module_name
        all_modules.append(module_name)
        os.makedirs(module_path, exist_ok=True)
        os.makedirs(module_path + '/defect_percentages/', exist_ok=True)
        os.makedirs(module_path + '/cells/', exist_ok=True)
        os.makedirs(module_path + '/stitched/', exist_ok=True)

        # analysis criterion
        crack_instances, contact_instances, corrosion_instances = 0, 0, 0
        cell_crack, cell_contact, cell_corrosion = True, True, True
        total_defective = torch.zeros(4)
        PASS = True

        for idx, cell in enumerate(cells):
            # opens up and preps image (RGB to benefit from pretrained model)
            if os.path.isdir(cell):
                print('There should only be cells in the module folder.')
                continue

            # we don't care about module in cell processing
            if '_module' in cell:
                continue

            im = Image.open(cell).convert('RGB')
            img = trans(im).unsqueeze(0)
            output = model(img)['out']

            # threshold to determine defect vs. non-defect instead of softmax (custom for this model)
            soft = softmax(output[0])
            nodef = soft[0]
            nodef[nodef < threshold] = -1
            nodef[nodef >= threshold] = 0
            nodef = nodef.type(torch.int)
            def_idx = soft[1:].argmax(0).type(torch.int)
            def_idx = def_idx + 1
            nodef[nodef == -1] = def_idx[nodef == -1]

            # name is for saving json with defect percentage
            name = f'{module_name}_{(idx+1):02d}'

            # counts stats of pixels/defect percentages
            output_pix = torch.count_nonzero(nodef)
            total_pix = torch.numel(nodef.detach())

            output_defect_percent = torch.div(output_pix.type(torch.float), total_pix)

            # defect portions of each category
            crack_portion = torch.mul(torch.div(torch.count_nonzero(nodef == 1), total_pix), 100)
            contact_portion = torch.mul(torch.div(torch.count_nonzero(nodef == 2), total_pix), 100)
            interconnect_portion = torch.mul(torch.div(torch.count_nonzero(nodef == 3), total_pix), 100)
            corrosion_portion = torch.mul(torch.div(torch.count_nonzero(nodef == 4), total_pix), 100)

            total_defective += torch.tensor([crack_portion, contact_portion, interconnect_portion, corrosion_portion])

            # add instance if single cell portion is of given size
            if crack_portion > 5:
                crack_instances += 1
                cell_crack = True
            if contact_portion > 10:
                contact_instances += 1
                cell_contact = True
            if corrosion_portion > 10:
                corrosion_portion += 1
                cell_corrosion = True

            # creates json to save defect percentage per class category
            defect_percentages = {'crack': round(float(crack_portion), 4), 'contact': round(float(contact_portion), 4),
                                  'interconnect': round(float(interconnect_portion), 4),
                                  'corrosion': round(float(corrosion_portion), 4), 'has_crack': cell_crack,
                                  'has_contact_defect': cell_contact, 'has_corrosion': cell_corrosion}

            with open(module_path + '/defect_percentages/' + name + '.json', 'w') as fp:
                json.dump(defect_percentages, fp)

            cell_crack, cell_contact, cell_corrosion = False, False, False

            orig_img = (img * .2) + .5
            nodef = np.ma.masked_where(nodef == 0, nodef)

            # plots the original image next to prediction (with defect percentage)
            plt.subplot(1, 2, 1)
            plt.imshow(orig_img[0][0].numpy(), cmap='gray', vmin=0, vmax=1)
            plt.axis('off')
            plt.title('original image')
            plt.subplot(1, 2, 2)
            plt.imshow(orig_img[0][0], cmap='gray', vmin=0, vmax=1)
            plt.imshow(nodef, cmap=cmap, vmin=0, vmax=4, alpha=.3)
            plt.title('image + prediction')
            plt.tick_params(axis='both', labelsize=0, length=0)
            plt.xlabel("Defective Portion: " + str(torch.mul(output_defect_percent, 100).numpy().round(4)))
            # plt.savefig(save_path + str(i) + '.png') # comment back in to save figures
            plt.show()
            plt.clf()

            plt.imshow(orig_img[0][0], cmap='gray', vmin=0, vmax=1)
            plt.imshow(nodef, cmap=cmap, vmin=0, vmax=4, alpha=.3)
            plt.axis('off')
            plt.savefig(module_path + '/cells/' + name + '.jpg', bbox_inches='tight', transparent=True, pad_inches=0)
            plt.clf()

        cell_glob = sorted(glob2.glob(module_path + '/cells/*'))
        num_cells = len(cell_glob)

        if num_cells == 36:
            h, w = 3, 12
        elif num_cells == 60:
            h, w = 6, 10
        elif num_cells == 72:
            h, w = 6, 12
        else:
            h, w = 8, 12

        stitch_cells.stitch_cells(cell_glob, h, w)

        total_defective = torch.div(total_defective, num_cells)

        # TODO: set module pass/fail criteria
        if total_defective[0] > 5:
            PASS = False
        elif total_defective[1] > 5:
            PASS = False
        elif total_defective[2] > 2:
            PASS = False
        elif total_defective[3] > 5:
            PASS = False

        total_defective = total_defective.numpy()
        print('Module ' + module_name + ': ' + str(total_defective))
        print('Crack Instances: ' + str(crack_instances))
        print('Contact Defect Instances: ' + str(contact_instances))
        print('Corrosion Defect Instances: ' + str(corrosion_instances))
        print('Pass: ' + str(PASS))

        # creates json to save defect percentage per class category
        module_defect_stats = {'crack': round(float(total_defective[0]), 4), 'contact': round(float(total_defective[1]), 4),
                               'interconnect': round(float(total_defective[2]), 4),
                               'corrosion': round(float(total_defective[3]), 4), 'crack_instances': crack_instances,
                               'contact_instances': contact_instances, 'corrosion_instances': corrosion_instances,
                               'rating': PASS}

        with open(module_path + '/defect_percentages/' + module_name + '.json', 'w') as fp:
            json.dump(module_defect_stats, fp)

    return all_modules


