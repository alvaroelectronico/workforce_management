from itertools import cycle

def fCyclicElement(list, currentPosition, distance):
    if currentPosition+distance<len(list):
        return list[currentPosition+distance]
    elif currentPosition+distance<0:
        return list[currentPosition+distance+len(list)]
    else:
        return list[currentPosition+distance-len(list)]



li = [0, 1, 2, 3]




for i in li:
    for j in range(-len(li)+1, len(li)-1):
        print("CurrentPosition: ",li.index(i))
        print("El elemento que está a distancia ", j, " de ", i, "es", fCyclicElement(li, li.index(i),j))
