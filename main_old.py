import random

class Line:
    def __init__(self, stops, time):
        self.stops = stops
        self.n = len(self.stops)
        self.time = time

POP = 10
EPOCHS = 20
RATE_CROSSOVER = 1
RATE_MUTATION = 1
N = 21
DEPARTURE = 2
ARRIVAL = 19
lines = [
    Line([_ for _ in range(N)], 2),
    Line([1, 6, 11, 16], 5),
    Line([0, 10, 20], 8)
]

TIMETABLE = [[0 for _ in range(N)] for _ in range(N)]
    
def hasDuplicates(l):
    return not len(l)==len(set(l))

def setTime(start, end, time):
    TIMETABLE[start][end] = time
    TIMETABLE[end][start] = time

def getTime(start, end):
    return TIMETABLE[start][end]

def addLine(line):
    n = len(line.stops)
    for i in range(n-1):
        for j in range(i+1, n):
            a = line.stops[i]
            b = line.stops[j]
            newTime = line.time * (j-i)
            curTime = getTime(a, b)
            if curTime==0 or newTime < getTime(a, b):
                setTime(a, b, newTime)

def printTimeTable():
    for i in range(N):
        for j in range(N):
            print(TIMETABLE[i][j], end="\t")
        print()

stops = list(map(lambda l: l.stops, lines))
hubs = list(set(sum(stops[1:], [])))

for line in lines:
    addLine(line)

class Path:
    def __init__(self, stops: list):
        self.stops = stops.copy()
        
        self.fullStops = [DEPARTURE] + self.stops + [ARRIVAL]
        self.n = len(self.stops)
        self.time = 0
        for i in range(self.n+1):
            timePortion = getTime(self.fullStops[i], self.fullStops[i+1])
            if timePortion > 0:
                self.time += timePortion
                # print("Stop {} to stop {} takes {} minutes".format(fullStops[i], fullStops[i+1], time))
            else:
                # self.time += abs(fullStops[i+1]-fullStops[i])*2
                raise RuntimeError
    def __str__(self):
        pathStr = '-'.join(list(map(str, self.fullStops)))
        return "{} ({}min)".format(pathStr, self.time)
    def __eq__(self, other):
        return self.stops == other.stops
    def __hash__(self):
        return sum(self.stops)

def crossover(p1: Path, p2: Path):
    if len(p1.stops) < 2 or len(p2.stops) < 2: return []

    i1, j1 = random.sample(range(len(p1.stops)), 2)

    a = p1.stops[i1]
    b = p1.stops[j1]

    if not (a in p2.stops and b in p2.stops): return []

    i2 = p2.stops.index(a)
    j2 = p2.stops.index(b)

    sub1 = p1.stops[i1+1:j1]
    sub2 = p2.stops[i2+1:j2]

    newStops1 = p1.stops.copy()
    newStops2 = p2.stops.copy()

    newStops1[i1+1:j1] = sub2 if i2 < j2 else list(reversed(sub2))
    newStops2[i2+1:j2] = sub1 if i2 < j2 else list(reversed(sub1))
    
    children = []
    if not hasDuplicates(newStops1):
        # print(newStops1)
        children += [Path(newStops1)]
    if not hasDuplicates(newStops2):
        # print(newStops2)
        children += [Path(newStops2)]

    return children
    
def mutation(p: Path):
    if not p.stops: return None
    newStops = p.stops.copy()
    newStop = random.choice(hubs)
    i = random.randrange(0, p.n)
    # print(p)
    # print(p.stops)
    # print(p.n, len(newStops), i)
    newStops[i] = newStop

    if hasDuplicates(newStops): return None
    else: return Path(newStops)

pool = set()

for _ in range(POP*2):
    pool.add(Path(random.sample(hubs, random.randrange(0, len(hubs)+1))))

pooll = list(pool)
pooll.sort(key=lambda x: x.time)
pooll = pooll[0:POP]
pool = set(pooll)

print("Initial pool------------------")
for path in pooll:
    print(path)
print("-------------------------------")

for epoch in range(EPOCHS):
    # reproduce next generation
    nextGen = []
    timer = 0
    while timer < 1000 and len(nextGen) < POP*RATE_CROSSOVER:
        timer += 1
        p1, p2 = random.sample(pool, 2)
        nextGen += crossover(p1, p2)
    # mutate
    mutants = []
    timer = 0
    while timer < 1000 and len(mutants) < POP*RATE_MUTATION:
        timer += 1
        p = random.sample(pool, 1)[0]
        if mutant:=mutation(p): mutants += [mutant]
    # merge all path pools
    pool = {*pool, *nextGen, *mutants}
    # select only the first POP paths fittest
    pooll = list(pool)
    pooll.sort(key=lambda x: x.time)
    pooll = pooll[0:POP]
    pool = set(pooll)
    # print the best path in current generation
    print("The fittest path in epoch {} is {}".format(epoch+1, pooll[0]))

