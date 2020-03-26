"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001

class CPU:
    """Main CPU class."""

    def __init__(self, pc=0):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = pc
        self.inc_size = 0
        self.running = True
        self.sp = 7
        self.op_pc = False

        self.branchtable = {}
        self.branchtable[HLT] = self.HLT
        self.branchtable[LDI] = self.LDI #'LDI'
        self.branchtable[PRN] = self.PRN
        self.branchtable[MUL] = self.alu
        self.branchtable[POP] = self.POP
        self.branchtable[PUSH] = self.PUSH
        self.branchtable[CALL] = self.CALL
        self.branchtable[RET] = self.RET
        self.branchtable[ADD] = self.alu

    def ram_read(self, mar):
        try:
            return self.ram[mar]
        except:
            print('address error')

    def ram_write(self, mdr, mar):
        if self.ram[mar] != 0:
            fomer_data = self.ram[mar]
            print(f'you have changed this data ram from {fomer_data} to {mdr}')
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        if len(sys.argv) != 2:
            print("another error")
            sys.exit(1)
        
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split('#')
                    num = comment_split[0].strip()

                    if num == '':
                        continue

                    val = int(num, 2)
                    self.ram[address] = val

                    address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} not found\nusage: ls8.py filepath')
            sys.exit(2)


    def alu(self, reg_a, reg_b):
        # print(op, reg_a, reg_b)
        """ALU operations."""

        if self.ram[self.pc] == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif self.ram[self.pc] == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

        self.op_pc = False

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
        ir = self.reg[self.pc]

        while self.running:
            cmd = self.ram[self.pc]

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            self.branchtable[cmd](operand_a, operand_b)
            
            if not self.op_pc:
                self.pc += self.inc_size

    def LDI(self, register, immediate):
        self.reg[int(register)] = immediate
        self.inc_size = 3
        self.op_pc = False

    def PRN(self, register, _):
        print(self.reg[int(register)])
        self.inc_size = 2
        self.op_pc = False

    def HLT(self, register, _):
        self.running = False
        self.op_pc = False

    def PUSH(self, register, _):
        val = self.reg[int(register)]

        self.reg[self.sp] -= 1
        self.ram_write(val, self.reg[self.sp])
        self.inc_size = 2
        self.op_pc = False

    def POP(self, register, _):
        val = self.ram_read(self.reg[self.sp])

        self.reg[register] = val
        self.reg[self.sp] += 1
        self.inc_size = 2
        self.op_pc = False

    def CALL(self, register, _):
        self.reg[self.sp] -= 1
        self.ram_write(self.pc + 2, self.reg[self.sp])

        self.pc = self.reg[register]
        self.op_pc = True

    def RET(self, register, _):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        self.op_pc = True
