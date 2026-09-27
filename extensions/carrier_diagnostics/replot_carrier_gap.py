#!/usr/bin/env python3
"""Render the saved carrier-gap coefficients using explicit other-code labels."""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--results',type=Path,default=Path(__file__).resolve().parent/'results')
a=p.parse_args()
events=pd.read_csv(a.results/'carrier_gap_event_coefficients.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,1,figsize=(7,5.2),sharex=True,layout='constrained')
for ax,(name,title) in zip(axes,[('all_products_baseline_paired','A. All single-carrier itineraries'),('two_coupon_only_baseline_paired','B. Two-coupon single-carrier itineraries')]):
    z=events[events.model.eq(name)].sort_values('t')
    ax.errorbar(z.t,z.b,yerr=[z.b-z.lo,z.hi-z.b],fmt='o',ms=3,capsize=2,color='#215b72',ecolor='#89aabb',lw=.8)
    ax.axhline(0,color='#758089',lw=.8)
    ax.axvspan(13.5,16.5,color='#d9b875',alpha=.18)
    ax.axvline(16,ls='--',lw=.8,color='#7c6853')
    ax.set_title(title,loc='left',fontsize=10)
    ax.set_ylabel('DL/NW minus other-code log fare\nrelative to 2007Q4')
    ax.grid(axis='y',alpha=.15)
axes[-1].set_xticks([1,5,9,12,16,20,24],['2005Q1','2006Q1','2007Q1','2007Q4','2008Q4','2009Q4','2010Q4'],rotation=20)
fig.savefig(a.results/'carrier_gap_event.png',dpi=220)
fig.savefig(a.results/'carrier_gap_event.pdf')
plt.close(fig)
print('Re-rendered existing estimates; no regression inputs or coefficients changed.')
