START:
    LOADI R0, #0xC0
    LUI   R0, #0x01
    LOADI R1, #0x01
    LUI   R1, #0x80

    SHFT  R2, R0, R1
    ADDI  R1, R1 #1
    SHFT  R3, R0, R1
    ADDI  R1, R1 #1
    SHFT  R4, R0, R1
    ADDI  R1, R1 #1
    SHFT  R5, R0, R1
    ADDI  R1, R1 #1
    SHFT  R6, R0, R1
    ADDI  R1, R1 #1
    SHFT  R7, R0, R1

    HALT
