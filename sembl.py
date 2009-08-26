import re
strings = []

def lex(code):
	class Counter():
		def __init__(self, s):
			self.s = s
			self.count = -1

		def __call__(self, match):
			self.count += 1
			return self.s % self.count

	global strings
	string = re.compile(r'"(?:[^"\\]|\\.)*"')
	strings = string.findall(code)
	code = re.sub(r'\s+',' ',code).strip()
	code = re.sub(r'"(?:[^"\\]|\\.)*"', Counter("%s __string__"), code)
	return code.split(' ')
	
def compile(toks):
	bytecode = []
	for x in toks:
		bytecode.append(x)
	
code = """
	3 4 +
"""
print lex(code)