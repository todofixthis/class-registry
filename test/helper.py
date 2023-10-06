import sys
from importlib.metadata import DistributionFinder, PathDistribution
from os import path
from pathlib import Path


class DummyDistributionFinder(DistributionFinder):
    """
    Injects a dummy distribution into the meta path finder, so that we can
    pretend like it's been pip installed during unit tests (i.e., so that we
    can test ``EntryPointsClassRegistry``), without polluting the persistent
    virtualenv.
    """

    DUMMY_PACKAGE_DIR = 'dummy_package.egg-info'

    @classmethod
    def install(cls):
        for finder in sys.meta_path:
            if isinstance(finder, cls):
                # If we've already installed an instance of the class, then
                # something is probably wrong with our tests.
                raise ValueError(f'{cls.__name__} is already installed')

        sys.meta_path.append(cls())

    @classmethod
    def uninstall(cls):
        for i, finder in enumerate(sys.meta_path):
            if isinstance(finder, cls):
                sys.meta_path.pop(i)
                return
        else:
            # If we didn't find an installed instance of the class, then
            # something is probably wrong with our tests.
            raise ValueError(f'{cls.__name__} was not installed')

    def find_distributions(self, context=...) -> list[PathDistribution]:
        return [PathDistribution(
            Path(path.join(path.dirname(__file__), self.DUMMY_PACKAGE_DIR))
        )]
