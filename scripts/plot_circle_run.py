"""Plot independently audited geometry from a completed circle run."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run');args=ap.parse_args()
    folder=Path(args.run)
    raw=json.loads((folder/'audit_raw.json').read_text())
    cfg=json.loads((folder/'config.json').read_text())
    candidate=raw['policies'][cfg['actual_gate']]['original']['rows'][0]
    reference=raw['reference']['rows'][0]
    fig,axes=plt.subplots(1,2,figsize=(9,4.8),layout='constrained')
    for ax,row,title in zip(axes,[reference,candidate],['Provided seed','Frozen generated solver']):
        if not row['valid']:raise ValueError('Cannot plot invalid audited geometry')
        centers,radii=row['construction']
        for index,(center,radius) in enumerate(zip(centers,radii)):
            ax.add_patch(Circle(center,radius,facecolor=plt.cm.viridis(radius/.15),edgecolor='#16324f',alpha=.82,linewidth=.8))
            if radius>.018:ax.text(*center,str(index+1),ha='center',va='center',fontsize=6,color='white')
        ax.set(xlim=(0,1),ylim=(0,1),aspect='equal',xlabel='x',ylabel='y')
        ax.set_title(f'{title}\nRadius sum {row["score"]:.6f}',fontsize=12)
        ax.grid(alpha=.12)
    fig.suptitle(f'n = 26 · First fresh audit case · Both pass strict geometry checks',fontsize=12)
    fig.savefig(folder/'construction.png',dpi=180)
    fig.savefig(folder/'construction.svg')
    print(folder/'construction.png')


if __name__=='__main__':main()
