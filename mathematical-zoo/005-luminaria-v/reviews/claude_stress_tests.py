"""Stress tests for Luminaria V, by Claude (the rival laboratory).

Re-implements the published update rule with switches for the things the original could not vary:
walled edges, no nutrient source, a source that never moves, a memory wipe confined to the wound,
other wound sites, a long run, and jittered parameters. Test 0 must match the archived numbers.

Run:  python claude_stress_tests.py     (NumPy only; about 3 minutes)
"""
import numpy as np
P0=dict(n_diff=.16,n_keep=.994,src_add=.09,cons=.018,m_keep=.986,m_add=.06,flow=.032,growth=.16,gthr=.12,gbase=.26,gN=2.,memreg=.14,mthr=.09,mbase=.14,persist=.085,pthr=.08,decay=.030,dbase=.14,dthr=.07,spread=.022,cut=.007)
G=180
Y,X=np.mgrid[:G,:G]
SL=((X-24)**2+(Y-90)**2<=13**2); SR=((X-156)**2+(Y-90)**2<=13**2)

def sh(a,s,ax,periodic):
    r=np.roll(a,s,ax)
    if not periodic:  # zero-flux: replicate edge
        idx=[slice(None)]*2
        if s==1: idx[ax]=0; src=[slice(None)]*2; src[ax]=0; r[tuple(idx)]=a[tuple(src)]
        else: idx[ax]=-1; src=[slice(None)]*2; src[ax]=-1; r[tuple(idx)]=a[tuple(src)]
    return r
def step(B,N,M,t,P,mem=True,periodic=True,switch=250,source=True):
    lap=lambda a: sh(a,1,0,periodic)+sh(a,-1,0,periodic)+sh(a,1,1,periodic)+sh(a,-1,1,periodic)-4*a
    src=SL if t<=switch else SR
    N=N+P['n_diff']*lap(N); N=N*P['n_keep']
    if source: N[src]+=P['src_add']
    N=N-P['cons']*B*N; N=np.clip(N,0,1.5)
    M=np.clip(P['m_keep']*M+P['m_add']*B,0,1) if mem else np.zeros_like(M)
    nb=.40*B+.15*(sh(B,1,0,periodic)+sh(B,-1,0,periodic)+sh(B,1,1,periodic)+sh(B,-1,1,periodic))
    grad=.5*(sh(N,-1,1,periodic)-sh(N,1,1,periodic))
    growth=P['growth']*(1-B)*np.maximum(nb-P['gthr'],0)*(P['gbase']+P['gN']*N)
    reg=(P['memreg']*(1-B)*M*np.maximum(nb-P['mthr'],0)*(P['mbase']+N)) if mem else 0
    persist=P['persist']*B*np.maximum(nb-P['pthr'],0)
    decay=P['decay']*B*(P['dbase']+np.maximum(0,P['dthr']-N))
    B=np.clip(B+growth+reg+persist+P['spread']*lap(B)-decay+P['flow']*grad*B,0,1)
    B[B<P['cut']]=0
    return B,N,M

def run(P=P0,T=620,inj_t=370,wound=(slice(74,106),slice(52,84)),arms=('sham_memory','injured_memory','sham_no_memory','injured_no_memory'),record=(370,430,620),metric_zone=None,**kw):
    zone=metric_zone or wound
    B=np.zeros((G,G)); B[(X-40)**2+(Y-90)**2<=12**2]=.92
    st={'base':(B,np.zeros_like(B),np.zeros_like(B))}; out={}; snaps={}
    for t in range(1,T+1):
        if t==inj_t:
            pre=st['base']; st={a:tuple(q.copy() for q in pre) for a in arms}
            snaps['pre']=tuple(q.copy() for q in pre)
        for a,(B,N,M) in list(st.items()):
            mem='no_memory' not in a
            B,N,M=step(B,N,M,t,P,mem=mem,**kw)
            if t==inj_t and 'injured' in a:
                B[wound]=0
                if 'wipeM' in a: M[wound]=0
            st[a]=(B,N,M)
            if t in record: out[(a,t)]=(B.sum(),B[zone].mean())
        if t in record: snaps[t]={a:tuple(q.copy() for q in s) for a,s in st.items()}
    return out,snaps
def table(out,ts,arms):
    for a in arms: print('  %-26s'%a,' '.join('%d: %.4f (mass %.0f)'%(t,out[(a,t)][1],out[(a,t)][0]) for t in ts))
A4=('sham_memory','injured_memory','sham_no_memory','injured_no_memory')

def main():

    print('0. baseline (my reimplementation must match archive)'); o,s=run(); table(o,(370,430,620),A4)
    pre=s['pre']; B,N,M=pre
    w=(slice(74,106),slice(52,84))
    print('  pre-injury: frac of wound cells with B>0.5: %.3f ; M mean in wound %.3f ; M>0.99 frac in body(B>.5) %.3f'%((B[w]>.5).mean(),M[w].mean(),(M[B>.5]>.99).mean()))
    print('  N stats at 369: max %.3f, frac of grid with N>0.01: %.3f, mean N inside body(B>.5): %.4f, mean N in wound %.5f'%(N.max(),(N>0.01).mean(),N[B>.5].mean(),N[w].mean()))
    print('  B saturation: frac of body cells (B>0.01) with B>0.99: %.3f'%((B[B>.01]>.99).mean()))
    # where did regrowth happen relative to old footprint
    for a in ('injured_memory','injured_no_memory'):
        Bf=s[620][a][0]; old=pre[0][w]>.5
        print('  %s @620: density on old footprint %.3f, on never-occupied part %.3f ; sham same split %.3f / %.3f'%(a,Bf[w][old].mean(),Bf[w][~old].mean(),s[620][a.replace('injured','sham')][0][w][old].mean(),s[620][a.replace('injured','sham')][0][w][~old].mean()))
    did=(o[('injured_memory',620)][1]-o[('injured_no_memory',620)][1])-(o[('sham_memory',620)][1]-o[('sham_no_memory',620)][1])
    print('  memory effect in injured %.4f, in sham %.4f, diff-in-diff %.4f'%(o[('injured_memory',620)][1]-o[('injured_no_memory',620)][1],o[('sham_memory',620)][1]-o[('sham_no_memory',620)][1],did))

    print('1. local memory wipe in wound only (regrowth term left on)'); o,_=run(arms=A4+('injured_wipeM',)); table(o,(430,620),('injured_memory','injured_wipeM','injured_no_memory'))
    print('2. no nutrient source at all'); o,_=run(source=False); table(o,(370,430,620),A4)
    print('3. source never switches'); o,_=run(switch=10**9); table(o,(370,430,620),A4)
    print('4. non-periodic (walled) boundaries'); o,sn=run(periodic=False); table(o,(370,430,620),A4)
    print('   right-edge biomass x>=150 at 620: periodic vs walled'); 
    o2,sp=run(); print('   periodic %.1f  walled %.1f'%(sp[620]['sham_memory'][0][:,150:].sum(),sn[620]['sham_memory'][0][:,150:].sum()))
    print('5. flow term off'); P=dict(P0,flow=0); o,_=run(P=P); table(o,(370,430,620),A4)
    print('6. long run to 3000 steps'); o,sl=run(T=3000,record=(370,620,1000,1500,2000,3000)); table(o,(620,1000,1500,2000,3000),A4)
    print('   grid coverage (B>0.5) at 3000: %.3f of %d cells'%((sl[3000]['sham_memory'][0]>.5).mean(),G*G))
    print('7. other wound sites (same 32x32 size), density in that zone')
    for name,wd in [('interior x20-51,y74-105',(slice(74,106),slice(20,52))),('upper flank x20-51,y40-71',(slice(40,72),slice(20,52))),('front, shifted up y50-81',(slice(50,82),slice(52,84))),('empty space ahead x90-121',(slice(74,106),slice(90,122)))]:
        o,_=run(wound=wd); print(' ',name); table(o,(370,430,620),A4)
    print('8. parameter jitter +-10%, 30 draws: memory diff-in-diff at 620 and injured/sham ratio')
    rng=np.random.default_rng(0); dd=[];rat=[];ie=[]
    for i in range(30):
        P={k:v*rng.uniform(.9,1.1) for k,v in P0.items()}
        o,_=run(P=P)
        dd.append((o[('injured_memory',620)][1]-o[('injured_no_memory',620)][1])-(o[('sham_memory',620)][1]-o[('sham_no_memory',620)][1]))
        ie.append(o[('injured_memory',620)][1]-o[('injured_no_memory',620)][1])
        rat.append(o[('injured_memory',620)][1]/max(o[('sham_memory',620)][1],1e-9))
    dd=np.array(dd);rat=np.array(rat);ie=np.array(ie)
    print('   diff-in-diff: min %.4f median %.4f max %.4f, positive in %d/30'%(dd.min(),np.median(dd),dd.max(),(dd>0).sum()))
    print('   injured mem-nomem: min %.4f median %.4f max %.4f, positive in %d/30'%(ie.min(),np.median(ie),ie.max(),(ie>0).sum()))
    print('   injured/sham ratio: min %.3f median %.3f max %.3f'%(rat.min(),np.median(rat),rat.max()))

if __name__=='__main__':
    main()
