import ply.yacc as yacc
from .lexer import tokens  # Changed from 'lexer' to '.lexer' for relative import

# AST Node classes
class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value

    def __repr__(self):
        return f"{self.type}: {self.value}" if self.value else self.type

# Precedence rules
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
)

# Grammar rules
def p_program(p):
    '''program : statement_list'''
    p[0] = Node('program', [p[1]])

def p_statement_list(p):
    '''statement_list : statement
                     | statement_list statement'''
    if len(p) == 2:
        p[0] = Node('statement_list', [p[1]])
    else:
        p[1].children.append(p[2])
        p[0] = p[1]

def p_statement(p):
    '''statement : declaration
                 | assignment
                 | if_statement
                 | while_statement
                 | for_statement
                 | expression_statement'''
    p[0] = p[1]

def p_declaration(p):
    '''declaration : type ID SEMICOLON
                   | type ID ASSIGN expression SEMICOLON'''
    if len(p) == 4:
        p[0] = Node('declaration', [
            Node('type', value=p[1]),
            Node('identifier', value=p[2])
        ])
    else:
        p[0] = Node('declaration', [
            Node('type', value=p[1]),
            Node('identifier', value=p[2]),
            p[4]
        ])

def p_type(p):
    '''type : INT
            | FLOAT
            | STRING
            | BOOL'''
    p[0] = p[1]

def p_assignment(p):
    '''assignment : ID ASSIGN expression SEMICOLON'''
    p[0] = Node('assignment', [
        Node('identifier', value=p[1]),
        p[3]
    ])

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN LBRACE statement_list RBRACE
                    | IF LPAREN expression RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE'''
    if len(p) == 8:
        p[0] = Node('if', [p[3], p[6]])
    else:
        p[0] = Node('if', [p[3], p[6], p[10]])

def p_while_statement(p):
    '''while_statement : WHILE LPAREN expression RPAREN LBRACE statement_list RBRACE'''
    p[0] = Node('while', [p[3], p[6]])

def p_for_statement(p):
    '''for_statement : FOR LPAREN declaration expression SEMICOLON expression RPAREN LBRACE statement_list RBRACE'''
    p[0] = Node('for', [p[3], p[4], p[6], p[9]])

def p_expression_statement(p):
    '''expression_statement : expression SEMICOLON'''
    p[0] = p[1]

def p_expression(p):
    '''expression : binary_expression
                  | unary_expression
                  | primary_expression'''
    p[0] = p[1]

def p_binary_expression(p):
    '''binary_expression : expression PLUS expression
                         | expression MINUS expression
                         | expression TIMES expression
                         | expression DIVIDE expression
                         | expression MODULO expression
                         | expression EQ expression
                         | expression NE expression
                         | expression LT expression
                         | expression LE expression
                         | expression GT expression
                         | expression GE expression'''
    p[0] = Node('binary', [p[1], p[3]], value=p[2])

def p_unary_expression(p):
    '''unary_expression : MINUS expression'''
    p[0] = Node('unary', [p[2]], value=p[1])

def p_primary_expression(p):
    '''primary_expression : ID
                          | NUMBER
                          | FLOAT_NUMBER
                          | STRING_LITERAL
                          | LPAREN expression RPAREN'''
    if len(p) == 2:
        if isinstance(p[1], int):
            p[0] = Node('number', value=p[1])
        elif isinstance(p[1], float):
            p[0] = Node('float', value=p[1])
        elif p.slice[1].type == 'STRING_LITERAL':
            p[0] = Node('string', value=p[1])
        else:
            p[0] = Node('identifier', value=p[1])
    else:
        p[0] = p[2]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

def parse_code(code):
    """Parse the input code and return the AST"""
    return parser.parse(code)