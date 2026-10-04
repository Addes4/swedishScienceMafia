# Squares in a square: maximise the sum of side lengths

Place n squares inside the unit square [0, 1] x [0, 1] so that no two share an interior
point. The squares may have different sizes and may be rotated. Maximise the sum of their
side lengths.

Write `solve(n)` returning a list of n tuples `(centre_x, centre_y, angle, side)`, every
number in [0, 1]. `angle` is a fraction of a full turn (0.25 = 90 degrees). A square with
side 0 is allowed and counts as a point.

Your program is scored on several values of n; the score for each n is divided by a
reference value. Work out a method that works for every n, not a table of answers.
Runs are limited to 60 seconds per n.
