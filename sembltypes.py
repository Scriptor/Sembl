import re
import pdb

pats = {
	'int': r"^[-+]?[0-9]+$",
	'float': r"^[-+]?[0-9]*\.?[0-9]+$",
	'block': r"^__block[0-9]+__$",
	'word': r'^.+$'
}

def number(tok):
	if isinstance(tok, float) or re.match(pats['float'], tok):
		return float(tok)
	return False

def block(tok):
	if hasattr(tok, 'block'):
		return tok
	return False

def null(tok):
	if tok == "null":
		return tok
	return False

def word(tok):
	if re.match(pats['word'], tok):
		return tok
	return False

def string(tok):
	return tok
	
type_funcs = (	
	('block', block),
	('number', number),
	('null', null),
	('string', string),
	('word', word)
)

types = [x[0] for x in type_funcs]

def isliteral(tok):
	return not block(tok) and not word(tok)
	
def typify(tok):
	for name, func in type_funcs:
		if func(tok) is not False:
			return func(tok)

def typeof(tok):
	for name, func in type_funcs:
		if func(tok) is not False:
			return name
	return "NOTYPE"