# Boolean functions must be input into the parser with the following structure:
# All operations (including the top operation) must be surrounded by parenthesis
# The function operating on the parentheses is then combined with the opening
# parenthesis "(-". The following three operations are defined: & (AND), | (OR),
# and (- (NOT). All clauses  and basic propositions joined by the operators are
# then separated by a space (including a space between the final operator and
# the closing parenthesis. Example: (& A B (- C ) (- (| C D ) ) )


class PropClause(object):
    def __init__(self, typeof, contents):
        # Propositions can be conjunctions, negation or terminal propositions
        # Check to make sure proper type was sent
        if typeof in ['&', '-', 't']:
            self.typeof = typeof
        else:
            raise TypeError('Not a valid operator')
        # Assign contents to proposition
        self.contents = frozenset(contents)
        # Make sure content is list of propositions (possibly unary)
        if False in [type(x) != '__main__.PropClause' for x in contents] and self.typeof != 't':
            raise TypeError('Contents are not propositions')
        else:
            # Recursive check for satisfiability
            # Three possible condtions:
            #   1) Terminal proposition (return satisfiable)
            #   2) Conjunction (check for contradictions)
            #   3) Negation (depends on content):
            #       a) If satisfiable, return satisfiable
            #       b) If contradictory, return tautological
            #       c) If tautological, return contradictory
            # Possible responses are: Satisfiable ('s'), Contradictory ('c'), or
            # Tautological ('t')
            # At end:
            #   Return True if not contradictory, otherwise return False
            if self.typeof == 't':
                self.satisfiable = 's'
            elif self.typeof == '-':
                if typeof == '-' and len(contents) != 1:
                    # Negation is a unary operator
                    raise TypeError('Provided non unary contents to unary operator')
                elif contents[0].satisfiable == 's':
                    self.satisfiable = 's'
                elif contents[0].satisfiable == 'c':
                    self.satisfiable = 't'
                elif contents[0].satisfiable == 't':
                    self.satisfiable = 'c'
            else:  # self.typeof == '&'
                # Contradictions arise when containing a negative conjunct
                # whose contents are a subset of the non-negative content of
                # the conjunction
                satiscon = [x.satisfiable for x in contents]
                if 'c' in satiscon: 
                    # Conjunction of contradictions are contradictions
                    self.satisfiable = 'c'
                if 's' not in satiscon:
                    # Conjunction of tautologies is a tautology
                    self.satisfiable = 't'
                else:
                    # Collect all negative content and use that to test for
                    # contradiction by checking if the content of each is a
                    # subset of the content of the conjunction
                    negatives = []
                    for x in contents:
                        if x.typeof == '-' and x.satisfiable != 't':
                            if list(x.contents)[0].typeof == 't':
                                negatives.append(set(x.contents))
                            else:
                                negatives.append(set(list(x.contents)[0].contents))
                    setcon = set([x for x in contents if x.satisfiable != 't'])
                    for neg in negatives:
                        if neg.issubset(setcon):
                            # The contents of the negative conjunct is a subset
                            # of the whole set, which is a contradiction (e.g.,
                            # A & -A)
                            self.satisfiable = 'c'
                            break
                    else:
                        # No contradictions were found, so the conjunction must
                        # be satisfiable
                        self.satisfiable = 's'

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
                contents.append(PropClause('t',[element]))
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
            if x.typeof == 't':
                newcontents.append(PropClause('-', [x]))
            elif x.typeof == '-':
                if list(x.contents)[0].typeof == 't':
                    newcontents += x.contents
                else:
                    newcontents += list(x.contents)[0].contents
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
a = '(& (| x1 y1 ) (| x2 y2 ) (| (- x3 ) (- y3 ) ) (| x4 y4 ) x3 (- y3 ) )'
a = '(& (- (& A (- A ) ) ) (- A ) B C (| (- B ) D ) )'
a = '(& (- (| A (- A ) ) ) (- (& B (- B ) ) ) )'
b = ParseFormula(a)
print(b[0][0])
print(b[0][0].satisfiable)
