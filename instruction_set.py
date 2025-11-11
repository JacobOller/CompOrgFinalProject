"""
This is the instruction set for our CPU---Catamount processing unit.
It supports only a small set of instructions.

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>

v. 1.0.0 2025-10-29
v. 1.0.1 2025-11-02
    Cleaned up SHFT; added utility function for displaying
    raw bits, and added conditional formatting for __repr__.

"""
from dataclasses import dataclass  # For Instruction class, below.


# Instruction set specification
ISA = {
    'LOADI': {
        'opcode': 0x0,
        'format': 'I',
        'variant': 'imm-only',
        'fields': ['opcode(4)', 'rd(3)', 'imm(8)', 'zero(1)'],
        'semantics': 'Rd <-- imm8 (zero-extended)',
        'description': 'Load immediate 8-bit constant into Rd.',
        'register_write': True,
        'memory_write': False,
        'alu': False,
        'immediate': True,
        'branch': False
    },
    'LUI': {
        'opcode': 0x1,
        'format': 'I',
        'variant': 'imm-only',
        'fields': ['opcode(4)', 'rd(3)', 'imm(8)', 'zero(1)'],
        'semantics': 'Rd[15:8] <-- imm8',
        'description': 'Load immediate into upper byte of Rd.',
        'register_write': True,
        'memory_write': False,
        'alu': False,
        'immediate': True,
        'branch': False
    },
    'LOAD': {
        'opcode': 0x2,
        'format': 'M',
        'fields': ['opcode(4)', 'rd(3)', 'ra(3)', 'addr(6)'],
        'semantics': 'Rd <-- MEM[Ra + signextend(addr6)]',
        'description': 'Load word from memory at Ra + offset into Rd.',
        'register_write': True,
        'memory_write': False,
        'alu': True,    # for computing effective address
        'immediate': False,
        'branch': False
    },
    'STORE': {
        'opcode': 0x3,
        'format': 'M',
        'fields': ['opcode(4)', 'ra(3)', 'rb(3)', 'addr(6)'],
        'semantics': 'MEM[Rb + signextend(addr6)] <-- Ra',
        'description': 'Store Ra to memory at Rb + offset.',
        'register_write': False,
        'memory_write': True,
        'alu': True,    # for computing effective address
        'immediate': False,
        'branch': False
    },
    'ADDI': {
        'opcode': 0x4,
        'format': 'I',
        'variant': 'reg+imm',
        'fields': ['opcode(4)', 'rd(3)', 'ra(3)', 'imm(6)'],
        'semantics': 'Rd <-- Ra + signextend(imm6)',
        'description': 'Add signed 6-bit immediate value to Ra.',
        'register_write': True,
        'memory_write': False,
        'alu': True,
        'immediate': True,
        'branch': False
    },
    'ADD': {
        'opcode': 0x5,
        'format': 'R',
        'fields': ['opcode(4)', 'rd(3)', 'ra(3)', 'rb(3)', 'zero(3)'],
        'semantics': 'Rd <-- Ra + Rb',
        'description': 'Add values in two registers.',
        'register_write': True,
        'memory_write': False,
        'alu': True,
        'immediate': False,
        'branch': False
    },
    'SUB': {
        'opcode': 0x6,
        'format': 'R',
        'fields': ['opcode(4)', 'rd(3)', 'ra(3)', 'rb(3)', 'zero(3)'],
        'semantics': 'Rd <-- Ra − Rb',
        'description': 'Subtract value in Rb from value in Ra.',
        'register_write': True,
        'memory_write': False,
        'alu': True,
        'immediate': False,
        'branch': False
    },
    'AND': {
        'opcode': 0x7,
        'format': 'R',
        'fields': ['opcode(4)', 'rd(3)', 'ra(3)', 'rb(3)', 'zero(3)'],
        'semantics': 'Rd <-- Ra & Rb',
        'description': 'Bitwise AND of two registers.',
        'register_write': True,
        'memory_write': False,
        'alu': True,
        'immediate': False,
        'branch': False
    },
    'OR': {
        'opcode': 0x8,
        'format': 'R',
        'fields': ['opcode(4)', 'rd(3)', 'ra(3)', 'rb(3)', 'zero(3)'],
        'semantics': 'Rd <-- Ra | Rb',
        'description': 'Bitwise OR of two registers.',
        'register_write': True,
        'memory_write': False,
        'alu': True,
        'immediate': False,
        'branch': False
    },
    'SHFT': {
        'opcode': 0x9,
        'format': 'R',
        'fields': ['opcode(4)', 'rd(3)', 'ra(3)', 'rb(3)', 'zero(3)'],
        'semantics': 'if Rb & 0x8000: Rd <-- Ra >> (Rb & 0xF) '
                     'else Rd <-- Ra << (Rb & 0xF)',
        'description': 'Logical shift left or right depending on MSB of Rb. '
                       'Absolute value of shift amount is limited to 15. '
                       'We use the MSB of Rb to indicate direction of the shift.'
                       'If MSB is zero, then left shift; otherwise, right shift.'
                       'We use the lowest four bits of Rb for shift amount.',
        'register_write': True,
        'memory_write': False,
        'alu': True,
        'immediate': False,
        'branch': False
    },
    'BEQ': {
        'opcode': 0xA,
        'format': 'B',
        'variant': 'cond',
        'fields': ['opcode(4)', 'ra(3)', 'offset(8)', 'zero(1)'],
        'semantics': 'if Z == 1: PC <-- Ra + signextend(offset8)',
        'description': 'Branch if zero flag is set.',
        'register_write': False,  # writes directly to PC, not general-purpose register
        'memory_write': False,
        'alu': True,          # for computing effective address
        'immediate': True,    # offset
        'branch': True
    },
    'BNE': {
        'opcode': 0xB,
        'format': 'B',
        'variant': 'cond',
        'fields': ['opcode(4)', 'ra(3)', 'offset(8)', 'zero(1)'],
        'semantics': 'if Z == 0: PC <-- Ra + signextend(offset8)',
        'description': 'Branch if zero flag is clear.',
        'register_write': False,  # writes directly to PC, not general-purpose register
        'memory_write': False,
        'alu': True,        # for computing effective address
        'immediate': True,  # offset
        'branch': True
    },
    'B': {
        'opcode': 0xC,
        'format': 'B',
        'variant': 'uncond',
        'fields': ['opcode(4)', 'offset(8)', 'zero(4)'],
        'semantics': 'PC <-- PC + signextend(offset8)',
        'description': 'Unconditional branch by signed 8-bit PC-relative offset.',
        'register_write': False,  # writes directly to PC, not general-purpose register
        'memory_write': False,
        'alu': False,
        'immediate': True,
        'branch': True
    },
    'CALL': {
        'opcode': 0xD,
        'format': 'B',
        'variant': 'link',
        'fields': ['opcode(4)', 'offset(8)', 'zero(4)'],
        'semantics': 'Push (PC + 2); PC <-- PC + signextend(offset8)',
        'description': 'Call subroutine at address given by PC + signed 8-bit immediate. '
                       'Return address (PC + 2) is pushed onto stack.',
        'register_write': False,  # writes directly to PC, not general-purpose register
        'memory_write': False,
        'alu': True,
        'immediate': True,  # offset
        'branch': True
    },
    'RET': {
        'opcode': 0xE,
        'format': 'B',
        'variant': 'ret',
        'fields': ['opcode(4)', 'zero(12)'],
        'semantics': 'Pop PC',
        'description': 'Return from subroutine.',
        'register_write': False,
        'memory_write': False,
        'alu': False,
        'immediate': False,
        'branch': True
    },
    'HALT': {
        'opcode': 0xF,
        'format': 'O',
        'variant': 'halt',
        'fields': ['opcode(4)', 'zero(12)'],
        'semantics': 'stop execution',
        'description': 'Halt CPU.',
        'register_write': False,
        'memory_write': False,
        'alu': False,
        'immediate': False,
        'branch': False
    }
}


# Reverse map for opcode lookup
OPCODE_MAP = {v['opcode']: k for k, v in ISA.items()}

def get_instruction_spec(key):
    """
    Helper function. Returns the ISA specification for a
    given mnemonic (str) or opcode (int).
    """
    if isinstance(key, str):
        return ISA[key.upper()]
    return ISA[OPCODE_MAP[key]]  # if it's not a str, assume it's an int


@dataclass
class Instruction:    # pylint: disable=too-many-instance-attributes
    """
    Represents a single decoded instruction for the Catamount
    Processing Unit (CPU).

    Fields correspond to the 16-bit ISA specification.

    We use Python dataclass for minimal, lightweight classes,
    almost like structs in C. When we instantiate an instruction,
    `i`, we can access its fields using dot notation, like this:

    i.opcode       # gets us the opcode of instruction i
    i.rd           # gets us the destination register of instruction i
    etc.
    """

    # Defaults (constructor is implicit)
    opcode: int = 0
    mnem: str = ""
    rd: int = 0
    ra: int = 0
    rb: int = 0
    imm: int = 0
    addr: int = 0
    zero: int = 0  # added 2025-10-31 not strictly nec. may be useful in debugging
    raw: int = 0

    def __post_init__(self):
        """
        This is called immediately after the object is instantiated.
        If raw bytes have been provided, the instruction is auto-
        decoded. If not, then we assume all necessary fields have
        been supplied to the constructor.
        """
        if self.raw:
            self._decode_from_word(self.raw)
        if not self.mnem and self.opcode:
            self.mnem = OPCODE_MAP.get(self.opcode, "???")
        if not self.opcode and self.mnem:
            self.opcode = ISA[self.mnem]['opcode']

    @property
    def format(self):
        """
        Get the instruction format.
        """
        spec = ISA.get(self.mnem)
        if not spec:
            return None
        return spec['format']

    def _decode_from_word(self, word):
        """
        Self-decode instruction from 16-bit word.
        """
        self.opcode = (word >> 12) & 0xF
        self.mnem = OPCODE_MAP.get(self.opcode, "???")
        fmt = self.format
        if fmt == 'R':
            self.rd = (word >> 9) & 0x7
            self.ra = (word >> 6) & 0x7
            self.rb = (word >> 3) & 0x7
            self.zero = word & 0x7            # 4-bit zero padding
        elif self.mnem in ('LOADI', 'LUI'):
            self.rd = (word >> 9) & 0x7
            self.imm = (word >> 1) & 0xFF     # fixed 2025-10-31
            self.zero = word & 1              # 1-bit zero padding
        elif self.mnem == 'ADDI':
            self.rd = (word >> 9) & 0x7
            self.ra = (word >> 6) & 0x7
            self.imm = word & 0x3F
            self.zero = 0                     # no zero padding
        elif fmt == 'M':
            self.rd = (word >> 9) & 0x7
            self.ra = (word >> 6) & 0x7
            self.addr = word & 0x3F           # 63 (6 bits)
            self.zero = 0                     # no zero padding
        elif self.mnem == 'CALL':             # added 2025-10-31
            self.imm = (word >> 4) & 0xFF
            self.zero = word & 0xF            # 4-bit zero padding
        elif self.mnem in ('RET', 'HALT'):    # added 2025-10-31
            self.zero = word & 0xFFF          # 12-bit zero padding
        elif self.mnem == 'B':                # added 2025-11-01
            self.imm = (word >> 4) & 0xFF
            self.zero = word & 0xF            # 4-bit zero padding
        elif fmt == 'B':                      # B, BEQ and BNE
            self.ra = (word >> 9) & 0x7
            self.imm = (word >> 1) & 0xFF     # fixed 2025-10-31
            self.zero = word & 1              # 1-bit zero padding
        else:
            raise ValueError(f"Unhandled instruction {self.mnem}")
        self.raw = word
        try:                                  # added 2025-10-31
            assert self.zero == 0
        except AssertionError:
            print(f"BAD zero padding on {self.mnem}!")
            print(f"Raw word (hex): {word:04X}")
            print(f"Raw word (bin): {word:16b}")
            print("Problem with decoding? Or assembler bug?")
            raise

    @property
    def raw_bin(self):              # added 2025-11-02
        """
        Return pretty, zero padded binary representation of raw bytes.
        """
        return "0b" + bin(self.raw)[2:].zfill(16)

    @property
    def raw_hex(self):              # added 2025-11-02
        """
        Return pretty, zero padded, upper-case hex representation of raw bytes.
        """
        return "0x" + hex(self.raw)[2:].zfill(4).upper()

    def __repr__(self):
        """
        Revised 2025-11-01 to include raw bytes and conditional
        formatting by opcode, and to format fields as hex.
        """
        s = f"Instruction({self.mnem} (opcode={self.opcode}): "
        fmt = self.format
        if fmt is None:
            raise ValueError("Instruction format unknown")
        if fmt == 'R':
            s += (f"rd=0x{self.rd:01X}, ra=0x{self.ra:01X}, "
                  f"rb=0x{self.rb:01X}, zero={self.zero:01X}, ")
        elif self.mnem in ('LOADI', 'LUI'):
            s += (f"rd=0x{self.rd:01X}, imm=0x{self.imm:02X}, "
                  f"zero=0x{self.zero:01X}, ")
        elif self.mnem == 'ADDI':
            s += (f"rd=0x{self.rd:01X}, ra=0x{self.ra:01X}, "
                  f"imm=0x{self.imm:02X}, ")
        elif fmt == 'M':
            s += (f"rd=0x{self.rd:01X}, ra=0x{self.ra:01X}, "
                  f"addr=0x{self.addr:03X}, ")
        elif self.mnem == 'CALL':
            s += f"imm=0x{self.imm:02X}, zero=0x{self.zero:01X}, "
        elif self.mnem in ('RET', 'HALT'):
            s += f"zero=0x{self.zero:03X}, "
        elif self.mnem == 'B':
            s += f"imm=0x{self.imm:02X}, zero=0x{self.zero:01X}, "
        elif fmt == 'B':
            s += (f"ra=0x{self.ra:01X}, imm=0x{self.imm:02X}, "
                  f"zero=0x{self.zero:01X}, ")
        s += f"raw_hex={self.raw_hex}, raw_bin={self.raw_bin})"
        return s
