#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 16:54:16 2020

@author: trismonok
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "3"      # openblas thread number
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# define current working directory
base_dir = os.getcwd() + "/"
os.chdir(base_dir)

# define path
output_dir = os.path.realpath(base_dir + "../OUTPUT") + "/"
fig_dir = os.path.realpath(base_dir + "../FIGURES") + "/"

# define timeframe (year to be processed)
years = [2015,2016] # this might be changed for different timeframe
nmonth = 12         # number of month per-year

# define province
province = ["Riau", "Jambi"]

# define array
mean_aod_1 = []
mean_aod_2 = []
axis_label = []

# loop over year and month
for year in years:
    for month in range(nmonth):
        # define string
        year_str = str(year).zfill(4)
        month_str = str(month+1).zfill(2)
            
        # define filename
        out_file = output_dir + "output_%s%s.xlsx" %(year_str,month_str)
                
        # read output
        df = pd.read_excel(out_file, sheet_name='Sheet1', header=0, skiprows=[1])
        
        # parse data
        prov_name = df["provname"].to_list()
        mean_AOD = df["mean_AOD"].to_list()
        
        # define dimension
        nkab = len(prov_name)

        # indexing
        index1 = [i for i, x in enumerate(prov_name) if x == province[0]]
        index2 = [i for i, x in enumerate(prov_name) if x == province[1]]
        
        # convert to array
        mean_AOD = np.array(mean_AOD)
        index1 = np.array(index1, dtype=int)
        index2 = np.array(index2, dtype=int)
        
        # calculate mean
        aod1 = mean_AOD[index1]
        aod2 = mean_AOD[index2]

        # define fill value        
        fill_value = -99999.0

        # remove fill values
        mean_aod_1.append(np.nanmean(aod1[aod1 != fill_value]))
        mean_aod_2.append(np.nanmean(aod2[aod2 != fill_value]))
        
        # define axis label
        axis_label.append("%s/%s" %(year_str, month_str))


# convert list to array
mean_aod_1 = np.array(mean_aod_1)
mean_aod_2 = np.array(mean_aod_2)

# define dimension
ndata = len(mean_aod_1)

# define xtick
xticks = np.arange(0,ndata)

# define increment
xticks_inc = np.arange(0,ndata,4)

# define xlabels
axis_labels = []
for i in range(len(xticks_inc)):
     axis_labels.append(axis_label[xticks_inc[i]])

# define limit
ymin, ymax = 0, 3

# plotting
fig = plt.figure(figsize=(5.6,3.4))
ax=fig.add_axes([0.13,0.16,0.84,0.79])

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.plot(xticks,mean_aod_1,color="grey",linestyle="-")
plt.plot(xticks,mean_aod_2,color="red",linestyle="-")
plt.xlabel("Time series []")
plt.ylabel("Aerosol optical thickness []")
plt.xlim(0,ndata)
plt.ylim(ymin,ymax)
plt.xticks(xticks_inc, axis_labels, rotation=0)
plt.legend(province, loc="best", frameon=False)
        
# save figure
fig.savefig(fig_dir + "time_series.png", format="png", dpi=400)        

            

            
            
        
        
        
