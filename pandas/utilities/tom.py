import os

TEMP_DIR="temp"
EXAMPLE_DIR="example_data"

#from generators import generators

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
        Return an absolute path for a temporary (output) file named name.
        """
        return self.cwd + self.sep + TEMP_DIR + self.sep + name

    def get_tmp_dir(self):
        return self.cwd + self.sep + TEMP_DIR

    def get_example_name(self, name):
        """
        Return an absolute path for an example (input) file named name.
        """
        return self.cwd + self.sep + EXAMPLE_DIR + self.sep + name
    


# class FileGenerator(object):
#     __shared__state = {}
#     def __init__(self):
#         self.__dict__ = self.__shared__state
#         self._tom = TomTom()

#     def get_example(self, file):
#         path = self._tom.get_tmp_name(file)
#         if not os.path.exists(path):
#             generators[file](self._tom)

#         return path
