"""
Constants used by our Catamount Processor Unit.

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>
"""

WORD_SIZE = 16  # 16 bits = 2 bytes
WORD_MASK = (1 << WORD_SIZE) - 1  # 16 ones
STACK_BASE = 0xFF00
STACK_TOP = 0xFFFF

if __name__ == "__main__":
    print(f"WORD_SIZE: {WORD_SIZE} (decimal)")
    print(f"WORD_MASK: {WORD_MASK:04X} (hex)")
    print(f"STACK_BASE: {STACK_BASE:04X} (hex)")
    print(f"STACK_TOP: {STACK_TOP:04X} (hex)")
