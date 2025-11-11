"""
Tests for Catamount Processor Unit ALU

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>

"""

from alu import Alu

if __name__ == '__main__':

    # Note that opcode here is ALU opcode, not instruction opcode.
    tests = [
        {'opcode': 0b000, 'mnemonic': 'ADD',
         'a': 6, 'b': 3, 'expected': 9,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Basic addition, no carry or overflow.'},

        {'opcode': 0b000, 'mnemonic': 'ADD',
         'a': 0, 'b': 0, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Zero result sets Z flag.'},

        {'opcode': 0b000, 'mnemonic': 'ADD',
         'a': 0xFFFF, 'b': 1, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': True, 'overflow': False},
         'comment': 'Unsigned wraparound with carry out.'},

        {'opcode': 0b000, 'mnemonic': 'ADD',
         'a': 32767, 'b': 1, 'expected': -32768,
         'flags': {'zero': False, 'negative': True, 'carry': False, 'overflow': True},
         'comment': 'Signed overflow on positive limit.'},

        {'opcode': 0b000, 'mnemonic': 'ADD',
         'a': -1, 'b': 1, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': True, 'overflow': False},
         'comment': 'Negative plus positive cancel to zero; carry set from unsigned wrap.'},

        {'opcode': 0b000, 'mnemonic': 'ADD',
         'a': -32768, 'b': -1, 'expected': 32767,
         'flags': {'zero': False, 'negative': False, 'carry': True, 'overflow': True},
         'comment': 'Addition of two negatives causes signed overflow to positive range.'},

        {'opcode': 0b001, 'mnemonic': 'SUB',
         'a': 3, 'b': 3, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': True, 'overflow': False},
         'comment': 'No borrow; result zero sets Z and carry.'},

        {'opcode': 0b001, 'mnemonic': 'SUB',
         'a': 3, 'b': 5, 'expected': -2,
         'flags': {'zero': False, 'negative': True, 'carry': False, 'overflow': False},
         'comment': 'Borrow required; carry cleared, result negative.'},

        {'opcode': 0b001, 'mnemonic': 'SUB',
         'a': -32768, 'b': 1, 'expected': 32767,
         'flags': {'zero': False, 'negative': False, 'carry': True, 'overflow': True},
         'comment': 'Signed underflow on negative limit.'},

        {'opcode': 0b001, 'mnemonic': 'SUB',
         'a': 0, 'b': -1, 'expected': 1,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Subtracting a negative equals addition.'},

        {'opcode': 0b010, 'mnemonic': 'AND',
         'a': 15, 'b': 240, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Non-overlapping bitmasks yield zero.'},

        {'opcode': 0b010, 'mnemonic': 'AND',
         'a': 15, 'b': 241, 'expected': 1,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Overlap of LSB only.'},

        {'opcode': 0b010, 'mnemonic': 'AND',
         'a': 0xFFFF, 'b': 0x1234, 'expected': 0x1234,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Mask of all ones, result identical to operand.'},

        {'opcode': 0b010, 'mnemonic': 'AND',
         'a': 0x0000, 'b': 0xFFFF, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Mask of zeros yields zero result.'},

        {'opcode': 0b010, 'mnemonic': 'AND',
         'a': 0xAAAA, 'b': 0x5555, 'expected': 0x0000,
         'flags': {'zero': True, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Complementary bit patterns yield zero.'},

        {'opcode': 0b011, 'mnemonic': 'OR',
         'a': 85, 'b': 42, 'expected': 127,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Alternating bits produce full lower byte.'},

        {'opcode': 0b011, 'mnemonic': 'OR',
         'a': 0x0000, 'b': 0x1234, 'expected': 0x1234,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'OR with zero preserves operand.'},

        {'opcode': 0b011, 'mnemonic': 'OR',
         'a': 0xAAAA, 'b': 0x5555, 'expected': -1,
         'flags': {'zero': False, 'negative': True, 'carry': False, 'overflow': False},
         'comment': 'Complementary bit patterns yield all ones.'},

        {'opcode': 0b011, 'mnemonic': 'OR',
         'a': -1, 'b': 0, 'expected': -1,
         'flags': {'zero': False, 'negative': True, 'carry': False, 'overflow': False},
         'comment': 'OR with -1 leaves operand unchanged, negative result sets N.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 1, 'b': 0x8001, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': True, 'overflow': False},
         'comment': 'Right shift by 1; LSB shifted out sets carry.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 1, 'b': 1, 'expected': 2,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Left shift by 1.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 1, 'b': 15, 'expected': -32768,
         'flags': {'zero': False, 'negative': True, 'carry': False, 'overflow': False},
         'comment': 'Left shift by maximum magnitude (15).'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 1, 'b': 100, 'expected': 16,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Shift count masked to 4 bits (100 -> 4). Left shift by 4.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 32768, 'b': 0b1000000000001111, 'expected': 1,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Right shift by 15; MSB determines direction.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 0x1234, 'b': 0x8000, 'expected': 0x1234,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'MSB set but shift count = 0; no shift performed.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 0x8000, 'b': 1, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': True, 'overflow': False},
         'comment': 'Left shift shifts out MSB; carry set.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 42, 'b': 0, 'expected': 42,
         'flags': {'zero': False, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Zero shift leaves operand unchanged.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 0b0000000000000010, 'b': 0x800F, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Right shift by 15 clears all bits; final bit out sets carry.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 0b0000000000000001, 'b': 0xF, 'expected': -32768,
         'flags': {'zero': False, 'negative': True, 'carry': False, 'overflow': False},
         'comment': 'Left shift by 15 moves low bit to MSB; sets N flag.'},

        {'opcode': 0b100, 'mnemonic': 'SHFT',
         'a': 0x0001, 'b': 0x8FFF, 'expected': 0,
         'flags': {'zero': True, 'negative': False, 'carry': False, 'overflow': False},
         'comment': 'Right shift by 15 with MSB=1; all bits shifted out.'},

    ]

    alu = Alu()  # instantiate ALU object

    failures = 0   # pylint: disable=C0103
    count = 0      # pylint: disable=C0103
    print("Running ALU self-test...")

    for count, t in enumerate(tests, 1):
        print(f"\n{t['mnemonic']}: {t['a']}, {t['b']}.")
        print(f"{t['comment']}")
        alu.decode(t['opcode'])
        if t['mnemonic'] == 'SHFT':
            direction = "RIGHT" if (t['b'] & 0x8000) else "LEFT"  # pylint: disable=C0103
            amt = t['b'] & 0xF
            print(f"Direction: {direction}. Shift amount (masked): {amt}.")
        try:
            r = alu.execute(t['a'], t['b'])
            expected = t['expected']
            assert r == expected, f"Expected {expected}, got {r}"
            for k, v in t['flags'].items():
                assert getattr(alu, k) == v, f"Expected {v} for {k}, got {getattr(alu, k)}"
            print(f"Expected {expected}, got {r}, with flags {t['flags']}")
            print(f"Flags: {alu._flags:04b} (NZCV)")  # pylint: disable=W0212
            print("Passed!")
        except AssertionError as e:
            failures += 1
            print("Failed!")
            print(f"   {e}\n")

    if failures:
        print(f"\n{failures} of {count} tests failed.")
    else:
        print(f"\nAll {count} tests passed.")
