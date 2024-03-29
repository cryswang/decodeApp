#!/usr/bin/env python

import sys, re
import base64
import codecs
import urllib
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
from itertools import cycle

@Configuration()
class decodeCommand(StreamingCommand):
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

    def stream(self, events):
	#self.logger.debug('field: %s', self)
	for event in events:
	    if not self.field in event:
		pass
	    elif self.type_ == "base64":
		decrypt = self.b64(event[self.field])

	    elif self.type_ == "ascii":
		decrypt = self.ascii(event[self.field])
		
	    elif self.type_ == "octal":
		decrypt = self.octal(event[self.field])
	    
	    elif self.type_ == "url":
		decrypt = self.url(event[self.field])
	    
	    elif self.type_ == "rot13":
		decrypt = self.url(event[self.field])

	    elif self.type_ == "caesar":
		decrypt = self.caesar(event[self.field], self.key)
	    
	    elif self.type_ == "xor":
		decrypt = self.caesar(event[self.field], self.key)

	    else:
		raise ValueError('type not supported')

	    event['decrypted'] = decrypt
	    yield event
	return
	
if __name__ == "__main__":
    dispatch(decodeCommand, sys.argv, sys.stdin, sys.stdout, __name__)
