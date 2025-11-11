"""
Constants used by our Catamount Processor Unit.
"""

WORD_SIZE = 16  # 16 bits = 2 bytes
WORD_MASK = (1 << WORD_SIZE) - 1   # 16 ones


if __name__ == '__main__':
    print(f"WORD_SIZE: {WORD_SIZE} (decimal)")
    print(f"WORD_MASK: {WORD_MASK:b} (binary)")