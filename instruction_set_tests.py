"""
Minimal human-eyeball tests for sanity of instruction set
helper function, opcode map, and Instruction class.

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>

"""

from instruction_set import OPCODE_MAP, get_instruction_spec, Instruction

if __name__ == '__main__':

    print("Test instruction spec helper function...")
    print(get_instruction_spec('ADD'))
    print(get_instruction_spec('LOADI'))
    print(get_instruction_spec('HALT'))
    print()

    print("Test opcode map...")
    print(OPCODE_MAP)
    print()

    print("Test instruction class...")

    print("Test LOADI...")
    i = Instruction(raw=0x0DFE)
    assert i.mnem == 'LOADI'
    assert i.rd == 0x6
    assert i.imm == 0xFF
    assert i.zero == 0x0
    print(i)
    print()

    print("Test LUI...")
    i = Instruction(raw=0x16DE)  # LUI
    # 0001 011 01101111 0  instruction
    # 0001 0110 1101 1110  nibbles
    assert i.mnem == 'LUI'
    assert i.rd == 0x3
    assert i.imm == 0x6F
    assert i.zero == 0x0
    print(i)
    print()

    print("Test LOAD...")
    i = Instruction(raw=0x257F)    # added 2025-11-02
    # 0010 010 101 111111  instruction
    # 0010 0101 0111 1111  nibbles
    assert i.mnem == 'LOAD'
    assert i.rd == 0x2
    assert i.ra == 0x5
    assert i.addr == 0x3F
    assert i.zero == 0x0
    print(i)
    print()

    print("Test STORE...")
    i = Instruction(raw=0x357F)    # added 2025-11-02
    # 0011 010 101 111111  instruction
    # 0011 0101 0111 1111  nibbles
    assert i.mnem == 'STORE'
    assert i.rd == 0x2
    assert i.ra == 0x5
    assert i.addr == 0x3F
    assert i.zero == 0x0
    print(i)
    print()

    print("Test BEQ...")
    i = Instruction(raw=0xA404)  # BEQ
    assert i.mnem == 'BEQ'
    assert i.ra == 0x2
    assert i.imm == 0x2
    assert i.zero == 0x0
    print(i)
    print()

    print("Test BNE...")
    i = Instruction(raw=0xB3FA)  # BNE
    assert i.mnem == 'BNE'
    assert i.ra == 0x1
    assert i.imm == 0xFD
    assert i.zero == 0x0
    print(i)
    print()

    print("Test B...")
    i = Instruction(raw=0xC010)  # B
    assert i.mnem == 'B'
    assert i.imm == 0x01
    assert i.zero == 0x0
    print(i)
    print()

    print("Test ADDI...")
    i = Instruction(raw=0x4E6B)    # added 2025-11-02
    # 0100 111 001 101011  instruction
    # 0100 1110 0110 1011  nibbles
    assert i.mnem == 'ADDI'
    assert i.rd == 0x7
    assert i.ra == 0x1
    assert i.imm == 0x2B
    print(i)
    print()

    print("Test ADD...")
    i = Instruction(raw=0x5488)  # ADD
    assert i.mnem == 'ADD'
    assert i.rd == 0x2
    assert i.ra == 0x2
    assert i.rb == 0x1
    assert i.zero == 0x0
    print(i)
    print()

    print("Test SUB...")
    i = Instruction(raw=0x6250)  # SUB
    assert i.mnem == 'SUB'
    assert i.rd == 0x1
    assert i.ra == 0x1
    assert i.rb == 0x2
    assert i.zero == 0x0
    print(i)
    print()

    print("Test AND...")
    i = Instruction(raw=0x7650)  # AND
    assert i.mnem == 'AND'
    assert i.rd == 0x3
    assert i.ra == 0x1
    assert i.rb == 0x2
    assert i.zero == 0x0
    print(i)
    print()

    print("Test OR...")
    i = Instruction(raw=0x8AE0)  # OR
    assert i.mnem == 'OR'
    assert i.rd == 0x5
    assert i.ra == 0x3
    assert i.rb == 0x4
    assert i.zero == 0x0
    print(i)
    print()

    print("Test SHFT...")
    i = Instruction(raw=0x9650)  # SHFT
    assert i.mnem == 'SHFT'
    assert i.rd == 0x3
    assert i.ra == 0x1
    assert i.rb == 0x2
    assert i.zero == 0x0
    print(i)
    print()

    print("Test CALL...")
    i = Instruction(raw=0xD010)  # CALL
    assert i.mnem == 'CALL'
    assert i.imm == 0x01
    assert i.zero == 0x0
    print(i)
    print()

    print("Test RET...")
    i = Instruction(raw=0xE000)  # RET
    assert i.mnem == 'RET'
    assert i.zero == 0x000
    print(i)
    print()

    print("Test HALT...")
    i = Instruction(raw=0xF000)  # HALT
    assert i.mnem == 'HALT'
    assert i.zero == 0x000
    print(i)
    print()

