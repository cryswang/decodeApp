#!/usr/bin/env python

import sys, re
import base64
import codecs
import urllib
#from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
from itertools import cycle

def xor(field, key):
	print(field)
	print(key)

	bitvalue = bytes(a ^ b for a, b in zip(field, cycle(key)))
	valueList = bitvalue.decode('utf-8')

	return valueList

def main():
	field = 'this is a test'
        key = b'1101'
	val = xor(field, key)
	
	print(val)

if __name__== "__main__":
	main()
