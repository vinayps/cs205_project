import Keccak
import CompactFIPS202_mod
import array
import time
import binascii
from multiprocessing import Pool
import sys, getopt
from functools import partial

def main(argv):
    inputfile = ''
    inputmessage = ''
    
    # Default values for Keccak and tree hashing parameters
    h = 3 # treeHeight - performs well for file sizes 1 MB and upwards; and smaller files have much smaller runtime anyway
    d = 4 # treeDegree
    outputLength = 512 # default with SHA3-512
    useAVX = True
    
    try: # if both i and m are passed in, we pick m
        opts, args = getopt.getopt(argv, "ui:m:h:d:o:", ["ifile=","imessage=", "treeHeight=", "treeDegree=", "outputLength="])
    except getopt.GetoptError:
        print 'tree.py -i <inputfile> -h 3 -d 4 -o 512\ntree.py -m <inputmessage> -h 3 -d 4 -o 512'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-u': #usage
            print 'tree.py -i <inputfile> -h 3 -d 4 -o 512\ntree.py -m <inputmessage> -h 3 -d 4 -o 512'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            M = getMessageFromFile(inputfile)
        elif opt in ("-m", "--imessage"):
            inputmessage = arg
            M = getMessageFromString(inputmessage)
        elif opt in ("-h", "--treeHeight"):
            assert arg.isdigit() == True, "treeHeight argument expected to be an integer"
            h = int(arg)
        elif opt in ("-d", "--treeDegree"):
            assert arg.isdigit() == True, "treeDegree argument expected to be an integer"
            d = int(arg)
        elif opt in ("-o", "--outputLength"):
            assert arg.isdigit() == True, "outputLength argument expected to be an integer"
            outputLength = int(arg)
            
    assert inputfile != '' or inputmessage != '', "no message or file provided" 
    
    print 'Final output: SHA3 - Keccak400'
    print '================='

    print 'Serial'
    startT = time.time()
    BStr = ''.join( map(str,M) )
    hexB = "{0:0x}".format(int(BStr, 2)) if BStr != '' else ''
    msg = bytearray(binascii.unhexlify(hexB))
    msg = msg[:len(msg)]
    res = binascii.hexlify(CompactFIPS202_mod.Keccak(144, 256, msg, 0x06, outputLength//8, useAVX = False)).upper()
    #print res
    #print res_avx
    #assert res == res_avx, "Not matching"
    print res, len(res)*4
    print 'time: ', time.time() - startT
    
    # Using normal Keccak function
    # http://stackoverflow.com/questions/3470398/list-of-integers-into-string-byte-array-python
    print 'AVX only'
    startT = time.time()
    BStr = ''.join( map(str,M) )
    hexB = "{0:0x}".format(int(BStr, 2)) if BStr != '' else ''
    #res = K.Keccak( (len(M), hexB), 144, 256, 0x06, 512, False) # r = 144, c = 256, suffix = 0x06, n (output) = 512
    msg = bytearray(binascii.unhexlify(hexB))
    msg = msg[:len(msg)]
    res = binascii.hexlify(CompactFIPS202_mod.Keccak(144, 256, msg, 0x06, outputLength//8, useAVX = True)).upper()
    #print res
    #print res_avx
    #assert res == res_avx, "Not matching"
    print res, len(res)*4
    print 'time: ', time.time() - startT
    
    # Tree hash
    #for h in xrange(0, 5):
    #print 'Height:', h
    print "Tree hashing only"
    startT = time.time()
    tRet = treeHash(M, h, d, outputLength, useAVX = False)
    print tRet, len(tRet)*4
    print 'time: ', time.time() - startT
    
    # Tree hash
    #for h in xrange(0, 5):
    #print 'Height:', h
    print "Tree hashing + AVX"
    startT = time.time()
    tRet = treeHash(M, h, d, outputLength, useAVX = True)
    print tRet, len(tRet)*4
    print 'time: ', time.time() - startT
    
    
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
    f = open(inputfile, 'r') 
    M = ''.join( map(str, [b for b in bits(f)]) )
    f.close()
    return M

def getMessageFromString(inputmessage):
    M = ''.join( map(str, [b for b in bits(inputmessage, message = True)]) )
    return M

def workProc(hashStr, outputLength, useAVX):
    msg = bytearray(binascii.unhexlify(hashStr))
    msg = msg[:len(msg)]
    return binascii.hexlify(CompactFIPS202_mod.Keccak(144, 256, msg, 0x06, outputLength//8, useAVX = useAVX)).upper()

def treeHash(M, H, D, outputLength, B = 1024, useAVX = True):
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
    
    # creating a partial function to use in pool.map 
    workProc_handler = partial(workProc, outputLength = outputLength, useAVX = useAVX)
    
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

        tree[curIdx: curIdx+curN] = p.map(workProc_handler, tree[curIdx: curIdx+curN])
    # print 'H = %d time:'%H, time.time() - startT2
    return tree[0]


if __name__ == "__main__":
    main(sys.argv[1:])
