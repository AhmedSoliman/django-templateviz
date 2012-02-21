import os, sys, re
import logging
import pydot
from ds import TemplateGraph

logger = logging.getLogger("TemplateViz")

patterns = ((True, "extended by", re.compile(r"""\{%\s+extends\s+["'](?P<file>.+)["']\s+%\}""")),
			(False, "includes", re.compile(r"""\{%\s+include\s+["'](?P<file>[a-zA-Z0-9\-_/\.]+)["']\s+.*%\}""")))

js_pattern = re.compile(r"""\<script\s+.*src="(?P<file>.*)"\s*.*>""")
static_pattern = re.compile(r"""\{\{\s*STATIC_URL\s*\}\}""")
		
def plot_relation_graph(path, graph, template_dirs, template_graph):
	def find_template_in_dirs(base, template_relpath, template_dirs):
		for template_dir in template_dirs:
			if os.path.isfile(os.path.join(base, template_dir, template_relpath)):
				return template_dir
		return None


	def update_graph(base, graph, dirname, f, template_dirs):
		fname = os.path.relpath(f, base)
		with open(f, 'r') as file:
			data = file.read()
			# import ipdb; ipdb.set_trace()
			for forward_direction, message, pattern in patterns:
				for match in pattern.finditer(data):
					node = pydot.Node(fname)				
					target =  match.groupdict()['file']
					#resolving template dir
					template_base = find_template_in_dirs(base, target, template_dirs)
					if template_base is None:
						logging.error("Couldn't locate the file %s mentioned in %s", target, fname)
						template_base = ""

					target = os.path.join(template_base, target)
					tnode = pydot.Node(target)
					if forward_direction:
						tnode.set_style("filled")
						tnode.set_fillcolor("green")
						edge = pydot.Edge(target, fname)
						extract_javascript_includes(os.path.join(base, fname))
						template_graph.add_child_template(target, fname, extract_javascript_includes(os.path.join(base, fname)))
					else:
						edge = pydot.Edge(fname, target)
						template_graph.add_child_template(fname, target, extract_javascript_includes(os.path.join(base, target)))
						edge.set_color("red")


					if template_base == "":
						tnode.set_style("filled")
						tnode.set_fillcolor("red")
					
					graph.add_node(node)
					graph.add_node(tnode)
					edge.set_label(message)
					graph.add_edge(edge)

	def scan_template(graph, dirname, fnames):
		for f in fnames:
			if f.endswith('.html'):			
				f = os.path.join(dirname, f)
				#scan relation
				update_graph(path, graph, dirname, f, template_dirs)

	os.path.walk(path, scan_template, graph)

def extract_javascript_includes(template):
	'''
		returns a list of javascript included in this file
	'''
	if not os.path.isfile(template):
		return []
	f = open(template, 'r')
	data = f.read()
	res = []
	for match in js_pattern.finditer(data):
		js_file = match.groupdict()['file']
		m = static_pattern.match(js_file)
		if m:
			js_file = js_file[m.end():]
		res.append(js_file)
	return res

def get_template_dirs(base, path):
	dirs = []
	def is_template(arg, dirname, fnames):
		if os.path.basename(dirname).startswith('.'):
			fnames[0:] = []
			return

		if os.path.basename(dirname) != "templates":
			return
		dirs.append(os.path.relpath(dirname, base))

	os.path.walk(path, is_template, None)
	return dirs

def main():
	if len(sys.argv) <= 1:
		print("Cannot operate without an entry path")
		return
	
	logging.basicConfig(level=logging.INFO)
	template_graph = TemplateGraph()
	logger.debug("Operating on directory %s", sys.argv[1])
	graph = pydot.Dot('relgraph', graph_type='digraph')
	# graph.set_size("7.5, 10")
	template_dirs = get_template_dirs(sys.argv[1], sys.argv[1])
	plot_relation_graph(sys.argv[1], graph, template_dirs, template_graph)
	print template_graph.get_children_rec('templates/_dark_base.html')
	logger.info("Saving to %s", "out.dot")
	f = open("out.dot", "w+")
	f.write(graph.to_string())
	f.close()

	

if __name__ == "__main__":
	main()