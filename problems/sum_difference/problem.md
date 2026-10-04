# Sets with many differences and few sums

Find a finite set A of integers for which the difference set A - A = {a - b} is large
while the sum set A + A = {a + b} is small. Maximise

    log |A - A| / log |A + A|

(plus a small bonus of (1 - 1/|A|) / 100 that favours larger sets).

Write `solve()` returning A as a list of distinct integers (at most 4000 of them, each with
absolute value at most 1e15). The program may run for up to 120 seconds.
