# CS205 Final Project
Parallel implementation of SHA3 - Keccakf(400)

## Introduction 
The goal of this project is to develop a parallel implementation of the SHA3-Keccak algorithm. We have taken two approaches to doing this - multi-core/multi-thread CPU parallelism and instruction-level parallelism (SIMD - AVX/AVX2). By combining both approaches hierarchically, we get speed ups of between 3x to 4x depending on the size of the input message (larger the message, greater the speedup). 
We have specifically implemented this for Keccak-f(400). 

## Content
1. Code - 
  1. AVX.h - AVX functions to be used are defined
  2. AVX.pxd - AVX functions are exposed to cython
  3. AVX_test.py - Test harness to test AVX implementation
  4. CompactFIPS202.py - Original serial implementation for Keccakf(1600) (derived from references)
  5. Keccak.py - Keccak class definitions for second independent serial implementation (derived from references)
  6. Keccak_Helper.pyx - Helper functions in cython implementing actual AVX operations
  7. Keccakf400_AVX_FIPS202.py - Implementation of Keccakf(400) that leverages AVX through cython
  8. avxintrin-emu.h - header with exhaustive set of AVX intrinsics
  9. driver.py - primary script; tree hashing functions are also implemented here
  10. performance_testing.py - primary performance testing script; all testing possibilities are enumerated; tree hashing functions are also implemented here
  11. set_compiler.py - utility script to set the right compiler for various environments (especially required for Mac users)
  12. timer.py - utility wrapper that makes timer functions easily accessible
2. Test_files 
  1. *.bin - various synthetically generated binary data files used in performance testing; generated using: head -c 1024 \</dev/urandom \>myfile
  2. Short* - hexadecimal strings of various lengths used by AVX_test to check for accuracy of the AVX implementation

## Usage 
1) To apply SHA3-Keccakf-400 on a message, one can directly use **driver.py** This program takes a number of command line inputs - 

driver.py -i [inputfile] -h 3 -d 4 -o 512 

driver.py -m [inputmessage] -h 3 -d 4 -o 512

  Argument details - 
- -i: input file
- -m: input message
- -h: height of tree for tree hashing - this argument influences the speed up offered by tree hashing and an optimal value depends on the size of the input message; default values are provided for this argument
- -d: degree of tree for tree hashing - this argument influences the speed up offered by tree hashing and an optimal value depends on the size of the input message; default values are provided for this argument
- -o: length of output message digest in bits - for the typical SHA3-512, this argument will take the value 512; default value for this argument is 512 bits

2) To study the performance improvements provided by our implementation, on can run **performance_testing.py** This program takes the same inputs as the **driver.py** program as command line arguments. It hashes the input message and provides the output and running time using all four possibilities - 
- Naive serial
- Only Tree Hashing
- Only AVX
- Tree Hashing + AVX

3) To test the AVX implementation, one can run **AVX_test.py** This program does not require any inputs from the user. However, it does depend on the files present in the Test_files directory. In this program, we hash the input message using our AVX approach and a different independently implemented serial approach and compare the results for a wide range of test data to ensure accuracy.

We couldn't find similar reference standards for the tree hashing approach and havent built a testing harness for the same. However, as a sanity check, the output of the tree hashing algorithm for zero height is identical to the non-tree hashing approach. 

## References - 
The base line code in this package essentially consists of two serial implementations of Keccakf. These were derived from https://github.com/gvanas/KeccakCodePackage (keccak.noekeon.org) who had very kindly licensed this to the public domain. These were built on the standards specified in the FIPS 202 (SHA-3) document issued by csrc.nist.gov - http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf

More information can be found on Keccak in general at keccak.noekeon.org and on the FIPS 202 standard at csrc.nist.gov


