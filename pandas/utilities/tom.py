import os

TEMPDIR="example_data"

from generators import generators

class TomTom(object):
    """
    This is an utility class that provides objects capable of telling where to save temporary files.
    It implements Borg design pattern.
    """
    __shared__state = {}
    def __init__(self):
        self.__dict__ = self.__shared__state
        self.cwd = os.getcwd()
        self.sep = os.path.sep

    def get_tmp_name(self, name):
        """
        Return an absolute path for a file named name.
        """
        return self.cwd + self.sep + TEMPDIR + self.sep + name

    def get_tmp_dir(self):
        return self.cwd + self.sep + TEMPDIR


class FileGenerator(object):
    __shared__state = {}
    def __init__(self):
        self.__dict__ = self.__shared__state
        self._tom = TomTom()

    def get_example(self, file):
        path = self._tom.get_tmp_name(file)
        if not os.path.exists(path):
            generators[file](self._tom)

        return path
