/* Exploratory (v2, not pre-registered): FWSS with a rollout finish.
 * Main phase as pack_fss (weights F(g)^-beta). Once the volume switch fires, each item is placed by
 * one-step rollout: for every distinct feasible gap (and a new bin), R futures of the remaining items
 * are sampled from the empirical size distribution seen so far (common random numbers across
 * candidates) and packed by best fit; the candidate with the fewest expected new bins wins
 * (ties: best fit's choice). Uses only past items, the item count n, and its own state. */
#include <stdlib.h>
#include <string.h>
#include <math.h>

static unsigned long long rs;
static inline double urand(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (rs >> 11) * (1.0 / 9007199254740992.0); }

static int bf_new_bins(int *N, int C, const int *fut, int k) {
    int opened = 0;
    for (int j = 0; j < k; j++) {
        int s = fut[j], g = s;
        while (g < C && !N[g]) g++;
        if (g == C) { opened++; } else N[g]--;
        if (g - s > 0) N[g - s]++;
    }
    return opened;
}

int pack_rollout(const int *items, int n, int C, double beta, double c, int R, unsigned long long seed) {
    int *N = calloc(C + 1, sizeof(int)), *cnt = calloc(C + 1, sizeof(int)), *tmp = malloc((C + 1) * sizeof(int));
    double *w = calloc(C + 1, sizeof(double)), *cdf = calloc(C + 1, sizeof(double));
    int *fut = malloc((size_t)R * n * sizeof(int));
    int opened = 0; long gap = 0, seen = 0; int sw = 0;
    rs = seed ? seed : 88172645463325252ULL;
    for (int t = 1; t <= n; t++) {
        int s = items[t - 1];
        seen += s; cnt[s]++;
        int gsel = C;
        if (!sw && c > 0 && (double)(n - t + 1) * ((double)seen / t) <= c * (double)gap) sw = 1;
        if (sw) {
            int left = n - t;
            int bfg = s; while (bfg < C && !N[bfg]) bfg++;
            if (left == 0) { gsel = bfg; }
            else {
                long cum = 0;
                for (int g = 1; g <= C; g++) { cum += cnt[g]; cdf[g] = (double)cum / t; }
                for (int r = 0; r < R; r++)
                    for (int j = 0; j < left; j++) {
                        double u = urand(); int x = 1; while (x < C && cdf[x] < u) x++;
                        fut[(size_t)r * left + j] = x;
                    }
                double best = 1e18; gsel = bfg;
                for (int g = s; g <= C; g++) {
                    if (g < C && !N[g]) continue;
                    double tot = 0;
                    for (int r = 0; r < R; r++) {
                        memcpy(tmp, N, (C + 1) * sizeof(int));
                        if (g < C) tmp[g]--;
                        if (g - s > 0) tmp[g - s]++;
                        tot += bf_new_bins(tmp, C, fut + (size_t)r * left, left) + (g == C);
                    }
                    double v = tot / R;
                    if (v < best - 1e-12 || (fabs(v - best) <= 1e-12 && g == bfg)) { best = v; gsel = g; }
                }
            }
        } else {
            long cum = 0;
            for (int g = 1; g <= C; g++) { cum += cnt[g]; w[g] = pow((1.0 + cum) / (1.0 + t), -beta); }
            int have = 0; double bd = 0; int br = 0;
            for (int g = s; g <= C; g++) {
                if (g < C && !N[g]) continue;
                int r = g - s;
                double d = (g < C ? w[g] * (double)(-2 * N[g] + 1) : 0.0) + (r > 0 ? w[r] * (double)(2 * N[r] + 1) : 0.0);
                if (!have || d < bd || (d == bd && r < br)) { have = 1; bd = d; br = r; gsel = g; }
            }
        }
        if (gsel == C) { opened++; gap += C - s; } else { N[gsel]--; gap -= s; }
        if (gsel - s > 0) N[gsel - s]++;
    }
    free(N); free(cnt); free(tmp); free(w); free(cdf); free(fut);
    return opened;
}
