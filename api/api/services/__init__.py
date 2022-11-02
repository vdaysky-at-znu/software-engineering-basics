from os.path import dirname, basename, isfile, join
import glob

from api.events.manager import EventManager

internalHandler = EventManager()


modules = glob.glob(join(dirname(__file__), "*.py"))

__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')
]

# import all services here to register event handlers defined within
for m in __all__:
    __import__(f"api.services.{m}", fromlist="dummy")
