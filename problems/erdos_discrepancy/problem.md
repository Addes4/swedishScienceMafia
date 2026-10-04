# Long sign sequences with small discrepancy

Find a sequence x_1, x_2, ..., x_L with every x_i equal to +1 or -1, as long as possible, such
that for every step d >= 1 and every k with kd <= L:

    | x_d + x_2d + x_3d + ... + x_kd | <= 2

Write `solve()` returning the list [x_1, x_2, ..., x_L]. The score is the length of the
longest prefix that satisfies the condition (plus a small bonus for having fewer violations
at the first failing length). The program may run for up to 120 seconds.
