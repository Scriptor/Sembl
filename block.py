from sembl import execute

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