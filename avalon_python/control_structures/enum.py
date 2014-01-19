# based on solution from http://stackoverflow.com/a/2182437
class Enum(list):
    'Enumeration type emulation'
    def __init__(self, iterable, sequence=None):
        if sequence:
            if callable(sequence):
                sequence = sequence(len(iterable))
            if len(iterable) > len(sequence):
                raise Exception('Length of iterable less than length of sequence')
            self.sequence = sequence
        super(Enum, self).__init__(iterable)

    def __getattr__(self, name):
        if name in self:
            if self.sequence == None:
                return name
            else:
                return self.sequence[self.index(name)]
        raise AttributeError

    def __contains__(self, key):
        # copy needed to prevent recursion
        if key in self[:] or key in self.sequence:
            return True
        return False
