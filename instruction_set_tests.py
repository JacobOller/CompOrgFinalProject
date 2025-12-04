"""
pytest tests for instruction_set

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>
"""

import pytest

from instruction_set import ISA, OPCODE_MAP, Instruction, get_instruction_spec


def test_get_instruction_spec_basic():
    assert get_instruction_spec("ADD")["opcode"] == 0x5
    assert get_instruction_spec("LOADI")["opcode"] == 0x0
    assert get_instruction_spec("HALT")["opcode"] == 0xF


def test_opcode_map_is_inverse_of_isa():
    for mnem, spec in OPCODE_MAP.items():
        assert isinstance(mnem, int)
        assert isinstance(spec, str)
    # round-trip check
    for mnem, info in ISA.items():
        code = info["opcode"]
        assert OPCODE_MAP[code] == mnem


# Fixed test for STORE. 2025-11-11. Students need update.
@pytest.mark.parametrize(
    "raw,mnem,expect",
    [
        (0x0000, "LOADI", {"rd": 0x0, "imm": 0x0, "zero": 0x0}),
        (0x0DFE, "LOADI", {"rd": 0x6, "imm": 0xFF, "zero": 0x0}),
        (0x16DE, "LUI", {"rd": 0x3, "imm": 0x6F, "zero": 0x0}),
        (0x257F, "LOAD", {"rd": 0x2, "ra": 0x5, "addr": 0x3F, "zero": 0x0}),
        (0x357F, "STORE", {"ra": 0x2, "rb": 0x5, "addr": 0x3F, "zero": 0x0}),
        (0xA404, "BEQ", {"imm": 0x04, "zero": 0x0}),
        (0xB3FA, "BNE", {"imm": 0xFA, "zero": 0x0}),
        (0xC010, "B", {"imm": 0x10, "zero": 0x0}),
        (0x4E6B, "ADDI", {"rd": 0x7, "ra": 0x1, "imm": 0x2B}),
        (0x5488, "ADD", {"rd": 0x2, "ra": 0x2, "rb": 0x1, "zero": 0x0}),
        (0x6250, "SUB", {"rd": 0x1, "ra": 0x1, "rb": 0x2, "zero": 0x0}),
        (0x7650, "AND", {"rd": 0x3, "ra": 0x1, "rb": 0x2, "zero": 0x0}),
        (0x8AE0, "OR", {"rd": 0x5, "ra": 0x3, "rb": 0x4, "zero": 0x0}),
        (0x9650, "SHFT", {"rd": 0x3, "ra": 0x1, "rb": 0x2, "zero": 0x0}),
        (0xD010, "CALL", {"imm": 0x01, "zero": 0x0}),
        (0xE000, "RET", {"zero": 0x000}),
        (0xF000, "HALT", {"zero": 0x000}),
    ],
)
def test_instruction_decoding(raw, mnem, expect):
    i = Instruction(raw=raw)
    assert i.mnem == mnem
    for field, val in expect.items():
        assert getattr(i, field) == val, (
            f"{mnem}.{field} expected {val:#x}, got {getattr(i, field):#x}"
        )


def test_repr_contains_fields():
    i = Instruction(raw=0x4E6B)  # ADDI example
    s = repr(i)
    assert "ADDI" in s
    assert "raw_hex=" in s
    assert "raw_bin=" in s

