#!/usr/bin/env python3
from datetime import timedelta
import pathlib
import sys
import getopt
import os

import json

def main(argv):
    x: float
    y: float
    zoom: float
    try:
        opts, args = getopt.getopt(argv,"hx:y:z:")
    except getopt.GetoptError:
        print('mandel.py -x <real axis center coordinate> -y <imaginary axis center coordinate> -z <zoom level>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('mandel.py -x <real axis center coordinate> -y <imaginary axis center coordinate> -z <zoom level>')
            sys.exit()
        elif opt in ("-x"):
            x = float(arg)
        elif opt in ("-y"):
            y = float(arg)
        elif opt in ("-z"):
            zoom = float(arg)

    # how much in x/y direction from the center will be rendered at default zoom(=1)
    original_half_size: float = 1.5
    # how much in x/y direction from the center will be rendered at requested zoom
    size_half: float = original_half_size/zoom
    # coordinates of the rectangle to render
    real_start: float = x - size_half
    real_end: float = x + size_half
    # I had to negate the value for the geomandel to work in an expected way
    imaginary_start: float = -y - size_half
    # I had to negate the value for the geomandel to work in an expected way
    imaginary_end: float = -y + size_half
    thread_number: int = 8
    width: int = 2000
    height: int = 2000

    geomandel_command: str = f"geomandel --quiet --image-png --multi {thread_number} --width {width} --height {height} --creal-min {real_start} --creal-max {real_end} --cima-min {imaginary_start} --cima-max {imaginary_end} --image-file /golem/work/output --rgb-freq=0,0.01,0 --rgb-base=255,0,0"

    os.system(geomandel_command)

if __name__ == "__main__":
   main(sys.argv[1:])
