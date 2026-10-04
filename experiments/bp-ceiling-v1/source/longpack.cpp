#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

// Fixed online packers for instances of any length (packing.cpp and contextual.cpp stop at
// 4,096 items). Candidates supply rules or weights only; this code owns feasibility.

// rule 0: best fit, 1: first fit, 2: worst fit. Only open bins are candidates; a new bin is
// opened when none fits. Ties go to the lowest bin index.
extern "C" int pack_rule(const int* items, int n, int capacity, int rule, int* assignments) {
    if (n < 0 || capacity < 1 || rule < 0 || rule > 2) return -1;
    std::vector<int> remaining;
    remaining.reserve(n);
    for (int k = 0; k < n; ++k) {
        const int item = items[k];
        if (item < 1 || item > capacity) return -1;
        int chosen = -1;
        for (int b = 0; b < (int)remaining.size(); ++b) {
            if (remaining[b] < item) continue;
            if (chosen < 0) { chosen = b; if (rule == 1) break; continue; }
            if (rule == 0 ? remaining[b] < remaining[chosen] : remaining[b] > remaining[chosen]) chosen = b;
        }
        if (chosen < 0) { chosen = (int)remaining.size(); remaining.push_back(capacity); }
        remaining[chosen] -= item;
        if (assignments) assignments[k] = chosen;
    }
    return (int)remaining.size();
}

// The twenty contextual features of contextual.cpp (capacity 100), computed identically.
// With allow_new = 1 an unused bin (remaining 100) is also a candidate, scored with the same
// features plus a 21st feature "is a new bin" (weight w[20]); open bins are scored exactly as
// in contextual.cpp. With allow_new = 0 and nw = 20 this reproduces pack_contextual.
extern "C" int pack_linear(const int* items, int n, const double* w, int nw, int allow_new, int* assignments) {
    if (n < 0 || (allow_new ? nw != 21 : nw != 20)) return -1;
    for (int j = 0; j < nw; ++j) if (!std::isfinite(w[j])) return -1;
    std::vector<int> remaining;
    remaining.reserve(n);
    int counts[101] = {0}, prefix[101] = {0}, nearest[101];
    std::fill(nearest, nearest + 101, 100);
    int past_sum = 0;
    for (int k = 0; k < n; ++k) {
        const int item = items[k];
        if (item < 1 || item > 100) return -1;
        prefix[0] = 0;
        for (int z = 1; z <= 100; ++z) prefix[z] = prefix[z-1] + counts[z];
        const double denominator = k + 25.0;
        const double past_mean = (past_sum + 1262.5) / denominator;
        auto score_of = [&](int r) {
            const int g = r - item;
            const double x = g / 100.0;
            const double p_fit = (prefix[g] + .25*g) / denominator;
            const double p_before = (prefix[r] + .25*r) / denominator;
            const int low = std::max(1, g-2), high = std::min(100, g+2);
            const double p_near = (prefix[high] - prefix[low-1] + .25*(high-low+1)) / denominator;
            const double distance = k ? nearest[g]/100.0 : std::fabs(g-50.5)/100.0;
            const double features[20] = {
                x, x*x, 1.0/(g+1.0), double(g==0), double(g>0 && g<10),
                double(g>0 && g<item), double(g>=item), std::fabs(x-.25),
                std::fabs(x-.5), std::fabs(x-.75), double(g>0 && g<33),
                double(g>0 && g<50), x*(1-p_fit), double(g>0)*(1-p_fit),
                p_near, distance, p_fit, x*p_fit, p_before-p_fit, x*past_mean/100.0
            };
            double score = 0;
            for (int j = 0; j < 20; ++j) score += w[j]*features[j];
            return score;
        };
        int chosen = -1;
        double best = -std::numeric_limits<double>::infinity();
        for (int b = 0; b < (int)remaining.size(); ++b) {
            if (remaining[b] < item) continue;
            const double score = score_of(remaining[b]);
            if (!std::isfinite(score)) return -1;
            if (score > best) { best = score; chosen = b; }
        }
        bool open_new = chosen < 0;
        if (allow_new) {
            const double score = score_of(100) + w[20];
            if (!std::isfinite(score)) return -1;
            if (score > best) open_new = true;
        }
        if (open_new) { chosen = (int)remaining.size(); remaining.push_back(100); }
        remaining[chosen] -= item;
        if (assignments) assignments[k] = chosen;
        ++counts[item]; past_sum += item;
        for (int z = 0; z <= 100; ++z) nearest[z] = std::min(nearest[z], std::abs(z - item));
    }
    return (int)remaining.size();
}
