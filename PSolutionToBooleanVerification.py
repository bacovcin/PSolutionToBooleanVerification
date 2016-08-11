# Boolean functions must be input into the parser with the following structure:
# All operations (including the top operation) must be surrounded by parenthesis
# The function operating on the parentheses is then combined with the opening
# parenthesis "(-". The following three operations are defined: & (AND), | (OR),
# and (- (NOT). All clauses  and basic propositions joined by the operators are
# then separated by a space (including a space between the final operator and
# the closing parenthesis. Example: (& A B (- C ) (- (| C D ) ) )


class PropClause:
    def __init__(self, typeof, contents):
        if typeof in ['&', '-']:
            self.typeof = typeof
        else:
            raise TypeError('Not a valid operator')
        if typeof == '-' and len(contents) != 1:
            print(contents)
            print(len(contents))
            raise TypeError('Provided non unary contents to unary operator')
        else:
            self.contents = frozenset(contents)

    def aSolution(self):
        if self.isSatisfiable():
            solution = {}
            if self.typeof == '-':
                lx = list(self.contents)
                if type(lx[0]) is str:
                    solution[lx[0]] = False
                else:
                    neg_sol = lx[0].aSolution()
                    for key in neg_sol.keys():
                        solution[key] = not neg_sol[key]
            else:
                for x in list(self.contents):
                    if type(x) is str:
                        solution[x] = True
                    else:
                        lx = list(x.contents)
                        if type(lx[0]) is str:
                            solution[lx[0]] = False
                        else:
                            neg_sol = lx[0].aSolution()
                            for key in neg_sol.keys():
                                if key not in solution.keys():
                                    solution[key] = not neg_sol[key]
            return solution
        else:
            return False

    def isSatisfiable(self):
        if self.typeof == '-':
            return True
        for x in (self.contents):
            try:
                if x.typeof == '-':
                    lx = list(x.contents)
                    if type(lx[0]) is str:
                        for y in list(self.contents):
                            if y == lx[0]:
                                return False
                    else:
                        for y in list(lx[0].contents):
                            for z in list(self.contents):
                                if z == y:
                                    break
                            else:
                                break
                        else:
                            return False
            except AttributeError:
                continue
        else:
            return True

    def __str__(self):
        return str('(' + self.typeof + ' ' +
                   ' '.join([str(x) for x in list(self.contents)]) + ' ' + ')')

    def __eq__(self, other):
        try:
            if self.typeof == other.typeof:
                if self.contents == other.contents:
                    return True
        except:
            return False

    def __hash__(self):
        return hash(frozenset([self.typeof, self.contents]))


def ParseFormula(x):
    # All formulas start with an open parenthesis
    # Second element in string is type of operator (&, |, or -)
    typeof = x[1]
    # Initialise elements that are operated over
    contents = []
    # Start looking from the 3rd element
    i = 2
    # Track the current element name
    element = ''
    # Iterate through the string
    while i < len(x):
        # Track the current character
        c = x[i]
        # If the character is an open parenthesis recurse the parse function
        if c == '(':
            y = ParseFormula(x[i:])
            contents += y[0]
            i += y[1]
        # Jump up a level if a end parenthesis is reached
        elif c == ')':
            i += 1
            break
        # If a space is reached append the current element name to list of
        # contents and reset the element tracker
        elif c == ' ':
            if element != '' and ' ' not in element:
                contents.append(element)
            element = ''
            i += 1
        # Current character is part of the name of an element, so add it to the
        # element tracker
        else:
            element += c
            i += 1
    # Create negative clauses
    if typeof == '-':
        try:
            # Eliminate double negation
            if contents[0].typeof == '-':
                outClause = [list(contents[0].contents)[0]]
            else:
                outClause = [PropClause('-', contents)]
        except AttributeError:
            outClause = [PropClause('-', contents)]
    # Replace disjunction by conjunction
    elif typeof == '|':
        newcontents = []
        for x in contents:
            if type(x) is str:
                newcontents.append(PropClause('-', [x]))
            elif x.typeof == '-':
                if type(list(x.contents)[0]) is str:
                    newcontents.append(list(x.contents)[0])
                else:
                    newcontents += list(list(x.contents)[0].contents)
            else:
                newcontents.append(PropClause('-', [x]))
        outClause = [PropClause('-', [PropClause('&', newcontents)])]
    # Create conjunctive clauses
    else:
        # Reduce double conjunctions
        newcontents = []
        for x in contents:
            try:
                if x.typeof == '&':
                    newcontents += list(x.contents)
                else:
                    newcontents.append(x)
            except:
                newcontents.append(x)
        outClause = [PropClause('&', newcontents)]
    return (outClause, i)


a = '(& A B (- C ) (- (| C D ) ) )'
a = '(| A (- A ) )'
# a = '(& (| x1 y1 ) (| x2 y2 ) (| x3 y3 ) (| x4 y4 ) (- x3 ) (- y3 ) )'
b = ParseFormula(a)
print(b[0][0])
print(b[0][0].isSatisfiable())
print(b[0][0].aSolution())
