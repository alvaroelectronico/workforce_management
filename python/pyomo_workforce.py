from pyomo.environ import *
from itertools import cycle


# Definición del modelo

# Crear modelo vacio
m = AbstractModel()

# Sets
m.sPeriods = Set()

# Parametros
m.pNoRequired = Param(m.sPeriods, mutable=True)
m.pNumWorkers = Param(mutable=True)

# Variables
m.vNoStartWorking = Var(m.sPeriods, within=NonNegativeIntegers)
m.vNoExtraHours = Var(m.sPeriods, within=NonNegativeIntegers)

# Definicion de restricciones
"""
Restriccion cambiada por una mas flexible

def fcNoRequired(model, p):
    currentIndex = Periods.index(p)
    lenPeriods = len(Periods)
    return model.vNoStartWorking[p] \
           + model.vNoStartWorking[Periods[(currentIndex - 1) % lenPeriods]] \
           + model.vNoStartWorking[Periods[(currentIndex - 3) % lenPeriods]] \
           + model.vNoStartWorking[Periods[(currentIndex - 4) % lenPeriods]] \
           >= model.pNoRequired[p]
"""

def fcNoRequired(model, p):
    return sum(model.vNoStartWorking[p] for p in p) >= model.pNoRequired[p[0]]

def fcExtraHoursBound(model, p):
    return model.vNoExtraHours[p] <= model.vNoStartWorking[p]

def fcMaxTotalWorkers(model):
    return sum(model.vNoStartWorking[p] for p in model.sPeriods) <= model.pNumWorkers

def fcNoRequiredWithExtra(model, p):
    currentIndex = Periods.index(p)
    lenPeriods = len(Periods)
    return model.vNoStartWorking[p] \
           + model.vNoStartWorking[Periods[(currentIndex - 1) % lenPeriods]] \
           + model.vNoStartWorking[Periods[(currentIndex - 3) % lenPeriods]] \
           + model.vNoStartWorking[Periods[(currentIndex - 4) % lenPeriods]] \
           + model.vNoExtraHours[Periods[(currentIndex - 5) % lenPeriods]] \
           >= model.pNoRequired[p]

def fcNoTotalWorkers(model):
    return sum(model.vNoStartWorking[p] for p in model.sPeriods)

def fcTotalExtraHours(model):
    return sum(model.vNoExtraHours[p] for p in model.sPeriods)

# Activar restricciones
m.cNoRequired = Constraint(m.sListWorkerPeriods, rule=fcNoRequiredWithExtra)
m.cExtraHoursBound = Constraint(m.sPeriods, rule=fcExtraHoursBound)
m.cMaxNumWorkers = Constraint(rule=fcMaxTotalWorkers)

# Funcion objetivo
m.vTotalExtraHours = Objective(rule=fcTotalExtraHours, sense=minimize)

"""
Datos de entrada
"""
Periods = ["00-02", "02-04", "04-06", "06-08", "08-10", "10-12", "12-14", "14-16", "16-18", "18-20", "20-22", "22-00"]
NoRequired = {'00-02': 15, '02-04': 15, '04-06': 15, '06-08': 35, '08-10': 40, '10-12': 40, '12-14': 40, '14-16': 30,
               '16-18': 31, '18-20': 35, '20-22': 30, '22-00': 20}
#PeriodsCyc = cycle(Periods)
NumWorkers = 80

lenPeriods = len(Periods)
sListWorkerPeriods = [(Periods[i], Periods[(i - 1) % lenPeriods],
                         Periods[(i - 3) % lenPeriods],
                         Periods[(i - 4) % lenPeriods])
                        for i in range(lenPeriods)]

# Pasar los datos de entrada en un diccionario con formato {None:{nombre_set_o_parametro:{indice:valor}}
# Si un parametro o un set no tiene indice, su indice es None
data1 = {None: {
    'sPeriods': {None: Periods},
    'sListWorkerPeriods': {None:sListWorkerPeriods},
    'pNoRequired': NoRequired,
    'pNumWorkers': {None:NumWorkers}
}}


# Generar instancias y resolver

"""
Este modelo reducido se pude generar a partir del modelo completo

model_no_min = AbstractModel()
model_no_min.sPeriods = Set()
model_no_min.pNoRequired = Param(model_no_min.sPeriods)
model_no_min.vNoStartWorking = Var(model_no_min.sPeriods, within=NonNegativeIntegers)
model_no_min.cNoRequired = Constraint(model_no_min.sPeriods, rule=fcNoRequired)
model_no_min.vTotalWorkers = Objective(rule=fcTotalWorkers, sense=minimize)


# Min. no. nurses. Creating the instance0
instance = model_no_min.create_instance(data1)
# Solving the instance
opt = SolverFactory("gurobi")
results = opt.solve(instance)
# Displyaing results
results.write()
print("Total workers %s" % value(instance.vTotalWorkers.expr()))
for p in instance.sPeriods:
    print("%i workers start at  %s" % (instance.vNoStartWorking[p].value, p))
"""

# Generar modelo reducido: generar el modelo completo y desactivar restricciones innecesarias.
instance1 = m.create_instance()
instance1.vNoExtraHours.fix(0)
instance1.cExtraHoursBound.deactivate()
instance1.cMaxNumWorkers.deactivate()
# Solving the instance
opt = SolverFactory("gurobi")
results = opt.solve(instance1)
# Displyaing results
results.write()
print("Total workers %s" % value(instance1.vTotalWorkers.expr()))
for p in instance1.sPeriods:
    print("%i workers start at  %s" % (instance1.vNoStartWorking[p].value, p))


# Min. no. extra hours. Creating the instance0
instance2 = m.create_instance()
# Solving the instance
opt = SolverFactory("gurobi")
results = opt.solve(instance2)
# Displying results
results.write()
print("Total extra hour workers %s" % value(instance2.vTotalExtraHours.expr()))
for p in instance.sPeriods:
    print("%i workers start at  %s (%i do Hours)" % (
    instance2.vNoStartWorking[p].value, p, instance2.vNoExtraHours[p].value))
