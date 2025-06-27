class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.current_scope = "global"
        self.errors = []
        self.warnings = []

    def analyze(self, node):
        if node is None:
            return
            
        if hasattr(node, 'type'):
            if node.type == 'program':
                for child in node.children:
                    self.analyze(child)
            elif node.type == 'statement_list':
                for child in node.children:
                    self.analyze(child)
            elif node.type == 'declaration':
                if len(node.children) >= 2:
                    var_type = node.children[0].value
                    var_name = node.children[1].value
                    if var_name in self.symbol_table:
                        self.errors.append(f"Redeclaration of variable '{var_name}'")
                    else:
                        self.symbol_table[var_name] = {
                            'type': var_type,
                            'used': False,
                            'scope': self.current_scope,
                            'initialized': len(node.children) > 2
                        }
                        if len(node.children) > 2:  # Has initialization
                            self.analyze(node.children[2])
            elif node.type == 'assignment':
                if len(node.children) >= 2:
                    var_name = node.children[0].value
                    if var_name not in self.symbol_table:
                        self.errors.append(f"Undeclared variable '{var_name}'")
                    else:
                        self.symbol_table[var_name]['used'] = True
                        self.analyze(node.children[1])
            elif node.type == 'identifier':
                if hasattr(node, 'value') and node.value in self.symbol_table:
                    self.symbol_table[node.value]['used'] = True
                elif hasattr(node, 'value'):
                    self.errors.append(f"Undeclared variable '{node.value}'")
            elif node.type in ['binary', 'unary']:
                for child in node.children:
                    self.analyze(child)
            elif node.type == 'if':
                if len(node.children) >= 2:
                    self.analyze(node.children[0])  # condition
                    self.analyze(node.children[1])  # then block
                    if len(node.children) > 2:  # else block
                        self.analyze(node.children[2])
            elif node.type == 'while':
                if len(node.children) >= 2:
                    self.analyze(node.children[0])  # condition
                    self.analyze(node.children[1])  # body
            elif node.type == 'for':
                # Analyze initialization, condition, increment, body
                for child in node.children:
                    self.analyze(child)
            else:
                # Recursively analyze all children for unknown node types
                for child in node.children:
                    self.analyze(child)

    def check_unused_variables(self):
        for var_name, info in self.symbol_table.items():
            if not info['used']:
                self.warnings.append(f"Unused variable '{var_name}'")
            if not info.get('initialized', True):
                self.warnings.append(f"Variable '{var_name}' declared but not initialized")

def analyze_semantics(ast):
    """Analyze semantics of an AST and return errors, warnings, and symbol table"""
    if ast is None:
        return {
            'errors': ['No AST provided for semantic analysis'],
            'warnings': [],
            'symbol_table': {}
        }
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    analyzer.check_unused_variables()
    
    return {
        'errors': analyzer.errors,
        'warnings': analyzer.warnings,
        'symbol_table': analyzer.symbol_table
    }
