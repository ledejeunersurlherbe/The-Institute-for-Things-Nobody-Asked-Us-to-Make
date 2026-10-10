"""Checks on Thirty-two Clocks, by Claude (the rival laboratory).

Re-run the original into a scratch folder first, then compare the two:
    mkdir /tmp/rerun && cp ../original/clock_choir.py /tmp/rerun/ && python /tmp/rerun/clock_choir.py
    python claude_choir_check.py ../original /tmp/rerun
Needs NumPy, SciPy, pandas.
"""
import sys, numpy as np, pandas as pd
from scipy.io import wavfile
A,B=sys.argv[1],sys.argv[2]
for f in ['order_parameter.csv','note_events.csv','oscillators.csv','seed_sweep.csv']:
    a,b=pd.read_csv(f'{A}/{f}'),pd.read_csv(f'{B}/{f}'); print(f,'rows',len(a),len(b),'max abs diff',float(np.abs(a.values-b.values).max()))
for f in ['thirty_two_clocks.wav','uncoupled_control.wav']:
    (sa,a),(sb,b)=wavfile.read(f'{A}/{f}'),wavfile.read(f'{B}/{f}'); print(f,sa,a.shape,'max sample diff',int(np.abs(a.astype(int)-b.astype(int)).max()))
sr,x=wavfile.read(f'{A}/listen_to_sync.wav'); sr2,full=wavfile.read(f'{A}/thirty_two_clocks.wav')
seg=full[int(44*sr2):int(44*sr2)+len(x)]; print('excerpt',sr,x.shape,len(x)/sr,'s; equals 44-74s slice of main:',x.shape==seg.shape and int(np.abs(x.astype(int)-seg.astype(int)).max()))
ev=pd.read_csv(f'{A}/note_events.csv'); osc=pd.read_csv(f'{A}/oscillators.csv'); op=pd.read_csv(f'{A}/order_parameter.csv')
f=osc.natural_frequency_hz.values
print('freqs: min %.3f max %.3f mean %.4f -> mean period %.4f ; n clipped at 0.55: %d'%(f.min(),f.max(),f.mean(),1/f.mean(),(f<=.5501).sum()))
def periods(lo,hi):
    out=[]
    for j,g in ev[(ev.time_s>=lo)&(ev.time_s<hi)].groupby('oscillator_id'): out.append(np.median(np.diff(g.time_s.values)))
    return np.array(out)
for lo,hi,n in [(0,22,'independent'),(35,48,'weak'),(62,79,'strong'),(93,105,'released')]:
    p=periods(lo,hi); print('%-11s median period per clock: min %.4f max %.4f spread %.4f'%(n,p.min(),p.max(),p.max()-p.min()))
# how tight is the "chord"? spread of strike times within each beat during strong coupling
s=ev[(ev.time_s>=62)&(ev.time_s<79)].sort_values('time_s'); t=s.time_s.values; gaps=np.diff(t); cuts=np.where(gaps>0.4)[0]
groups=np.split(t,cuts+1); full_g=[g for g in groups if len(g)==32]
print('strong window: %d beats, %d with all 32 clocks; within-beat spread (first to last strike): median %.3f s, of a %.3f s cycle'%(len(groups),len(full_g),np.median([g.max()-g.min() for g in full_g]),1/f.mean()))
# order of strikes within a beat vs natural frequency
g0=s.iloc[:0]
import scipy.stats as st
rho=[st.spearmanr(g_t, f[g_id]).statistic for g_t,g_id in [(g, s.oscillator_id.values[np.isin(t,g)]) for g in full_g]]
print('strike order vs natural frequency within each full beat (Spearman): min %.3f max %.3f over %d beats'%(min(rho),max(rho),len(rho)))
# theory: critical coupling for this spread
sig=2*np.pi*0.115; print('theory: critical K about %.2f (weak phase K=1 is below it, strong K=3 well above)'%(2/(np.pi/(sig*np.sqrt(2*np.pi)))))
# decay after release
for tt in (80,85,86,88,90,93,100): print('  R at %ds: %.3f'%(tt,op.coherence_R[(op.time_s-tt).abs().idxmin()]),end='')
print(); print('events coupled vs control: equal totals?', len(ev))
# dt sensitivity
sys.path.insert(0,B); import clock_choir as cc
for dt in (0.005,0.001):
    cc.DT=dt; ts,r,_,_,e=cc.simulate(); print('dt',dt,'strong-window mean R %.4f'%r[(ts>=62)&(ts<79)].mean(),'events',len(e))
