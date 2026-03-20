import sys

def double_loc_inst(self,machine_code,instruction,operand,line):
    machine_code.append((self.lc, instruction, line.strip()))
              
    if operand is None:
        print ("No Memory Address Defined In Extended Arithmetic Memory Reference Instruction") 
        return 
              
    self.lc += 1
    machine_code.append((self.lc,int(operand,8)," "))

class HP1000Assembler:
    def __init__(self):
        self.symbol_table = {}
        self.location_counter = 0
        
        # 1. Memory Reference (MRI)
        self.mri = {
        "ADA": 0o040000, "ADB": 0o044000, "AND": 0o010000,
        "CPA": 0o054000, "CPB": 0o050000, "IOR": 0o030000, 
        "ISZ": 0o034000, "JMP": 0o024000, "JSB": 0o014000,
        "LDA": 0o060000, "LDB": 0o064000, "STA": 0o070000,
        "STB": 0o074000, "XOR": 0o020000
        }

        self.non_mri = { 
            
        "ALF": 0o001700, "ALR": 0o001400, "ALS": 0o001000, 
        "ARS": 0o001100, "BLF": 0o005700, "BLR": 0o005400,
        "BLS": 0o005020, "BRS": 0o005100, "CLE": 0o000040, 
        "ELA": 0o001600, "ELB": 0o005600, "ERA": 0o001500,
        "ERB": 0o005500, "NOP": 0o000000, "RAL": 0o001200,
        "RAR": 0o001300, "RBL": 0o005200, "RBR": 0o005300, 
        "SLA": 0o000010, "SLB": 0o004010,

        "CLA": 0o002400, "CLB": 0o006400, "CMA": 0o000200, 
        "CMB": 0o004200, "CCA": 0o000600, "CCB": 0o004600,
        "CLE": 0o000100, "CME": 0o000040, "CCE": 0o000140,
        "SZA": 0o002002, "SZB": 0o006002, "RSS": 0o002001,
        "CLC": 0o106700, "CLF": 0o103100, "CLO": 0o103101,
        "INA": 0o002004, "SEZ": 0O002040, "INB": 0o006004,
        "SSA": 0o002020, "SSB": 0o006020
        }

        self.io = { 
        "HLT": 0o102000, "LIA": 0o102500, "LIB":0o106500, 
        "MIA": 0o102400, "MIB": 0o106400, "OTA":0o102600,
        "OTB": 0o106600, "SFC": 0o102200, "SFS":0o102300, 
        "SOC": 0o102201, "SOS": 0o102301, "STC":0o102700,
        "STF": 0o102100, "STO": 0o102101, "CLO":0O103101,
        "CLC": 0o106700
        }
        
        self.eamr = { #eamr is extended memory reference 
        "DIV": 0o100400, "DLD":0o104200, "DST":0o104400,
        "MPY": 0o100200
        }
        self.earr = {
        "ASR": 0o101020, "ASL": 0o100020, "LSR": 0o101040,
        "LSL": 0o100040, "RRR": 0o101100, "RRL": 0o100100 


        }
        self.itw = { # instructions triple word
            "TBS": 0o105775, "SBS": 0o105774, "CBS":0o105776,  

        }
        self.idw = { # instructions double word
            "ADX": 0o105746, "ADY": 0o105756, "LAX": 0o101742, 
            "LAY": 0o101752, "LBX": 0o105742, "LBY": 0o105752, 
            "LDX": 0o105745, "LDY": 0o105755, "SAX": 0o101740,
            "SAY": 0o101750, "STX": 0o105743, "STY": 0o105753, 
            "JLY": 0o105762, "JPY": 0o105772, "CBT": 0o105766, 
            "MBT": 0o105765, "XSB": 0o105725, "XSA": 0o101725, 
            "XMS": 0o105721, "CMW": 0o105776, "MVW": 0o105777,
            "FAD": 0o105000, "FDV": 0o105060, "FMP": 0o105040,
            "FSB": 0o105020
        }
        

        self.isw = { # instructions single word 
            "CAX": 0o101741, "CAY": 0o101751, "CBX": 0o105741, 
            "CBY": 0o105751, "CXA": 0o101744, "CXB": 0o105754, 
            "CYA": 0o101754, "CYB": 0o105754, "DSX": 0o105761,
            "DSY": 0o105771, "ISX": 0o105760, "ISY": 0o105770,
            "XAX": 0o101747, "XAY": 0o101757, "XBX": 0o105747, 
            "XBY": 0o105757, "LBT": 0o105763, "SFB": 0o105767,
            "SBT": 0o105764, "XMA": 0o101722, "XMM": 0o105720,
            "XMB": 0o105722, "FIX": 0o105120, "FLT": 0o105120,


        }
        self.bit = {
        }
        self.extra = {}
        self.symbols = {}
        self.define = {}
        self.lc = 0  # Location Counter

   


    def parse_line(self, line):
        """Extracts Label, Mnemonic, and Operand from a line."""
        line = line.split('/')[0].strip() # Remove comments
        if not line: return None, None, None
        
        label = None
        # Labels in HP1000 usually end with a comma
        if ':' in line.split()[0]:
            parts = line.split(maxsplit=1)
            label = parts[0].replace(':', '')
            line = parts[1] if len(parts) > 1 else ""
            
        parts = line.split()
        mnemonic = parts[0] if len(parts) > 0 else None
        operand = parts[1] if len(parts) > 1 else None
        return label, mnemonic, operand

    def pass_one(self, source):
        """First Pass: Populate Symbol Table."""
        self.lc = 0
        for line in source:
            label, mnemonic, _ = self.parse_line(line)
            if label:
                self.symbols[label] = self.lc
            
            if mnemonic == 'ORG':
                _, _, op = self.parse_line(line)
                self.lc = int(op, 8)

            elif mnemonic:
                self.lc += 1

    def pass_two(self, source):
        """Second Pass: Generate Binary/Octal."""
        self.lc = 0
        machine_code = []
        
        for line in source:
            _, mnemonic, operand = self.parse_line(line)
            if not mnemonic or mnemonic == 'ORG':
                if mnemonic == 'ORG': self.lc = int(operand, 8)
                continue

            instruction = 0
            
            if operand in self.symbols:
                addr = self.symbols[operand]
                # Bit 10-0 is the address; Bit 11 is the 'Current Page' flag
                # If addr is on page 0 (0-1023), bit 11 is 0.
                page_bit = 0o004000 if addr > 0o1777 else 0
                instruction |= (page_bit | (addr & 0o3777))
            else:
                    print(f"Error: Undefined label '{operand}' at line {line}")

            if mnemonic in self.mri:
                instruction = self.mri[mnemonic]
                # Check for indirect bit
                
                if (',I') in operand: #set I bit
                    instruction |= 0b1000000000000000
                    operand = operand[:-2]
               
                if (',C') in operand: #set c bit
                    instruction |= 0b10000000000
                    operand = operand[:-2]
               
                if (',I,C') in operand: #set both (better way to do this is to use shifts, TODO: use shifts)
                    instruction |= 0b1000000000000000 | 0b10000000000
                    operand = operand[:-4]
              
                if "*" in operand: #check if we're using relative mode. 
                    bin_operand = int(operand.split('*',1)[-1],8) #if relative, split, get offset
                    bin_self_lc = self.lc #temporary location counter
                    instruction |=  bin_operand + bin_self_lc #add the offset to the current location. 
              
                if operand.isdigit(): #if we're defining a number after the instruction
                    operand_oct = int(operand,8) # force it to be octal
                    if operand_oct < 0o1001: #limit it,
                        instruction |= operand_oct #append it
                    else:
                        instruction |= 0o1000 #if out of bounds, restrain it. 
                
                if operand.isalpha():
                    operand_oct =self.symbols[operand]
                    instruction |= operand_oct

            if mnemonic in self.idw or mnemonic in self.eamr:                 
                try:
                    instruction = self.idw[mnemonic]  #if instruction is in idw, take the opcode from there
                except:
                    instruction = self.eamr[mnemonic] #if the instruction is in eamr, opcode lives there. 
                double_loc_inst(self,machine_code,instruction,operand,line) #double loc inst is for instructions that take more than one word of memory. 
            
            if mnemonic in self.isw: #isw instructions don't have operands, so return the octal from the dict. 
                instruction = self.isw[mnemonic]

            if mnemonic in self.earr: #if earr, append the operand to the last 4 bits. 
                instruction = self.earr[mnemonic]
                instruction |= (0o17 & int(operand,8))

            if mnemonic in self.non_mri: #if combinational "," split and combine opcodes. This right now will allow illegal combinations and may cause unintended results. 
                instruction = self.non_mri[mnemonic]
                try:
                    if "," in operand:
                        additional_operand = operand.split(",")[1]
                        instruction |= self.non_mri[additional_operand]
                except: 
                        instruction = self.non_mri[mnemonic] # if not combinational, just use the mnemonic. 

            if mnemonic in self.io: #if the instruction is in the IO section. 
                instruction = self.io[mnemonic] # grab instruction
                try:
                    operand_oct_io = int(operand,8) #add operand 
                    if operand.isdigit() & operand_oct_io < 0o100: #check boundary condition 
                        instruction |= operand_oct_io
                except: 
                    print("Error: IO instruction has no operand or referenced out of bounds IO address") #print an error if there is one. 
           

            if mnemonic == 'DEC':
                instruction = int(operand) & 0xFFFF
            if mnemonic == 'OCT':
                instruction = int(operand, 8) & 0xFFFF
            
            if mnemonic not in self.eamr and mnemonic not in self.idw:
                machine_code.append((self.lc, instruction, line.strip()))
                self.lc += 1

        return machine_code

# --- Testing the Label Resolution ---
asm_source = [

]
parsed_source = []

argument_len = len(sys.argv)
input_file_name = sys.argv[1]
output_file_name = sys.argv[2]
#output_file_bin = sys.argv[3]
print(input_file_name)
print(output_file_name)

with open(input_file_name, "r") as input_file, open(output_file_name, "w") as output_file: 
    asm_source = input_file.readlines()
    print(asm_source)
    assembeler = HP1000Assembler()
    assembeler.pass_one(asm_source)
    results = assembeler.pass_two(asm_source)
    print(results)
    output_file.writelines(f"{'LOC':<6} | {'OCTAL':<6} | {'SOURCE'}" + "\n")
    output_file.writelines("-" * 45 + "\n")
    for loc, code, src in results:
        output_file.writelines(f"{oct(loc)[2:]:>6} | {oct(code)[2:].zfill(6):>6} | {src}\n")
    
input_file.close()
output_file.close()


