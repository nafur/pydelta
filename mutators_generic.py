
class PassConstant:
    """Replaces any node by a single constant."""
    def __init__(self, filter, constant):
        self.__filter = filter
        self.__constant = constant
    def filter(self, node):
        """Use :code:`filter(node)`."""
        return self.__filter(node)
    def mutations(self, node):
        """Return :code:`[constant]`."""
        return [self.__constant]
    def __str__(self):
        return 'substitute by constant \"{}\"'.format(self.__constant)
