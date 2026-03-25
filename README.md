USAGE: python3 hpasm.py [input_file] [output_file] 
Released under the MIT license 

This is the simplest possible assembler I could come up with for the HP21xx platform. There are most certainly bugs in the code. This code will be updated with time. 

For now, the assembler works for basic code. 

Instruction pairs such as CLA,INA need a space between the first and second instruction, such as CLA ,INA 

Labels are defined with a colon ":"

Variables are defined with OCT and DEC for octal and decimal.

Origins are defined with an ORG

comments can be made with a semicolon. 

