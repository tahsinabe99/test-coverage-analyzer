import sys, os, ast
from statementCov import Coverage, cond, branch, BranchCoverage, CoverageTransformer, output

def input_provider(inputs):
    for inp in inputs:
        yield inp

def main():
    #checking for enough inputs
    if len(sys.argv) != 3:
        print("Some input is missing")
        sys.exit(1)

    #openning the files given
    program_file = sys.argv[1]
    input_file_dir = sys.argv[2]

    if not os.path.isfile(program_file) and not os.path.isdir(input_file_dir):
        sys.exit(1)

    with open(program_file, 'r') as file:
        program_lines = file.readlines()

    coverage = Coverage()
    coverage.setup_lines(program_lines) #we store all the program lines
    
    x=''.join(program_lines) 
    x=x.strip()
    brCov=CoverageTransformer()

    parsed_code=brCov.parseCode(x)
    brCov.visit(parsed_code)
    new_code=ast.unparse(parsed_code)
    
    #printing the output of the file in a .out file
    original_Stdout=sys.stdout
    with open("output.out", "w") as outputfile:
        sys.stdout=outputfile
    
    #for statement coverage
        for input_file in sorted(os.listdir(input_file_dir)):
            if input_file.endswith('.in'):
                full_path=os.path.join(input_file_dir, input_file)
                with open (full_path, 'r') as file:
                    input_data=file.read()
                    input_data=input_data.strip()
                    input_data_list=input_data.split('\n')
                    #print(input_data_list)
                    
                
                input_gen= input_provider(input_data_list)        
                local_context = {'input': lambda *args, **kwargs: next(input_gen)}
                with coverage:
                    exec(''.join(program_lines), globals(), local_context)
                coverage.code_ran()

        #for branch coverage
        for input_file in sorted(os.listdir(input_file_dir)):
            if input_file.endswith('.in'):
                full_path=os.path.join(input_file_dir, input_file)
                with open (full_path, 'r') as file:
                    input_data=file.read()
                    input_data=input_data.strip()
                    input_data_list=input_data.split('\n')

                
                input_gen= input_provider(input_data_list)        
                local_context = {'input': lambda *args, **kwargs: next(input_gen)}
                exec(new_code, globals(), local_context)

    
    bc = BranchCoverage()
    

    sys.stdout=original_Stdout
    #print(bc.calculate_branch_coverage())
    #bc.report()
    output(coverage.statementCoverage(), bc.calculate_branch_coverage())



    




    

    
    
    # print(coverage)
    # print(coverage.statementCoverage())
    
    

if __name__ == "__main__":
    main()

