LOADI R0, #0
LOADI R1, #5
LOADI R2, #1
LOADI R3, #9

LOOP:
    SHFT R4, R1, R2
    STORE R4, [R0+#0]
    ADDI R0, R0, #1
    ADDI R2, R2, #1
    ADDI R3, R3, #-1
    BNE LOOP

HALT





