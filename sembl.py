import re
import pdb
from sembltypes import types, typeof, typify, isliteral, block

strings = []

plus = lambda stack: stack.append(stack.pop() + stack.pop())
minus = lambda stack: stack.append(-stack.pop() + stack.pop())
mul = lambda stack: stack.append(stack.pop() * stack.pop())
div = lambda stack: stack.append(stack.pop(1) / stack.pop())
dup = lambda stack: stack.append(stack[-1])

def do(stack):
	blocks[stack.pop()][0](stack)
	
def string(stack):
	s = strings[int(stack.pop())]
	stack.append(s)
	
def define(stack):
	block, name = stack.pop(), stack.pop()
	words[name] = words[block]
	
words = {
	'+': (plus, ('number', 'number'), ('number',)),
	'-': (minus, ('number', 'number'), ('number',)),
	'*': (mul, ('number', 'number'), ('number',)),
	'/': (div, ('number', 'number'), ('number',)),
	'do': (do, ('block',), ()),
	'dup': (dup, ('x',), ('x', 'x')),
	'__string__': (string, ('number',), ('string',)),
	'def': (define, ('string', 'block'), ('block'))
}

blocks = {}

class Block(object):
	pointers = {}
	cur_id = -1
	
	@classmethod
	def next_id(cls):
		cls.cur_id += 1
		return cls.cur_id
	
	def __init__(self, parent=None):
		self.parent = parent
		self.bytecode = []
		self.id = "__block%s__" % Block.next_id()
	
	def __call__(self, stack):
		execute(self.bytecode, stack)
		
	def append(self,tok):
		self.bytecode.append(tok)
	
	def extend(self,toks):
		self.bytecode.extend(toks)
	
	def __str__(self):
		return repr(self.bytecode)

class CompileError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

def replace(type_vars, xs):
	for i,x in enumerate(xs):
		for var in type_vars:
			if x == var:				
				typ = type_vars[var]
				xs[i] = typ
	return xs	
	
def match_types(expected_types, given_types, tok="block"):
	type_vars = {}
	for i, expected in enumerate(reversed(expected_types)):
		if len(given_types) == 0:
			break
		expected_types.pop()
		given = given_types.pop()
		if expected != given:
			if expected not in types:
				if not type_vars.has_key(expected) or type_vars[expected] == given:
					type_vars[expected] = given
					continue
			if given not in types:
				if not type_vars.has_key(given) or type_vars[given] == expected:
					type_vars[given] = expected
					continue
			raise CompileError("%s expects a %s for input %s, got %s" % (tok, expected, i, given))
	
	return expected_types, given_types, type_vars

def infer(bytecode):
	inputs = []
	surplus = []
	type_vars = {}
	
	for tok in bytecode:
		if words.has_key(tok):
			decl = words[tok][1:]
		elif block(tok):
			decl = blocks[block][1:]
		else:
			decl = [[], [typeof(tok),]]
		new_inputs, _, type_vars = match_types(list(decl[0]), surplus, tok)
		inputs.extend(new_inputs)
		surplus.extend(decl[1])
		inputs = replace(type_vars, inputs)
		surplus = replace(type_vars, surplus)
	return (tuple(inputs), tuple(surplus))
	
def typecheck(tok, typecode):
	if words.has_key(tok):
		inputs = list(words[tok][1])
		products = list(words[tok][2])
		
		if len(inputs) > len(typecode):
			raise CompileError("%s tok expects %s items on stack, %s given" % (tok, len(inputs), len(typecode)))
	
		match_types(inputs, typecode, tok)
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
	for m in string.finditer(code):
		strings.append(m.group(0)[1:-1])
	code = re.sub(r'\s+',' ',code).strip()
	code = re.sub(r'"(?:[^"\\]|\\.)*"', Counter("%s __string__"), code)
	return code.split(' ')
	
def compile(toks):
	saved_bytecodes = []
	bytecode = []
	typecode = []
	
	for tok in toks:
		if tok == '{':
			saved_bytecodes.append(bytecode)
			bytecode = Block()
		elif tok == '}':
			words[bytecode.id] = (bytecode,) + infer(bytecode.bytecode)
			saved_bytecodes[-1].append(bytecode.id)
			bytecode = saved_bytecodes.pop()
			typecode.append('block')
		else:
			if tok == 'do':
				typecode.pop()
				tok = bytecode.pop()
			if isinstance(bytecode, list):
				typecheck(tok, typecode)
			bytecode.append(typify(tok))
	return bytecode
	
def execute(bytecode, stack=[]):
	for term in bytecode:
		if words.has_key(term):
			words[term][0](stack)
		else:
			stack.append(term)
	return stack

if __name__ == "__main__":
	code = """
	2 { dup * }
	"""
	toks = lex(code)
	try:
		bytecode = compile(toks)
	except CompileError as err:
		print "   Compile error:\n\t %s\n" % err
	else:
		print execute(bytecode)