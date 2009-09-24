import re
import pdb
import copy
from sembltypes import types, typeof, typify, isliteral, block

plus = lambda stack: stack.append(stack.pop() + stack.pop())
minus = lambda stack: stack.append(-stack.pop() + stack.pop())
mul = lambda stack: stack.append(stack.pop() * stack.pop())
div = lambda stack: stack.append(stack.pop(1) / stack.pop())
dup = lambda stack: stack.append(stack[-1])

bool_dict = {True: "True", False: "False"}

def do(stack):
	block = stack.pop()
	block(stack)
	
def string(stack):
	s = vm.strings[int(stack.pop())]
	stack.append(s)

def imprt(stack):
	fname = stack.pop() + '.sb'
	code = open(fname, 'r').read()
	main(code,stack)
	
def equals(stack):
	stack.append(bool_dict[stack.pop() == stack.pop()])
		
def ge(stack):
	stack.append(bool_dict[stack.pop(-2) > stack.pop()])
	
def le(stack):
	stack.append(bool_dict[stack.pop(-2) < stack.pop()])
	
def define(stack):
	stack.pop(-2)
	
def if_statement(stack):
	if stack.pop(-2) == "True":
		stack.pop()(stack)
	
def se(stack):
	def unempty(xs):
		new = []
		for x in xs:
			if len(x) > 0:
				new.append(x)
		return tuple(new)
	
	inputs, products = [tuple(x.strip().split(' ')) for x in stack.pop().split('->')]		
	inputs = unempty(inputs)
	products = unempty(products)
	block = stack.pop()
	decl = vm.words[block.id][1:]
	if (inputs, products) != decl:
		raise ExeError("Given stack effect of %s -> %s does not match actual effect of %s" % (inputs, products, decl))

	
class VirtualMachine(object):
	def __init__(self):
		self.strings = []
		self.words = {
			'+': (plus, ('number', 'number'), ('number',)),
			'-': (minus, ('number', 'number'), ('number',)),
			'*': (mul, ('number', 'number'), ('number',)),
			'/': (div, ('number', 'number'), ('number',)),
			
			'==': (equals, ('x', 'y'), ('string',)),
			'>': (ge, ('number', 'number'), ('string',)),
			'<':(le, ('number', 'number'), ('string',)),
			
			'if': (if_statement, ('string', 'block'), ()),
			'do': (do, ('block',), ()),
			'dup': (dup, ('x',), ('x', 'x')),
			'__string__': (string, ('number',), ('string',)),
			'def': (define, ('string', 'block'), ('block',)),
			'se': (se, ('block', 'string'), ('block',)),
			'import': (imprt, ('string',), ())
		}
	
	def lex(self, code):
		class Counter():
			def __init__(self, s):
				self.s = s
				self.count = -1

			def __call__(self, match):
				self.count += 1
				return self.s % self.count
				
		self.counter = Counter("%s __string__")
		string = re.compile(r'"(?:[^"\\]|\\.)*"')
		for m in string.finditer(code):
			self.strings.append(m.group(0)[1:-1])
		code = re.sub(r'\s+',' ',code).strip()
		code = re.sub(r'"(?:[^"\\]|\\.)*"', self.counter, code)
		return code.split(' ')
		
	# def compile(self, toks):
	# 	saved_bytecodes = []
	# 	bytecode = []
	# 	typecode = []
	# 	
	# 	for tok in toks:
	# 		if tok == '{':
	# 			saved_bytecodes.append(bytecode)
	# 			bytecode = Block()
	# 		elif tok == '}':
	# 			self.words[bytecode.id] = (bytecode,) + infer(bytecode.bytecode)
	# 			saved_bytecodes[-1].append(bytecode)
	# 			bytecode = saved_bytecodes.pop()
	# 			if isinstance(bytecode, list):
	# 				typecode.append('block')
	# 		else:
	# 			if tok == 'do':
	# 				typecode.pop()
	# 				tok = bytecode.pop()
	# 			elif tok == 'def':
	# 				name = self.strings[int(bytecode[-3])]
	# 				block = bytecode[-1]
	# 				self.words[name] = self.words[block.id]
	# 
	# 			if isinstance(bytecode, list):
	# 				typecheck(tok, typecode)
	# 			bytecode.append(typify(tok))
	# 	return bytecode
	
	def execute(self, bytecode, stack=[]):
		for term in bytecode:
			if self.words.has_key(term):
				self.words[term][0](stack)
			else:
				stack.append(term)
		return stack
	
class Compiler(object):
	
	def __init__(self, vm, toks):
		self.vm = vm
		bc = self.blockify(toks)
		bc = self.defy(bc)
		self.infer()
		bc = self.typecheck(bc)
		bc = self.typify(bc)
		self.bc = bc
		
	def blockify(self, toks):
		bytecode = []
		saved_bytecodes = []
		for tok in toks:
			if tok == '{':
				saved_bytecodes.append(bytecode)
				bytecode = Block()
			elif tok == '}':
				self.vm.words[bytecode.id] = (bytecode,)
				saved_bytecodes[-1].append(bytecode)
				bytecode = saved_bytecodes.pop()
			else:
				bytecode.append(tok)
				
		return bytecode
	
	def defy(self, toks):
		bytecode = []
		for tok in toks:
			if tok == 'def':
				name = self.vm.strings[int(bytecode[-3])] # Fetches number for string index
				block = bytecode[-1]
				self.vm.words[name] = self.vm.words[block.id]
			else:
				bytecode.append(tok)
				
		return bytecode
	
	def infer(self):
		for word in self.vm.words:
			decl = self.vm.words[word]
			if len(decl) == 1:
				self.vm.words[word] = decl + infer(decl[0].bytecode)
				
	def typecheck(self, toks):
		typecode = []
		for tok in toks:
			typecheck(tok, typecode)
		return toks
	
	def typify(self, toks):
		bytecode = []
		for tok in toks:
			if block(tok):
				bytecode.append(tok)
			else:
				bytecode.append(typify(tok))
		return bytecode
	
class Block(object):
	pointers = {}
	cur_id = -1
	
	@classmethod
	def next_id(cls):
		cls.cur_id += 1
		return cls.cur_id
	
	def __init__(self, parent=None):
		self.block = True
		self.parent = parent
		self.bytecode = []
		self.id = "__block%s__" % Block.next_id()
	
	def __call__(self, stack):
		vm.execute(self.bytecode, stack)
		
	def append(self,tok):
		self.bytecode.append(tok)
	
	def extend(self,toks):
		self.bytecode.extend(toks)
	
	def pop(self):
		return self.bytecode.pop()
	
	def __str__(self):
		return repr(self.bytecode)

class CompileError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

class ExeError(Exception):
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
		if vm.words.has_key(tok):
			decl = vm.words[tok][1:]
		elif block(tok):
			decl = ((), ('block',))
		else:
			decl = [[], [typeof(tok),]]
		new_inputs, _, type_vars = match_types(list(decl[0]), surplus, tok)
		inputs.extend(new_inputs)
		surplus.extend(decl[1])
		inputs = replace(type_vars, inputs)
		surplus = replace(type_vars, surplus)
	return (tuple(inputs), tuple(surplus))
	
def typecheck(tok, typecode):
	if vm.words.has_key(tok):
		inputs = list(vm.words[tok][1])
		products = list(vm.words[tok][2])
		
		if len(inputs) > len(typecode):
			raise CompileError("%s tok expects %s items on stack, %s given" % (tok, len(inputs), len(typecode)))
	
		match_types(inputs, typecode, tok)
		typecode.extend(products)
	else:
		typecode.append(typeof(tok))

vm = VirtualMachine()
def main(code, stack=[]):
	toks = vm.lex(code)
	try:
		bytecode = Compiler(vm, toks).bc
	except CompileError as err:
		print "   Compile error:\n\t %s\n" % err
	else:
		try:
			print vm.execute(bytecode)
		except ExeError as err:
			print "   Runtime error: \n\t %s\n" % err

if __name__ == "__main__":
	code = """
	"cubed" { 
		dup dup * * 
	} def "number -> number" se

	"squared" {
		dup *
	} def "number -> number" se

	"power-of-four" {
		squared squared
	} def "number -> number" se
	
	2 power-of-four
	
	"stf" {
		{ "abc" }
	} def
	"""
	main(code)