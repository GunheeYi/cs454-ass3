from math import sqrt
from random import shuffle, randrange, sample
import argparse

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
parser.add_argument('-p', required=False, default='100', help='population')
parser.add_argument('-f', required=False, default='100000', help='limit on number of fitness evaluations')
args = parser.parse_args()

pts = [XY(0,0)]

with open(args.filename, 'r') as file:
    while True:
        line = file.readline()
        if line=='NODE_COORD_SECTION\n': break
        # print(line, end="")
    while True:
        line = file.readline()
        if line=='EOF\n': break
        words = line[:-1].split()
        pts += [XY(float(words[1]), float(words[2]))]

N = len(pts)-1
POP = int(args.p)
EPOCHS = 3000
EVAL_LIMIT = int(args.f)
EVAL_COUNT = 0
RATE_CROSSOVER = 1
RATE_MUTATION = 1

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

def optimize(l=[], pool=[], pop=20, epochs=20, rate_crossover=1, rate_mutation=1, printt=False, savee=False):
    if not (l or pool) or (l and pool): raise ValueError # at least one of sol or pool of sol must be provided
    if l: # if sol is given, initialize pool by random permutating
        pool = []
        for _ in range(pop*2): pool.append(sample(l, len(l)))
    
    for epoch in range(epochs):
        crossovers = []
        while len(crossovers) < pop*rate_crossover:
            p1, p2 = sample(pool, 2)
            crossovers += [crossoverPMX(p1, p2)]
        
        mutants = []
        while len(mutants) < pop*rate_mutation:
            p = sample(pool, 1)[0]
            mutants += [mutateAdjacent(p)]

        # merge all path pools
        pool = pool + crossovers + mutants
        # select only the first POP paths fittest
        pool.sort(key=lambda _: cost(_))
        pool = pool[0:pop]

        if savee:
            solStr = ""
            for i in pool[0]: solStr += str(i)+"\n"
            with open('solution - cost {}.csv'.format(cost(pool[0])), 'w') as solution: solution.write(solStr[:-1])

        # print the best path in current generation
        if printt: print("The fittest cycle in epoch {} costs {}".format(epoch+1, cost(pool[0])))
    return pool[0]

xs = list(map(lambda _: _.x, pts))
ys = list(map(lambda _: _.y, pts))
xMin, xMax, yMin, yMax = min(xs), max(xs)+1, min(ys), max(ys)+1
# (0 19153.0 0 13146.0)


pool = []

# initiate pool by random permutation
# root = list(range(1,N+1))
# for _ in range(POP*2):
#     pool.append(sample(root, N))

# initiate pool based on grid
for xDiv in range(87, 88, 1):
    for yDiv in range(309, 310, 1):
        print("xDiv {}, yDiv {}".format(xDiv, yDiv))
        xSpan, ySpan = (xMax-xMin)/xDiv, (yMax-yMin)/yDiv
        ptsGrid = [[[] for _ in range(yDiv)] for _ in range(xDiv)]

        for idx, pt in enumerate(pts[1:]):
            i, j = int((pt.x-xMin)/xSpan), int((pt.y-yMin)/ySpan)
            ptsGrid[i][j] += [idx+1]

        sol = []
        for i in range(xDiv):
            for j in (range(yDiv) if i%2==0 else reversed(range(yDiv))):
                print(i, j)
                if ptsGrid[i][j]:
                    sol += optimize(l=ptsGrid[i][j])
                    # sol += ptsGrid[i][j]
        pool.append({
            'xDiv': xDiv,
            'yDiv': yDiv,
            'dir': 'x',
            'sol': sol
        })
        
        # sol = []
        # for i in range(yDiv):
        #     for j in (range(xDiv) if i%2==0 else reversed(range(xDiv))):
        #         if ptsGrid[j][i]:
        #             sol += optimize(l=ptsGrid[j][i])
        # pool.append({
        #     'xDiv': xDiv,
        #     'yDiv': yDiv,
        #     'dir': 'y',
        #     'sol': sol
        # })


pool.sort(key=lambda _: cost(_['sol']))
pool = pool[0:POP]

print("Initial pool------------------")
for d in pool:
    print("xDiv {}, yDiv {}, dir {}, cost {}".format(d['xDiv'], d['yDiv'], d['dir'], cost(d['sol'])))
print("-------------------------------")

# optimize(pool=pool, pop=POP, epochs=EPOCHS, 
#     rate_crossover=RATE_CROSSOVER, rate_mutation=RATE_MUTATION, 
#     printt=True, savee=True
# )

solStr = ""
for i in pool[0]['sol']: solStr += str(i)+"\n"
with open('solution - cost {}.csv'.format(cost(pool[0]['sol'])), 'w') as solution: solution.write(solStr[:-1])