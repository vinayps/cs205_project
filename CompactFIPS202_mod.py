# -*- coding: utf-8 -*-
# Implementation by the Keccak, Keyak and Ketje Teams, namely, Guido Bertoni,
# Joan Daemen, Michaël Peeters, Gilles Van Assche and Ronny Van Keer, hereby
# denoted as "the implementer".
#
# For more information, feedback or questions, please refer to our websites:
# http://keccak.noekeon.org/
# http://keyak.noekeon.org/
# http://ketje.noekeon.org/
#
# To the extent possible under law, the implementer has waived all copyright
# and related or neighboring rights to the source code in this file.
# http://creativecommons.org/publicdomain/zero/1.0/

import sys
import os.path
import numpy as np
import set_compiler
set_compiler.install()

import pyximport
from distutils.extension import Extension 
ext_modules = [Extension('Keccak_Helper', ['Keccak_Helper.pyx'],
                          extra_compile_args=['-Wno-unused-function',
                                              '-std=gnu99',
                                              '-Ofast',
                                              '-march=native',
                                              '-fopenmp',
                                              '-I{}'.format(np.get_include()),
                                              '-I.',
                                              '-mfma',
                                              '-mavx',
                                              '-mavx2'], 
                          extra_link_args=['-fopenmp'])] 
pyximport.install(reload_support=True, setup_args={"include_dirs": [np.get_include(), os.curdir], 'ext_modules': ext_modules})
import Keccak_Helper as kh
reload(kh)

def ROL16(a, n):
    return ((a >> (16-(n%16))) + (a << (n%16))) % (1 << 16)

def KeccakF400onLanes(lanes):
    ## Round constants
    RC=[0x0000000000000001,
        0x0000000000008082,
        0x800000000000808A,
        0x8000000080008000,
        0x000000000000808B,
        0x0000000080000001,
        0x8000000080008081,
        0x8000000000008009,
        0x000000000000008A,
        0x0000000000000088,
        0x0000000080008009,
        0x000000008000000A,
        0x000000008000808B,
        0x800000000000008B,
        0x8000000000008089,
        0x8000000000008003,
        0x8000000000008002,
        0x8000000000000080,
        0x000000000000800A,
        0x800000008000000A,
        0x8000000080008081,
        0x8000000000008080,
        0x0000000080000001,
        0x8000000080008008]

    for round in range(20):
        # θ
        C = [lanes[x][0] ^ lanes[x][1] ^ lanes[x][2] ^ lanes[x][3] ^ lanes[x][4] for x in range(5)]
        D = [C[(x+4)%5] ^ ROL16(C[(x+1)%5], 1) for x in range(5)]
        lanes = [[lanes[x][y]^D[x] for y in range(5)] for x in range(5)]
        # ρ and π
        (x, y) = (1, 0)
        current = lanes[x][y]
        for t in range(24):
            (x, y) = (y, (2*x+3*y)%5)
            (current, lanes[x][y]) = (lanes[x][y], ROL16(current, (t+1)*(t+2)//2))
        # χ
        for y in range(5):
            T = [lanes[x][y] for x in range(5)]
            for x in range(5):
                lanes[x][y] = T[x] ^((~T[(x+1)%5]) & T[(x+2)%5])
        # ι
        lanes[0][0] = lanes[0][0] ^ RC[round]%(1<<16)
    return lanes

def load16(b):
    return sum((b[i] << (8*i)) for i in range(2)) 

def store16(a):
    return list((a >> (8*i)) % 256 for i in range(2))

def KeccakF400(state, useAVX = True):
    if useAVX:
        state1 = bytearray(50)
        kh.KeccakF400_avx(state, state1)
        state = state1
    else:
        lanes = [[load16(state[2*(x+5*y):2*(x+5*y)+2]) for y in range(5)] for x in range(5)]
        lanes = KeccakF400onLanes(lanes)
        state = bytearray(50)
        for x in range(5):
            for y in range(5):
                state[2*(x+5*y):2*(x+5*y)+2] = store16(lanes[x][y])
    return state

def Keccak(rate, capacity, inputBytes, delimitedSuffix, outputByteLen, useAVX = True):
    
    outputBytes = bytearray()
    state = bytearray([0 for i in range(50)]) 
    rateInBytes = rate//8
    blockSize = 0
    
    if (((rate + capacity) != 400) or ((rate % 8) != 0)): 
        return
    
    inputOffset = 0
    
    # === Absorb all the input blocks ===
    while(inputOffset < len(inputBytes)):
        blockSize = min(len(inputBytes)-inputOffset, rateInBytes)
        
        if useAVX:
            state1 = bytearray([0 for i in range(50)]) 
            kh.keccak_absorb( inputBytes, blockSize, state, state1, inputOffset )
            state = state1
        else:
            for i in range(blockSize):
                state[i] = state[i] ^ inputBytes[i+inputOffset]
                
        inputOffset = inputOffset + blockSize
        
        if (blockSize == rateInBytes):
            state = KeccakF400(state, useAVX)
            blockSize = 0
            
    # === Do the padding and switch to the squeezing phase ===
    state[blockSize] = state[blockSize] ^ delimitedSuffix
    
    if (((delimitedSuffix & 0x80) != 0) and (blockSize == (rateInBytes-1))):
        state = KeccakF400(state, useAVX)
        
    state[rateInBytes-1] = state[rateInBytes-1] ^ 0x80
    state = KeccakF400(state, useAVX)
    
    # === Squeeze out all the output blocks ===
    while(outputByteLen > 0):
        blockSize = min(outputByteLen, rateInBytes)
        outputBytes = outputBytes + state[0:blockSize]
        outputByteLen = outputByteLen - blockSize
        
        if (outputByteLen > 0):
            state = KeccakF400(state, useAVX)
            
    return outputBytes

# Example function calls for Keccak 1600
def SHAKE128(inputBytes, outputByteLen):
    return Keccak(1344, 256, inputBytes, 0x1F, outputByteLen)

def SHAKE256(inputBytes, outputByteLen):
    return Keccak(1088, 512, inputBytes, 0x1F, outputByteLen)

def SHA3_224(inputBytes):
    return Keccak(1152, 448, inputBytes, 0x06, 224//8)

def SHA3_256(inputBytes):
    return Keccak(1088, 512, inputBytes, 0x06, 256//8)

def SHA3_384(inputBytes):
    return Keccak(832, 768, inputBytes, 0x06, 384//8)

def SHA3_512(inputBytes):
    return Keccak(576, 1024, inputBytes, 0x06, 512//8)
