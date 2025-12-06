START:
    LOADI   R0, #3
    LOADI   R1, #1

    SHFT    R2, R0, R1
    SHFT    R3, R2, R1
    SHFT    R4, R3, R1
    SHFT    R5, R4, R1
    SHFT    R6, R5, R1
    SHFT    R7, R6, R1

    ADDI    R1, R0, #0
    ADDI    R1, R2, #0
    ADDI    R1, R1, #0
    ADDI    R1, R1, #0
    ADDI    R1, R1, #0

    HALT
