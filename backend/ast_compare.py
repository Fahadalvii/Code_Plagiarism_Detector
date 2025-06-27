from copy import deepcopy
from .parser import parse_code  

class ASTNormalizer:
    def __init__(self):
        self.var_counter = 1
        self.var_map = {}

    def normalize(self, node):
        if node is None:
            return None
        
        # Create a deep copy to avoid modifying the original AST
        normalized_node = deepcopy(node)
        
        # Normalize based on node type
        if normalized_node.type == 'identifier':
            if normalized_node.value not in self.var_map:
                self.var_map[normalized_node.value] = f'var{self.var_counter}'
                self.var_counter += 1
            normalized_node.value = self.var_map[normalized_node.value]
        elif normalized_node.type in ['number', 'float', 'string']:
            # Normalize literals to generic values
            if normalized_node.type == 'number':
                normalized_node.value = 0
            elif normalized_node.type == 'float':
                normalized_node.value = 0.0
            else:
                normalized_node.value = ""
        
        # Recursively normalize children
        normalized_node.children = [self.normalize(child) for child in normalized_node.children]
        
        return normalized_node

def subtree_size(node):
    """Calculate the size of a subtree (number of nodes)"""
    if node is None:
        return 0
    return 1 + sum(subtree_size(child) for child in node.children)

def tree_edit_distance(node1, node2, memo=None):
    """Calculate the tree edit distance between two ASTs with memoization"""
    if memo is None:
        memo = {}
    
    # Create a key for memoization (using object ids)
    key = (id(node1) if node1 else None, id(node2) if node2 else None)
    if key in memo:
        return memo[key]
    
    if node1 is None and node2 is None:
        result = 0
    elif node1 is None:
        result = subtree_size(node2)
    elif node2 is None:
        result = subtree_size(node1)
    elif node1.type != node2.type or node1.value != node2.value:
        # If nodes are different, cost is 1 + optimal alignment of children
        result = 1 + min_children_distance(node1.children, node2.children, memo)
    else:
        # Nodes are the same, just align children
        result = min_children_distance(node1.children, node2.children, memo)
    
    memo[key] = result
    return result

def min_children_distance(children1, children2, memo):
    """Find minimum distance to align two lists of children using DP"""
    len1, len2 = len(children1), len(children2)
    
    # DP table
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    # Initialize base cases
    for i in range(len1 + 1):
        dp[i][0] = sum(subtree_size(children1[j]) for j in range(i))
    for j in range(len2 + 1):
        dp[0][j] = sum(subtree_size(children2[j]) for j in range(j))
    
    # Fill DP table
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            # Cost of aligning children1[i-1] with children2[j-1]
            align_cost = tree_edit_distance(children1[i-1], children2[j-1], memo)
            
            dp[i][j] = min(
                dp[i-1][j] + subtree_size(children1[i-1]),  # delete children1[i-1]
                dp[i][j-1] + subtree_size(children2[j-1]),  # insert children2[j-1]
                dp[i-1][j-1] + align_cost  # align children1[i-1] with children2[j-1]
            )
    
    return dp[len1][len2]

def calculate_similarity(ast1, ast2):
    """Calculate the similarity percentage between two ASTs"""
    # Handle edge cases
    size1 = subtree_size(ast1)
    size2 = subtree_size(ast2)
    
    # Empty strings should have 0% similarity
    if size1 == 0 and size2 == 0:
        return 0.0
    
    if size1 == 0 or size2 == 0:
        return 0.0
    
    # Normalize both ASTs
    normalizer1 = ASTNormalizer()
    normalized_ast1 = normalizer1.normalize(ast1)
    
    normalizer2 = ASTNormalizer()
    normalized_ast2 = normalizer2.normalize(ast2)
    
    # Calculate tree edit distance
    distance = tree_edit_distance(normalized_ast1, normalized_ast2)
    
    # Use correct similarity formula
    max_size = max(size1, size2)
    similarity = (1 - distance / max_size) * 100
    
    return max(0.0, min(100.0, similarity))  # Clamp between 0 and 100

def compare_code(code1, code2):
    """Compare two code snippets and return similarity score"""
    try:
        # Parse both code snippets
        ast1 = parse_code(code1)
        ast2 = parse_code(code2)
        
        # Calculate similarity
        similarity = calculate_similarity(ast1, ast2)
        
        return {
            'similarity': similarity,
            'ast1': ast1,
            'ast2': ast2
        }
    except Exception as e:
        print(f"Error comparing code: {e}")
        return {
            'similarity': 0.0,
            'ast1': None,
            'ast2': None,
            'error': str(e)
        }
