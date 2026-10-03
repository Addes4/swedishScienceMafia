#include <algorithm>
#include <cmath>
#include <limits>

// Twenty bounded scoring features. Online statistics contain past items only.
extern "C" int pack_contextual(const int* items, int n, const double* w, int* assignments) {
    if (n < 0 || n > 4096) return -1;
    for (int j=0;j<20;++j) if (!std::isfinite(w[j])) return -1;
    int remaining[4096], counts[101]={0}, prefix[101]={0}, nearest[101];
    std::fill(nearest,nearest+101,100);
    int bins=0, past_sum=0;
    for (int k=0;k<n;++k) {
        const int item=items[k];
        if (item<1 || item>100) return -1;
        prefix[0]=0;
        for (int z=1;z<=100;++z) prefix[z]=prefix[z-1]+counts[z];
        const double denominator=k+25.0;
        const double past_mean=(past_sum+1262.5)/denominator;
        int chosen=-1;
        double best=-std::numeric_limits<double>::infinity();
        for (int b=0;b<bins;++b) {
            const int r=remaining[b];
            if (r<item) continue;
            const int g=r-item;
            const double x=g/100.0;
            const double p_fit=(prefix[g]+.25*g)/denominator;
            const double p_before=(prefix[r]+.25*r)/denominator;
            const int low=std::max(1,g-2), high=std::min(100,g+2);
            const double p_near=(prefix[high]-prefix[low-1]+.25*(high-low+1))/denominator;
            const double distance=k ? nearest[g]/100.0 : std::fabs(g-50.5)/100.0;
            const double features[20]={
                x,x*x,1.0/(g+1.0),double(g==0),double(g>0 && g<10),
                double(g>0 && g<item),double(g>=item),std::fabs(x-.25),
                std::fabs(x-.5),std::fabs(x-.75),double(g>0 && g<33),
                double(g>0 && g<50),x*(1-p_fit),double(g>0)*(1-p_fit),
                p_near,distance,p_fit,x*p_fit,p_before-p_fit,x*past_mean/100.0
            };
            double score=0;
            for (int j=0;j<20;++j) score+=w[j]*features[j];
            if (!std::isfinite(score)) return -1;
            if (score>best) {best=score;chosen=b;}
        }
        if (chosen<0) {chosen=bins++;remaining[chosen]=100;}
        remaining[chosen]-=item;
        if (assignments) assignments[k]=chosen;
        ++counts[item];past_sum+=item;
        for (int z=0;z<=100;++z) nearest[z]=std::min(nearest[z],std::abs(z-item));
    }
    return bins;
}
