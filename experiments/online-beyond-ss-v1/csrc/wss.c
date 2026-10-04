/* Fast gap-histogram packing for online-beyond-ss-v1 (checked against sim.py in check_c.py).
 *
 * pack_wss: weighted Sum-of-Squares. Item s goes to the open gap g >= s (or a new bin, g = C)
 * that minimises  w[g]*(1 - 2N[g]) [g < C]  +  w[r]*(2N[r] + 1) [r = g - s > 0];
 * ties go to the smaller remainder r. For the last K items (t > T - K) it uses best fit
 * instead. With all w = 1 and K = 0 this is Csirik et al.'s Sum-of-Squares.
 * Returns the number of bins; the final gap histogram is written to N_out (length C + 1).
 */
#include <stdlib.h>
#include <string.h>
#include <math.h>

int pack_wss(const int *items, int n, int C, const double *w, int K, int *N_out) {
    int *N = (int *)calloc(C + 1, sizeof(int));
    int opened = 0;
    for (int t = 1; t <= n; t++) {
        int s = items[t - 1];
        int gsel = C;
        if (t > n - K) {
            for (int g = s; g < C; g++) if (N[g]) { gsel = g; break; }
        } else {
            int have = 0; double bd = 0; int br = 0;
            for (int g = s; g <= C; g++) {
                if (g < C && !N[g]) continue;
                int r = g - s;
                double d = (g < C ? w[g] * (double)(-2 * N[g] + 1) : 0.0) + (r > 0 ? w[r] * (double)(2 * N[r] + 1) : 0.0);
                if (!have || d < bd || (d == bd && r < br)) { have = 1; bd = d; br = r; gsel = g; }
            }
        }
        if (gsel == C) opened++; else N[gsel]--;
        if (gsel - s > 0) N[gsel - s]++;
    }
    if (N_out) memcpy(N_out, N, (C + 1) * sizeof(int));
    free(N);
    return opened;
}

/* pack_wss_vol: like pack_wss, but switches to best fit once the expected volume of the
 * remaining items, (n - t + 1) * mean_so_far, is at most c times the total open gap. The mean is
 * learned online from the items seen so far (the current item included). If c <= 0 it never switches. */
int pack_wss_vol(const int *items, int n, int C, const double *w, double c, int *N_out, int *switch_t) {
    int *N = (int *)calloc(C + 1, sizeof(int));
    int opened = 0; long gap = 0; long seen = 0; int sw = 0;
    for (int t = 1; t <= n; t++) {
        int s = items[t - 1];
        seen += s;
        int gsel = C;
        if (!sw && c > 0 && (double)(n - t + 1) * ((double)seen / t) <= c * (double)gap) { sw = 1; if (switch_t) *switch_t = t; }
        if (sw) {
            for (int g = s; g < C; g++) if (N[g]) { gsel = g; break; }
        } else {
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
    if (N_out) memcpy(N_out, N, (C + 1) * sizeof(int));
    free(N);
    return opened;
}

/* pack_fss: distribution-learning weighted SS with the volume switch of pack_wss_vol.
 * The weight on N(g) is F(g)^(-beta), where F(g) = (1 + #{seen items <= g}) / (1 + #seen) is the
 * empirical CDF of the item sizes seen so far, the current item included, times g^(-alpha)
 * (alpha = 0 gives the pure CDF weight). No distribution- or capacity-specific constant is built in. */
int pack_fss(const int *items, int n, int C, double beta, double alpha, double c, int *N_out, int *switch_t) {
    int *N = (int *)calloc(C + 1, sizeof(int));
    int *cnt = (int *)calloc(C + 1, sizeof(int));
    double *w = (double *)calloc(C + 1, sizeof(double));
    int opened = 0; long gap = 0; long seen = 0; int sw = 0;
    for (int t = 1; t <= n; t++) {
        int s = items[t - 1];
        seen += s; cnt[s]++;
        int gsel = C;
        if (!sw && c > 0 && (double)(n - t + 1) * ((double)seen / t) <= c * (double)gap) { sw = 1; if (switch_t) *switch_t = t; }
        if (sw) {
            for (int g = s; g < C; g++) if (N[g]) { gsel = g; break; }
        } else {
            long cum = 0;
            for (int g = 1; g <= C; g++) { cum += cnt[g]; w[g] = pow((1.0 + cum) / (1.0 + t), -beta) * pow((double)g, -alpha); }
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
    if (N_out) memcpy(N_out, N, (C + 1) * sizeof(int));
    free(N); free(cnt); free(w);
    return opened;
}
