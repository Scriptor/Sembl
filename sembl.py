import re
from sembltypes import typeof, typify

strings = []

plus = lambda stack: stack.append(stack.pop() + stack.pop())
minus = lambda stack: stack.append(-stack.pop() + stack.pop())
mul = lambda stack: stack.append(stack.pop() * stack.pop())
div = lambda stack: stack.append(stack.pop(1) / stack.pop())

def do(stack):
	blocks[stack.pop()](stack)
	
words = {
	'+': (plus, ('number', 'number'), ('number',)),
	'-': (minus, ('number', 'number'), ('number',)),
	'*': (mul, ('number', 'number'), ('number',)),
	'/': (div, ('number', 'number'), ('number',)),
	'do': (do, ('block',), ())
}

blocks = {}

def block_start(saved_bytecodes, typecode):
	return Block()
	
def block_end(saved_bytecodes, typecode):
	block = saved_bytecodes.pop()
	blocks[block.id] = block
	saved_bytecodes[-1].append(block.id)
	typecode.append('block')
	return saved_bytecodes[-1]
	
hooks = {
	'{': block_start,
	'}': block_end,
}

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
	
def typecheck(tok, typecode):
	if words.has_key(tok):
		inputs = words[tok][1]
		products = words[tok][2]
		
		if len(inputs) > len(typecode):
			raise CompileError("%s tok expects %s items on stack, %s given" % (tok, len(inputs), len(typecode)))
		for i,expected_typ in enumerate(reversed(inputs)):
			if expected_typ != typecode[-1]:
				raise CompileError("%s expects %s for argument %s, got %s" % (tok, expected_typ, i, typecode[-1]))
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
	saved_bytecodes = []
	bytecode = []
	typecode = []
	
	for tok in toks:
		if tok == '{':
			saved_bytecodes.append(bytecode)
			bytecode = Block()
		elif tok == '}':
			blocks[bytecode.id] = bytecode
			saved_bytecodes[-1].append(bytecode.id)
			bytecode = saved_bytecodes.pop()
			typecode.append('block')
		else:
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

code = """
abc def +
"""
toks = lex(code)
try:
	bytecode = compile(toks)
except CompileError as err:
	print "   Compile error:\n\t %s\n" % err
else:
	print execute(bytecode)