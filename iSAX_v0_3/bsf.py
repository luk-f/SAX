from numpy import argmax as np_argmax
from numpy import amax as np_amax

class BestSoFarElement:

    def __init__(self, dist, indexFile, st):

        self.dist = dist
        self.indexFile = indexFile
        self.st = st

    def __lt__(self, other):
        if other is None:
            return False
        return self.dist < other.dist

    def __le__(self, other):
        if other is None:
            return False
        return self.dist <= other.dist

    def __eq__(self, other):
        if other is None:
            return False
        return self.dist == other.dist

    def __ge__(self, other):
        if other is None:
            return True
        return self.dist >= other.dist

    def __gt__(self, other):
        if other is None:
            return True
        return self.dist > other.dist

    def __ne__(self, other):
        if other is None:
            return True
        return self.dist != other.dist

    def __str__(self):
        return str(self.indexFile)


class BestSoFarList(object):

    def __init__(self, size):
        self.__list = []
        self.size_max = size
        self.size = 0

    def addElement(self, dist, indexFile, st):
        bsf_temp = BestSoFarElement(dist, indexFile, st)
        if self.size < self.size_max and not self.alreadyPresent(st):
            self.__list.append(bsf_temp)
            self.size += 1
        elif dist < self.worstedDistElement() and not self.alreadyPresent(st):
            self.deleteWorstElement()
            self.__list.append(bsf_temp)
            self.size += 1
        elif not self.alreadyPresent(st):
            print("Attention BestSoFarList plein ! ", self.size)

    def alreadyPresent(self, st):
        for ts_list in self.__list:
            if st is ts_list.st:
                return True
        return False

    def worstedDistElement(self):
        worstedElt = self.worstedElement()
        return worstedElt.dist

    def worstedElement(self):
        return np_amax(self.__list)

    def _get_list(self):
        return self.__list

    def deleteWorstElement(self):
        del self.__list[np_argmax(self.__list)]
        self.size -= 1

    def isFull(self):
        if self.size == self.size_max:
            return True
        else:
            return False

    list = property(_get_list)
    dist = property(worstedDistElement)

