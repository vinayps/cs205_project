import sha3
import Keccak
import KeccakError
import array
import time
from multiprocessing import Pool

# http://stackoverflow.com/questions/2576712/using-python-how-can-i-read-the-bits-in-a-byte
def bits(f):
    bytes = (ord(b) for b in f.read())
    for b in bytes:
        for i in reversed(xrange(8)):
            yield (b >> i) & 1

f = open('100KB.bin', 'r')
M = ''.join( map(str, [b for b in bits(f)]) )
f.close()
K = Keccak.Keccak(1600)

fM1, fM2 = None, None

def workProc(hashStr):
    return K.Keccak((len(hashStr)*4, hashStr))

def treeHash(M, B = 1024, H = 2, D = 4):
    # Perform hashing at each layer and then concatenate
    L = D**H
    TS = sum([D**i for i in xrange(0, H+1)])
    curIdx = TS
    tree = [None for i in xrange(TS)]
    print 'Message:', len(M)

    # Get message into the leaves of the tree
    for i in xrange(0, L):
        tree[len(tree) - i - 1] = []

    # for i in xrange(0, len(M)):
    #     # if i%100000 == 0:
    #     #     print i
    #
    #     j = int(i/B) % L
    #     tree[len(tree) - L + j].append(M[i])

    nGroups = len(M)/B + (len(M)%B != 0)
    for i in xrange(0, nGroups):
        tree[len(tree) - L + i%L].append(M[i*B: (i+1)*B])


    for i in xrange(0, L):
        curB = ''.join(tree[len(tree) - i - 1])
        if len(curB) % B != 0: # Add padding if not a multiple of B
            tree[len(tree) - i - 1] = (B - len(curB)) * '0' + curB
        else:
            tree[len(tree) - i - 1] = curB

    startT2 = time.time()
    for curL in range(H, -1, -1):
        print 'Level', curL
        curN = D**curL
        curIdx -= curN

        # if curL == 0:
        #     print len(tree[0])

        # Hash nodes on this level in parallel
        p = Pool(4)
        for i in xrange(curIdx, curIdx + curN):
            if curL < H:
                tree[i] = []
                for j in xrange(i*D+1, i*D+(D+1)):
                    tree[i].append(tree[j])

                tree[i] = ''.join(tree[i])
            else:
                tree[i] = "{0:0{1}x}".format(int(tree[i], 2), len(tree[i])/4)

        # if curL == 0:
        #     global fM1
        #     fM1 = tree[0]
        tree[curIdx: curIdx+curN] = p.map(workProc, tree[curIdx: curIdx+curN])
    print time.time() - startT2
    return tree[0]

print 'Final output'
print '================='


for h in xrange(0, 5):
    print 'Height:', h
    startT = time.time()
    tRet = treeHash(M, H=h)
    print tRet, len(tRet)*4
    print 'Time = ', time.time() - startT

# Using normal Keccak function

# http://stackoverflow.com/questions/3470398/list-of-integers-into-string-byte-array-python
startT = time.time()
BStr = ''.join( map(str,M) )
hexB = "{0:0x}".format(int(BStr, 2))
# print 'Equal?', (hexB == fM1)
res = K.Keccak( (len(M), hexB) )
print res, len(res)*4
print 'Time = ', time.time() - startT



