from gurobipy import *

def fCyclicElement(list, currentPosition, distance):
    if currentPosition+distance<len(list):
        return list[currentPosition+distance]
    elif currentPosition+distance<0:
        return list[currentPosition+distance+len(list)]
    else:
        return list[currentPosition+distance-len(list)]

sPeriods = ["00-02", "02-04","04-06","06-08","08-10","10-12","12-14","14-16","16-18","18-20","20-22","22-00"]
pNumRequired = {"00-02":15, "02-04":15,"04-06":15,"06-08":35,"08-10":40,"10-12":40,"12-14":40,"14-16":30,"16-18":31,"18-20":35,"20-22":30,"22-00":20}
model = Model('Nurse Rostering')

viNumStarting={}
for iPeriod in sPeriods:
        viNumStarting[iPeriod] = model.addVar(vtype=GRB.INTEGER,
                                            name="NumStarting_{}".format(iPeriod))

model.update()

for iPeriod in sPeriods:
    consExpr=LinExpr()
    consExpr=viNumStarting[iPeriod]
    for pos in [-1,-3,-4]:
        consExpr+= viNumStarting[fCyclicElement(sPeriods,sPeriods.index(iPeriod),pos)]
    model.addConstr(consExpr,">=",pNumRequired[iPeriod])

obj = quicksum(viNumStarting[iPeriod] for iPeriod in sPeriods)
model.setObjective(obj, GRB.MINIMIZE)
model.optimize()
model.printAttr('X')
