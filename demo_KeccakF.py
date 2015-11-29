#! /usr/bin/pythonw
# Algorithm Name: Keccak
# Authors: Guido Bertoni, Joan Daemen, Michaël Peeters and Gilles Van Assche
# Implementation by Renaud Bauvin, STMicroelectronics
#
# This code, originally by Renaud Bauvin, is hereby put in the public domain.
# It is given as is, without any guarantee.
# 
# For more information, feedback or questions, please refer to our website:
# http://keccak.noekeon.org/

import Keccak

A=[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

myKeccak=Keccak.Keccak(1600)

myKeccak.KeccakF(A, True)

myKeccak.printState(A,'Final result')
