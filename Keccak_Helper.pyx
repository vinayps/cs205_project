import numpy as np
cimport numpy as np
cimport cython
cimport AVX
#import numpy
from cython.parallel import prange, parallel


@cython.boundscheck(True)
@cython.wraparound(True)


# An example using AVX instructions
cpdef example_sqrt_8(np.int32_t[:] values):
    cdef:
        AVX.int8 avxval, tmp, mask
        int out_vals[8]
        int [:] out_view = out_vals

    assert values.shape[0] == 8

    # Note that the order of the arguments here is opposite the direction when
    # we retrieve them into memory.
    avxval = AVX.make_int8(values[7],
                             values[6],
                             values[5],
                             values[4],
                             values[3],
                             values[2],
                             values[1],
                             values[0])
    
    offsets = AVX.make_int8_reverse(7, 0, 1, 2, 3, 4, 5, 6)
                                  
    #avxval = AVX.sqrt(avxval)
    avxval1 = AVX.permute8( avxval, offsets )
    # mask will be true where 2.0 < avxval
    #mask = AVX.less_than(AVX.float_to_float8(2.0), avxval)

    # invert mask and select off values, so should be 2.0 >= avxval
    #avxval = AVX.bitwise_andnot(mask, avxval)

    AVX.to_mem_int(avxval1, &(out_vals[0]))

    return np.array(out_view)


cpdef void keccak_absorb(bytearray inputBytes, int blockSize, bytearray state, bytearray state1, int inputOffset):
    cdef:
        int i = 0
        int j = 7
        int k # index to help handle blocksize < 8 cases
        int l # index to help prevent segfault while accessing inputBytes
        int state_float[8]
        int inputBytes_proxy[8]
        int state_concat[200]
        #np.float32_t [:, :] in_coords_real
        #np.float32_t [:, :] in_coords_imag

        # To declare AVX.float8 variables, use:
        cdef:
            AVX.int8 avx_state, avx_inputBytes
    
    state_concat[:] = state
    #print "keccak"
    #print inputBytes
    #print blockSize 
    # seems like a bug in prange, add 7 to get the actual full range
    for i in range(0, blockSize, 8):  
        # handle the case when size of inputBytes is not a multiple of 8; 
        # ensure we are not taking data from random memory locations beyond size of inputBytes; set that to zero on purpose
        if (blockSize - i) < 8:
            j = 7
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
        #state_float = <unsigned char*>&(avx_inputBytes)
        if (blockSize - i) < 8:
            for k in range((blockSize - i)):
                state_concat[i+k] = state_float[k]   
        else:
            state_concat[i:i+8] = state_float
                    
    for i in range(200):
        state1[i] = <unsigned char>state_concat[i]
    #print state1
    #return state_char
        
cpdef ROL64(int a, int n):
    return ((a >> (64-(n%64))) + (a << (n%64))) % (1 << 64)

cpdef ROL64_avx_one(int [:] values): #forcing n = 1
    cdef:
        AVX.int8 ret_val, val1, val2
        int ret_val_serial[8]
    a = AVX.make_int8(values[7],
                      values[6],
                      values[5],
                      values[4],
                      values[3],
                      values[2],
                      values[1],
                      values[0])
    val1 = AVX.sub_int( AVX.int_to_int8(64), AVX.int_to_int8(1))
    val2 = AVX.int_to_int8(1)
    ret_val = AVX.add_int( AVX.bitwise_right_shift( a, val1 ), AVX.bitwise_left_shift( a, val2 ) )
    AVX.to_mem_int(ret_val, &(ret_val_serial[0]))
    return ret_val_serial



cpdef store64(int a):
    cdef:
        int i
        int val[8]
    for i in range(8):
        val[i] = ((a >> (8*i)) % 256 )    
    return val

cpdef load64(int [:] b):
    cdef:
        int i
        int val = 0
    for i in range(8):
        val = val + (b[i] << (8*i))
    return val

cpdef KeccakF1600_avx(bytearray state, bytearray state1):
    
    lanes = [[load64(state[8*(x+5*y):8*(x+5*y)+8]) for y in range(5)] for x in range(5)]
    cdef:
        int R = 1
        int C_ROL64_serial[8]
        int D_serial[8]
        cdef:
            AVX.int8 avx_lanes0, avx_lanes1, avx_lanes2, avx_lanes3, avx_lanes4, \
                     avx_Cprime, avx_C_rol64

    # an avx variable for each column
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
   
    for round in range(24):
        # θ
        C = AVX.bitwise_xor_int( AVX.bitwise_xor_int( AVX.bitwise_xor_int( avx_lanes0, avx_lanes1 ), 
                                                      AVX.bitwise_xor_int( avx_lanes2, avx_lanes3 ) ), avx_lanes4 )
        #C = [lanes[x][0] ^ lanes[x][1] ^ lanes[x][2] ^ lanes[x][3] ^ lanes[x][4] for x in range(5)]
        C_prime_offset = AVX.make_int8_reverse(4, 0, 1, 2, 3, 5, 6, 7)
        C_prime = AVX.permute8( C, C_prime_offset )
        C_ROL64_offset = AVX.make_int8_reverse(1, 2, 3, 4, 0, 5, 6, 7)
        C_ROL64 = AVX.permute8( C, C_ROL64_offset )
        AVX.to_mem_int(C_ROL64, &(C_ROL64_serial[0]))
        C_ROL64_serial = ROL64_avx_one( C_ROL64_serial )
        for rol64_counter in range(8):
            C_ROL64_serial[rol64_counter] = C_ROL64_serial[rol64_counter] % (1 << 64)
        C_ROL64 = AVX.make_int8_reverse( C_ROL64_serial[0],
                                         C_ROL64_serial[1],
                                         C_ROL64_serial[2],
                                         C_ROL64_serial[3],
                                         C_ROL64_serial[4],
                                         C_ROL64_serial[5],
                                         C_ROL64_serial[6],
                                         C_ROL64_serial[7] )
        D = AVX.bitwise_xor_int( C_prime, C_ROL64 )
        AVX.to_mem_int(D, &(D_serial[0]))
        
        #D = [C[(x+4)%5] ^ ROL64(C[(x+1)%5], 1) for x in range(5)]
        lanes = [[lanes[x][y]^D_serial[x] for y in range(5)] for x in range(5)]
        # ρ and π
        (x, y) = (1, 0)
        current = lanes[x][y]
        for t in range(24):
            (x, y) = (y, (2*x+3*y)%5)
            (current, lanes[x][y]) = (lanes[x][y], ROL64(current, (t+1)*(t+2)//2))
        # χ
        for y in range(5):
            T = [lanes[x][y] for x in range(5)]
            for x in range(5):
                lanes[x][y] = T[x] ^((~T[(x+1)%5]) & T[(x+2)%5])
        # ι
        for j in range(7):
            R = ((R << 1) ^ ((R >> 7)*0x71)) % 256
            if (R & 2):
                lanes[0][0] = lanes[0][0] ^ (1 << ((1<<j)-1))
    
    state1 = bytearray(200)
    for x in range(5):
        for y in range(5):
            state1[8*(x+5*y):8*(x+5*y)+8] = list(store64(lanes[x][y]))
    
    


