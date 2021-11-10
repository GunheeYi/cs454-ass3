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
parser.add_argument('-f', required=False, default='10000', help='limit on number of fitness evaluations')
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
    totalDist = 0
    for i in range(N-1):
        totalDist += dist(pts[l[i]], pts[l[i+1]])
    totalDist += dist(pts[l[-1]], pts[l[0]])
    return totalDist

def crossoverPMX(l1, l2):
    l3 = [0 for _ in range(N)]
    cut1, cut2 = sorted(sample(range(N+1), 2))
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
    
    for i in range(N):
        if l3[i]==0: l3[i] = l2[i]

    return l3

def swap(l, i, j):
    ll = l.copy()
    temp = ll[i]
    ll[i] = ll[j]
    ll[j] = temp
    return ll

def mutateRandom(l):
    i, j = sample(range(N), 2)
    return swap(l, i, j)

def mutateAdjacent(l):
    i = randrange(N)
    return swap(l, i, 0 if i==N-1 else i+1)




xs = list(map(lambda _: _.x, pts))
ys = list(map(lambda _: _.y, pts))
xMin, xMax, yMin, yMax = min(xs), max(xs)+1, min(ys), max(ys)+1
# (0 19153.0 0 13146.0)

# for xDiv in range(60, 80, 1):
#     for yDiv in range(90, 110, 1):
xDiv, yDiv = 60, 100
xSpan, ySpan = (xMax-xMin)/xDiv, (yMax-yMin)/yDiv
ptsGrid = [[[] for _ in range(yDiv)] for _ in range(xDiv)]

for idx, pt in enumerate(pts[1:]):
    i, j = int((pt.x-xMin)/xSpan), int((pt.y-yMin)/ySpan)
    ptsGrid[i][j] += [idx+1]

sol = []

for i in range(xDiv):
    for j in (range(yDiv) if i%2==0 else reversed(range(yDiv))):
        # print(len(ptsGrid[i][j]), end=" ")
        sol += ptsGrid[i][j]
    # print()

print("Cost {} for xDiv {} and yDiv {}".format(cost(sol), xDiv, yDiv))

solStr = ""
for i in sol: solStr += str(i)+"\n"
with open('cost {} - {}, {}.csv'.format(int(cost(sol)), xDiv, yDiv), 'w') as solution: solution.write(solStr[:-1])





# root = list(range(1,N+1))

# pool = []

# for _ in range(POP*2):
#     pool.append(sample(root, N))

# pool.sort(key=lambda _: cost(_))
# pool = pool[0:POP]

# print("Initial pool------------------")
# for sol in pool:
#     print(str(cost(sol)))
# print("-------------------------------")

# for epoch in range(EPOCHS):
#     # reproduce next generation
#     crossovers = []
#     timer = 0
#     while timer < 1000 and len(crossovers) < POP*RATE_CROSSOVER:
#         timer += 1
#         p1, p2 = sample(pool, 2)
#         crossovers += [crossoverPMX(p1, p2)]
#     # mutate
#     mutants = []
#     timer = 0
#     while timer < 1000 and len(mutants) < POP*RATE_MUTATION:
#         timer += 1
#         p = sample(pool, 1)[0]
#         mutants += [mutateAdjacent(p)]
#     # merge all path pools
#     pool = pool + crossovers + mutants
#     # select only the first POP paths fittest
#     pool.sort(key=lambda _: cost(_))
#     pool = pool[0:POP]

#     solStr = ""
#     for i in pool[0]: solStr += str(i)+"\n"
#     with open('solution - cost {}.csv'.format(cost(pool[0])), 'w') as solution: solution.write(solStr[:-1])

#     # print the best path in current generation
#     print("The fittest cycle in epoch {} costs {}".format(epoch+1, cost(pool[0])))
