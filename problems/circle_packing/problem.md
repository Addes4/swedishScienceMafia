# Circle packing: maximise the sum of radii

Place n = 26 circles inside the unit square [0, 1] x [0, 1] without overlaps (touching is
fine). Circles may have different radii. Maximise the sum of the radii.

Write `solve(n=26)` returning `(centers, radii)`: `centers` an n x 2 array of (x, y)
coordinates and `radii` an array of n non-negative numbers. The program may run for up to
300 seconds.
