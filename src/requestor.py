#!/usr/bin/env python3
import asyncio
import sys
import getopt

from yapapi.log import enable_default_logger

import utils
from core import MandelbrotGenerationParameters, GolemParameters, RequestorParameters
from task import SubtaskGenerator, GeomandelData
from engine import GeomandelEngine

class MandelbrotProcessor:
    """Based on parameters creates subtasks and passes them to engine for execution
    
    ...

    Attributes
    ----------
    subtask_generator : SubtaskGenerator
        creates geomandel subtasks
    engine : GeomandelEngine
        link to the Golem platform
    """

    def __init__(self, subtask_generator: SubtaskGenerator, engine: GeomandelEngine):
        self.subtask_generator = subtask_generator
        self.engine = engine

    @staticmethod
    async def instance(golemParameters: GolemParameters):
        """Creates processor with default settings"""
        return MandelbrotProcessor(SubtaskGenerator(), await GeomandelEngine.instance(golemParameters))

    async def generate_frames(self, parameters: RequestorParameters):
        """Generates mandelbrot images using Golem for the provided coordinates
        
        Parameters
        ----------
        parameters : RequestorParameters
            Central point coordinates and frame details
        """
        geomandel_tasks: [GeomandelData] = self.subtask_generator.create_geomandel_tasks(parameters.mandelbrot)
        await self.engine.execute(geomandel_tasks)

def print_help():
    print('requestor.py -x <real axis center coordinate> -y <imaginary axis center coordinate> -m <zoom multiplier> -o <starting frame index> -c <number of frames to render> -w <max golem providers> -b <budget> -s <subnet tag>')

def parse_params(argv) -> RequestorParameters:
    # prepare default values for subtask generation
    x: float = -0.235124965
    y: float = 0.827215300
    multiplier: float = 2.0
    offset: int = 0
    count: int = 1
    
    # prepare default values for golem parameters
    subnet_tag = 'devnet-alpha.2'
    max_workers = 10
    budget = 10.0

    try:
        opts, args = getopt.getopt(argv,"hx:y:m:o:c:w:b:s:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-x"):
            x = float(arg)
        elif opt in ("-y"):
            y = float(arg)
        elif opt in ("-m"):
            multiplier = float(arg)
        elif opt in ("-o"):
            offset = int(arg)
        elif opt in ("-c"):
            count = int(arg)
        elif opt in ("-w"):
            max_workers = int(arg)
        elif opt in ("-b"):
            budget = float(arg)
        elif opt in ("-s"):
            subnet_tag = arg

    mandelbrotParams = MandelbrotGenerationParameters(x, y, multiplier, offset, count)
    golemParams = GolemParameters(subnet_tag, max_workers, budget)
    return RequestorParameters(golemParams, mandelbrotParams)

async def main(argv):
    """Parsing arguments and executing the logic"""
    enable_default_logger()
    params: RequestorParameters = parse_params(argv)
    processor: MandelbrotProcessor = await MandelbrotProcessor.instance(params)
    await processor.generate_frames(params)

def asyncio_loop_setup(coroutine):
    """Setting up the event loop for any coroutine"""
    # This is only required when running on Windows with Python prior to 3.8:
    utils.windows_event_loop_fix()

    loop = asyncio.get_event_loop()
    task = loop.create_task(coroutine)

    try:
        loop.run_until_complete(task)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        task.cancel()
        loop.run_until_complete(task)

# script entrypoint
if __name__ == "__main__":
    coroutine = main(sys.argv[1:])
    asyncio_loop_setup(coroutine)

