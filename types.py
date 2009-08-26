import re
pats = {
	'int': r"^[-+]?[0-9]+$",
	'float': r"^[-+]?[0-9]*\.?[0-9]+$",
	'word': r'^[^"].+[^"]$'
}

def number(tok):
	if re.match(pats['int'], tok):
		return int(tok)
	elif re.match(pats['float'], tok):
		return float(tok)
	else:
		return False

def word(tok):
	if re.match(pats['word'], tok):
		return tok
	return False

type_funcs = (
	('number', number),
	('string', string),
	('name', name)
)

def typeof(tok):
	for name, func in type_funcs:
		if func(tok) is not False:
			return name
	return "NOTYPE"