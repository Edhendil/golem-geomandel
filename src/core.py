from dataclasses import dataclass
from yapapi.runner import Task

@dataclass
class GeomandelData:
    """Data structure for geomandel subtasks"""
    x: float
    y: float
    zoom: float
    output_path: str

@dataclass 
class GolemParameters:
    """Parameters for golem internals"""
    subnet_tag: str
    max_workers: int
    budget: float


@dataclass
class MandelbrotGenerationParameters:
    """Input parameters for the requestor script"""
    x: float
    y: float
    multiplier: float
    offset: int
    count: int

@dataclass
class RequestorParameters:
    """Container for all requestor script parameters"""
    golem: GolemParameters
    geomandel: MandelbrotGenerationParameters

# Alias for Yagna tasks with GeomandelData input and file path result
GeomandelTask = Task[GeomandelData, str]
