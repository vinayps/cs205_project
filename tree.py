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

f = open('50MB.bin', 'r')
M = ''.join( map(str, [b for b in bits(f)]) )
f.close()
K = Keccak.Keccak(1600)


def workProc(hashStr):
    return K.Keccak((len(hashStr), hashStr))

def treeHash(MString, B = 1024, H = 2, D = 4):
    # Perform hashing at each layer and then concatenate
    L = D**H
    TS = sum([D**i for i in xrange(0, H+1)])
    curIdx = TS
    tree = [None for i in xrange(TS)]

    # Get message into the leaves of the tree
    for i in xrange(0, L):
        tree[len(tree) - i - 1] = []

    for i in xrange(0, len(M)):
        # if i%100000 == 0:
        #     print i

        j = int(i/B) % L
        tree[len(tree) - L + j].append(M[i])

    for i in xrange(0, L):
        curB = ''.join(tree[len(tree) - i - 1])
        if len(curB) % B != 0: # Add padding if not a multiple of B
            tree[len(tree) - i - 1] = (B - len(curB)) * '0' + curB
        else:
            tree[len(tree) - i - 1] = curB

    startT = time.time()
    for curL in range(H, -1, -1):
        print 'Level', curL
        curN = D**curL
        curIdx -= curN

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

        tree[curIdx: curIdx+curN] = p.map(workProc, tree[curIdx: curIdx+curN])
    print time.time() - startT
    return tree[0]

print 'Final output'
print '================='


startT = time.time()
tRet = treeHash(M)
print tRet, len(tRet)
print 'Time = ', time.time() - startT

# Using normal Keccak function
startT = time.time()
# http://stackoverflow.com/questions/3470398/list-of-integers-into-string-byte-array-python
BStr = ''.join( map(str,M) )
hexB = "{0:0x}".format(int(BStr, 2))
res = K.Keccak( (len(M), hexB) )
print res, len(res)*4
print 'Time = ', time.time() - startT



