class TemplateGraph(object):
	def __init__(self):
		# parent -> children_list
		self._node_list = {} #nodes cache
		self._nodes = [] #top level nodes
	
	def add_child_template(self, parent, child, contents):
		'''
			@param contents: a list with all the (javascript/css/etc) contents in the template
		'''
		if parent not in self._node_list:
			self._node_list[parent] = GraphNode(child, contents, self)
		# self._node_list[parent].append((child, contents))
		node = self.find_node(parent)
		if node: node.add_child(self._node_list[parent])
	
	def find_node(self, node_name):
		results = []
		for node in self._nodes:
			if node.name == node_name:
				return node
		
		return results

	def get_all_nodes(self):
		return self._node_list.keys()

	def get_node(self, node_name):
		return self._node_list[node_name]
			
	def get_children_rec(self, node):
		if node not in self._node_list:
			return {node: None}
		else:
			return {node: [self.get_children_rec(n) for n, _ in self._node_list[node]]}
	
	def get_duplicates(self, template):		


class GraphNode(object):
	def __init__(self, name, js, graph):
		'''
			@param name: template name
			@param js: list of javascript files
		'''
		self.name = name
		self._js = js
		self._parents = set()
		self._children = set()

	def __hash__(self):
		return self.name

	def __str__(self):
		return self._name

	def _get_parent(self, node_name):
		for node in self._parents:
			if node.name == node_name:
				return node

	def get_js(self):
		return self._js

	def add_child(self, node):
		node.add_parent(self)
		self._children.add(node)
	
	def add_parent(self, node):
		self._parents.add(node)
	
	def _get_all_parent_js(self, parent_name):
		if not self._get_parent(parent_name):
			return set()
		else:
			return set(self._js) + self._parent._get_all_parent_js(parent_name)
	
	def _print_duplicates_rec(self, parent, js):
		intersection = self._js.intersect(js)
		for js in self.

	def print_duplicates(self):
		for node in self._children:
			node.print_duplicates_rec(self._js)