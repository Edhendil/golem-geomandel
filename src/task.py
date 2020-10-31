
from typing import Generator
from itertools import islice

import utils
from core import GeomandelData, MandelbrotGenerationParameters

# local generator alias
ZoomGenerator = Generator[float, None, None]

def _local_output_path(index: int):
    """Calculates absolute path to output file for a particular frame"""
    return f'{utils.PROJECT_ROOT}/output/output-{index}.png'

def _zoom_sequence(multiplier: float) -> ZoomGenerator:
    """Generates an infinite sequence of numbers representing zoom factor for frames"""
    current_zoom: float = 1.0
    while True:
        yield current_zoom
        current_zoom *= multiplier

def _zoom_sequence_limited(offset: int, count: int, multiplier: float) -> ZoomGenerator:
    """Generates a limited sequence of zoom factors"""
    return islice(_zoom_sequence(multiplier), offset, offset + count)

class SubtaskGenerator:
    """Generates subtask data"""
    def create_geomandel_tasks(self, mandelbrotParameters: MandelbrotGenerationParameters) -> [GeomandelData]:
        """Generates subtask data for X/Y coordinates and a limited set of frames.
        
        Parameters
        ----------
        mandelbrotParameters : MandelbrotGenerationParameters
            all params required to generate the sequence of subtasks (x, y, offset, count, zoom_multiplier)
        """
        # 1.02337
        # enumerate used as I need each item index
        for inner_index, zoom in enumerate(_zoom_sequence_limited(mandelbrotParameters.offset, mandelbrotParameters.count, mandelbrotParameters.multiplier)):
            # calculate the global index
            frame_index = mandelbrotParameters.offset + inner_index
            yield GeomandelData(mandelbrotParameters.x, mandelbrotParameters.y, zoom, _local_output_path(frame_index))