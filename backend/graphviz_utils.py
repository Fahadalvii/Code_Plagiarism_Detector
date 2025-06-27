try:
    from graphviz import Digraph
except ImportError:
    print("Warning: Graphviz not installed. Install with: pip install graphviz")
    Digraph = None

def ast_to_graphviz(ast, graph_name="AST"):
    """Convert AST to Graphviz DOT format"""
    if Digraph is None:
        raise ImportError("Graphviz is not installed")
    
    if ast is None:
        dot = Digraph(name=graph_name, format='svg')
        dot.node('empty', 'Empty AST')
        return dot
    
    dot = Digraph(name=graph_name, format='svg')
    dot.attr('node', shape='box')
    
    def add_nodes_edges(node, parent_id=None):
        if node is None:
            return
        
        # Create node ID
        node_id = str(id(node))
        
        # Create node label
        label = str(node.type) if hasattr(node, 'type') else 'Unknown'
        if hasattr(node, 'value') and node.value is not None:
            label += f"\n{node.value}"
        dot.node(node_id, label)
        
        # Connect to parent if exists
        if parent_id is not None:
            dot.edge(parent_id, node_id)
        
        # Add children
        if hasattr(node, 'children'):
            for child in node.children:
                add_nodes_edges(child, node_id)
    
    add_nodes_edges(ast)
    return dot

def ast_to_dot(ast, graph_name="AST"):
    """Convert AST to DOT format string"""
    try:
        dot = ast_to_graphviz(ast, graph_name)
        return dot.source
    except (ImportError, AttributeError) as e:
        return f"// Error generating DOT: {e}"