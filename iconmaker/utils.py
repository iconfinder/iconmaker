# -*- coding: utf-8 -*-

from PIL import Image


def get_image_sizes(image_list):
    image_dict = {}
    for image in image_list:
        image_dict[image] = get_image_size(image)

    return image_dict


def get_image_size(path):
    """Return the size of the image

    :param path: path of the image 
    :returns `tuple` containing `int` width and size 
    """

    im = Image.open(path)
    return im.size[0]


def which(program):
    """Determine if a specific executable exists

    :param program: name of the executable to check for
    :returns full path to the executable or None if not found
    """

    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None