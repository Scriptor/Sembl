import re
from sembltypes import typeof, typify

strings = []

plus = lambda stack: stack.pop() + stack.pop()
minus = lambda stack: -stack.pop() + stack.pop()
mul = lambda stack: stack.pop() * stack.pop()
div = lambda stack: stack.pop(1) / stack.pop()

words = {
	'+': (plus, ('number', 'number'), ('number',)),
	'-': (minus, ('number', 'number'), ('number',)),
	'*': (mul, ('number', 'number'), ('number',)),
	'/': (div, ('number', 'number'), ('number',)),
}

class CompileError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg
	
def typecheck(tok, typecode):
	if words.has_key(tok):
		inputs = words[tok][1]
		products = words[tok][2]
		for i,expected_typ in enumerate(reversed(inputs)):
			if not len(typecode):
				typecode.append("null")

			if expected_typ != typecode[-1]:
				raise CompileError("Expecting %s, got %s" % (expected_typ, typecode[-1]))
			else:
				typecode.pop()
		typecode.extend(products)
			
	else:
		typecode.append(typeof(tok))
	
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
	typecode = []
	
	for tok in toks:
		typecheck(tok, typecode)
		bytecode.append(typify(tok))
	return bytecode
	
def execute(bytecode):
	stack = []
	for term in bytecode:
		if words.has_key(term):
			stack.append(words[term][0](stack))
		else:
			stack.append(term)
	return stack

code = """
	2 3 +
	3 *
"""
toks = lex(code)
try:
	bytecode = compile(toks)
except CompileError as err:
	print "   Compile error:\n\t %s\n" % err
else:
	print execute(compile(toks))