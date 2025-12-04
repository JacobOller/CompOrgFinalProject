"""
Tests for the Catamount Processing Unit (CPU) assembler.

This uses PyTest, a unit testing framework for Python.
PyTest is pip-installable.
Run with: python -m pytest assembler_tests.py

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>
"""

import pytest  # pip install pytest

from assembler import _imm, _is_label, _mem_operand, _reg, _strip, assemble


def test_strip():
    assert _strip("ADD R1, R2 ; comment") == "ADD R1, R2"
    assert _strip("; full comment") == ""
    assert _strip("  LOADI R3, #10  ") == "LOADI R3, #10"


def test_is_label():
    assert _is_label("LOOP:")
    assert not _is_label("LOOP")


def test_reg():
    assert _reg("R0") == 0
    assert _reg("R7") == 7
    with pytest.raises(ValueError):
        _reg("R8")


def test_imm():
    assert _imm("#15", 8) == 15
    assert _imm("0xFF", 8) == 0xFF
    assert _imm("#-1", 6) == 0b111111  # wraps correctly


def test_mem_operand():
    assert _mem_operand("[R3]") == (3, 0)
    assert _mem_operand("[R2 + #5]") == (2, 5)
    assert _mem_operand("[R2 + -3]") == (2, 0b111101)


def test_loadi_encodes_correctly():
    src = ["LOADI R5 #123"]
    prog = assemble(src)
    # first line is the only line
    assert prog[0] == 0x0 << 12 | 0x5 << 9 | 0b1111011 << 1

    # What happens if immediate is too large?
    # High order bits should be masked.
    src = ["LOADI R5 #257"]
    prog = assemble(src)
    assert prog[0] == 0x0 << 12 | 0x5 << 9 | 0b1 << 1

    # What about a negative immediate?
    src = ["LOADI R5 #-1"]
    prog = assemble(src)
    assert prog[0] == 0x0 << 12 | 0x5 << 9 | 0b11111111 << 1


def test_lui_encodes_correctly():
    src = ["LUI R7 #123"]
    prog = assemble(src)
    assert prog[0] == 0x1 << 12 | 0x7 << 9 | 0b1111011 << 1

    # What happens if immediate is too large?
    # We have only 8 bits for the immediate.
    # High order bits should be masked.
    src = ["LUI R5 #257"]
    prog = assemble(src)
    assert prog[0] == 0x1 << 12 | 0x5 << 9 | 0b1 << 1

    # What about a negative immediate?
    src = ["LUI R5 #-1"]
    prog = assemble(src)
    assert prog[0] == 0x1 << 12 | 0x5 << 9 | 0b11111111 << 1


def test_load_encodes_correctly():
    src = ["LOAD R1, [R2 + #5]"]
    prog = assemble(src)
    assert prog[0] == 0x2 << 12 | 0x1 << 9 | 0x2 << 6 | 0x5

    # What happens if addr offset is too large?
    # We have only 6 bits for the addr offset.
    # High order bits should be masked.
    src = ["LOAD R2 [R3 + #65]"]
    prog = assemble(src)
    assert prog[0] == 0x2 << 12 | 0x2 << 9 | 0x3 << 6 | 0x1

    # What about a negative offset?
    src = ["LOAD R2 [R3 + #-5]"]
    prog = assemble(src)
    assert prog[0] == 0x2 << 12 | 0x2 << 9 | 0x3 << 6 | 0b111011

    # What about no offset?
    src = ["LOAD R2 [R3]"]
    prog = assemble(src)
    assert prog[0] == 0x2 << 12 | 0x2 << 9 | 0x3 << 6 | 0x0


def test_store_encodes_correctly():
    src = ["STORE R1, [R2 + #5]"]
    prog = assemble(src)
    assert prog[0] == 0x3 << 12 | 0x1 << 9 | 0x2 << 6 | 0x5


def test_addi_encodes_correctly():
    src = ["ADDI R1, R2, #123"]
    prog = assemble(src)
    assert prog[0] == 0x4 << 12 | 0x1 << 9 | 0x2 << 6 | 0b111011


def test_add_encodes_correctly():
    src = ["ADD R1, R2, R3"]
    prog = assemble(src)
    assert prog[0] == 0x5 << 12 | 0x1 << 9 | 0x2 << 6 | 0x3 << 3


def test_sub_encodes_correctly():
    src = ["SUB R1, R2, R3"]
    prog = assemble(src)
    assert prog[0] == 0x6 << 12 | 0x1 << 9 | 0x2 << 6 | 0x3 << 3


def test_and_encodes_correctly():
    src = ["AND R1, R2, R3"]
    prog = assemble(src)
    assert prog[0] == 0x7 << 12 | 0x1 << 9 | 0x2 << 6 | 0x3 << 3


def test_or_encodes_correctly():
    src = ["OR R1, R2, R3"]
    prog = assemble(src)
    assert prog[0] == 0x8 << 12 | 0x1 << 9 | 0x2 << 6 | 0x3 << 3


def test_shft_encodes_correctly():
    src = ["SHFT R3, R4, R5"]
    prog = assemble(src)
    assert prog[0] == 0x9 << 12 | 0x3 << 9 | 0x4 << 6 | 0x5 << 3


def test_beq_encodes_with_forward_label():
    src = ["BEQ TARGET", "LOADI R0, #0", "TARGET:", "HALT"]
    prog = assemble(src)
    # Manually compute target address for testing.
    # opcode = 0xA (BEQ)
    # offset = (TARGET - PC - 1) & 0xFF
    expected = (0xA << 12) | 1
    assert prog[0] == expected  # check first instruction


def test_beq_encodes_with_backward_label():
    src = ["LOOP:", "LOADI R0, #0", "BEQ LOOP"]
    prog = assemble(src)
    # Manually compute target address for testing.
    # labels['LOOP'] = 0
    # pc = 2 for BEQ
    # offset = (0 - 2 - 1) & 0xFF
    expected_offset = (0 - 1 - 1) & 0xFF
    expected = (0xA << 12) | expected_offset
    assert prog[1] == expected  # check second instruction


def test_bne_encodes_with_forward_label():
    src = ["BNE TARGET", "LOADI R0, #0", "TARGET:", "HALT"]
    prog = assemble(src)
    # Manually compute target address for testing.
    # opcode = 0xB (BNE)
    # offset = (TARGET - PC - 1)
    expected = (0xB << 12) | 1
    assert prog[0] == expected  # check first instruction


def test_bne_encodes_with_backward_label():
    src = ["LOOP:", "LOADI R0, #0", "BNE LOOP"]
    prog = assemble(src)
    # Manually compute target address for testing.
    # labels['LOOP'] = 0
    # pc = 2 for BNE
    # offset = (0 - 2 - 1) & 0xFF
    expected_offset = (0 - 1 - 1) & 0xFF
    expected = (0xB << 12) | expected_offset
    assert prog[1] == expected  # check second instruction


def test_b_encodes_with_forward_label():
    src = ["B TARGET", "TARGET:", "HALT"]
    prog = assemble(src)
    # Manually compute target address for testing.
    # labels['TARGET'] = 1
    # pc = 0 for B
    # offset = (1 - 0 - 1) & 0xFF = 0
    expected_offset = 0
    expected = (0xC << 12) | expected_offset
    assert prog[0] == expected


def test_b_encodes_with_backward_label():
    src = ["LOOP:", "LOADI R0, #0", "B LOOP"]
    prog = assemble(src)
    # Manually compute target address for testing.
    # labels['LOOP'] = 0
    # pc = 1 for B
    # offset = (TARGET - PC - 1)
    expected_offset = (0 - 1 - 1) & 0xFF
    expected = (0xC << 12) | expected_offset
    assert prog[1] == expected  # check first instruction


def test_call_encodes_correctly():
    src = [
        "START:",
        "    LOADI R6, #0xFF",
        "    CALL FOO",
        "    HALT",
        "FOO:",
        "    BEQ DONE",
        "    SUB R1, R1, R2",
        "    BNE FOO",
        "DONE:",
        "    RET",
    ]
    target_index = 3  # GCD:
    pc = 1  # CALL is second instruction
    expected_offset = (target_index - pc - 1) & 0xFF
    expected = (0xD << 12) | (expected_offset << 4)
    prog = assemble(src)
    assert prog[1] == expected


def test_ret_encodes_correctly():
    src = ["RET"]
    prog = assemble(src)
    assert prog[0] == 0xE << 12


def test_halt_encodes_correctly():
    src = ["HALT"]
    prog = assemble(src)
    assert prog[0] == 0xF << 12


def test_unknown_instruction_raises():
    with pytest.raises(ValueError, match="Unknown instruction"):
        assemble(["FOO R0, R1"])


def test_duplicate_label_raises():
    with pytest.raises(ValueError, match="Duplicate label"):
        assemble(["LOOP:", "LOOP:", "HALT"])


if __name__ == "__main__":
    pytest.main()
