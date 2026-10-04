#include <cmath>
#include <limits>

// Only this fixed packer owns feasibility and scoring evaluation.
// Candidate parameters cannot inspect the instance, future items, or the grader.
extern "C" int pack(const int* items, int n, const double* w, int* assignments) {
    int remaining[4096];
    if (n < 0 || n > 4096) return -1;
    int bins = 0;
    for (int k = 0; k < n; ++k) {
        const int item = items[k];
        if (item < 1 || item > 100) return -1;
        int chosen = -1;
        double best = -std::numeric_limits<double>::infinity();
        for (int b = 0; b < bins; ++b) {
            if (remaining[b] < item) continue;
            const int g = remaining[b] - item;
            const double x = g / 100.0;
            const double features[12] = {
                x, x*x, 1.0/(g+1.0), double(g==0),
                double(g>0 && g<10), double(g>0 && g<item),
                double(g>=item), std::fabs(x-.25), std::fabs(x-.5),
                std::fabs(x-.75), double(g>0 && g<33), double(g>0 && g<50)
            };
            double score = 0;
            for (int j=0; j<12; ++j) score += w[j]*features[j];
            if (!std::isfinite(score)) return -1;
            if (score > best) {best=score; chosen=b;}
        }
        if (chosen < 0) {chosen=bins++; remaining[chosen]=100;}
        remaining[chosen] -= item;
        if (assignments) assignments[k]=chosen;
    }
    return bins;
}
