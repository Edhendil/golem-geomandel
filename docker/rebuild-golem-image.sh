#!/bin/bash
./build-image.sh
rm *.gvmi
gvmkit-build yagna-geomandel:0.1
gvmkit-build yagna-geomandel:0.1 --push