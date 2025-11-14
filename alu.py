"""
Starter code for Catamount Processor Unit ALU

We are limited to 16 bits, and five operations: ADD, SUB, AND, OR, and SHFT.

ALU maintains status flags:

    - N: negative, 1000   (8)
    - Z: zero, 0100       (4)
    - C: carry out, 0010  (2)
    - V: overflow, 0001   (1)

Our ALU will set flags as appropriate on each operation (no special
instructions are needed for setting flags).

- Negative flag is set if the MSB = 1, regardless of operation.

- Zero flag is set if result is zero, regardless of operation.

- Carry flag under the following conditions:
    - If an arithmetic operation is used and a bit is carried out.
    - For similarity with ARM architecture carry is set on a SUB
      if the minuend is larger than the subtrahend, e.g., with
      5 - 2 = 3, 5 is the minuend, and 2 is the subtrahend.
    - On a left shift, the carry flag is set to the value of the last
      bit shifted out. So, for example, in four bits, `0b1001 << 1`
      would set the carry flag to 1. However, `0b1001 << 2` would set
      the carry flag to 0, because the last bit shifted out was 0.
      On a right shift, the carry flag is set to the value of the last
      bit shifted out on the right. For example, `0b1001 >> 1` would
      set carry flag to 1, and `0b1001 >> 2` would set carry flag to 0.
    - In the odd but permitted case of shift by zero, the carry flag
      is left unchanged.
    - Carry flag is never changed on a bitwise operation.

- Overflow only applies to arithmetic operations.
"""

from constants import WORD_SIZE, WORD_MASK

N_FLAG = 0b1000
Z_FLAG = 0b0100
C_FLAG = 0b0010
V_FLAG = 0b0001

# hello
class Alu:

    def __init__(self):
        """
        Here we initialize the ALU when instantiated.
        """
        self._op = None
        self._flags = 0b0000
        # Dictionary to look up methods by operation name.
        self._ops = {
            "ADD"  : self._add,
            "SUB"  : self._sub,
            "AND"  : self._and,
            "OR"   : self._or,
            "SHFT" : self._shft
        }
    def set_op(self, op):
        """
        Public-facing setter. Added 2025-11-09. Students will need to add this
        to their ALU implementation.
        """
        if op in self._ops.keys():
            self._op = op
        else:
            raise ValueError(f"Bad op: {op}")
    
    def decode(self, c):
        """
        Decode control signal to determine operation.
        """
        c = c & 0b111 # ensure only three bits are used
        match c:
            case 0b000:
                self._op = "ADD"
            case 0b001:
                self._op = "SUB"
            case 0b010:
                self._op = "AND"
            case 0b011:
                self._op = "OR"
            case 0b100:
                self._op = "SHFT"
            case _:
                raise ValueError("Invalid control signal")
        # Return value is for testing.
        # We don't really need return value for normal use.
        return self._op

    # The @property decorator makes a getter method accessible
    # as if it were a property or attribute. For example, we can
    # access the zero flag with `alu.zero`.

    @property
    def zero(self):
        # Return zero flag; do not modify this method!
        return bool(self._flags & Z_FLAG)

    @property
    def negative(self):
        # Return negative flag
        return bool(self._flags & N_FLAG)

    @property
    def carry(self):
        # Return carry flag
        return bool(self._flags & C_FLAG)

    @property
    def overflow(self):
        # Return overflow flag
        return bool(self._flags & V_FLAG)

    def execute(self, a, b):
        """
        Execute operation with operands a and b. This will
        clear flags before operation, then call the function
        that we looked up in self._ops. It returns the result
        as signed to handle two's complement correctly.

        Do not change this method!
        """
        self._flags = 0   # clear flags before operation
        result = self._ops[self._op](a, b)
        return self._to_signed(result)

    
    def _add(self, a, b):
        """
        ADD
        """
        a = a & WORD_MASK
        b = b & WORD_MASK
        result = (a + b) & WORD_MASK
        self._update_arith_flags_add(a, b, result)
        return result

    def _sub(self, a, b):
        """
        SUB
        """
        a = a & WORD_MASK
        b = b & WORD_MASK
        result = (a - b) & WORD_MASK
        self._update_arith_flags_sub(a, b, result)
        return result

    def _and(self, a, b):
        """
        Bitwise AND
        """
        a = a & WORD_MASK
        b = b & WORD_MASK
        result = (a & b) & WORD_MASK
        self._update_logic_flags(result)
        return result

    def _or(self, a, b):
        """
        Bitwise OR
        """
        a = a & WORD_MASK
        b = b & WORD_MASK
        result = (a | b) & WORD_MASK
        self._update_logic_flags(result)
        return result

    def _shft(self, a, b):
        """
        SHFT
        
        Per the tests, the shift logic is as follows:
        - The shift amount is the lower 4 bits of b (b & 0xF).
        - The shift direction is determined by the MSB of b:
          - MSB = 0: Shift LEFT
          - MSB = 1: Shift RIGHT
        """
        a &= WORD_MASK  # Keep this line as is

        # Get the shift amount from only the first 4 bits of b
        shift_amount = b & 0b1111
        
        # 2. Get the direction from the MSB
        msb_mask = 1 << (WORD_SIZE - 1) 
        right_shift = ((b & msb_mask) != 0) # If the MSB is 1, then we know that b > 32768 (negative)

        if shift_amount == 0:
            # b = 0, so no shift performed.
            result = a
            bit_out = None
        
        elif right_shift:
            # Case for a right shift (b < 1)
            bit_out = (a >> (shift_amount - 1)) & 1 # Shift_amount - 1 because we want the last bit BEFORE it "falls over the edge"
            result = a >> shift_amount & WORD_MASK
            
        else:
            # Case for Left Shift (else because all other cases have been handled)
            # Overflow in bit_out occurs if we shift out bits
            if shift_amount >= WORD_SIZE:
                 bit_out = 0 # All bits are shifted out, including MSB
            else:
                 bit_out = (a >> (WORD_SIZE - shift_amount)) & 1 # Same logic as right_shift, just complementary
            result = (a << shift_amount) & WORD_MASK

        # Keep these last two lines as they are
        self._update_shift_flags(result, bit_out)
        return result

    def _to_signed(self, x):
        """
        Helper to convert unsigned to signed

        Do not modify this method!
        """
        if x & (1 << (WORD_SIZE - 1)):
            return x - (1 << WORD_SIZE)
        return x

    def _update_logic_flags(self, result):
        """
        Update flags for bitwise operations.
        """
        if result & (1 << (WORD_SIZE - 1)):
            self._flags |= N_FLAG
        if result == 0:
            self._flags |= Z_FLAG
        # Carry and Overflow are not affected by bitwise ops.
    def _update_arith_flags_add(self, a, b, result):
        """
        This is given to you as an example which will help you write
        the other methods to update flags.
        """
        if result & (1 << (WORD_SIZE - 1)):
            self._flags |= N_FLAG
        if result == 0:
            self._flags |= Z_FLAG
        if a + b > WORD_MASK:
            self._flags |= C_FLAG
        sa, sb, sr = ((a >> (WORD_SIZE - 1)) & 1,
                      (b >> (WORD_SIZE - 1)) & 1,
                      (result >> (WORD_SIZE - 1)) & 1)
        if sa == sb and sr != sa:
            self._flags |= V_FLAG

    def _update_arith_flags_sub(self, a, b, result):
        """
        Update flags for SUB operation.
        """
        if result & (1 << (WORD_SIZE - 1)):
            self._flags |= N_FLAG
        if result == 0:
            self._flags |= Z_FLAG
        if a >= b:
            self._flags |= C_FLAG
        sa, sb, sr = ((a >> (WORD_SIZE - 1)) & 1,
                      (b >> (WORD_SIZE - 1)) & 1,
                      (result >> (WORD_SIZE - 1)) & 1)
        if sa != sb and sr != sa:
            self._flags |= V_FLAG


    def _update_shift_flags(self, result, bit_out):
        """
        Update flags for SHFT operation.
        """
        if result & (1 << (WORD_SIZE - 1)):
            self._flags |= N_FLAG
        if result == 0:
            self._flags |= Z_FLAG
        if bit_out:
            self._flags |= C_FLAG
