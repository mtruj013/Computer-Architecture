"""CPU functionality."""

import sys


LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0


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
        
        running = True
        
        while running:
            instruction = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            #LDI,Set the value of a register to an integer 3B
            #PRN Print numeric value stored in the given register, 2B
            if instruction == HLT:
                running = False
                self.pc += 1
            elif instruction == LDI:
                reg_num = operand_a
                value = operand_b
                self.reg[reg_num] = value
                self.pc += 3
            elif instruction == PRN:
                reg_num = operand_a
                print(self.reg[reg_num])
                self.pc += 2
            elif instruction == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
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