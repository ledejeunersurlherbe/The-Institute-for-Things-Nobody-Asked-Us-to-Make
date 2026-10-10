"""Luminaria V controlled experiment. numpy/matplotlib. python luminaria_v_controlled.py"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
P = dict(n_diff=.16,n_keep=.994,src_add=.09,cons=.018,m_keep=.986,m_add=.06,flow=.032,growth=.16,gthr=.12,gbase=.26,gN=2.,memreg=.14,mthr=.09,mbase=.14,persist=.085,pthr=.08,decay=.030,dbase=.14,dthr=.07,spread=.022,cut=.007)
NGRID=180; T_END=620; INJURY_T=370
Y,X=np.mgrid[:NGRID,:NGRID]; source_left=((X-24)**2+(Y-90)**2<=13**2); source_right=((X-156)**2+(Y-90)**2<=13**2)
wound=(slice(74,106),slice(52,84))

def lap(a):
    return np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)-4*a

def one_step(B,N,M,t,memory_on=True):
    src=source_left if t<=250 else source_right
    N=N.copy(); B=B.copy(); M=M.copy()
    N += P['n_diff']*lap(N)
    N *= P['n_keep']; N[src] += P['src_add']; N -= P['cons']*B*N
    N=np.clip(N,0,1.5)
    if memory_on:
        M=np.clip(P['m_keep']*M+P['m_add']*B,0,1)
    else: M[:]=0
    nb=.40*B+.15*(np.roll(B,1,0)+np.roll(B,-1,0)+np.roll(B,1,1)+np.roll(B,-1,1))
    grad=.5*(np.roll(N,-1,1)-np.roll(N,1,1))
    growth=P['growth']*(1-B)*np.maximum(nb-P['gthr'],0)*(P['gbase']+P['gN']*N)
    reg=(P['memreg']*(1-B)*M*np.maximum(nb-P['mthr'],0)*(P['mbase']+N)) if memory_on else 0
    persist=P['persist']*B*np.maximum(nb-P['pthr'],0)
    decay=P['decay']*B*(P['dbase']+np.maximum(0,P['dthr']-N))
    B=np.clip(B+growth+reg+persist+P['spread']*lap(B)-decay+P['flow']*grad*B,0,1)
    B[B<P['cut']]=0
    return B,N,M

def state_metrics(B):
    m=float(B.sum()); return (m,float((B*X).sum()/m) if m>0 else float('nan'),float(B[wound].mean()))

def run():
    B0=np.zeros((NGRID,NGRID)); B0[(X-40)**2+(Y-90)**2<=12**2]=.92
    states={'base':(B0,np.zeros_like(B0),np.zeros_like(B0))}
    histories=[]; images={}
    for t in range(1,T_END+1):
        if t==INJURY_T:
            pre=states['base']; states={
                'sham_memory':tuple(q.copy() for q in pre),
                'injured_memory':tuple(q.copy() for q in pre),
                'sham_no_memory':tuple(q.copy() for q in pre),
                'injured_no_memory':tuple(q.copy() for q in pre)
            }
        for arm,(B,N,M) in list(states.items()):
            has_memory=not ('no_memory' in arm)
            B,N,M=one_step(B,N,M,t,memory_on=has_memory)
            if t==INJURY_T and 'injured' in arm: B[wound]=0
            states[arm]=(B,N,M)
            mass,com,density=state_metrics(B)
            histories.append((t,arm,mass,com,density))
            if t in (369,370,430,520,620): images[(arm,t)]=B.copy()
    return histories,images

if __name__=='__main__':
    histories,images=run()
    with open(OUT/'luminaria_v_measurements.csv','w',newline='') as f:
        w=csv.writer(f);w.writerow(['step','arm','total_biomass','center_x','wound_zone_mean_density']);w.writerows(histories)
    d={(t,arm):(mass,com,dens) for t,arm,mass,com,dens in histories}
    arms=['sham_memory','injured_memory','sham_no_memory','injured_no_memory']
    print('PREINJURY',d[(369,'base')]);
    for arm in arms:
        print(arm,'t370',d[(370,arm)],'t430',d[(430,arm)],'t620',d[(620,arm)])
    # Observe wound-area recovery vs simultaneous sham, for matched initial worlds.
    for typ in ['memory','no_memory']:
        s=d[(620,'sham_'+typ)][2];inj=d[(620,'injured_'+typ)][2]
        print(typ,'final wound region density:',inj,'sham:',s,'injured/sham:',inj/s if s else None)
    fig,ax=plt.subplots(figsize=(9,5),dpi=160)
    for arm in arms:
        data=[(t,d[(t,arm)][2]) for t in range(370,621)]
        ax.plot([v[0] for v in data],[v[1] for v in data],label=arm.replace('_',' '))
    ax.set(title='Paired injury and memory-ablation trials',xlabel='Time step',ylabel='Mean biomass in target region');ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'luminaria_v_recovery.png');plt.close(fig)
    fig,axes=plt.subplots(2,4,figsize=(13,7),dpi=155)
    for i,arm in enumerate(arms):
        for j,t in enumerate((370,620)):
            ax=axes[j,i];ax.imshow(images[(arm,t)],vmin=0,vmax=1,cmap='magma',interpolation='nearest');ax.set_title(f'{arm.replace("_"," ")} • {t}',fontsize=9);ax.set_xticks([]);ax.set_yticks([])
            from matplotlib.patches import Rectangle
            ax.add_patch(Rectangle((52,74),32,32,fill=False,edgecolor='cyan',linewidth=1))
    fig.suptitle('Luminaria V: four identical pre-injury histories; condition changes at step 370')
    fig.tight_layout();fig.savefig(OUT/'luminaria_v_specimens.png',bbox_inches='tight');plt.close(fig)
    lines=['# Luminaria V — controlled laboratory record','','## Design','Four arms share identical initial conditions and steps 1–369. At step 370, one factor is injury (removing biomass from cells x=52..83, y=74..105), one is memory ablation (M reset to zero and memory-dependent regrowth removed thereafter). Source switches from x=24 to x=156 after step 250. All conditions otherwise identical.','', '## Outcomes','', '| Arm | Wound area mean immediately after intervention | At step 430 | At step 620 | Total biomass at 620 |','|---|---:|---:|---:|---:|']
    for arm in arms: lines.append(f'| {arm} | {d[(370,arm)][2]:.4f} | {d[(430,arm)][2]:.4f} | {d[(620,arm)][2]:.4f} | {d[(620,arm)][0]:.1f} |')
    lines+=['','## Limitations','- Regrowth is not by itself proof of homeostasis, self-directed repair, cognition, or living status.','- This is one seeded environment and one wound location, not a statistical sample.','- The sham branches provide matched counterfactuals; conclusions are limited to these deterministic rules.','- The memory ablation also changes the local growth dynamics and so does not isolate mnemonic content from a growth contribution.','- The model has no autonomous reproduction, and body boundaries are diffuse.','','## Reproducibility','Run `python luminaria_v_controlled.py` with NumPy and Matplotlib. Parameters, initial conditions, update equations, intervention schedule, metrics, and figures are all embedded in that source file. CSV records each trial.']
    (OUT/'luminaria_v_lab_report.md').write_text('\n'.join(lines))
