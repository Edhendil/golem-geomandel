from yapapi.runner import Engine, Task, vm
from yapapi.runner.ctx import WorkContext
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from datetime import timedelta

from core import GeomandelData, GeomandelTask, MandelbrotGenerationParameters, GolemParameters
import utils

# image hash of the geomandel docker image uploaded to golem
_IMAGE_LINK = "47cd0f045333d837304d61f74266a1bcd49ad3cb0690a10f08d37bf4"

class ImageRepository:
    async def get_geomandel_image(self, minimal_memory: float, minimal_storage: float):
        """Retrieve a link to the geomandel image together with constraints"""
        return await vm.repo(
            image_hash = _IMAGE_LINK,
            min_mem_gib = minimal_memory,
            min_storage_gib = minimal_storage,
        )

class YagnaContext:
    """Holds information about the docker image and constraints for all the tasks to be executed in this context."""
    def __init__(self, package, max_workers: int, budget: float, subnet_tag: str):
        self.package = package
        self.max_workers = max_workers
        self.budget = budget
        self.subnet_tag = subnet_tag

    def __create_engine(self):
        """Creates yagna engine"""
        return Engine(
            package=self.package,
            max_workers=self.max_workers,
            budget=self.budget,
            timeout=timedelta(minutes=25),
            subnet_tag=self.subnet_tag,
            # By passing `event_emitter=log_summary()` we enable summary logging.
            # See the documentation of the `yapapi.log` module on how to set
            # the level of detail and format of the logged information.
            event_emitter=log_summary(log_event_repr),
        )   

    async def execute(self, tasks: [Task], worker_function, on_task_complete):
        """Executes a set of tasks on a preconfigured docker image.
        
        Parameters
        ----------
        tasks : [Task]
            Yagna tasks
        worker_function : (ctx: WorkContext, tasks) -> [Work]
            Function returning a sequence of instructions for each of the provided tasks.
        on_task_complete : (task: Task) -> None
            Callback executed when a task has been processed.
        """
        async with self.__create_engine() as engine:
            async for task in engine.map(worker_function, tasks):
                on_task_complete(task)

# docker image path to JSON file with task parameters
_TASK_INPUT_PATH = "/golem/work/task.json"
# docker image path to generated image
_TASK_OUTPUT_PATH = "/golem/work/output.png"
# docker command generating the image
# /bin/sh -c part is there for a reason
# either use this pattern or an absolute path to python
_GEOMANDEL_COMMAND = ["/bin/sh", "-c", "python /golem/scripts/golem-mandel.py"]

# minimal provider node memory constraint, not configurable
_MINIMAL_MEMORY = 0.5
# minimal provider node storage constraint, not configurable
_MINIMAL_STORAGE = 2.0

class GeomandelEngine:
    """Converts geomandel subtasks to yagna subtasks and sends them to Yagna Engine"""
    def __init__(self, yagna):
        self.yagna = yagna

    @staticmethod
    async def instance(golem_parameters: GolemParameters):
        """Creates an instance of GeomandelEngine. Static factory."""
        repository = ImageRepository()
        # retrieve the image link to geomandel docker image together with constraints
        package = await repository.get_geomandel_image(_MINIMAL_MEMORY, _MINIMAL_STORAGE)
        # prepares the yagna engine
        yagna = YagnaContext(package, golem_parameters.max_workers, golem_parameters.budget, golem_parameters.subnet_tag)
        # wraps it in geomandel layer
        return GeomandelEngine(yagna)

    async def execute(self, tasks: [GeomandelData]):
        """Translates geomandel subtasks into Yagna format and executes them."""
        wrappedTasks = self.__wrap_in_yagna_task(tasks)
        await self.yagna.execute(wrappedTasks, self.__worker_render_frame, self.__log_completion)

    async def __worker_render_frame(self, ctx: WorkContext, tasks: [GeomandelTask]):
        """Creates a set of instructions for each subtask"""
        async for task in tasks: 
            # Send subtask data as JSON to the remote execution environment.
            ctx.send_json(_TASK_INPUT_PATH, task.data.__dict__)
            # Run python script loading the data from JSON and executing the geomandel binary to generate the image.
            ctx.run(*_GEOMANDEL_COMMAND)
            # Download the output file.
            ctx.download_file(_TASK_OUTPUT_PATH, task.data.output_path)
            # Return a sequence of commands to be executed when remote node agrees to process a task.
            yield ctx.commit()
            # TODO: actual verification
            task.accept_task(result=task.data.output_path)

    def __log_completion(self, task: GeomandelTask):
        """Logs the completion of a task"""
        print(
            f"{utils.TEXT_COLOR_CYAN}"
            f"Task computed: {task}"
            f"{utils.TEXT_COLOR_DEFAULT}"
        )

    def __wrap_in_yagna_task(self, data: []):
        """Converts any task data sequence to Yagna wrapper"""
        for item in data:
            yield Task(data=item)
