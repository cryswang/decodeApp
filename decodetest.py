#!/usr/bin/env python

import sys, re
import base64
import codecs
import urllib
#from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
from itertools import cycle

def xor(field, key):	
	value = ''.join([chr(ord(a) ^ ord(b)) for a, b in zip(field, cycle(key))])	
	return value

def b64(field):
        value = base64.b64decode(field)
        return value

def ascii(field):
        value = ''.join(field).decode('ascii')
        return value

def octal(field):
        decoded = field.decode('unicode-escape')
        for octc in re.findall(r'\\(\d{3})', decoded):
        	decoded = decoded.replace(r'\%s' % octc, chr(int(octc, 8)))
        return decoded

def url(field):
        value = urllib.unquote(field).decode('utf8')
        return value

def rot13(field):
        value = ''.join(field)
        try:
        	value = codecs.decode(field, 'rot_13')
        except ValueError as error:
        	logger.error(error)
        	raise
        return value

def caesar(field, key):
        if(key > 26 or key <= 0):
        	raise ValueError("key value invalid: must be 1-26")
        key = -key
	print(key)
        value = ''
        for character in field:
        	if character.isalpha():
        	        num = ord(character)
        	        num += key
                	if character.isupper():
                		if num > ord('Z'):
                        		num -= 26
                        	elif num < ord('A'):
                        		num +=26
               		elif character.islower():
                   		if num > ord('z'):
                        		num -= 26
                    		elif num < ord('a'):
                        		num += 26
			value += chr(num)
                else:
                	value += character
        return value

def main():
	field = 'XFQ_TYRURCTQ\\'
        key = '1101 0101'
	val = xor(field, key)
	print(val)

	field = 'aGVyZSBpcyBzb21lIGRhdGE='
	val = b64(field) 
	print(val)

	field = '/%7Econnolly/'
	val = url(field)
	print(val)

	field = '\040\040\040\040\146\165\156\143\164\151\157\156'
	val = octal(field)
	print(val)

	field = 'vz uhatel :('
	val = rot13(field)
	print(val)

	field = 'Pm ol ohk HUFAOPUN ptwvyahua av zhf...'
	key = 0
	val = caesar(field, key)
	print(val)

if __name__== "__main__":
	main()
