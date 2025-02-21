import sys, trace, inspect, string, ast, math
branch_coverage = {}
Counter=0

"""
Reference URLS
https://edstem.org/au/courses/15196/lessons/51460/slides/349548

"""

def cond(cond_id, condition):
    """
    Records the evaluation of a condition.
    Stores condition id for each condition to keep track of how many times each conditio has been evaluated
    [0,0] 1st element counts how many times conditionn evaluated , second element counts how many times  each possible branch has been taken
    introduced third element in the list for taking into account the false branch of if statements

    """
    global branch_coverage
    branch_coverage.setdefault(cond_id, [0, 0,0])[0] += 1
    return condition

def branch(cond_id, kind):
    """
    Records the branch taken for a given condition.
    """
    global branch_coverage
    #branch_coverage.setdefault(cond_id, [0, 0])[1] += kind
    if cond_id not in branch_coverage:
        branch_coverage[cond_id]=[0,0,0]
    else:
        
        if kind == 1:
            branch_coverage[cond_id][1]+=1
        elif kind==-2:
            branch_coverage[cond_id][1]+=-2
        elif kind==math.sqrt(2):
             branch_coverage[cond_id][2]+=math.sqrt(2)
        else:
            branch_coverage[cond_id][2]+=1

    

class Coverage():
    def __init__(self):
        self.trace = []  #-- the usual
        #will store all the lines of the code
        self.all_lines = {} #dictionary with key as line number, tuple (line, bool)
       
    
    def traceit(self, frame, event, arg):
        if event == "line":
            #contains metadata about the code
            code_data=frame.f_code
            fileName=code_data.co_filename
            lineNo=frame.f_lineno
            self.trace.append((fileName, lineNo))


        return self.traceit
    
    def __enter__(self):  #the usual form tute
        """
        Sets the trace function to this instance's traceit method.
        """
        self.orig_trace = sys.gettrace()
        sys.settrace(self.traceit)
        return self


    def __exit__(self,exc_type, exc_value, tb):  #from tute
        """
        Restores the original trace function upon exiting the context.
        """
        sys.settrace(self.orig_trace)
    
    def coverage(self):  #from tute
        """
        Returns a set of tuples representing the covered lines.
        """
        return set(self.trace)
    
    def setup_lines(self, programLines):
        for indx, line in enumerate(programLines, 1):
            #checking for comments and empty lines
            line=line.strip()
            
            if line.startswith('#') or len(line)==0 or "else" in line:
                continue
            
            self.all_lines[indx]=(line, False) #storing code and false to indicate not ran

    
    def code_ran(self):
        for line, lineNo in self.trace:
            if lineNo in self.all_lines:
                lineCode=self.all_lines[lineNo][0]
                self.all_lines[lineNo]=(lineCode, True)

    
    def statementCoverage(self):
        lineRan=0
        total=0

        for lineNo, (line, ran) in self.all_lines.items():
            if ran:
                lineRan+=1
            total+=1
        statementCoverage=(lineRan/total)*100
        return statementCoverage
    

    def __repr__(self):
        result = ""
        for lineno, (line, executed) in self.all_lines.items():
            indicator = "Executed" if executed else "Not executed"
            result += f"{lineno}: {line.strip()} - {indicator}\n"
        return result
    

class CoverageTransformer(ast.NodeTransformer):
    """
    A custom AST transformer that instruments the code for branch coverage analysis.
    """
    def visit_If(self, node):
        """
        Visits each 'if' node in the AST and instruments it for branch coverage.
        """
        global Counter
        self.generic_visit(node)  # Visit all other node types
        node.test = self.make_test(node.test, Counter)
        node.body = self.make_body(node.body, node, Counter, 1)
        node.orelse = self.make_body(node.orelse, node, Counter, 0)
        Counter += 1
        return node
    
    def visit_IfExp(self, node):  #inspired from tute
        """
         visit_IfExp  used to handle ternary conditions.
        """
        global Counter
        self.generic_visit(node)  # Visit all other node types
        node.test = self.make_test(node.test, Counter)
        node.body = self.make_body_ternary(node.body, Counter, -2)
        node.orelse = self.make_body_ternary(node.orelse, Counter, math.sqrt(2))
        Counter += 1
        return node
    
    def visit_For(self, node):
        global Counter
        self.generic_visit(node)  
        node.iter=self.make_test(node.iter, Counter)
        node.body=self.make_body(node.body, node, Counter, 1)
        node.orelse=self.make_body(node.orelse, node, Counter, 0)
        Counter+=1
        return node
    
    def visit_Try(self, node) :
        global Counter
        self.generic_visit(node) 
        node.test = self.make_test(node.test, Counter)
        node.body = self.make_body(node.body, node, Counter, 1)

        for each_except in node.handlers:
            each_except.make_body(node.orelse, node, Counter, 0)
        
        Counter+=1
        return node

    def visit_Match(self, node):
        global Counter
        self.generic_visit(node) 
        node.test = self.make_test(node.test, Counter)
        node.body = self.make_body(node.body, node, Counter, 1)

        for each_case in node.handlers:
            each_case.make_body(node.orelse, node, Counter, 0)
        
        Counter+=1
        return node


    def visit_GeneratorExp(self, node):
        global Counter
        self.generic_visit(node)
        for item in node.generators:
            item.iter=self.make_test(item.iter, Counter)
            Counter+=1

            conditions=[]

            for condition in item.ifs:
                conditions.append(self.make_test(condition, Counter))
                Counter+=1
            item.ifs=conditions
        return node
        

    def make_body(self, block, node, Counter, kind):
        """
        Instruments the body of an 'if' or 'else' block.
        """
        new_node = ast.Expr(ast.Call(func=ast.Name(id='branch', ctx=ast.Load()),
                            args=[ast.Constant(Counter), ast.Constant(kind)],
                            keywords=[]))
        ast.copy_location(new_node, node)
        return [new_node] + block
       
    #Same as make body but since IfExp expects single node and not list
    def make_body_ternary(self, node, Counter, kind):  #inspired from tute, for ternary conditions
        # return ast.Call(
        #     func=ast.Name(id='branch', ctx=ast.Load()),
        #     args=[ast.Constant(Counter), ast.Constant(kind)],
        #     keywords=[]
        # )
        new_node = ast.Expr(ast.Call(func=ast.Name(id='branch', ctx=ast.Load()),
                            args=[ast.Constant(Counter), ast.Constant(kind)],
                            keywords=[]))
        ast.copy_location(new_node, node)
        return new_node
    

    def make_test(self, test, Counter):
        """
        Instruments the test condition of an 'if' statement.
        """
        new_test = ast.Call(func=ast.Name(id="cond", ctx=ast.Load()),
                         args=[ast.Constant(Counter), test],
                         keywords=[])
        ast.copy_location(new_test, test)
        return new_test


    def parseCode(self, programLines):
        v = ast.parse(programLines)
        # self.visit(v)
        # print(ast.unparse(v))
        return v


class BranchCoverage:
    """
    A class to analyze and report branch coverage based on the recorded execution paths.
    """
    def report(self):
        """
        Generates a report of the branch coverage analysis.
        """
        for cond_id, (conditions_evaluated, branches_taken) in branch_coverage.items():
            print(f"Condition {cond_id}: Evaluated {conditions_evaluated} times, Branch taken {branches_taken} times")

    def calculate_branch_coverage(self):

        total_branches = len(branch_coverage)
        #print(total_branches)
        if(total_branches)==0:
            return 100
        total_branch=0
        executed_branch=0
        for cond_id, list_of_branches in branch_coverage.items():
            #print(cond_id, "->", list_of_branches)
            total_branch+=2
            if list_of_branches[1]>0:
                executed_branch+=1
            elif list_of_branches[1]<0:
                total_branch-=1
                executed_branch+=1
            if list_of_branches[2] % (math.sqrt(2))==0 and list_of_branches[2]!=0:
                total_branch-=1
            elif list_of_branches[2]>0:
                executed_branch+=1 
                      
        #print("Total branch: ",total_branch, "executed branch", executed_branch)
        # if executed_branch==0:
        #     return 0
        total_branch_coverage= (executed_branch/total_branch)*100
        return total_branch_coverage

    def printdict(self):
        # for key, value in branch_coverage.items():
        #     print(key, "->", value)
        print(branch_coverage)

def output(statementCov, branchCov):
        print("Statement Coverage: {:.2f}%".format(statementCov))
        print("Branch Coverage: {:.2f}%".format(branchCov))
