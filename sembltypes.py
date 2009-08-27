import re
pats = {
	'int': r"^[-+]?[0-9]+$",
	'float': r"^[-+]?[0-9]*\.?[0-9]+$",
	'word': r'^.+$'
}

def number(tok):
	if re.match(pats['float'], tok):
		return float(tok)
	else:
		return False

def word(tok):
	if re.match(pats['word'], tok):
		return tok
	return False

def null(tok):
	if tok == "null":
		return tok
	return False

type_funcs = (
	('number', number),
	('null', null),
	('word', word)
)

def typify(tok):
	for name, func in type_funcs:
		if func(tok) is not False:
			return func(tok)

def typeof(tok):
	for name, func in type_funcs:
		if func(tok) is not False:
			return name
	return "NOTYPE"