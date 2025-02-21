#Test Coverage Analyzer

##Introduction
This project is a comprehensive tool to analyse a provided test suite for
a piece of software. The analysis covers two key white-box testing metrics: statement coverage
and branch coverage. The aim is to assess the efficacy and thoroughness of the test suite in detecting
faults and ensuring robustness in the software.

##Objectives
• Implement a tool that takes a series of given test inputs and runs them on a program.
• Report the statement coverage and branch coverage for the program when run using the series
of test inputs.

##Requirements
1. Statement Coverage
Objective: Determine the percentage of executable statements in the software that are executed by
the test cases in the test suite.
2. Branch Coverage
Objective: Identify and report the number of branches through the program’s control flow graph that
are covered by the test suite.

##Input Specifications
The program take 2 command-line arguments:
1. The path to a Python script
2. The path to a directory containing a set of input (.in) files

Program is called using the following command:
python coverage.py <python_program> <input_file_dir>
