from tkinter import *
import re

class GUI:
    def __init__(self, root):
        self.master = root
        self.width=1190
        self.height=780
        self.master.config(height=self.height, width=self.width)
        self.master.title("Lexical Analyzer for TinyPie")

        self.source_label = Label(self.master, text="Source Code Input:")
        self.source_label.place(x=30, y=5)

        self.source_text = Text(self.master)
        self.source_text.place(x=30, y=30, height=350, width=300)

        self.line_label = Label(self.master, text="Current Processing Line:")
        self.line_label.place(x=30, y=385)

        self.line_entry = Entry(self.master)
        self.line_entry.place(x=300, y=385, width=30)
        self.line_entry.insert(0, 0)
        self.line_entry.config(state=DISABLED)

        self.lexer_label = Label(self.master, text="Lexical Analyzed Result:")
        self.lexer_label.place(x=370, y=5)

        self.lexer_text = Text(self.master, state=DISABLED)
        self.lexer_text.place(x=370, y=30, height=350, width=300)
        self.lexer_line = "1"

        self.lexer_label = Label(self.master, text="Parser Result:")
        self.lexer_label.place(x=710, y=5)

        self.parser_text = Text(self.master, state=DISABLED)
        self.parser_text.place (x=710, y=30, height=350, width=450)

        self.quit_button = Button(self.master, text="Quit", command=exit)
        self.quit_button.place(x=1095, y=410, width = 70)

        self.line_button = Button(self.master, text="Next Line", command=self.read_line)
        self.line_button.place(x=260, y=410, width=70)

        self.tree_visualizer = Canvas(self.master, width=1130, height=300, bg="blue", scrollregion=(0, 0, 0, 400)) # color is for testing purposes
        self.tree_visualizer.place(x=30, y=450)

        self.vbar = Scrollbar(self.master, orient=VERTICAL, command=self.tree_visualizer.yview)
        self.vbar.place(x=1160, y=450, height=300)

        self.tree_visualizer.config(yscrollcommand=self.vbar.set, yscrollincrement=0)
        
        offset = 50
        root_coord = self.width/2-offset, 10, self.width/2+offset, 60
        self.tree_visualizer.create_rectangle(root_coord)
        line_coord = root_coord[0]+offset, root_coord[3], root_coord[0]+offset, root_coord[3]+40
        self.tree_visualizer.create_line(line_coord)
        child_coord = line_coord[2]-offset, line_coord[3], line_coord[2]+offset, line_coord[3]+50
        self.tree_visualizer.create_rectangle(child_coord)

        self.tree = None

    def read_line(self):
        # use line number from line_entry
        current_line = str(int(self.line_entry.get()) + 1)
        next_line = str(int(current_line) + 1)

        # read a line from source_text
        line = self.source_text.get(current_line + ".0", next_line + ".0")

        # only print the line if it is not empty
        if  line != "" and line != "\n":
            # turn it into tokens
            tokens = tokenizer(line)

            # print it on lexer_text
            self.lexer_text.config(state=NORMAL)
            # print each token on a seperate line
            for token in tokens:
                self.lexer_text.insert(END, "<" + token[0] + ", " + token[1] + ">"+ "\n") # append a token with a new line
                self.lexer_line = str(int(self.lexer_line) + 1)
            
            self.lexer_text.config(state=DISABLED)

            # print it on parser_text
            self.parser_text.config(state=NORMAL)
            # for each line printed to terminal use: self.parser_text.insert(END,
            self.parser(tokens)
            self.parser_text.config(state=DISABLED)
            
            # go to the next line
            self.line_entry.config(state=NORMAL)
            self.line_entry.delete(0)
            self.line_entry.insert(0, int(current_line))
            self.line_entry.config(state=DISABLED)


    Mytokens=[]
    inToken = ("empty","empty")
    def accept_token(self):
        global inToken
        self.parser_text.insert(END, "     accept token from the list:"+inToken[1]+"\n")
        inToken=Mytokens.pop(0)


    def math(self, parent_node):
        self.parser_text.insert(END, "\n----parent node math, finding children nodes:\n")
        global inToken
        self.parser_text.insert(END, "Child node (internal): multi\n")
        multi_node = self.tree.add_node(parent_node, "Multi")
        self.multi(multi_node) # left side of +
        if(inToken[1] == "+"):
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
            self.parser_text.insert(END, "child node (internal): multi\n")
            multi_node = self.tree.add_node(parent_node, "Multi")
            self.multi(multi_node) # right side of +
        else:
            self.parser_text.insert(END, "error, you need + after the int in the math\n")


    def multi(self, parent_node):
        self.parser_text.insert(END, "\n----parent node multi, finding children nodes:\n")
        global inToken
        if(inToken[0]=="lit_float"): # multi => float
            self.parser_text.insert(END, "child node (internal): float\n")
            self.parser_text.insert(END, "   float has child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        elif (inToken[0]=="lit_int"): # multi => int * multi
            self.parser_text.insert(END, "child node (internal): int\n")
            self.parser_text.insert(END, "   int has child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
            if(inToken[1]=="*"):
                self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
                self.tree.add_node(parent_node, inToken[1])
                self.accept_token()
                self.parser_text.insert(END, "child node (internal): multi\n")
                self.multi(parent_node)
            else:
                self.parser_text.insert(END, "error, you need * after the int in the multi\n")
        else:
            self.parser_text.insert(END, "error, multi expects float or int\n")


    '''
    BNF:
    exp->key id = math
    math->multi + multi
    multi->int * float|float
    '''
    def exp(self, parent_node):
        self.parser_text.insert(END, "\n----parent node exp, finding children nodes:\n")
        global inToken
        self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
        self.tree.add_node(parent_node, inToken[1])
        self.accept_token()
        if(inToken[0]=="id"):
            self.parser_text.insert(END, "child node (internal): identifier\n")
            self.parser_text.insert(END, "   identifier has child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect identifier as the second element of the expression!\n")
            return  
        if(inToken[1]=="="): 
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect = as the third element of the expression!\n")
            return
        self.parser_text.insert(END, "Child node (internal): math\n")
        math_node = self.tree.add_node(parent_node, "Math")
        self.math(math_node) # math->multi + multi


    def comparison_exp(self, parent_node):
        self.parser_text.insert(END, "\n----parent node comparison_exp, finding children nodes:\n")
        global inToken
        if(inToken[0]=="id"):
            self.parser_text.insert(END, "child node (internal): identifier\n")
            self.parser_text.insert(END, "   identifier has child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect identifier as the third element of the expresison!\n")
            return
        if(inToken[1]==">"):
            self.parser_text.insert(END, "child node (token)"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect > as the fourth element of the expression!\n")
            return
        if(inToken[0]=="id"):
            self.parser_text.insert(END, "child node (internal): identifier\n")
            self.parser_text.insert(END, "   identifier has child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect identifier as the fifth element of the expresison!\n")


    '''
    BNF:
    if_exp->if(comparsion_exp):
    comparison_exp->identifier > identifier
    '''
    def if_exp(self, parent_node):
        self.parser_text.insert(END, "\n----parent node if_exp, finding children nodes:\n")
        global inToken
        self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
        self.tree.add_node(parent_node, inToken[1])
        self.accept_token()
        if(inToken[1]=="("):
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect ( as the second element of the expression!\n")
            return
        self.parser_text.insert(END, "Child node (internal): comparison_exp\n")
        compare_node = self.tree.add_node(parent_node, "Comparison Expression")
        self.comparison_exp(compare_node) # comparison_exp->identifier > identifier
        if(inToken[1]==")"):
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect ) as the sixth element of the expression!\n")
            return
        
    '''
    BNF:
    print_exp->print("string");
    '''
    def print_exp(self, parent_node):
        self.parser_text.insert(END, "\n----parent node print_exp, finding children nodes:\n")
        global inToken
        self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
        self.tree.add_node(parent_node, inToken[1])
        self.accept_token()
        if(inToken[1]=="("):
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect ( as the second element of the expression!\n")
            return
        if(inToken[1]=="\""):
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect \" as the third element of the expression!\n")
            return
        if(inToken[0]=="lit_string"):
            self.parser_text.insert(END, "child node (internal): string literal\n")
            self.parser_text.insert(END, "   identifier has child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser.text.insert(END, "expect string literal as the fourth element of the expression!\n")
            return
        if(inToken[1]=="\""):
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect \" as the fifth element of the expression!\n")
            return
        if(inToken[1]==")"):
            self.parser_text.insert(END, "child node (token):"+inToken[1]+"\n")
            self.tree.add_node(parent_node, inToken[1])
            self.accept_token()
        else:
            self.parser_text.insert(END, "expect ) as the sixth element of the expression!\n")
            return
            

    def parser(self, tokens):
        message = ""
        if str(int(self.line_entry.get()) + 1) != "1":
            message = "\n"
        message += "####parse tree for line " + str(int(self.line_entry.get()) + 1) + "####\n"
        self.parser_text.insert(END, message)
        global Mytokens
        Mytokens = tokens
        global inToken
        inToken=Mytokens.pop(0)
        match (inToken[1]):
            case "float":
                self.tree = Tree("Expression")
                self.exp(self.tree.root) # exp => id = math
                if(inToken[1]==";"):
                    self.tree.add_node(self.tree.root, inToken[1])
                    self.parser_text.insert(END, "\nparse tree building success!\n")
                    self.draw_tree()
            case "if":
                self.tree = Tree("If Expression")
                self.if_exp(self.tree.root)
                if(inToken[1]==":"):
                    self.tree.add_node(self.tree.root, inToken[1])
                    self.parser_text.insert(END, "\nparse tree building success!\n")
                    self.draw_tree()
            case "print":
                self.tree = Tree("Print Expression")
                self.print_exp(self.tree.root)
                if(inToken[1]==";"):
                    self.tree.add_node(self.tree.root, inToken[1])
                    self.parser_text.insert(END, "\nparse tree building success!\n")
                    self.draw_tree()
            case _:
                self.parser_text.insert(END, "\nError: cannot parse this!\n")


    def draw_tree(self):
        # level 1 - nodes have gap 1
        # level 2 - nodes have gap 1/2
        # level 3 - nodes have gap 1/4
        self.tree_visualizer.delete('all')

        offset = 50
        root_coord = self.width/2-offset, 10, self.width/2+offset, 60
        self.tree_visualizer.create_rectangle(root_coord)
        # add text in center of rectangle

        self.draw_children(self.tree.root, root_coord, offset, 1)


    def draw_children(self, parent_node, parent_coord, parent_offset, gap_multiplier):
        children_coords = []
        children_gaps_num = parent_node.children.__len__() - 1
        for child in parent_node.children:
            child_coord = parent_coord[0]+10*gap_multiplier*children_gaps_num-parent_offset, parent_coord[3]+50, parent_coord[0]+10*gap_multiplier*children_gaps_num+parent_offset,parent_coord[3]+100
            self.tree_visualizer.create_rectangle(child_coord)
            line_coord = parent_coord[0]+parent_offset, parent_coord[3],child_coord[0]+parent_offset, child_coord[1]
            self.tree_visualizer.create_rectangle(line_coord)
            children_coords.append((child, child_coord))
           # add text in center of rectangle


        for child in children_coords:
            self.draw_children(child[0], child[1], parent_offset, gap_multiplier/2)


def tokenizer(line):
    tokens = [] # list containing tokens formatted <type, token>

    # will create tokens until all tokens are removed or a non token is found (error, exits)
    while line != None:
        line = line.strip()

        # testing for any keyword
        key, line = test_keywords(line)
        # keep cutting keywords until none are left
        if (key != None):
            tokens.append(("key", key))
            line = line.strip()

        # testing for any string literals, includes quotation separators
        lit_sep, line = test_string_literals(line)
        # keep cutting string liteals until none are left
        if (lit_sep != None):
            # append all three tokens from string literal
            tokens.append(lit_sep[0])
            tokens.append(lit_sep[1])
            tokens.append(lit_sep[2])
            line = line.strip()

        # testing for any identifier
        id, line = test_identifiers(line)
        # keep cutting identifiers until none are left
        if (id != None):
            tokens.append(("id", id))
            line = line.strip()

        # testing for any float literals
        lit, line = test_literals(line)
        
        if (lit != None):
            tokens.append(lit)
            line = line.strip()
        
        # testing for any operator
        op, line = test_operators(line)
        # keep cutting operators until none are left
        if (op != None):
            tokens.append(("op", op))
            line = line.strip()

        # testing for any separator
        sep, line = test_separators(line)
        # keep cutting separators until none are left
        if (sep != None):
            tokens.append(("sep", sep))
            line = line.strip()

        # test if line is empty
        if line == '':
            line = None
        
    return tokens


def test_keywords(line):
    # use variables to reduce # of func calls
    key_if = re.match(r'\bif\b', line)
    key_else = re.match(r'\belse\b', line)
    key_int = re.match(r'\bint\b', line)
    key_float = re.match(r'\bfloat\b', line)

    # testing for 'if' keyword
    if (key_if != None):
        # cuts 'if' out of the long string
        line = line.replace(key_if.group(), ' ', 1)
        return key_if.group(), line
    # testing for 'else' keyword    
    elif (key_else != None):
        # cuts 'else' out of the long string
        line = line.replace(key_else.group(), ' ', 1)
        return key_else.group(), line
    # testing for 'int' keyword
    elif (key_int != None):
        # cuts 'int' out of the long string
        line = line.replace(key_int.group(), ' ', 1)
        return key_int.group(), line
    # testing for 'float' keyword
    elif (key_float != None):
        # cuts 'float' out of the long string
        line = line.replace(key_float.group(), ' ', 1)
        return key_float.group(), line
    else:
        # no keyword
        return None, line


def test_string_literals(line):
    # use variables to reduce # of func calls
    lit_sep = re.match(r'\".*\"', line) # speical case: grabs both quotation marks and the string literal inside

    tokens = [] # list of tokens (2 seps, 1 lit)

    # testing for a string literal
    if (lit_sep != None):
        # cuts the string literal out of the long string
        line = line.replace(lit_sep.group(), ' ', 1)
        tokens.append(("sep", "\"")) # append just the open quote
        tokens.append(("lit_string", lit_sep.group())) # append the string literal (w/ quotes)
        tokens.append(("sep", "\"")) # append just the close quote
        return tokens, line
    else:
        # no string literal
        return None, line
    

def test_identifiers(line):
    # use variables to reduce # of func calls
    id = re.match(r'[A-z]+\d*', line) # TODO make it not grab strings

    # testing for letters, or letters followed by digits
    if (id != None):
        # cuts the identifier out of the long string
        line = line.replace(id.group(), ' ', 1)
        return id.group(), line
    else:
        # no identifier
        return None, line


def test_literals(line):
    # use variables to reduce # of func calls
    lit_float = re.match(r'[+-]?\d+\.\d+', line)
    lit_int = re.match(r'[+-]?\d+', line) # will grab the int part of floats (i.e. grabs '22' from '22.1'), but shouldn't matter as it will test for floats first
    
    # testing for float literals
    if (lit_float != None):
        # cuts the float literal out of the long string
        line = line.replace(lit_float.group(), ' ', 1)
        return ("lit_float", lit_float.group()), line
         # testing for int literals
    elif (lit_int != None):
        # cuts the float literal out of the long string
        line = line.replace(lit_int.group(), ' ', 1)
        return ("lit_int", lit_int.group()), line
    else:
        # no literal
        return None, line


def test_operators(line):
    # use variables to reduce # of func calls
    op_equals = re.match(r'\=', line)
    op_plus = re.match(r'\+', line)
    op_gtr = re.match(r'\>', line)
    op_mult = re.match(r'\*', line)

    # testing for '=' operator
    if (op_equals != None):
        # cuts '=' out of the long string
        line = line.replace(op_equals.group(), ' ', 1)
        return op_equals.group(), line
    # testing for '+' operator
    elif (op_plus != None):
        # cuts '+' out of the long string
        line = line.replace(op_plus.group(), ' ', 1)
        return op_plus.group(), line
    # testing for '>' operator
    elif (op_gtr != None):
        # cuts '>' out of the long string
        line = line.replace(op_gtr.group(), ' ', 1)
        return op_gtr.group(), line
    # testing for '*' operator
    elif (op_mult != None):
        # cuts '*' out of the long string
        line = line.replace(op_mult.group(), ' ', 1)
        return op_mult.group(), line
    else:
        # no operator
        return None, line


def test_separators(line):
    # use variables to reduce # of func calls
    sep_oparen = re.match(r'\(', line)
    sep_cparen = re.match(r'\)', line)
    sep_colon = re.match(r'\:', line)
    sep_semicolon = re.match(r';', line)

    # testing for open parentheses
    if (sep_oparen != None):
        # cuts '(' out of the long string
        line = line.replace(sep_oparen.group(), ' ', 1)
        return sep_oparen.group(), line
    # testing for closed parentheses
    elif (sep_cparen != None):
        # cuts ')' out of the long string
        line = line.replace(sep_cparen.group(), ' ', 1)
        return sep_cparen.group(), line
    # testing for colon
    elif (sep_colon != None):
        # cuts ':' out of the long string
        line = line.replace(sep_colon.group(), ' ', 1)
        return sep_colon.group(), line
    # testing for semicolon
    elif (sep_semicolon != None):
        # cuts ';' out of the long string
        line = line.replace(sep_semicolon.group(), ' ', 1)
        return sep_semicolon.group(), line
    else:    
        # no seperator
        return None, line
    

class Node:
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class Tree:
    def __init__(self, root_data):
        self.root = Node(root_data)

    def add_node(self, parent_node, node_data):
        node = Node(node_data)
        parent_node.add_child(node)
        return node

    def traverse(self):
        self._traverse(self.root)

    def traverse(self, current_node):
        self._traverse(current_node)

    def _traverse(self, current_node):
        print(current_node.data)
        for child in current_node.children:
            self._traverse(child)


if __name__ == '__main__':
    TkRoot = Tk()
    gui = GUI(TkRoot)
    TkRoot.mainloop()