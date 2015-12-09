# Cython Definition file for AVX.h

cdef extern from "AVX.h" nogil:
    ctypedef struct float8:
        pass
    ctypedef struct int8:
        pass

    # Create a vector of 8 floats
    #     from one value
    float8 float_to_float8(float)
    # int vector set with one int value
    int8 int_to_int8(int)
    #     from 8 values
    float8 make_float8(float, float, float, float, float, float, float, float)
    # int vector from eight int values; and the reverse to make inputs easier
    int8 make_int8(int, int, int, int, int, int, int, int)
    int8 make_int8_reverse(int, int, int, int, int, int, int, int)
    # Arithmetic:
    #     Each of these operate on their 8 values independently, and return a
    #     new float8
    float8 add(float8, float8)
    float8 sub(float8, float8)
    float8 mul(float8, float8)
    float8 div(float8, float8)
    float8 sqrt(float8)
    float8 fmadd(float8 a, float8 b, float8 c)  # a * b + c
    float8 fmsub(float8 a, float8 b, float8 c)  # a / b + c
    # Basic arithmetic for int8
    int8 add_int(int8, int8)
    int8 sub_int(int8, int8)    

    # Comparisons:
    #     When comparing to vectors of float, the result is either 0.0 or -1.0,
    #     in each of the 8 locations.  Note that -1.0 is all 1s in its
    #     repesentation.  This can be useful with bitwise_and(), below.
    float8 less_than(float8 a, float8 b)     # (a < b) -> 0.0 or -1.0
    float8 greater_than(float8 a, float8 b)  # (a > b) -> 0.0 or -1.0

    # Bitwise AND:
    #     Note that 0.0 = all zeros,
    #              -1.0 == all 1s
    #     So, (val & 0.0) == 0.0
    #     and, (val & -1.0) == val
    float8 bitwise_and(float8, float8)
    # This version inverts its first argument before the and
    float8 bitwise_andnot(float8 mask, float8 val)
    float8 bitwise_xor(float8, float8)  # 1010 xor 0011 = 1001
    # Bitwise XOR for int
    int8 bitwise_xor_int(int8 a, int8 b)

    # Helpers:
    #     This extracts the signs of each float into an 8-bit value.
    int signs(float8)

    #     This copies the contents of the float8 into a memory location
    void to_mem(float8, float *)
    #     This copies the contents of the int8 into a memory location    
    void to_mem_int(int8, int *)
    
    #Permute - helps move values around in a vector inplace
    int8 permute8( int8 a, int8 b)
    
    #Shift
    int8 bitwise_right_shift(int8 a, int8 b)
    int8 bitwise_left_shift(int8 a, int8 b)
    
    #Rotate - unfortunately doesnt work on our processors - needs AVX 512
    #int8 bitwise_rot_l_64(int8 a, int b) 
    #int8 bitwise_rot_r_64(int8 a, int b)
    
