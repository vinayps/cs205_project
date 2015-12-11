# CS205 Final Project
Parallel implementation of SHA3 - Keccakf(400)

## Introduction 
The goal of this project is to develop a parallel implementation of the SHA3-Keccak algorithm. We have taken two approaches to doing this - multi-core/multi-thread CPU parallelism and instruction-level parallelism (SIMD - AVX/AVX2). By combining both approaches hierarchically, we get speed ups of between 3x to 4x depending on the size of the input message (larger the message, greater the speedup). 
We have specifically implemented this for Keccak-f(400). 

## Usage 
1) To apply SHA3-Keccakf-400 on a message, one can directly use driver.py. This program takes a number of command line inputs - 

driver.py -i <inputfile> -h 3 -d 4 -o 512 

driver.py -m <inputmessage> -h 3 -d 4 -o 512

  Argument details - 
- -i: input file
- -m: input message
- -h: height of tree for tree hashing - this argument influences the speed up offered by tree hashing and an optimal value depends on the size of the input message; default values are provided for this argument
- -d: degree of tree for tree hashing - this argument influences the speed up offered by tree hashing and an optimal value depends on the size of the input message; default values are provided for this argument
- -o: length of output message digest in bits - for the typical SHA3-512, this argument will take the value 512; default value for this argument is 512 bits

2) To study the performance improvements provided by our implementation, on can run performance_testing.py. This program takes the same inputs as the driver.py program as command line arguments. It hashes the input message and provides the output and running time using all four possibilities - 
- Naive serial
- Only Tree Hashing
- Only AVX
- Tree Hashing + AVX

3) To test the AVX implementation, one can run AVX_test.py. This program does not require any inputs from the user. However, it does depend on the files present in the Test_files directory. In this program, we hash the input message using our AVX approach and a different independently implemented serial approach and compare the results for a wide range of test data to ensure accuracy.

We couldn't find similar reference standards for the tree hashing approach and havent built a testing harness for the same. However, as a sanity check, the output of the tree hashing algorithm for zero height is identical to the non-tree hashing approach. 

## References - 
The base line code in this package essentially consists of two serial implementations of Keccakf. These were derived from https://github.com/gvanas/KeccakCodePackage (keccak.noekeon.org) who had very kindly licensed this to the public domain. These were built on the standards specified in the FIPS 202 (SHA-3) document issued by csrc.nist.gov - http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf

More information can be found on Keccak in general at keccak.noekeon.org and on the FIPS 202 standard at csrc.nist.gov


