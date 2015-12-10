# -*- coding: utf-8 -*-
# Implementation by Renaud Bauvin,
# hereby denoted as "the implementer".
#
# To the extent possible under law, the implementer has waived all copyright
# and related or neighboring rights to the source code in this file.
# http://creativecommons.org/publicdomain/zero/1.0/

import binascii
import Keccakf400_AVX_FIPS202
#import CompactFIPS202
import os
from timer import Timer 
import Keccak
    
## Iterate through the files 'Short... and LongMsgKAT_XXX.txt' containing the
## test vectors and compare the computed values to the provided ones
## In case of difference, it stops the processing and print a message

dirTestVector=os.path.abspath(os.path.join('./Test_Files'))
verbose=False
instances=[
    ['SHAKE128', 336, 64, 0x1F, 0], # 1344, 256
    ['SHAKE256', 272, 128, 0x1F, 0], # 1088, 512
    ['SHA3-224', 288, 112, 0x06, 224], # 1152, 448
    ['SHA3-256', 272, 128, 0x06, 256], # 1088, 512
    ['SHA3-384', 208, 192, 0x06, 384], # 832, 768
    ['SHA3-512', 144, 256, 0x06, 512],  # change 576  1024
]
fileTypes=['Short']

#Create an instance for reference
myKeccak=Keccak.Keccak(400)

def delimitedSuffixInBinary(delimitedSuffix):
    binary = ''
    while(delimitedSuffix != 1):
        binary = binary + ('%d' % (delimitedSuffix%2))
        delimitedSuffix = delimitedSuffix//2
    return binary


with Timer() as t:

    for i in range(1):
        for instance in instances:
            [fileNameSuffix, r, c, delimitedSuffix, n] = instance
            for fileType in fileTypes:
                print('Processing file: %sMsgKAT_%s.txt...' % (fileType, fileNameSuffix))
                print("Keccak[r=%d, c=%d] with '%s' suffix" % (r, c, delimitedSuffixInBinary(delimitedSuffix)))

                #Open the corresponding file
                try:
                    referenceFile=open(os.path.join(dirTestVector,fileType+('MsgKAT_%s.txt' % fileNameSuffix)), 'r')
                except IOError:
                    print("Error: test vector files must be stored in %s" % (dirTestVector))
                    exit()

                #Parse the document line by line (works only for Short and Long files)
                for line in referenceFile:
                    if line.startswith('Len'):
                        Len=int(line.split(' = ')[1].strip('\n\r'))
                    if line.startswith('Msg'):
                        Msg=line.split(' = ')[1].strip('\n\r')
                        msg = bytearray(binascii.unhexlify(Msg))
                        msg = msg[:Len//8]
                    if (line.startswith('MD') or line.startswith('Squeezed')):
                        MD_ref=line.split(' = ')[1].strip('\n\r')
                        reference = bytearray(binascii.unhexlify(MD_ref))
                        # If line starts with 'Squeezed', use the output length from the test vector
                        if line.startswith('Squeezed'):
                            n = len(reference)*8
                        elif n == 0:
                            print("Error: the output length should be specified")
                            exit()

                        if ((Len % 8) == 0 ): #and ( Len == 104 )): 
                            #print Len
                            # Perform our own computation
                            #computed = CompactFIPS202.Keccak(r, c, msg, delimitedSuffix, n//8)
                            computed = Keccakf400_AVX_FIPS202.Keccak(r, c, msg, delimitedSuffix, n//8, useAVX = True)
                            #print binascii.hexlify(computed)
                            #Compare the results
                            reference = myKeccak.Keccak((Len,Msg), r, c, delimitedSuffix, (len(MD_ref)//2)*8, False)
                            #print reference
                            if (binascii.hexlify(computed).upper() != reference):
                                print('ERROR: \n\t type=%s\n\t length=%d\n\t message=%s\n\t reference=%s\n\t computed=%s' % (fileNameSuffix, Len, Msg, reference, binascii.hexlify(computed))) # binascii.hexlify(reference)
                                exit()

                print("OK\n")
                referenceFile.close()
            
seconds = t.interval
print("Total time taken (seconds) = %s" %(seconds))

