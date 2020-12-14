#!/usr/bin/env python
from PIL import Image, ExifTags
import piexif
from termcolor import colored

import argparse
import os

# Found using PIL ExifTags, following the method from: https://stackoverflow.com/a/26928142/1027706
# They are not required anymore, since we use piexif additional module
EXIF_ORIENTATION = 274
EXIF_IMAGEWIDTH  = 40962
EXIF_IMAGEHEIGHT = 40963

def is_landscape(image):
    return image.size[0] >= image.size[1]

def print_warn(msg):
    print(colored("\tWARNING: {}".format(msg), "yellow"))

def print_alarm(msg):
    print(colored("\tATTENTION: {}".format(msg), "red"))

def print_info(msg):
    print("\tINFO: {}".format(msg))

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Resizes all images from working directory preserving aspect"
                                     " ratio, with target size as lower bounds")
    parser.add_argument("destination", help="The folder where modified images are saved")
    parser.add_argument("-t", "--target", help="Target size with format \"x,y\" (lower bounds)",
                        default="2288,1525") # real 3:2
    parser.add_argument("-q", "--quality", type=int, help="Jpeg quality", default=83)
    parser.add_argument("--keep-gps", help="Maintain GPS data", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.destination):
        os.mkdir(args.destination)

    target = [int(dimension) for dimension in args.target.split(",")]

    for image, filename in [(Image.open(fn), fn) for fn in os.listdir()
                                if os.path.splitext(fn)[1] in (".jpg", ".jpeg")]:
        (x, y) = (image.size[0], image.size[1])
        source_filesize = os.path.getsize(filename)
        print("File: \'{}\' with dimensions ({}, {}), ratio {:.2f}, filesize {} kB"
                .format(filename, x, y, max(x, y)/min(x, y), int(source_filesize/1024)))

        # Pillow does not forward the EXIF info into the output, we do that manually
        # Getting exif dictionary from Pillow, we did not find a way to save it back
        #exif_dict = dict(image._getexif().items())
        exif_dict = piexif.load(image.info["exif"])

        # If the image is portrait, the target dimensions are reversed
        if not is_landscape(image):
            target.reverse()

        factor = max(target[0]/image.size[0], target[1]/image.size[1])

        if factor >= 1:
            print_warn("Image already smaller than the target, ignoring resize factor {}".format(factor))
        else:
            print_info("Resize factor: {}".format(factor))
            new_size = [round(d*factor) for d in image.size]
            image = image.resize(new_size, resample=Image.LANCZOS)
            exif_dict["Exif"][EXIF_IMAGEWIDTH] = new_size[0]
            exif_dict["Exif"][EXIF_IMAGEHEIGHT] = new_size[1]
            # Equivalent :
            #exif_dict["Exif"][piexif.ExifIFD.PixelYDimension] = new_size[1]

        if not args.keep_gps:
            del exif_dict["GPS"]

        destination = os.path.join(args.destination, os.path.basename(filename))
        image.save(destination, format="JPEG", quality=args.quality, exif=piexif.dump(exif_dict))
        destination_filesize = os.path.getsize(destination)
        print_info("Final dimensions {}, filesize {} kB (compression ratio {:.1f}%)"
                .format(image.size,
                        int(destination_filesize/1024),
                        destination_filesize*100/source_filesize))

        if (destination_filesize > source_filesize):
            print_alarm("Resulting image is larger in filesize !")
