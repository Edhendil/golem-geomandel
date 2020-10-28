# Geomandel Golem requestor

Geomandel requestor is a python script for generating sequences of Mandelbrot images centered on a single point and with zoom increasing in each image.
Each image is a separate subtask processed on a Golem network provider node. And when all subtasks are completed you can create a video out of generated images.

It also is a full example showing how to build your own Docker image and use it for task execution in Golem network with the new Yagna python API.

Special thanks to the owner of https://github.com/crapp/geomandel github project which I use to generate Mandelbrot images.

## Project structure

* docker/scripts/mandel.py - python script included in the Docker image which wraps the geomandel binary for ease of interaction
* docker/scripts/golem-mandel.py - python script reading Golem subtask details and passing them to mandel.py
* docker/geomandel.Dockerfile - instructions for building the Docker image with geomandel binary and wrapper scripts on board
* docker/rebuild-golem-image.sh - set of instructions for building the Docker image and uploading it to the Golem network repository
* output - all of the generated images end up in here
* src/core.py - basic data types used across the project
* src/engine.py - integration with Yagna API
* src/requestor.py - entry point of the whole program
* src/task.py - generation of subtask details
* src/utils.py - utils copied from yapapi examples

## Setup

Golem setup. If you encounter an issue then refer to https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development for full set of instructions.

1. Install python 3
1. `curl -sSf https://join.golem.network/as-requestor | bash -`
2. `~/.local/bin/yagna service run`
3. `~/.local/bin/yagna payment init -r`
4. `yagna app-key create requestor`
5. Copy the generated key to clipboard
6. `export YAGNA_APPKEY=<requestor app-key>`

Geomandel requestor setup

1. `git clone https://github/`
2. (optional) Create virtual environment and activate it
3. `pip install -r requirements.txt`

You're now ready to generate some Mandelbrot images.

## Requestor script execution

To start the requestor you just need to run `python ./src/requestor.py`. It will generate a single image based on default values. Here's a list of all parameters you might want to set.

All parameters are optional. If not provided then the default values presented below will be used.

* X: `-x -0.235124965` - real axis coordinate of the image center point
* Y: `-y 0.827215300` - imaginary axis coordinate of the image center point
* Zoom multiplier: `-m 2.0` - zoom multiplier, current frame zoom will be multiplied by that factor to calculate the next frame zoom
* Frame offset: `-o 0` - how many frames should be omitted at the start, with multiplier set to 2.0 and offset to 2 the first frame will be generated with zoom equal to 4.0
* Frame count: `-c 1` - how many frames should be generated in total / how many subtasks should be sent to the golem network

* Budget: `-b 10.0` - budget for executing tasks on golem network
* Max workers: `-w 10` - how many golem providers will execute subtasks
* Subnet tag: `-s devnet-alpha.2` - name of the subnet

## Limitations

Due to how geomandel is implemented the generated images start to lose details at the zoom factor of 3,000,000,000. Generating images with zoom greater than this value will not be fun.

## Zoom multiplier you might want to use

Double the zoom value every:

* 10 frames: 1.0717734625 -> max number of frames: 315
* 15 frames: 1.0472941228 -> max number of frames: 473
* 24 frames: 1.0293022366 -> max number of frames: 756
* 30 frames: 1.0233738920 -> max number of frames: 945
* 60 frames: 1.0116194403 -> max number of frames: 1889

## Interesting coordinates to generate images

X: -0.235124965
Y:  0.827215300

## Turn still images into a video

After successful generation of multiple images with increasing zoom factor you might want to combine all of them into a video using `ffmpeg` command line tool.

1. cd ./output
2. cat \`ls -v | grep '\.png'\` | ffmpeg -f image2pipe -i - -framerate 60 -c:v libx264 -pix_fmt yuv420p mandelbrot_video.mp4

And voila. You can check out your fresh video. Go ahead and upload it to YouTube. I know there's a lot of Mandelbrot videos but there's never enough of them.

Here's some explanation what happens here.

* cd ./output - that one's obvious
* ls -v - list all files in order dictated by the number in the filename
* ls -v | grep '\.png' - restrict the list of files only to .png images
* cat \`ls -v | grep '\.png'\` - retrieve contents of all png files in ascending order
* the whole command - read all png files and pass them to ffmpeg to combine them into a single mp4 file

