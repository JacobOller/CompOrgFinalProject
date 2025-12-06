START:
    LOADI R0, #0xAA
    LOADI R1, #0x55
    LOADI R2, #0x00

    AND R3, R0, R1
    BNE UNSAFE

SAFE:
    OR R2, R0, R1
    HALT

UNSAFE:
    HALT
