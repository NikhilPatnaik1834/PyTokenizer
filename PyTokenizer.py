import copy
import re


f = open("tokenizereg.py","r")
lines = f.readlines()


#Tokenizer function takes a python script as input
def tokenizer(input_expression):
    #counter variable for iterating through input array
    current = 0
    #array to store tokens
    tokens = []
    ##use regex library to create search patterns for
    #letters a,z
    alphabet = re.compile(r"[a-z]", re.I)
    #numbers 1-9
    numbers = re.compile(r"[0-9]")
    #white space
    whiteSpace = re.compile(r"\s")
    #iterate through input
    while current < len(input_expression):
        #track position
        char = input_expression[current]
        if re.match(whiteSpace, char):
            current = current + 1
            continue
        #create + add token to array for open parens
        if char == '(':
            tokens.append({
                    'type': 'left_paren',
                    'value': '('
                })
            #continue iterating
            current = current + 1
            continue
        #create + add token to array for closed parens
        if char == ')':
            tokens.append({
                    'type': 'right_paren',
                    'value': ')'
                })
        #create + add token to array for numbers
        if re.match(numbers, char):
            value = ''
            #nested iteration if a number is multi-num 
            while re.match(numbers, char):
                value += char
                current = current + 1
                char = input_expression[current];
            tokens.append({
                    'type': 'number',
                    'value': value
                })
        #create + add token to array for letters
        if re.match(alphabet, char):
            value = ''
            #nested iteration if a word is multi-char (all are in this case)
            while re.match(alphabet, char):
                value += char
                current = current + 1
                char = input_expression[current];
            tokens.append({
                    'type': 'name',
                    'value': value
                })
            continue
        #error condition if we find an unknown value in the input
        raise ValueError("Unable to identify" + char);
    print(tokens)    
    return tokens            

#tokenizer(lines)


#The parse function creates an Abstract Syntax Tree given the computed
#tokens from the previous function  
def parser(tokens):
    global current
    current = 0
    #nested walk function for building an abstract syntax tree
    def walk():
        #keep track of position while iterating
        global current
        token = tokens[current]
        #if a number is encountered, return a "NumberLiteral" node
        if token.get('type') == 'number':
            current = current + 1
            return{
                    'type': 'NumberLiteral',
                    'value': token.get('value')
                }
        #if open parentheses encountered, return a "CallExpression" node
        if token.get('type') == 'left_paren':
            current = current + 1
            token = tokens[current]
            #store the name of operation
            node = {
                    'type': 'CallExpression',
                    'name': token.get('value'),
                    'params': []
                }
            #looking for nested expressions using recursion to build a tree of relations
            current = current + 1
            token = tokens[current]
            #stop when the expression ends with a closed parens
            while token.get('type') != 'right_paren':
                #recursively add nodes to the params array via the walk function
                node['params'].append(walk());
                token = tokens[current]
            current = current + 1
            return node
            raise TypeError(token.get('type'))

    #Initialize an empty Abstract Syntax Tree
    ast = {
            'type': 'Program',
            'body': []
        }
    #Populate Ast using walk() function until global current variable reaches end of tokens array
    while current > len(tokens):
        ast['body'].append(walk())
    #return the completed AST
    return ast

#Traverse new Ast        
def traverser(ast, visitor):
    #child node (current AST) and parent node (new AST) as params
    def traverseArray(array, parent):
        #iterate through every parameter element in our current AST
        for child in array:
            traverseNode(child, parent)
    
    def traverseNode(node, parent):
        method = visitor.get(node['type'])
        if method:
            method(node, parent)
        elif node['type'] == 'Program':
            traverseArray(node['body'], node)
        elif node['type'] == 'CallExpression':
            traverseArray(node['params'], node)
        elif node['type'] == 'NumberLiteral':
            0
        else:
            raise TypeError(node['type'])
    traverseNode(ast, None)
    
#transform our exsiting AST
def transformer(ast):
    #Define an empty new AST
    newAst = {
            'type': 'Program',
            'body': []
        }
    oldAst = ast
    ast = copy.deepcopy(oldAst)
    ast['_context'] = newAst.get('body')
    
    def CallExpressionTraverse(node, parent):
        expression = {
                'type' = 'CallExpression',
                'callee': {
                        'type': 'Identifier'
                        'name': node['name']
                    }
            }
        node['_context'] = expression['arguments']
        
        if parent['type'] != 'CallExpression':
            expression = {
                    'type': 'ExpressionStatement',
                    'expression': expression
                }
        parent['_context'].append(expression)
        
        
    def NumberLiteralTraverse(node,parent):
        parent['_context'].append({
                'type': 'NumberLiteral',
                'value': node['value']
            })
    traverser(ast, {
            'NumberLiteral': NumberLiteralTraverse,
            'CallExpression': CallExpressionTraverse
        })
    return newAst

#A recursive stringify function that iterates through new Ast to build string output
        
def codeGenerator(node):
    if node['type'] == 'Program':
        return '\n'.join([code for code in map(codeGenerator, node['body'])])
    elif node['type'] == 'Identifier':
        return node['name']
    elif node['type'] == 'NumberLiteral':
        return node['value']
    elif node['type'] == 'ExpressionStatement':
        expression = codeGenerator(node['expression']) 
        return '%s;' % expression
    elif node['type'] == 'CallExpression':
        callee = codeGenerator(node['callee']) 
        params = ', '.join([code for code in map(codeGenerator, node['arguments'])])
        return "%s(%s)" % (callee, params)
    else:
        raise TypeError(node['type'])

def compiler(input_expression):
    tokens = tokenizer(input_expression)
    ast = parser(tokens)
    newAst = transformer(ast)
    output = codeGenerator(newAst)
    
    return output

def main():
    #test 
    input = lines
    output = compiler(lines)
    print(output)


if __name__ == "__main__":
    main()
