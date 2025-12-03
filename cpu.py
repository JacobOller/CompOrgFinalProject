"""
Catamount Processing Unit
A toy 16-bit Harvard architecture CPU.

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>

STARTER CODE
"""

from alu import Alu
from constants import STACK_TOP
from instruction_set import Instruction
from memory import DataMemory, InstructionMemory
from register_file import RegisterFile


class Cpu:
    """
    Catamount Processing Unit
    """

    def __init__(self, *, alu, regs, d_mem, i_mem):
        """
        Constructor
        """
        self._i_mem = i_mem
        self._d_mem = d_mem
        self._regs = regs
        self._alu = alu
        self._pc = 0  # program counter
        self._ir = 0  # instruction register
        self._sp = STACK_TOP  # stack pointer
        self._decoded = Instruction()
        self._halt = False

    @property
    def running(self):
        return not self._halt

    @property
    def pc(self):
        return self._pc

    @property
    def sp(self):
        return self._sp

    @property
    def ir(self):
        return self._ir

    @property
    def decoded(self):
        return self._decoded

    def get_reg(self, r):
        """
        Public accessor (getter) for single register value.
        Added 2025-11-15. Notify students.
        """
        return self._regs.execute(ra=r)[0]

    def tick(self):
        """
        Fetch-decode-execute
        Implementation incomplete.
        """
        if not self._halt:
            self._fetch()
            self._decode()

            # execute...
            match self._decoded.mnem:
                case "LOADI":
                    self._regs.execute(rd=self._decoded.rd, data=self._decoded.imm, write_enable=True)
                    self._pc += 1
                case "LUI":
                    # TODO Refactor for future semester(s) if any.
                    # Cheating for compatibility with released ALU tests
                    # and starter code. Leave as-is for 2025 Fall.
                    rd = self._decoded.rd
                    imm = self._decoded.imm & 0xFF
                    upper = imm << 8
                    lower, _ = self._regs.execute(ra=rd)
                    lower &= 0x00FF  # clear upper bits
                    data = upper | lower
                    self._regs.execute(rd=rd, data=data, write_enable=True)
                case "LOAD":
                    # [0] because this method returns 2 variables (ra and rb).
                    initial_address = self._regs.execute(ra=self._decoded.ra)[0]
                    # Add initial_address and immediate value with ALU.
                    final_address = self._alu.execute("ADD", initial_address, self._decoded.imm)

                    data_to_load = self._d_mem.read(final_address) # Reading from data memory.
                    self._regs.execute(rd=self._decoded.rd, data=data_memory_value, write_enable=True)

                    self._pc += 1
                case "STORE":
                    # Get both the value to be stored and the initial address from register.
                    (value_stored, initial_address) = self._regs.execute(ra=self._decoded.ra, rb=self._decoded.rd)
                    # Add the initial address to the offset.
                    final_address = self._alu.execute("ADD", initial_address, self._decoded.imm)
                    
                    # Write enable resets after each method call, so set it to be true.
                    self._d_mem.write_enable(True)
                    # Write the value_stored to the final_address.
                    self._d_mem.write(final_address, value_stored)

                    self._pc += 1
                case "ADDI":
                    # Get the value stored in register a.
                    source_value = self._regs.execute(ra=self._decoded.ra)[0]
                    # Calculate the sum of the source value and offset using the ALU.
                    result = self._alu.execute("ADD", self._decoded.imm, source_value)
                    
                    # Write the result to the destination register (rd).
                    self._regs.execute(rd=self._decoded.rd, data=result, write_enable=True)

                    self._pc += 1
                case "ADD":
                    # Get the values stored in register a and b.
                    (ra_source_value, rb_source_value) = self._regs.execute(ra=self._decoded.ra, rb=self._decoded.rb)
                    # Calculate the sum of these two values using the ALU.
                    result = self._alu.execute("ADD", ra_source_value, rb_source_value)

                    # Write the result to the destination register.
                    self._regs.execute(rd=self._decoded.rd, data=result, write_enable=True)

                    self._pc += 1
                case "SUB":
                    # Get the values stored in register a and b.
                    (ra_source_value, rb_source_value) = self._regs.execute(ra=self._decoded.ra, rb=self._decoded.rb)
                    # Calculate the difference of these two values using the ALU.
                    result = self._alu.execute("SUB", ra_source_value, rb_source_value)

                    # Write the result to the destination register.
                    self._regs.execute(rd=self._decoded.rd, data=result, write_enable=True)

                    self._pc += 1
                case "AND":
                    pass  # complete implementation here
                case "OR":
                    pass  # complete implementation here
                case "SHFT":
                    self._alu.set_op("SHFT")
                    rd = self._decoded.rd
                    ra = self._decoded.ra
                    rb = self._decoded.rb
                    op_a, op_b = self._regs.execute(ra=ra, rb=rb)
                    result = self._alu.execute(op_a, op_b)
                    self._regs.execute(rd=rd, data=result, write_enable=True)
                case "BEQ":
                    if self._alu.zero:
                        offset = self.sext(self._decoded.imm, 8)
                        self._pc += offset  # take branch
                case "BNE":
                    pass  # complete implementation here
                case "B":
                    pass  # complete implementation here
                case "CALL":
                    self._sp -= 1  # grow stack downward
                    # PC is incremented immediately upon fetch so already
                    # pointing to next instruction, which is return address.
                    ret_addr = self._pc  # explicit
                    self._d_mem.write_enable(True)
                    # push return address...
                    self._d_mem.write(self._sp, ret_addr, from_stack=True)
                    offset = self._decoded.imm
                    self._pc += self.sext(offset, 8)  # jump to target
                case "RET":
                    # Get return address from memory via SP
                    # Increment SP
                    # Update PC
                    pass  # complete implementation here
                case "HALT":
                    pass  # complete implementation here
                case _:  # default
                    raise ValueError(
                        "Unknown mnemonic: " + str(self._decoded) + "\n" + str(self._ir)
                    )

            return True
        return False

    def _decode(self):
        """
        We're effectively delegating decoding to the Instruction class.
        """
        self._decoded = Instruction(raw=self._ir)

    def _fetch(self):
        pass  # complete implementation here

    def load_program(self, prog):
        self._i_mem.load_program(prog)

    @staticmethod
    def sext(value, bits=16):
        mask = (1 << bits) - 1
        value &= mask
        sign_bit = 1 << (bits - 1)
        return (value ^ sign_bit) - sign_bit


# Helper function
def make_cpu(prog=None):
    alu = Alu()
    d_mem = DataMemory()
    i_mem = InstructionMemory()
    if prog:
        i_mem.load_program(prog)
    regs = RegisterFile()
    return Cpu(alu=alu, d_mem=d_mem, i_mem=i_mem, regs=regs)
