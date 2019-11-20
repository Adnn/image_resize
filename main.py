#!/usr/bin/env python
from PIL import Image

import os

IDEAL_SIZE = (2288, 1525) # real 3:2
JPG_QUALITY = 95
DEST = "resized"
# Found using PIL ExifTags, following the method from: https://stackoverflow.com/a/26928142/1027706
EXIF_ORIENTATION = 274

def is_landscape(image):
    print("x:{} y:{}".format(image.size[0], image.size[1]))
    return image.size[0] >= image.size[1]

if __name__ == "__main__":

    if not os.path.exists(DEST):
        os.mkdir(DEST)

    #for filename in [fn for fn in os.listdir()]:
    #    print("{}".format(os.path.splitext(filename)[1]))
    for image, filename in [(Image.open(fn), fn) for fn in os.listdir() if os.path.splitext(fn)[1] in (".jpg", ".jpeg")]:
        x = image.size[0]
        y = image.size[1]

        # We must "bake" the rotation into the image, because PIL does not forward the EXIF info into the output
        exif = dict(image._getexif().items())
        try:
            rotation = exif[EXIF_ORIENTATION]
        except KeyError:
            rotation = 0

        if (rotation == 6): # The image is rotated 90° clockwise when presented
            image = image.rotate(90*3, expand=True) # It must be rotated 270° counter clockwise to be up
        elif (rotation == 8): # The image is rotated 90° counterclockwise when presented
            image = image.rotate(90, expand=True) # It must be rotated 90° counter clockwise to be up

        target = IDEAL_SIZE if is_landscape(image) else (IDEAL_SIZE[1], IDEAL_SIZE[0])

        resize_ratio = max(target[0]/x, target[1]/y)
        resized_image = \
            image.resize([round(dimension * resize_ratio) for dimension in image.size], resample=Image.LANCZOS)
        print("Input ratio: {}. New size with ratio of {} is {}".format(max(x, y)/min(x, y), resize_ratio, resized_image.size))

        destination = os.path.join(DEST, os.path.basename(filename))
        resized_image.save(destination , fomat="JPEG", quality=JPG_QUALITY)
