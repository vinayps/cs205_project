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
  1. *.bin - various synthetically generated binary data files used in performance testing; generated using: 
``` head -c 1024 </dev/urandom>myfile ```
  2. Short* - hexadecimal strings of various lengths used by AVX_test to check for accuracy of the AVX implementation

## Usage 
1) To apply SHA3-Keccakf-400 on a message, one can directly use **driver.py** This program takes a number of command line inputs - 
```
driver.py -i <inputfile> -h 3 -d 4 -o 512 
driver.py -m <inputmessage> -h 3 -d 4 -o 512
```

  Argument details - 
- -i: input file
- -m: input message
- -h: height of tree for tree hashing - this argument influences the speed up offered by tree hashing and an optimal value depends on the size of the input message; default values are provided for this argument
- -d: degree of tree for tree hashing - this argument influences the speed up offered by tree hashing and an optimal value depends on the size of the input message; default values are provided for this argument
- -o: length of output message digest in bits - for the typical SHA3-512, this argument will take the value 512; default value for this argument is 512 bits

```
user$ python driver.py -i ../Test_files/100KB.bin -h 3 -d 4 -o 512
Compiling with /usr/local/bin/clang-omp
Final output (tree hashing + AVX) - SHA3 - Keccak400
=================
30A0A704CE528751D3379B84A1AD2C1B27B61B40F06317ECC8342D392922A6B214C2DFDDC9C3E5C995CF0E11B4AAFB1785EBA9AB85686FAA86136E7D6C68DE59 512
```

2) To study the performance improvements provided by our implementation, on can run **performance_testing.py** This program takes the same inputs as the **driver.py** program as command line arguments. It hashes the input message and provides the output and running time using all four possibilities - 
- Serial
- AVX only
- Tree hashing only
- Tree hashing + AVX

```
user$ python performance_testing.py -i ../Test_files/100KB.bin -h 3 -d 4 -o 512
Compiling with /usr/local/bin/clang-omp
Final output: SHA3 - Keccak400
=================
Serial
6FF18BF2333448B36CCEDF815766100EF6C2BDA08F72A3E24AD22E05C4B0159DC12E8B988F64FAB2F34AC3D07C981CEF43DF7E9CA93EC5AF81653ECEDC00AB1A 512
time:  8.02229189873
AVX only
6FF18BF2333448B36CCEDF815766100EF6C2BDA08F72A3E24AD22E05C4B0159DC12E8B988F64FAB2F34AC3D07C981CEF43DF7E9CA93EC5AF81653ECEDC00AB1A 512
time:  4.54654216766
Tree hashing only
30A0A704CE528751D3379B84A1AD2C1B27B61B40F06317ECC8342D392922A6B214C2DFDDC9C3E5C995CF0E11B4AAFB1785EBA9AB85686FAA86136E7D6C68DE59 512
time:  4.92956495285
Tree hashing + AVX
30A0A704CE528751D3379B84A1AD2C1B27B61B40F06317ECC8342D392922A6B214C2DFDDC9C3E5C995CF0E11B4AAFB1785EBA9AB85686FAA86136E7D6C68DE59 512
time:  2.82117891312
```

3) To test the AVX implementation, one can run **AVX_test.py** This program does not require any inputs from the user. However, it does depend on the files present in the Test_files directory. In this program, we hash the input message using our AVX approach and a different independently implemented serial approach and compare the results for a wide range of test data to ensure accuracy.

We couldn't find similar reference standards for the tree hashing approach and havent built a testing harness for the same. However, as a sanity check, the output of the tree hashing algorithm for zero height is identical to the non-tree hashing approach. 

```
user$ python AVX_test.py
Compiling with /usr/local/bin/clang-omp
Processing file: ShortMsgKAT_SHAKE128.txt...
Keccak[r=336, c=64] with '1111' suffix
OK

Processing file: ShortMsgKAT_SHAKE256.txt...
Keccak[r=272, c=128] with '1111' suffix
OK

Processing file: ShortMsgKAT_SHA3-224.txt...
Keccak[r=288, c=112] with '01' suffix
OK

Processing file: ShortMsgKAT_SHA3-256.txt...
Keccak[r=272, c=128] with '01' suffix
OK

Processing file: ShortMsgKAT_SHA3-384.txt...
Keccak[r=208, c=192] with '01' suffix
OK

Processing file: ShortMsgKAT_SHA3-512.txt...
Keccak[r=144, c=256] with '01' suffix
OK

Total time taken (seconds) = 33.1799860001
```

## References - 
1. The base line code in this package essentially consists of two serial implementations of Keccak-f. These were derived from https://github.com/gvanas/KeccakCodePackage (keccak.noekeon.org) who had very kindly licensed this to the public domain. These were built on the standards specified in the FIPS 202 (SHA-3) document issued by csrc.nist.gov - http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf and http://csrc.nist.gov/publications/PubsFIPS.html
2. Introduction to Keccak - http://www.drdobbs.com/security/keccak-the-new-sha-3-encryption-standard/240154037?pgno=1
3. AVX/AVX2 Intrinsics
  1. https://software.intel.com/sites/landingpage/IntrinsicsGuide/#
  2. https://software.intel.com/en-us/node/513925
4. AVX tutorial - http://www.codeproject.com/Articles/874396/Crunching-Numbers-with-AVX-and-AVX
5. Sponge functions - http://sponge.noekeon.org/
6. Tree Hashing - Bertoni, Guido, et al. "Sakura: a flexible coding for tree hashing." Applied Cryptography and Network Security. Springer International Publishing, 2014
7. Tree Hashing - Lowden, Jason Michael. "Analysis of KECCAK Tree Hashing on GPU Architectures." (2014).
8. Tree Hashing - Cayrel, Pierre-Louis, Gerhard Hoffmann, and Michael Schneider. "GPU implementation of the Keccak Hash function family." Information Security and Assurance. Springer Berlin Heidelberg, 2011. 33-42.


