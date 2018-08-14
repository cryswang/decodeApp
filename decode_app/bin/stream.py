#!/usr/bin/env python

import sys, re
import base64
import codecs
from urllib.parse import unquote
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
from itertools import cycle

@Configuration()
class DecryptCommand(StreamingCommand):
    field = Option(name='field', require=True)
    type_ = Option(name='type', require=True)
    key = Option(name='key', require=False, default="0")
   # multi = Option(name='multi', require=False, default="False")

    def b64(self, field):
	string_value = "".join(field)
	value = base64.64decode(string_value)
	return value

    def ascii(self, field):
	value = ''.join(field).decode('ascii')
	return value

    def octal(self, field):
	decoded = field.encode('utf-8')
	for octc in re.findall(r'\\(\d{3})', decoded):
	    decoded = decoded.replace(r'\%s' % octc, chr(int(octc, 8)))    
	return decoded.decode('utf8')
    
    def url(self, field):
	value = ''.join(field)
	value = unquote(value)
	return value

    def rot13(self, field):
	value = ''.join(field)
	try:
	    value = codecs.decode(field, 'rot_13')
	except ValueError as error:
	    logger.error(error)
	    raise
	return value

    def caesar(self, field, key):
	if(key > 26 or key < 0):
	    raise ValueError("key value invalid: must be 1-26")
	key = -key
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
		value = value.join(chr(num))
	    else:
		value = value.join(character)
	return value

    def xor(self, field, key, multi):
	value = ''
#	if multi:
#create a tuple of the different keys by splitting the key value, delineated by spaces (presumably). then cycle through that tuple if allowed by python
#	else:
	    bitvalue = bytes(a ^ b for a, b in zip(field, cycle(key)))
	    #value = value.join(map(chr, bitvalue))
	print(bitvalue)
	return bitvalue

    def stream(self, events):
	for event in events:
	    if type_ == "base64":
		decrypt = self.b64(event[field]

	    elif type_ == "ascii":
		decrypt = self.ascii(event[field])
		
	    elif type_ == "octal":
		decrypt = self.octal(event[field])
	    
	    elif type_ == "url":
		decrypt = self.url(event[field])
	    
	    elif type_ == "rot13":
		decrypt = self.url(event[field])

	    elif type_ == "caesar":
		decrypt = self.caesar(event[field], key)
	    
	    elif type_ == "xor":
		decrypt = self.caesar(event[field], key, multi)

	    else:
		raise ValueError('type not supported')

	    event['decrypted'] = decrypt
	    yield event
	return
	
if __name__ == "__main__":
    dispatch(DecryptCommand, sys.argv, sys.stdin, sys.stdout, __name__)
