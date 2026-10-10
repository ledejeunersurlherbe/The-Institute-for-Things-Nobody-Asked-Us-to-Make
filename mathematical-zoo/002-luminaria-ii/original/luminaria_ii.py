"""Luminaria II: 16-state-channel neural cellular automaton.
Reproducible experiment: growth, injury, regrowth metrics.
Requires numpy, matplotlib, torch.
"""
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F, matplotlib.pyplot as plt
from pathlib import Path
import time
start=time.time(); torch.manual_seed(17);np.random.seed(17);torch.set_num_threads(3)
N=32; C=16; B=4; iterations=280
# The target is a translucent ring with a bright core, an evocative simple 'organism'.
yy,xx=np.mgrid[:N,:N]; r=np.sqrt((xx-15.5)**2+(yy-15.5)**2)
target=np.exp(-((r-8)/2.2)**2)*0.85+np.exp(-(r/4.0)**2)*0.65
target=np.clip(target,0,1).astype('float32')
target=torch.tensor(target)[None,None]
# Sobel perceptions are locally available spatial gradients, same rule every cell.
sobel_x=torch.tensor([[-1,0,1],[-2,0,2],[-1,0,1]],dtype=torch.float32)/8
sobel_y=sobel_x.T.contiguous()
k=torch.stack([torch.zeros((3,3)).index_put((torch.tensor([1]),torch.tensor([1])),torch.tensor([1.])),sobel_x,sobel_y])
perception_kernel=k[:,None].repeat(C,1,1,1) # reorder for channel-major grouped convolution

class NCA(nn.Module):
 def __init__(self):
  super().__init__()
  self.l1=nn.Conv2d(C*3,64,1)
  self.l2=nn.Conv2d(64,C,1,bias=False)
  nn.init.zeros_(self.l2.weight)
 def forward(self,x, update_prob=.5):
  z=F.conv2d(x,perception_kernel,padding=1,groups=C)
  dx=self.l2(F.relu(self.l1(z)))
  fire=(torch.rand_like(x[:,:1]) < update_prob).float()
  # channel 0 = visible density, other channels represent hidden cell states
  return x+dx*fire

def seed(batch=1):
 x=torch.zeros(batch,C,N,N)
 x[:,3,15,15]=1
 return x

model=NCA();opt=torch.optim.Adam(model.parameters(),lr=.003)
losses=[]
for i in range(iterations):
 x=seed(B)
 rollout=20+(i%12)
 for _ in range(rollout):x=model(x)
 visible=torch.sigmoid(x[:,:1]*3)-.5 # map ~0 baseline, increasing visibility
 loss=((visible-target)**2).mean() + .0002*(x**2).mean()
 opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step()
 losses.append(loss.item())
 if (i+1)%70==0:print('trained',i+1,'loss',round(loss.item(),5),'seconds',round(time.time()-start,1),flush=True)

# Run deterministic reproducible stochastic updates from the same RNG state.
torch.manual_seed(2026)
x=seed()
snaps={}
with torch.no_grad():
 for t in range(1,49):
  x=model(x)
  if t in (1,16,32,48):snaps[f'growth {t}']=torch.clamp((torch.sigmoid(x[0,0]*3)-.5)*2,0,1).numpy()
 baseline=x.clone()
 # Identical continued stochastic masks for wounded and control, minimizing measurement noise
 wounded=x.clone(); wounded[:,:,9:23,16:28]=0
 wound0=torch.clamp((torch.sigmoid(wounded[0,0]*3)-.5)*2,0,1).numpy()
 snaps['injured']=wound0
 control=x.clone()
 for t in range(1,65):
  state=torch.get_rng_state()
  control=model(control)
  torch.set_rng_state(state)
  wounded=model(wounded)
  if t in (16,32,64):snaps[f'repair {t}']=torch.clamp((torch.sigmoid(wounded[0,0]*3)-.5)*2,0,1).numpy()

out=Path('/mnt/data'); torch.save({'state_dict':model.state_dict(),'seed':17,'n':N,'channels':C,'iterations':iterations},out/'luminaria_ii_weights.pt')
fig, axes=plt.subplots(2,4,figsize=(13,7),dpi=130,facecolor='#0e1018')
keys=['growth 1','growth 16','growth 32','growth 48','injured','repair 16','repair 32','repair 64']
for ax,key in zip(axes.flat,keys):
 ax.imshow(snaps[key],cmap='magma',vmin=0,vmax=1);ax.set_title(key,color='white');ax.set_axis_off()
fig.suptitle('LUMINARIA II  /  GROWTH AND WOUND RESPONSE',color='white',fontsize=17)
fig.tight_layout();fig.savefig(out/'luminaria_ii_experiment.png',facecolor=fig.get_facecolor(),bbox_inches='tight');plt.close(fig)
ref=snaps['growth 48']; injury=snaps['injured']; after=snaps['repair 64']; controls=torch.clamp((torch.sigmoid(control[0,0]*3)-.5)*2,0,1).numpy()
patch=np.s_[9:23,16:28]
print('baseline visible total',round(ref.sum(),2),'injured total',round(injury.sum(),2),'final total',round(after.sum(),2))
print('wound mean initial',round(injury[patch].mean(),4),'wound mean after',round(after[patch].mean(),4),'undamaged control final patch',round(controls[patch].mean(),4))
print('full grid MSE vs control',round(np.mean((after-controls)**2),5),'elapsed',round(time.time()-start,1))
print('figure',out/'luminaria_ii_experiment.png')
