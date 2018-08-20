#!/usr/bin/env python

import sys, re
import base64
import codecs
from urlparse import urlparse
import splunklib.client as client
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
from itertools import cycle

@Configuration()
class decryptcommand(StreamingCommand):
    field = Option(name='field', require=True)
    type_ = Option(name='type', require=True)
    key = Option(name='key', require=False, default="0")
   # multi = Option(name='multi', require=False, default="False")

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

    def stream(events):
	for event in events:
	    if type_ == "base64":
		decrypt = b64(event[field])

	    elif type_ == "ascii":
		decrypt = ascii(event[field])
		
	    elif type_ == "octal":
		decrypt = octal(event[field])
	    
	    elif type_ == "url":
		decrypt = url(event[field])
	    
	    elif type_ == "rot13":
		decrypt = url(event[field])

	    elif type_ == "caesar":
		decrypt = caesar(event[field], key)
	    
	    elif type_ == "xor":
		decrypt = caesar(event[field], key)

	    else:
		raise ValueError('type not supported')

	    event['decrypted'] = decrypt
	    yield event
	return
	
if __name__ == "__main__":
    dispatch(DecryptCommand, sys.argv, sys.stdin, sys.stdout, __name__)
