#import sha3
import Keccak
#import KeccakError
import array
import time
from multiprocessing import Pool
import sys, getopt

# setting this globally
K = Keccak.Keccak(400)

def main(argv):
    inputfile = ''
    inputmessage = ''
    try:
        opts, args = getopt.getopt(argv, "hi:m:", ["ifile=","imessage="])
    except getopt.GetoptError:
        print 'tree.py -i <inputfile> \ntest.py -m <inputmessage>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'tree.py -i <inputfile> \ntest.py -m <inputmessage>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            M = getMessageFromFile(inputfile)
        elif opt in ("-m", "--imessage"):
            inputmessage = arg
            M = getMessageFromString(inputmessage)
            
    fM1, fM2 = None, None

    print 'Final output (tree hashing)'
    print '================='

    # print M

    # Tree hash
    for h in xrange(0, 5):
        print 'Height:', h
        startT = time.time()
        tRet = treeHash(M, K, H=h)
        print tRet, len(tRet)*4
        print 'H = %d time:'%h, time.time() - startT
    
    # Using normal Keccak function
    # http://stackoverflow.com/questions/3470398/list-of-integers-into-string-byte-array-python
    print 'Final output (serial)'
    print '================='
    startT = time.time()
    BStr = ''.join( map(str,M) )
    hexB = "{0:0x}".format(int(BStr, 2)) if BStr != '' else ''
    res = K.Keccak( (len(M), hexB), 144, 256, 0x06, 512, False) # r = 144, c = 256, suffix = 0x06, n (output) = 512
    print res, len(res)*4
    print 'Time = ', time.time() - startT
        

# http://stackoverflow.com/questions/2576712/using-python-how-can-i-read-the-bits-in-a-byte
def bits(f, message = False):
    if message:
        bytes = (ord(b) for b in f)
    else:
        bytes = (ord(b) for b in f.read())
    for b in bytes:
        for i in reversed(xrange(8)):
            yield (b >> i) & 1

def getMessageFromFile(inputfile):
    f = open(inputfile, 'r') # '100KB.bin'
    M = ''.join( map(str, [b for b in bits(f)]) )
    f.close()
    return M

def getMessageFromString(inputmessage):
    #f = open(inputfile, 'r') # '100KB.bin'
    M = ''.join( map(str, [b for b in bits(inputmessage, message = True)]) )
    #f.close()
    return M

def workProc(hashStr):
    return K.Keccak((len(hashStr)*4, hashStr), 144, 256, 0x06, 512, False) # r = 144, c = 256, suffix = 0x06, n (output) = 512

def treeHash(M, K, B = 1024, H = 2, D = 4):
    # Perform hashing at each layer and then concatenate
    L = D**H
    TS = sum([D**i for i in xrange(0, H+1)])
    curIdx = TS
    tree = [None for i in xrange(TS)]

    # Initialize the leaves
    for i in xrange(0, L):
        tree[len(tree) - i - 1] = []

    # Get message into the leaves of the tree
    nGroups = len(M)/B + (len(M)%B != 0)
    for i in xrange(0, nGroups):
        tree[len(tree) - L + i%L].append(M[i*B: (i+1)*B])


    for i in xrange(0, L):
        curB = ''.join(tree[len(tree) - i - 1])
        tree[len(tree) - i - 1] = curB
    
    # startT2 = time.time()
    for curL in range(H, -1, -1): # Work through each level of the tree in turn
        # print 'Level', curL
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
                if tree[i] != '':
                    tree[i] = "{0:0{1}x}".format(int(tree[i], 2), len(tree[i])/4)

        tree[curIdx: curIdx+curN] = p.map(workProc, tree[curIdx: curIdx+curN])
    # print 'H = %d time:'%H, time.time() - startT2
    return tree[0]


if __name__ == "__main__":
    main(sys.argv[1:])
