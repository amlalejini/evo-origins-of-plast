#!/usr/bin/python2
import os, errno, math

def binary(num, length=8):
    """
    Given a base 10 number and a length, output the binary representation of
     the base 10 number with length amount of binary digits.
    """
    return format(num, '#0{}b'.format(length + 2))

def mkdir_p(path):
    """
    This is functionally equivalent to the mkdir -p [fname] bash command
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def shannon_diversity(cnts):
    """
    This function calculates the shannon diversity index given a list of values.
    Each index in cnts represents one 'type' (species, genotype, phenotype, etc).
    Each value in cnts represents the # of individuals of that 'type'.
    Summing cnts equals the population size.
    the length of cnts is the number of unique 'types' in the population.
    """
    h = 0
    for i in range(0, len(cnts)):
        pi = cnts[i] / float(sum(cnts)) # number of individuals of this type / total number of all individuals in sample
        h += -1 * (pi * math.log(pi))
    return h
