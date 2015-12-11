import numpy as np
cimport numpy as np
cimport cython
cimport AVX
from cython.parallel import prange, parallel

@cython.boundscheck(True)
@cython.wraparound(True)

cpdef void keccak_absorb(bytearray inputBytes, int blockSize, bytearray state, bytearray state1, int inputOffset):
    cdef:
        int i = 0
        int j = 7
        int k # index to help handle blocksize < 8 cases
        int l # index to help prevent segfault while accessing inputBytes
        int state_float[8]
        int inputBytes_proxy[8]
        int state_concat[50] 

        cdef:
            AVX.int8 avx_state, avx_inputBytes
    
    state_concat[:] = state
    for i in range(0, blockSize, 8):  
        # handle the case when size of inputBytes is not a multiple of 8
        if (blockSize - i) < 8:
            j = 7
            # ensure we are not taking data from memory locations beyond size of inputBytes; set that to zero on purpose
            while j >= (blockSize - i):
                inputBytes_proxy[j] = 0
                j = j - 1
            for l in range(blockSize - i):
                inputBytes_proxy[l] = inputBytes[i + inputOffset + l]       
        else:
            for l in range(8):
                inputBytes_proxy[l] = inputBytes[i + inputOffset + l]
                
        avx_state = AVX.make_int8(state[i + 7],
                                  state[i + 6],
                                  state[i + 5],
                                  state[i + 4],
                                  state[i + 3],
                                  state[i + 2],
                                  state[i + 1],
                                  state[i + 0])
            
        avx_inputBytes = AVX.make_int8(inputBytes_proxy[7],
                                       inputBytes_proxy[6],
                                       inputBytes_proxy[5],
                                       inputBytes_proxy[4],
                                       inputBytes_proxy[3],
                                       inputBytes_proxy[2],
                                       inputBytes_proxy[1],
                                       inputBytes_proxy[0])

        avx_state = AVX.bitwise_xor_int( avx_state, avx_inputBytes )
        AVX.to_mem_int(avx_state, &(state_float[0]))
        
        if (blockSize - i) < 8:
            for k in range((blockSize - i)):
                state_concat[i+k] = state_float[k]   
        else:
            state_concat[i:i+8] = state_float
                    
    for i in range(50): 
        state1[i] = <unsigned char>state_concat[i]


def ROL16(a, n):
    return ((a >> (16-(n%16))) + (a << (n%16))) % (1 << 16)

def load16(b):
    return sum((b[i] << (8*i)) for i in range(2)) 

def store16(a):
    return list((a >> (8*i)) % 256 for i in range(2))

cpdef void KeccakF400_avx(bytearray state, bytearray state1):
    
    # load the 5x5 lanes matrix from state
    lanes = [[load16(state[2*(x+5*y):2*(x+5*y)+2]) for y in range(5)] for x in range(5)]
    
    ## Round constants for step = iota
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

    cdef:
        int R = 1
        int rol16_counter
        int C_ROL16_serial[8]
        int C_serial[8]
        int D_serial[8]
        
        cdef:
            AVX.int8 avx_lanes0, avx_lanes1, avx_lanes2, avx_lanes3, avx_lanes4, \
                     C_rol64, C, C_prime_offset, C_prime, C_ROL16_offset, C_ROL16, D
   
    # repeated iterations of the five steps in each round - theta, rho, pi, chi and iota
    for round in range(20):
        
        # an avx variable for each column; columns only have depth of five
        avx_lanes0 = AVX.make_int8(0,
                                   0,
                                   0,
                                   lanes[4][0],
                                   lanes[3][0],
                                   lanes[2][0],
                                   lanes[1][0],
                                   lanes[0][0])
        avx_lanes1 = AVX.make_int8(0,
                                   0,
                                   0,
                                   lanes[4][1],
                                   lanes[3][1],
                                   lanes[2][1],
                                   lanes[1][1],
                                   lanes[0][1])
        avx_lanes2 = AVX.make_int8(0,
                                   0,
                                   0,
                                   lanes[4][2],
                                   lanes[3][2],
                                   lanes[2][2],
                                   lanes[1][2],
                                   lanes[0][2])
        avx_lanes3 = AVX.make_int8(0,
                                   0,
                                   0,
                                   lanes[4][3],
                                   lanes[3][3],
                                   lanes[2][3],
                                   lanes[1][3],
                                   lanes[0][3])
        avx_lanes4 = AVX.make_int8(0,
                                   0,
                                   0,
                                   lanes[4][4],
                                   lanes[3][4],
                                   lanes[2][4],
                                   lanes[1][4],
                                   lanes[0][4])
        
        # θ
        C = AVX.bitwise_xor_int( AVX.bitwise_xor_int( AVX.bitwise_xor_int( avx_lanes0, avx_lanes1 ), 
                                                      AVX.bitwise_xor_int( avx_lanes2, avx_lanes3 ) ), avx_lanes4 )
        C_prime_offset = AVX.make_int8_reverse(4, 0, 1, 2, 3, 5, 6, 7)
        C_prime = AVX.permute8( C, C_prime_offset )
        C_ROL16_offset = AVX.make_int8_reverse(1, 2, 3, 4, 0, 5, 6, 7)
        C_ROL16 = AVX.permute8( C, C_ROL16_offset )

        AVX.to_mem_int(C_ROL16, &(C_ROL16_serial[0]))

        # Applying bit rotation (circular shift) serially as intrinsic bit rotation isnt supported outside of AVX512
        for rol16_counter in range(8):
            C_ROL16_serial[rol16_counter] = ROL16(C_ROL16_serial[rol16_counter], 1) 
            
        C_ROL16 = AVX.make_int8_reverse( C_ROL16_serial[0],
                                         C_ROL16_serial[1],
                                         C_ROL16_serial[2],
                                         C_ROL16_serial[3],
                                         C_ROL16_serial[4],
                                         C_ROL16_serial[5],
                                         C_ROL16_serial[6],
                                         C_ROL16_serial[7] )
        
        D = AVX.bitwise_xor_int( C_prime, C_ROL16 )
        AVX.to_mem_int(D, &(D_serial[0]))
        
        lanes = [[lanes[x][y]^D_serial[x] for y in range(5)] for x in range(5)]

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
    
    # load data from 5x5 lanes matrix back into state
    for x in range(5):
        for y in range(5):
            state1[2*(x+5*y):2*(x+5*y)+2] = list(store16(lanes[x][y]))
    
    



