import sha3
import Keccak
import array
import time
from multiprocessing import Pool

# http://stackoverflow.com/questions/2576712/using-python-how-can-i-read-the-bits-in-a-byte
def bits(f):
    bytes = (ord(b) for b in f.read())
    for b in bytes:
        for i in reversed(xrange(8)):
            yield (b >> i) & 1

f = open('imgtest.jpg', 'r')
M = ''.join( map(str, [b for b in bits(f)]) )
f.close()

B = 1024
H = 2
D = 4
L = D**H
TS = sum([D**i for i in xrange(0, H+1)])
tree = [None for i in xrange(TS)]
curIdx = TS

print 'Tree size =', TS
print 'Leaves =', L

startT = time.time()

# Perform hashing at each layer and then concatenate
K = Keccak.Keccak(1600)

# Get message into the leaves of the tree
for i in xrange(0, L):
    tree[len(tree) - i - 1] = ''

for i in xrange(0, len(M)):
    if i%10000 == 0:
        print i

    j = int(i/B) % L
    tree[len(tree) - L + j] += M[i]

for i in xrange(0, L):
    curB = tree[len(tree) - i - 1]
    if len(curB) % B != 0:
        tree[len(tree) - i - 1] = (B - len(curB)) * '0' + str(curB)

def workProc(hashStr):
    # Concatenate strings into current node, i
#     print 'Current node:', i
    return K.Keccak((len(hashStr), hashStr))

#         print len(tree[i]), hex(int(tree[i], 2))
#         hexB = tree[i]

#         print hexB, len(hexB)

#         tree[i] = K.Keccak((len(tree[i]), hexB))
#         print tree[i]

for curL in range(H, -1, -1):
    print curL
    curN = D**curL
    curIdx -= curN

    # Hash nodes on this level in parallel

    p = Pool(5)
    for i in xrange(curIdx, curIdx + curN):
        if curL < H:
            tree[i] = ''
            for j in xrange(i*D+1, i*D+(D+1)):
#                 print '    Adding', j
                tree[i] += tree[j]
        else:
            tree[i] = "{0:0x}".format(int(tree[i], 2))

    tree[curIdx: curIdx+curN] = p.map(workProc, tree[curIdx: curIdx+curN])

print 'Final output'
print '================='
print tree[0], len(tree[0]*4)

print 'Time = ', time.time() - startT

startT = time.time()
# http://stackoverflow.com/questions/3470398/list-of-integers-into-string-byte-array-python
BStr = ''.join( map(str,M) )
hexB = "{0:0x}".format(int(BStr, 2))
# hexB = hex(int(BStr,2))[2:-1]
# print hexB
res = K.Keccak( (len(M), hexB) )
print res, len(res)*4
print 'Time = ', time.time() - startT



