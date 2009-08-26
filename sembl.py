import re
from sembltypes import typeof, typify

strings = []

plus = lambda stack: stack.pop() + stack.pop()

words = {
	'+': plus
}

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
	for tok in toks:
		bytecode.append(typify(tok))
	return bytecode
	
def execute(bytecode):
	stack = []
	for term in bytecode:
		if words.has_key(term):
			stack.append(words[term](stack))
		else:
			stack.append(term)
	return stack

code = """
	3 4 +
"""
toks = lex(code)
print execute(compile(toks))