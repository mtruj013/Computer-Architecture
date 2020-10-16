"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.running = True
        self.operand_a = self.ram_read(self.pc + 1)
        self.operand_b = self.ram_read(self.pc + 2)
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        self.reg[7] = 0xF4
        self.sp = self.reg[7]
        self.equal_fl = 0
        self.greater_fl = 0
        self.less_fl = 0


    def handle_HLT(self):
        self.running = False
        sys.exit(1)
        self.pc += 1

    def handle_LDI(self, operand_a, operand_b):

        reg_num = operand_a
        value = operand_b
        self.reg[reg_num] = value
        self.pc += 3

    def handle_PRN(self, operand_a):
        reg_num = operand_a
        print(self.reg[reg_num])
        self.pc += 2

    def handle_MUL(self, op, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def handle_PUSH(self):
        self.sp -= 1 # decrease stack pointer
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        self.ram[self.sp] = value
        self.pc += 2 # b/c this is 2 bits

    def handle_POP(self):
        value = self.ram[self.sp]
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value
        self.sp += 1 # increase stack pointer
        self.pc += 2

    def handle_CALL(self):
        # Get address of the next instruction after the CALL
        return_addr = self.pc + 2
        self.sp -= 1
        # Push it on the stack
        # self.handle_PUSH(return_addr)
        self.ram[self.sp] = return_addr
        # Get subroutine address from register
        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]

        # Jump to it
        self.pc = subroutine_addr

    def handle_RET(self):
        # Get return addr from top of stack
		# Store it in the PC
        return_addr = self.ram[self.sp]
        self.sp += 1
        self.pc = return_addr

    def handle_ADD(self, op, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def handle_CMP(self, op, reg_a, reg_b):
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3

    def handle_JMP(self, address):
        self.pc = self.reg[address]

    def handle_JEQ(self, address):
        if self.equal_fl == 1:
            self.pc = self.reg[address]
        else:
            self.pc += 2

    def handle_JNE(self, address):
        if self.equal_fl == 0:
            self.pc = self.reg[address]
        else:
            self.pc += 2

    def load(self):
        """Load a program into memory."""
        
        address = 0

        if len(sys.argv) != 2:
            print(f"usage: {sys.argv[0]} filename")
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()

                    if line == '' or line[0] == "#": 
                        continue

                    try:
                        str_value = line.split("#")[0]
                        value = int(str_value, 2)

                    except ValueError:
                        print(f"Invalid number: {str_value}")
                        sys.exit(1)
                    
                    self.ram[address] = value
                    address += 1
        
        except FileNotFoundError:
            print(f"file not found: {sys.argv[1]}")
            sys.exit(2)



    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            # Multiply the values in two registers together and store the result in registerA.
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            
            if self.reg[reg_a] < self.reg[reg_b]:
                self.less_fl = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.greater_fl = 1
            else:
                self.equal_fl = 1


            # * If registerA is less than registerB, set the Less-than `L` flag to 1,
            #   otherwise set it to 0. 

            # * If registerA is greater than registerB, set the Greater-than `G` flag
            #   to 1, otherwise set it to 0.
            
            #   * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.
        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        # running = True
        
        while self.running:
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            
            instruction = self.ram[self.pc]
            
            if instruction == HLT:
            #    self.handle_HLT()
                self.branchtable[instruction]()
            elif instruction == LDI:
                # self.handle_LDI()
                self.branchtable[instruction](operand_a, operand_b)
            elif instruction == PRN:
                # self.handle_PRN()
                self.branchtable[instruction](operand_a)
            elif instruction == MUL:
                # self.handle_MUL()    
                self.branchtable[instruction]("MUL", operand_a, operand_b)
            elif instruction == PUSH:
                self.branchtable[instruction]()
            elif instruction == POP:
                self.branchtable[instruction]()
            elif instruction == CALL:
                self.branchtable[instruction]()
            elif instruction == RET:
                self.branchtable[instruction]()
            elif instruction == ADD:
                self.branchtable[instruction]("ADD", operand_a, operand_b)
            elif instruction == CMP:
                self.branchtable[instruction]("MUL", operand_a, operand_b)
            elif instruction == JMP:
                self.branchtable[instruction](operand_a)
            elif instruction == JEQ:
                self.branchtable[instruction](operand_a)
            elif instruction == JNE:
                self.branchtable[instruction](operand_a)
            else:
                print(f"unknown instruction {instruction} at address {self.pc}")
                sys.exit(1)
    
    def ram_read(self, address):
        # accept the address to read and return the value stored
        # there.
        return self.ram[address]

    def ram_write(self, value, address):
        #  accept a value to write, and the address to write it to.
        self.ram[address] = value