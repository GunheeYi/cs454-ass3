from math import sqrt
from random import randrange, sample
import argparse
import json

class XY:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return "X: {}, Y: {}".format(self.x, self.y)
    def __repr__(self) -> str:
        return self.__str__()

def dist(xy1, xy2):
    return sqrt((xy1.x-xy2.x)**2+(xy1.y-xy2.y)**2)

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-p', required=False, default='10', help='population')
parser.add_argument('-f', required=False, default='100000', help='limit on number of fitness evaluations')
parser.add_argument('-c', required=False, default='', help='previous checkpoints')
args = parser.parse_args()

pts = [XY(0,0)]

with open(args.filename, 'r') as file:
    while True:
        line = file.readline()
        if line in ['NODE_COORD_SECTION\n', 'DISPLAY_DATA_SECTION\n']: break
        # print(line, end="")
    while True:
        line = file.readline()
        if line=='EOF\n': break
        words = line[:-1].split()
        pts += [XY(float(words[1]), float(words[2]))]

N = len(pts)-1
if N < 2: raise ValueError("Less than 2 points provided. Solver needs at least 2 points to solve the problem.")
POP = int(args.p)
EPOCHS = 10000
EVAL_LIMIT = int(args.f)
EVAL_COUNT = 0
RATE_CROSSOVER = 1
RATE_MUTATION = 1
CHECKPOINT = args.c

root = list(range(1, N+1)) # ordered list of points, later to be used to generate random permutations

def cost(l):
    global EVAL_COUNT
    EVAL_COUNT += 1
    totalDist = 0
    for i in range(len(l)-1):
        totalDist += dist(pts[l[i]], pts[l[i+1]])
    totalDist += dist(pts[l[-1]], pts[l[0]])
    return totalDist

def crossoverPMX(l1, l2):
    n = len(l1)
    l3 = [0 for _ in range(n)]
    cut1, cut2 = sorted(sample(range(n+1), 2))
    for i in range(cut1, cut2): l3[i] = l1[i]

    for i in range(cut1, cut2):
        if l2[i] not in l3[cut1:cut2]:
            j = l2.index(l1[i])
            if l3[j]==0:
                l3[j] = l2[i]
            else:
                while True:
                    k = l2.index(l1[j])
                    if l3[k]==0:
                        l3[k] = l2[i]
                        break
                    j = k
    
    for i in range(n):
        if l3[i]==0: l3[i] = l2[i]

    return l3

def swap(l, i, j):
    ll = l.copy()
    temp = ll[i]
    ll[i] = ll[j]
    ll[j] = temp
    return ll

def mutateRandom(l):
    i, j = sample(range(len(l)), 2)
    return swap(l, i, j)

def mutateAdjacent(l):
    n = len(l)
    i = randrange(n)
    return swap(l, i, 0 if i==n-1 else i+1)

def save(sol, pool):
    solStr = ""
    for i in sol: solStr += str(i)+"\n"
    with open('sol_{}.csv'.format(cost(sol)), 'w') as solution: solution.write(solStr[:-1])
    with open('ckpt_{}.json'.format(cost(sol)), 'w') as poolF: json.dump(pool, poolF, indent=2)

def optimize(pool, pop=POP, epochs=EPOCHS, rate_crossover=1, rate_mutation=1, printt=False, savee=False):
    global EVAL_LIMIT, EVAL_COUNT
    
    for epoch in range(epochs):
        crossovers = []
        while len(crossovers) < pop*rate_crossover:
            p1, p2 = sample(pool, 2)
            crossovers += [crossoverPMX(p1, p2)]
        
        mutantsAdjacent = []
        while len(mutantsAdjacent) < pop*rate_mutation:
            p = sample(pool, 1)[0]
            mutantsAdjacent += [mutateAdjacent(p)]
        mutantsRandom = []
        while len(mutantsRandom) < pop*rate_mutation:
            p = sample(pool, 1)[0]
            mutantsRandom += [mutateRandom(p)]
        
        poolTemp = pool + crossovers + mutantsAdjacent + mutantsRandom # merge all path pools
        poolTemp.sort(key=lambda _: cost(_)) # select only the first POP paths fittest

        if EVAL_COUNT > EVAL_LIMIT: # save and return immediately if evaluation limit exceeded
            print("Evaluation limit exceeded. The fittest current cycle costs {}".format(cost(pool[0])))
            save(pool[0], pool)
            return pool[0]
        pool = poolTemp[0:pop]

        
        if savee: save(pool[0], pool) # save the best solution in current generation
        if printt: # print the best solution in current generation
            print("The fittest cycle in epoch {} costs {}".format(epoch+1, cost(pool[0])))

    save(pool[0], pool)
    return 

xs = list(map(lambda _: _.x, pts))
ys = list(map(lambda _: _.y, pts))
xMin, xMax, yMin, yMax = min(xs), max(xs)+1, min(ys), max(ys)+1
# (0 19153.0 0 13146.0)

def init_grid(xDiv, yDiv, xDir):
    xSpan, ySpan = (xMax-xMin)/xDiv, (yMax-yMin)/yDiv
    ptsGrid = [[[] for _ in range(yDiv)] for _ in range(xDiv)]

    for idx, pt in enumerate(pts[1:]):
        i, j = int((pt.x-xMin)/xSpan), int((pt.y-yMin)/ySpan)
        ptsGrid[i][j] += [idx+1]

    sol = []
    if xDir:
        for i in range(xDiv):
            for j in (range(yDiv) if i%2==0 else reversed(range(yDiv))):
                if ptsGrid[i][j]: sol += ptsGrid[i][j]
    else:
        for i in range(yDiv):
            for j in (range(xDiv) if i%2==0 else reversed(range(xDiv))):
                if ptsGrid[j][i]: sol += ptsGrid[j][i]
    
    return sol

if CHECKPOINT:
    with open(CHECKPOINT, 'r') as f: pool = json.load(f)
else:
    pool = []

    if N <= 50:
        for _ in range(POP): pool.append(sample(root, N))
    else:
        estSide = sqrt(N)
        divMin, divMax = max(int(estSide*0.5), 1), max(int(estSide*1.5), 2)+1
        divStep = max(int(estSide*0.05), 1)
        for xDiv in range(divMin, divMax, divStep):
            for yDiv in range(divMin, divMax, divStep):
                pool.append(init_grid(xDiv, yDiv, True))
                pool.append(init_grid(xDiv, yDiv, False))
    
    # pool.append(init_grid(87, 309, True))
    # pool.append(init_grid(960, 61, False))

pool.sort(key=cost)
pool = pool[0:POP]

print("Initial pool------------------")
for sol in pool:
    print("cost {}".format(cost(sol)))
print("-------------------------------")

optimize(pool, printt=True, savee=True)