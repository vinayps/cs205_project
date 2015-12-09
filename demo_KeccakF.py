# -*- coding: utf-8 -*-
# The Keccak sponge function, designed by Guido Bertoni, Joan Daemen,
# Michaël Peeters and Gilles Van Assche. For more information, feedback or
# questions, please refer to our website: http://keccak.noekeon.org/
# 
# Implementation by Renaud Bauvin,
# hereby denoted as "the implementer".
# 
# To the extent possible under law, the implementer has waived all copyright
# and related or neighboring rights to the source code in this file.
# http://creativecommons.org/publicdomain/zero/1.0/

import Keccak
import CompactFIPS202_mod

import sys
import os.path
sys.path.append(os.path.join('..', 'util'))
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
                                              '-mavx2',
                                              ], #'-mavx512f'
                          extra_link_args=['-fopenmp'])] 
pyximport.install(reload_support=True, setup_args={"include_dirs": [np.get_include(), os.curdir], 'ext_modules': ext_modules})
import Keccak_Helper as kh
reload(kh)

A=[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

myKeccak=Keccak.Keccak(400)

myKeccak.KeccakF(A, True)

myKeccak.printState(A,'Final result')

# Use as a harness to test the modified Keccak 400 algorithm
B=[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

B = CompactFIPS202_mod.KeccakF400onLanes(B)

print B

