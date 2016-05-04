#!/usr/bin/python2
import os, errno

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
