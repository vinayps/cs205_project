#include <math.h>

#ifdef __AVX__
#  include <immintrin.h>
#else
#  include "avxintrin-emu.h"
#endif

#ifdef __FMA__
#  include <fmaintrin.h>
#else
#  define _mm256_fmadd_ps(a, b, c) _mm256_add_ps(_mm256_mul_ps((a), (b)), (c))
#  define _mm256_fmsub_ps(a, b, c) _mm256_sub_ps(_mm256_mul_ps((a), (b)), (c))
#endif
    
//Float
typedef __m256 float8;
//Int
typedef __m256i int8;

//Construction
#define float_to_float8(v) _mm256_set1_ps(v)
#define make_float8(v1, v2, v3, v4, v5, v6, v7, v8) _mm256_set_ps((v1), (v2), (v3), (v4), (v5), (v6), (v7), (v8))
#define int_to_int8(v) _mm256_set1_epi32(v)
#define make_int8(v1, v2, v3, v4, v5, v6, v7, v8) _mm256_set_epi32((v1), (v2), (v3), (v4), (v5), (v6), (v7), (v8))
#define make_int8_reverse(v1, v2, v3, v4, v5, v6, v7, v8) _mm256_setr_epi32((v1), (v2), (v3), (v4), (v5), (v6), (v7), (v8))
    
//Arithmetic
#define fmadd(a, b, c)        _mm256_fmadd_ps((a), (b), (c))  // a * b + c
#define fmsub(a, b, c)        _mm256_fmsub_ps((a), (b), (c))  // a * b - c
#define sqrt(val)             _mm256_sqrt_ps(val)
#define mul(a, b)             _mm256_mul_ps((a), (b))
#define add(a, b)             _mm256_add_ps((a), (b))
#define add_int(a, b)         _mm256_add_epi32((a), (b))
#define sub(a, b)             _mm256_sub_ps((a), (b))
#define sub_int(a, b)         _mm256_sub_epi32((a), (b))    
#define div(a, b)             _mm256_div_ps((a), (b))
    
//Bitwise
#define bitwise_and(a, b)     _mm256_and_ps((a), (b))
#define bitwise_andnot(a, b)  _mm256_andnot_ps((a), (b))
#define bitwise_xor(a, b)     _mm256_xor_ps((a), (b)) 
#define bitwise_xor_int(a, b)  _mm256_xor_si256((a), (b)) 
#define bitwise_right_shift(a, b) _mm256_srlv_epi32(a, b)
#define bitwise_left_shift(a, b) _mm256_sllv_epi32(a, b)
    
// Rotate - unfortunately doesnt work on our processors - needs AVX 512
#define bitwise_rot_l_64(a, b) _mm256_rol_epi64(a, b)  
#define bitwise_rot_r_64(a, b) _mm256_ror_epi64(a, b)
    
//Logical
#define less_than(a, b)        _mm256_cmp_ps((a), (b), _CMP_LT_OS)
#define greater_than(a, b)     _mm256_cmp_ps((a), (b), _CMP_GT_OS)
    
//Helpers
#define signs(a)               (_mm256_movemask_ps(a) & 255)

#define to_mem(reg, mem)       _mm256_storeu_ps(mem, reg)
#define to_mem_int(reg, mem)   _mm256_storeu_si256(mem, reg)
    
// Permute
#define permute8(a, b) _mm256_permutevar8x32_epi32(a, b)
    
    
