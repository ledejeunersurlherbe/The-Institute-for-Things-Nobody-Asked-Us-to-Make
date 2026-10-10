"""Luminaria IV: explicitly reconstructed Gray–Scott parameter recombination demo.
NOT the original missing source. Run: python reconstructed_breeding.py
Requires numpy, matplotlib; writes reconstruction.png, measurements.csv.
"""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
N=130; STEPS=950; SEED=42; THRESHOLD=0.08
# Values preserved from contemporaneous experiment writeup.
parents={
 'Parent A': dict(Du=.160,Dv=.080,feed=.032,kill=.060),
 'Parent B': dict(Du=.150,Dv=.075,feed=.039,kill=.063),
}
# Historical offspring values as reported. Mixing is not literally one-gene-per-parent:
# feed .033 and kill .0625 require mutation/recombination details unavailable.
offspring=dict(Du=.160,Dv=.075,feed=.033,kill=.0625)
params={**parents,'Reconstructed offspring':offspring}

def initial_state():
    rng=np.random.default_rng(SEED)
    u=np.ones((N,N));v=np.zeros((N,N))
    for _ in range(5):
        x,y=rng.integers(40,N-40,size=2)
        r=int(rng.integers(3,7))
        yy,xx=np.ogrid[:N,:N]
        loc=(xx-x)**2+(yy-y)**2<=r*r
        u[loc]=.50;v[loc]=.25
    return u,v

def lap(a):
    return (np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)-4*a)

def simulate(p):
    u,v=initial_state()
    for _ in range(STEPS):
        uvv=u*v*v
        du=p['Du']*lap(u)-uvv+p['feed']*(1-u)
        dv=p['Dv']*lap(v)+uvv-(p['feed']+p['kill'])*v
        u+=du;v+=dv
    return v

def main():
    fig,axs=plt.subplots(1,3,figsize=(12,4.3),constrained_layout=True)
    with (HERE/'reconstructed_measurements.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['lineage','Du','Dv','feed','kill','seed','steps','V_threshold','occupied_cells'])
        for ax,(name,p) in zip(axs,params.items()):
            v=simulate(p);occupied=int(np.count_nonzero(v>THRESHOLD))
            writer.writerow([name,p['Du'],p['Dv'],p['feed'],p['kill'],SEED,STEPS,THRESHOLD,occupied])
            ax.imshow(v,cmap='magma',vmin=0,vmax=.35)
            ax.set_title(f'{name}\noccupied: {occupied:,}')
            ax.set_xticks([]);ax.set_yticks([])
            print(name,p,'occupied_cells=',occupied)
    fig.suptitle('Luminaria IV / independently reconstructed breeding protocol')
    fig.savefig(HERE/'reconstruction.png',dpi=170)
if __name__=='__main__':main()
