"""
Assembler for the Catamount Processing Unit (CPU).

Instructions are encoded as 16-bit (2-byte) words.
This takes a list of lines of assembly code and returns
a list of 16-bit words.

Two-pass assembler:
  1. First pass collects labels and assigns addresses.
  2. Second pass encodes instructions into 16-bit words.

Supports the ISA defined in instruction_set.py.

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>
"""

import glob
import os
import re

from instruction_set import ISA


def _strip(line):
    """Remove comments and surrounding whitespace."""
    return line.split(";", 1)[0].strip()


def _is_label(line):
    """Detect label definitions (lines ending with ':')."""
    return line.endswith(":")


def _reg(token):
    """Parse register tokens like R0..R7."""
    if not token.startswith("R"):
        raise ValueError("Expected register, got " + token)
    n = int(token[1:])
    if not (0 <= n <= 7):
        raise ValueError("Register out of range 0..7: " + token)
    return n


def _imm(token, bits):
    """Parse an immediate (#n or numeric literal) and mask to width."""
    if token.startswith("#"):
        token = token[1:]
    value = int(token, 0)
    mask = (1 << bits) - 1
    return value & mask


def _mem_operand(token):
    """
    Parse memory operand like [R3 + #5] or [R3].
    Returns (base_reg, 6-bit offset).
    """
    m = re.match(r"\[(R\d)(?:\s*\+\s*#?(-?\w+))?\]", token)

    if not m:
        raise ValueError("Bad memory operand: " + token)
    base = _reg(m.group(1))
    offset = int(m.group(2), 0) if m.group(2) else 0
    return base, offset & 0x3F


def assemble(lines):
    """
    Assemble a list of source lines into 16-bit instruction words.
    """
    # Pass 1: record labels and strip comments
    labels = {}
    pc = 0
    cleaned = []

    for raw in lines:
        line = _strip(raw)
        if not line:
            continue
        cleaned.append(line)
        if _is_label(line):
            name = line[:-1]
            if name in labels:
                raise ValueError("Duplicate label: " + name)
            labels[name] = pc
        else:
            pc += 1

    # Pass 2: encode instructions
    program = []
    pc = 0

    for line in cleaned:
        if _is_label(line) or not line:
            continue

        tokens = re.findall(r"\[[^\]]+\]|[^\s,]+", line)
        mnemonic = tokens[0].upper()
        if mnemonic not in ISA:
            raise ValueError("Unknown instruction " + mnemonic)

        info = ISA[mnemonic]
        opcode = info["opcode"]
        word = 0  # leave this as-is for now

        if info["format"] == "R":
            rd, ra, rb = map(_reg, tokens[1:4])
            word = (opcode << 12) | (rd << 9) | (ra << 6) | (rb << 3)

        elif mnemonic in ("LOADI", "LUI"):
            rd = _reg(tokens[1])
            imm = _imm(tokens[2], 8)
            word = (opcode << 12) | (rd << 9) | (imm << 1)

        elif mnemonic == "ADDI":
            rd, ra = map(_reg, tokens[1:3])
            imm = _imm(tokens[3], 6)
            word = (opcode << 12) | (rd << 9) | (ra << 6) | imm

        elif mnemonic == "LOAD":
            rd = _reg(tokens[1])
            ra, offset = _mem_operand(tokens[2])
            word = (opcode << 12) | (rd << 9) | (ra << 6) | offset

        elif mnemonic == "STORE":
            ra = _reg(tokens[1])
            rb, offset = _mem_operand(tokens[2])
            word = (opcode << 12) | (ra << 9) | (rb << 6) | offset

        elif mnemonic in ("BEQ", "BNE", "B"):
            label = tokens[-1]
            if label not in labels:
                raise ValueError(f"Unknown label {label}")
            offset = (labels[label] - pc - 1) & 0xFF
            word = (opcode << 12) | offset

        elif mnemonic == "CALL":
            label = tokens[1]
            if label not in labels:
                raise ValueError(f"Unknown label {label}")
            offset = (labels[label] - pc - 1) & 0xFF
            word = (opcode << 12) | (offset << 4)

        elif mnemonic in ("RET", "HALT"):
            word = opcode << 12

        else:
            raise ValueError("Unhandled instruction " + mnemonic)

        program.append(word & 0xFFFF)
        pc += 1

    return program


if __name__ == "__main__":
    directory_path = "asm"
    for filename in glob.glob(os.path.join(directory_path, "*.asm")):
        basename = os.path.basename(os.path.normpath(filename))
        print(basename)
        with open(filename, "r") as f:
            src = f.readlines()
        prog = assemble(src)
        for i, w in enumerate(prog):
            print(f"{i:02X}: {w:04X}")
        print()
