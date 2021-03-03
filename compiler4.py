########################################################################
# Name: Devon Knudsen
# Assignment: Compiler #4
# Date: 28 February 2020
########################################################################

import sys, string

norw = 28      #number of reserved words
txmax = 100   #length of identifier table
nmax = 14      #max number of digits in number
al = 10          #length of identifiers
CXMAX = 500 #maximum allowed lines of assembly code
STACKSIZE = 500
a = []
chars = []
rword = []
table = []        #symbol table
code = []         #code array
stack = [0] * STACKSIZE     #interpreter stack
global infile, outfile, ch, sym, id, num, linlen, kk, line, errorFlag, linelen, codeIndx, prevIndx, codeIndx0
#-------------values to put in the symbol table------------------------------------------------------------
class tableValue():                          
    def __init__(self, name, kind, level, adr, value, params = None):
        self.name = name
        self.kind = kind
        self.adr = adr
        self.value = value
        self.level = level
        self.params = params
#----------commands to put in the array of assembly code-----------------------------------------------
class Cmd():                            
    def __init__(self, line, cmd, statLinks, value):
        self.line = line
        self.cmd = cmd
        self.statLinks = statLinks
        self.value = value
#-------------function to generate assembly commands--------------------------------------------------
def gen(cmd, statLinks, value):            
    global codeIndx, CXMAX
    if codeIndx > CXMAX:
        print >>outfile, "Error, Program is too long"
        exit(0)
    x = Cmd(codeIndx, cmd, statLinks, value)
    code.append(x)
    codeIndx += 1
#--------------function to change jump commands---------------------------------------
def fixJmp(cx, jmpTo):
    code[cx].value = jmpTo
#--------------Function to print p-Code for a given block-----------------------------
def printCode():
    global codeIndx, codeIndx0
    print>>outfile
    for i  in range(codeIndx0, codeIndx):
        print >>outfile, code[i].line, code[i].cmd, code[i].statLinks, code[i].value
    prevIndx = codeIndx
#-------------Function to find a new base----------------------------------------------
def Base(statLinks, base):
    b1 = base
    while(statLinks > 0):
        b1 = stack[b1]
        statLinks -= 1
    return b1
#-------------P-Code Interpreter-------------------------------------------------------
def Interpret():
    print >>outfile, "Start PL/0"
    top = 0
    base = 1
    pos = 0
    stack[1] = 0
    stack[2] = 0
    stack[3] = 0
    while True:
        instr = code[pos]
        pos += 1
        #       LIT COMMAND
        if instr.cmd == "LIT":    
            top += 1
            stack[top] = int(instr.value)
        #       OPR COMMAND
        elif instr.cmd == "OPR":
            if instr.value == 0:         #end
                top = base - 1
                base = stack[top+2]
                pos = stack[top + 3]
            elif instr.value == 1:         #unary minus
                stack[top] = -stack[top]
            elif instr.value == 2:         #addition
                top -= 1
                stack[top] = stack[top] + stack[top+1]
            elif instr.value == 3:         #subtraction
                top -= 1
                stack[top] = stack[top] - stack[top+1]
            elif instr.value == 4:         #multiplication
                top -= 1
                stack[top] = stack[top] * stack[top+1]
            elif instr.value == 5:         #integer division
                top -= 1
                stack[top] = stack[top] / stack[top+1]
            elif instr.value == 6:         #logical odd function
                if stack[top] % 2 == 0:
                    stack[top] = 1
                else:
                    stack[top] = 0
            # case 7 n/a, used to debuge programs
            elif instr.value == 8:        #test for equality if stack[top-1] = stack[top], replace pair with true, otherwise false
                top -= 1
                if stack[top] == stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 9:         #test for inequality
                top -= 1
                if stack[top] != stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 10:         #test for < (if stack[top-1] < stack[t])
                top -= 1
                if stack[top] < stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 11:        #test for >=
                top -= 1
                if stack[top] >= stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 12:        #test for >
                top -= 1
                if stack[top] > stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 13:        #test for <=
                top -= 1
                if stack[top] <= stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 14:        #write/print stack[top]  
                print >>outfile, stack[top],
                top -= 1
            elif instr.value == 15:        #write/print a newline
                print
        #      LOD COMMAND
        elif instr.cmd == "LOD":
            top += 1
            stack[top] = stack[Base(instr.statLinks, base) + instr.value]
        #    STO COMMAND
        elif instr.cmd == "STO":
            stack[Base(instr.statLinks, base) + instr.value] = stack[top]
            top -= 1
        #    CAL COMMAND
        elif instr.cmd == "CAL": 
            stack[top+1] = Base(instr.statLinks, base)
            stack[top+2] = base
            stack[top+3] = pos
            base = top + 1
            pos = instr.value
        #    INT COMMAND
        elif instr.cmd == "INT":
            top = top + instr.value
        #     JMP COMMAND
        elif instr.cmd == "JMP":
            pos = instr.value
        #     JPC COMMAND
        elif instr.cmd == "JPC":
            if stack[top] == instr.statLinks:
                pos = instr.value
            top -= 1
        #   CTS COMMAND
        elif instr.cmd == "CTS":
            top += 1
            stack[top] = stack[top - 1]
        
        # ADDED THE STI, LDI and LDA COMMANDS
        #   STI COMMAND 
        elif instr.cmd == "STI":
            stack[stack[Base(instr.statLinks, base) + instr.value]] = stack[top]
            top -= 1
        #   LDI COMMAND
        elif instr.cmd == "LDI":
            top += 1
            stack[top] = stack[stack[Base(instr.statLinks, base) + instr.value]]
        #   LDA COMMAND
        elif instr.cmd == "LDA":
            top += 1
            stack[top] = Base(instr.statLinks, base) + instr.value
        # END OF CODE CHANGES
        
        if pos == 0:
            break
    print "End PL/0"
#--------------Error Messages----------------------------------------------------------
def error(num):
    global errorFlag;
    errorFlag = 1
    print
    if num == 1: 
        print >>outfile, "Use = instead of :="
    elif num ==2: 
        print >>outfile, "= must be followed by a number."
    elif num ==3: 
        print >>outfile, "Identifier must be followed by ="
    elif num ==4: 
        print >>outfile, "Const, Var, Procedure must be followed by an identifier."
    elif num ==5: 
        print >>outfile, "Semicolon or comma missing"
    elif num == 6: 
        print >>outfile, "Incorrect symbol after procedure declaration."
    elif num == 7:  
        print >>outfile, "Statement expected."
    elif num == 8:
        print >>outfile, "Incorrect symbol after statment part in block."
    elif num == 9:
        print >>outfile, "Period expected."
    elif num == 10: 
        print >>outfile, "Semicolon between statements is missing."
    elif num == 11:  
        print >>outfile, "Undeclared identifier"
    elif num == 12:
        print >>outfile, "Assignment to a constant or procedure is not allowed."
    elif num == 13:
        print >>outfile, "Assignment operator := expected."
    elif num == 14: 
        print >>outfile, "Call must be followed by an identifier"
    elif num == 15:  
        print >>outfile, "Call of a constant or a variable is meaningless."
    elif num == 16:
        print >>outfile, "Then expected"
    elif num == 17:
        print >>outfile, "Semicolon or end expected."
    elif num == 18: 
        print >>outfile, "DO expected"
    elif num == 19:  
        print >>outfile, "Incorrect symbol following statement"
    elif num == 20:
        print >>outfile, "Relational operator expected."
    elif num == 21:
        print >>outfile, "Expression must not contain a procedure identifier"
    elif num == 22: 
        print >>outfile, "Right parenthesis missing"
    elif num == 23:  
        print >>outfile, "The preceding factor cannot be followed by this symbol."
    elif num == 24:
        print >>outfile, "An expression cannot begin with this symbol."
    elif num ==25:
        print >>outfile, "Constant or Number is expected."
    elif num == 26: 
        print >>outfile, "This number is too large."
    elif num == 27:
        print >>outfile, "UNTIL expected."
    elif num == 28:
        print >>outfile, "Left parenthesis missing."
    elif num == 29:
        print >>outfile, "TO or DOWNTO expected."
    elif num == 30:
        print >>outfile, "FOR must be followed by an identifier."
    elif num == 31:
        print >>outfile, "OF expected."
    elif num == 32:
        print >>outfile, "Colon missing."
    elif num == 33:
        print >>outfile, "CEND expected."
    elif num == 34:
        print >>outfile, "Variable or Function expected."
    elif num == 35:
        print >>outfile, "Function expected."
    elif num == 36:
        print >>outfile, "Identifier expected."
    elif num == 37:
        print >>outfile, "Can't assign to this function here"
    elif num == 38:
        print >>outfile, "Value or Reference expected."
    exit(0)
#---------GET CHARACTER FUNCTION-------------------------------------------------------------------
def getch():
    global  whichChar, ch, linelen, line;
    if whichChar == linelen:         #if at end of line
        whichChar = 0
        line = infile.readline()     #get next line
        linelen = len(line)
        sys.stdout.write(line)
    if linelen != 0:
        ch = line[whichChar]
        whichChar += 1
    return ch
#----------GET SYMBOL FUNCTION---------------------------------------------------------------------
def getsym():
    global charcnt, ch, al, a, norw, rword, sym, nmax, id, num
    while ch == " " or ch == "\n" or ch == "\r":
        getch()
    a = []
    if ch.isalpha():
        k = 0
        while True:
            a.append(string.upper(ch))
            getch()
            if not ch.isalnum():
                break
        id = "".join(a)
        flag = 0
        for i in range(0, norw):
            if rword[i] == id:
                sym = rword[i]
                flag = 1
        if  flag == 0:    #sym is not a reserved word
            sym = "ident"
    elif ch.isdigit():
        k=0
        num=0
        sym = "number"
        while True:
            a.append(ch)
            k += 1
            getch()
            if not ch.isdigit():
                break
        if k>nmax:
            error(30)
        else:
            num = "".join(a)
    elif ch == ':':
        getch()
        if ch == '=':
            sym = "becomes"
            getch()
        else:
            sym = "colon"
    elif ch == '>':
        getch()
        if ch == '=':
            sym = "geq"
            getch()
        else:
            sym = "gtr"
    elif ch == '<':
        getch()
        if ch == '=':
            sym = "leq"
            getch()
        elif ch == '>':
            sym = "neq"
            getch()
        else:
            sym = "lss"
    else:
        sym = ssym[ch]
        getch()
#--------------POSITION FUNCTION----------------------------
def position(tx, id):
    global  table;
    table[0] = tableValue(id, "TEST", "TEST", "TEST", "TEST")
    i = tx
    while table[i].name != id:
        i=i-1
    return i
#---------------ENTER PROCEDURE-------------------------------
def enter(tx, k, level, dx):
    global id, num, codeIndx;
    tx[0] += 1
    while (len(table) > tx[0]):
      table.pop()
    if k == "const":
        x = tableValue(id, k, level, "NULL", num)
    
    # ADDED THE ABILITY TO ENTER VAL AND REF INTO SYMBOL TABLE
    elif k == "variable" or k == "val" or k == "ref":
        x = tableValue(id, k, level, dx, "NULL")
        dx += 1
    # END OF CODE CHANGES
    
    elif k == "procedure" or k == "function":
        x = tableValue(id, k, level, dx, "NULL", [])
        
    table.append(x)
    return dx
#--------------CONST DECLARATION---------------------------
def constdeclaration(tx, level):
    global sym, id, num;
    if sym=="ident":
        getsym()
        if sym == "eql":
            getsym()
            if sym == "number":
                enter(tx, "const", level, "null")
                getsym()
            else:
                error(2)
        else:
            error(3)
    else:
        error(4)
#-------------VARIABLE DECLARATION--------------------------------------
def vardeclaration(tx, level, dx):
    global sym;
    if sym=="ident":
        dx = enter(tx, "variable", level, dx)
        getsym()
    else:
        error(4)
    return dx
#-------------BLOCK-------------------------------------------------------------
def block(tableIndex, level):
    global sym, id, codeIndx, codeIndx0;
    tx = [1]
    tx[0] = tableIndex
    tx0 = tableIndex
    dx = 3
    cx1 = codeIndx
    gen("JMP", 0 , 0)
    
    # ADDED IF LEVEL IS GREATER THAN 0 (WITHIN PARAMETERS OF FUNCITON OR PROCEDURE)
    if level > 0:
        if sym == "lparen":
            while True:
                getsym()
                if sym != "VAL" and sym != "REF":
                    error(38)
                saveSym = sym
                while True:
                    getsym()
                    if sym != "ident":
                        error(36)
                    if saveSym == "VAL":
                        dx = enter(tx, "val", level, dx)
                        table[tx0].params.append(False)
                    elif saveSym == "REF":
                        dx = enter(tx, "ref", level, dx)
                        table[tx0].params.append(True)
                    getsym()
                    if sym != "comma":
                        break
                if sym != "semicolon":
                    break
            if sym != "rparen":
                error(22)
            getsym()
        if sym != "semicolon":
            error(17)
        getsym()
    # END OF CODE CHANGES
                
    while sym == "PROCEDURE" or sym == "VAR" or sym == "CONST" or sym == "FUNCTION": 
        
        if sym == "CONST":
            while True:               #makeshift do while in python
                getsym()
                constdeclaration(tx, level)
                if sym != "comma":
                    break
            if sym != "semicolon":
                error(10);
            getsym()
        if sym == "VAR":
            while True:
                getsym()
                dx = vardeclaration(tx, level, dx)
                if sym != "comma":
                    break
            if sym != "semicolon":
                error(10)
            getsym()
        
        # REMOVED FIRST SEMICOLON CHECK
        while sym == "PROCEDURE" or sym == "FUNCTION":
            saveSym = sym
            getsym()
            if sym == "ident":
                if saveSym == "PROCEDURE":
                    enter(tx, "procedure", level, codeIndx)
                    getsym()
                else:
                    enter(tx, "function", level, codeIndx)
                    getsym()
            else:
                error(4)
            block(tx[0], level + 1)
            if sym != "semicolon":
                error(10)
            getsym()
        # END OF CODE CHANGES
    fixJmp(cx1, codeIndx)
    if tx0 != 0:
        table[tx0].adr = codeIndx
    codeIndx0 = codeIndx
    gen("INT", 0, dx)
    statement(tx[0], level, tx0)
    gen("OPR", 0, 0)
    #print code for this block
    printCode()
#--------------STATEMENT----------------------------------------
def statement(tx, level, tx0):
    global sym, id, num;
    
    if sym == "ident":
        i = position(tx, id)
        if i==0:
            error(11)
        saveKind = table[i].kind
        saveID = id
        getsym()
        if sym != "becomes":
            error(13)
        getsym()
        expression(tx, level)
        
        # ADDED THE P CODE GENERATION FOR VAL AND REF
        if saveKind == "variable" or saveKind == "val":
            gen("STO", level - table[i].level, table[i].adr)
        elif saveKind == "function":
            i = position(tx, saveID)
            if i != tx0:
                error(37)
            gen("STO", 0, -1)
        elif saveKind == "ref":
            gen("STI", level - table[i].level, table[i].adr)
        else:
            error(34)
        # END OF CODE CHANGES
        
    elif sym == "CALL":
        getsym()
        if sym != "ident":
            error(14)
        i = position(tx, id)
        if i==0:
            error(11)
        if table[i].kind != "procedure":
            error(15)
        
        # ADDED THE ABILITY TO HAVE ACTUAL PARAMETERS IN CALL
        getsym()
        s = sym
        if sym == "lparen":
            p = 0
            gen("INT", 0, 3)
            while True:
                getsym()
                if table[i].params[p] == True:
                    j = position(tx, id)
                    if j==0:
                        error(11)
                    if sym != "ident":
                        error(14)
                    if table[j].kind == "variable" or table[j].kind == "val":
                        gen("LDA", level - table[j].level, table[j].adr)
                    elif table[j].kind == "ref":
                        gen("LOD", level - table[j].level, table[j].adr)
                    getsym()
                else:
                    expression(tx, level)
                p += 1
                if sym != "comma":
                    break
            if sym != "rparen":
                error(22)
            gen("INT", 0, -(3 + p))
        gen("CAL", level - table[i].level, table[i].adr)
        if s == "lparen":
            getsym()
        # END OF CODE CHANGES
        
    elif sym == "IF":
        getsym()
        generalexpression(tx, level)
        cx1 = codeIndx
        gen("JPC", 0, 0)
        fixed = False
        if sym != "THEN":
            error(16)
        getsym()
        statement(tx, level, tx0)
        if sym == "ELSE":
            getsym()
            cx2 = codeIndx
            gen("JMP", 0, 0)
            fixJmp(cx1, codeIndx)
            fixed = True
            statement(tx, level, tx0)
            fixJmp(cx2, codeIndx)
        if(fixed == False):
            fixJmp(cx1, codeIndx)
            
    elif sym == "BEGIN":
        while True:
            getsym()
            statement(tx, level, tx0)
            if sym != "semicolon":
                break
        if sym != "END":
            error(17)
        getsym()
        
    elif sym == "WHILE":
        getsym()
        cx1 = codeIndx
        generalexpression(tx, level)
        cx2 = codeIndx
        gen("JPC", 0, 0)
        if sym != "DO":
            error(18)
        getsym()
        statement(tx, level, tx0)
        gen("JMP", 0, cx1)
        fixJmp(cx2, codeIndx)
        
    elif sym == "REPEAT":
        cx = codeIndx
        while True:
            getsym()
            statement(tx, level, tx0)
            if sym != "semicolon":
                break
        if sym != "UNTIL":
            error(27)
        getsym()
        generalexpression(tx, level)
        gen("JPC", 0, cx)
        
    elif sym == "FOR":
        getsym()
        if sym != "ident":
            error(14)
        i = position(tx, id)
        if i==0:
            error(11)
        elif table[i].kind != "variable":
            error(12)
        getsym()
        if sym != "becomes":
            error(13)
        getsym()
        expression(tx, level)
        gen("STO", level - table[i].level, table[i].adr)
        if sym != "TO" and sym != "DOWNTO":
            error(29)
        saveSym = sym
        getsym()
        expression(tx, level)
        cx1 = codeIndx
        gen("CTS", 0, 0)
        gen("LOD", level - table[i].level, table[i].adr)
        if saveSym == "TO":
            gen("OPR", 0, 11)
        elif saveSym == "DOWNTO":
            gen("OPR", 0, 13)
        cx2 = codeIndx
        gen("JPC", 0, 0)
        if sym != "DO":
            error(18)
        getsym()
        statement(tx, level, tx0)
        gen("LOD", level - table[i].level, table[i].adr)
        gen("LIT", 0, 1)
        if saveSym == "TO":
            gen("OPR", 0, 2)
        elif saveSym == "DOWNTO":
            gen("OPR", 0, 3)
        gen("STO", level - table[i].level, table[i].adr)
        gen("JMP", 0, cx1)
        fixJmp(cx2, codeIndx)
        gen("INT", 0, -1)
        
    elif sym == "CASE":
        getsym()
        expression(tx, level)
        if sym != "OF":
            error(31)
        firstCase = True
        while True:
            getsym()
            if sym != "number" and sym != "ident":
                break
            if sym == "ident":
                i = position(tx, id)
                if i==0:
                    error(11)
                elif table[i].kind != "const":
                    error(25)
            gen("CTS", 0, 0)
            if sym == "number":
                gen("LIT", 0, num)
            elif sym == "ident":
                gen("LIT", 0, table[i].value)
            gen("OPR", 0, 8)
            cx1 = codeIndx
            gen("JPC", 0, 0)
            getsym()
            if sym != "colon":
                error(1)
            getsym()
            statement(tx, level, tx0)
            if sym != "semicolon":
                error(1)
            if firstCase:
                cx2 = codeIndx
                gen("JMP", 0, 0)
                firstCase = False
            else:
                gen("JMP", 0, cx2)
            fixJmp(cx1, codeIndx)
        if sym != "CEND":
            error(33)
        fixJmp(cx2, codeIndx)
        gen("INT", 0, -1)
        getsym()
        
    elif sym == "WRITE" or sym == "WRITELN":
        tempSym = sym
        getsym()
        if sym != "lparen":
            error(28)
        while True:
            getsym()
            expression(tx, level)
            gen("OPR", 0, 14)
            if sym != "comma":
                break
        if sym != "rparen":
            error(22)
        if tempSym == "WRITELN":
            gen("OPR", 0, 15)
        getsym()
#--------------EXPRESSION--------------------------------------
def expression(tx, level):
    global sym;
    if sym == "plus" or sym == "minus": 
        addop = sym
        getsym()
        term(tx, level)
        if (addop == "minus"):         #if minus sign, do negate operation
            gen("OPR", 0, 1)
    else:
        term(tx, level)
    
    while sym == "plus" or sym == "minus" or sym == "OR":
        addop = sym
        getsym()
        term(tx, level)
        if(addop == "minus"):
            gen("OPR", 0, 3)       #subtract operation
        else:
            gen("OPR", 0, 2)       #add operation  
#-------------TERM----------------------------------------------------
def term(tx, level):
    global sym;
    factor(tx, level)
    
    while sym=="times" or sym=="slash" or sym == "AND":
        mulop = sym
        getsym()
        factor(tx, level)
        if mulop == "slash":
            gen("OPR", 0, 5)         #divide operation
        else:
            gen("OPR", 0, 4)         #multiply operation
#-------------FACTOR--------------------------------------------------
def factor(tx, level):
    global sym, num, id;
    if sym == "ident":
        z = position(tx, id)
        if z==0:
            error(11)
        
        # ADDED THE ABILITY TO GENERATE P CODE FOR VAL AND REF
        if table[z].kind == "const":
            gen("LIT", 0, table[z].value)
        elif table[z].kind == "variable" or table[z].kind == "val":
            gen("LOD", level-table[z].level, table[z].adr)
        elif table[z].kind == "ref":
            gen("LDI", level - table[z].level, table[z].adr)
        elif table[z].kind == "procedure" or table[z].kind == "function":
            error(21)
        # END OF CODE CHANGES
        
        getsym()
        
    elif sym == "number":
        gen("LIT", 0, num)
        getsym()
    elif sym == "lparen":
        getsym()
        generalexpression(tx, level)
        if sym != "rparen":
            error(22)
        getsym()
    
    elif sym == "CALL":
        getsym()
        if sym != "ident":
            error(36)
        i = position(tx, id)
        if i == 0:
            error(11)
        if table[i].kind != "function":
            error(35)
        gen("INT", 0, 1)
        
        # ADDED THE ABILITY TO HAVE ACTUAL PARAMETERS IN CALL
        getsym()
        s = sym
        if sym == "lparen":
            p = 0
            gen("INT", 0, 3)
            while True:
                getsym()
                if table[i].params[p] == True:
                    j = position(tx, id)
                    if j==0:
                        error(11)
                    if sym != "ident":
                        error(14)
                    if table[j].kind == "variable" or table[j].kind == "val":
                        gen("LDA", level - table[j].level, table[j].adr)
                    elif table[j].kind == "ref":
                        gen("LOD", level - table[j].level, table[j].adr)
                    getsym()
                else:
                    expression(tx, level)
                p += 1
                if sym != "comma":
                    break
            if sym != "rparen":
                error(22)
            gen("INT", 0, -(3 + p))
        gen("CAL", level - table[i].level, table[i].adr)
        if s == "lparen":
            getsym()
        # END OF CODE CHANGES
    
    elif sym == "NOT":
        getsym()
        factor(tx, level)
        gen("LIT", 0, 0)
        gen("OPR", 0, 8)
    else:
        error(24)
#-----------generalexpression-------------------------------------------------
def generalexpression(tx, level):
    global sym;
    if sym == "ODD":
        getsym()
        expression(tx, level)
        gen("OPR", 0, 6)
    else:
        expression(tx, level)
        if sym in ["eql","neq","lss","leq","gtr","geq"]:
            temp = sym
            getsym()
            expression(tx, level)
            if temp == "eql":
                gen("OPR", 0, 8)
            elif temp == "neq":
                gen("OPR", 0, 9)
            elif temp == "lss":
                gen("OPR", 0, 10)
            elif temp == "geq":
                gen("OPR", 0, 11)
            elif temp == "gtr":
                gen("OPR", 0, 12)
            elif temp == "leq":
                gen("OPR", 0, 13)
#-------------------MAIN PROGRAM------------------------------------------------------------#

# ADDED RESEREVED WORDS: 'VAL' and 'REF'
rword.append('AND')
rword.append('BEGIN')
rword.append('CALL')
rword.append('CASE')
rword.append('CEND')
rword.append('CONST')
rword.append('DO')
rword.append('DOWNTO')
rword.append('ELSE')
rword.append('END')
rword.append('FOR')
rword.append('FUNCTION')
rword.append('IF')
rword.append('NOT')
rword.append('ODD')
rword.append('OF')
rword.append('OR')
rword.append('PROCEDURE')
rword.append('REF')
rword.append('REPEAT')
rword.append('THEN')
rword.append('TO')
rword.append('UNTIL')
rword.append('VAL')
rword.append('VAR')
rword.append('WHILE')
rword.append('WRITE')
rword.append('WRITELN')

ssym = {'+' : "plus",
             '-' : "minus",
             '*' : "times",       
             '/' : "slash",
             '(' : "lparen",
             ')' : "rparen",
             '=' : "eql",
             ',' : "comma",
             '.' : "period",
             '#' : "neq",
             '<' : "lss",
             '>' : "gtr",
             '"' : "leq",
             '@' : "geq",
             ';' : "semicolon",
             ':' : "colon",}
charcnt = 0
whichChar = 0
linelen = 0
ch = ' '
kk = al                
a = []
id= '     '
errorFlag = 0
table.append(0)    #making the first position in the symbol table empty
sym = ' '       
codeIndx = 0         #first line of assembly code starts at 1
prevIndx = 0
infile =    sys.stdin       #path to input file
outfile =  sys.stdout     #path to output file, will create if doesn't already exist

getsym()            #get first symbol
block(0, 0)             #call block initializing with a table index of zero
if sym != "period":      #period expected after block is completed
    error(9)
print  
if errorFlag == 0:
    print >>outfile, "Successful compilation!\n"
    
Interpret()