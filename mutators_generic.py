
class PassConstant:
    def __init__(self, f, constant):
        self.__filter = f
        self.__constant = constant
    def filter(self, node):
        return self.__filter(node)
    def mutations(self, node):
        return [self.__constant]
    def __str__(self):
        return 'substitute by constant \"{}\"'.format(self.__constant)
