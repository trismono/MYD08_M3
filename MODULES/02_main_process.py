#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 10:38:26 2020

@author: trismonok
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "3"      # openblas thread number

from mpl_toolkits.basemap import Basemap
from pyhdf.SD import SD, SDC 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt
import glob
import pandas as pd
import xlsxwriter 

# define current working directory
base_dir = os.getcwd() + "/"
os.chdir(base_dir)

# define path
input_dir = os.path.realpath(base_dir + "../INPUT") + "/"
output_dir = os.path.realpath(base_dir + "../OUTPUT") + "/"
fig_dir = os.path.realpath(base_dir + "../FIGURES") + "/"
modis_dir = os.path.realpath(input_dir + "MYD08_M3") + "/"

# define timeframe (year to be processed)
years = [2015,2016]     # this might be changed for different timeframe
nmonth = 12             # number of month per-year

# timeformat
time_format = "%Y/%m/%d %H:%M:%S"

# loop over year and month
for year in years:
    for month in range(nmonth):
        # ++++++++++++++++++++
        # setting up parameter
        # ++++++++++++++++++++
        # date string
        year_str = str(year).zfill(4)
        month_str = str(month+1)
        month_str2 = str(month+1).zfill(2)

        # define day of year (doy)    
        date = dt.strptime("%s/%s/01 00:00:00" %(year_str,month_str2), time_format)     # date is fixed to 1 (first day of the month)
        doy = date.timetuple().tm_yday
        
        # integer month to string
        datetime_object = dt.strptime(month_str, "%m")
        month_str = datetime_object.strftime("%b")
        
        # update modis path
        modis_path = os.path.realpath(modis_dir + str(year).zfill(4) + "/" + str(doy).zfill(3)) + "/"
        
        # +++++++++++
        # define grid
        # +++++++++++
        # define res
        res = 1.0                           # decimal degree
        lat_min, lat_max = -90, 90.0        # decimal degree
        lon_min, lon_max = -180.0, 180.0    # degree
        
        # define grid
        x = np.arange(lon_min+0.5, lon_max, res)        # +0.5 as it represents central pixel
        y = np.arange(lat_min+0.5, lat_max, res)
        lon, lat = np.meshgrid(x,y)
        
        # +++++++++++++++
        # read modis data
        # +++++++++++++++
        # define filename 
        filename = np.sort(glob.glob(modis_path + 'MYD08_M3*.hdf'))[0]
        
        # print statement
        print("Info     | Reading file", filename) 
        
        # define variable name
        varname = "Aerosol_Optical_Depth_Land_Ocean_Mean_Mean"
        
        # open file
        file = SD(filename, SDC.READ)
        
        # read data
        data_selected_id = file.select(varname) 
        data = data_selected_id.get()
        data_selected_attributes = data_selected_id.attributes()
        scale_factor = data_selected_attributes['scale_factor']
        
        # multiply with scale factor
        data = data * scale_factor
        
        # remove fill-value
        data[data<0] = np.nan
        
        # flip data
        data = np.flipud(data)
        
        # +++++++++
        # plot data
        # +++++++++
        # setup figure
        fig = plt.figure(figsize=(7,5))
        fig.subplots_adjust(left=0.01, right=0.95, bottom=0., top=0.9)
        
        # plot map
        m = Basemap(projection='moll', llcrnrlat=-90, urcrnrlat=90,\
                    llcrnrlon=-180, urcrnrlon=180, resolution='c', lon_0=0)
        m.drawcoastlines()
        m.drawmapboundary(fill_color="lightgrey")
        m.drawparallels(np.arange(-90,90,30.),labels=[False,True,True,False], dashes=[2,2])
        m.drawmeridians(np.arange(-180,180,30.),labels=[False,False,False,False], dashes=[2,2])
        zmin = 0.0
        zmax = 1.0
        zgrid = 0.2
        cs = m.pcolormesh(lon, lat, data, latlon=True, cmap=plt.cm.Spectral_r, vmin=zmin, vmax=zmax)
        cbar = plt.colorbar(cs, orientation='horizontal', shrink=0.55, aspect=35, pad=0.05,
                            ticks= np.arange(zmin,zmax+zgrid,zgrid), format = '%.1f')
        cbar.set_label("Aerosol Optical Depth at 550 nm []")
        plt.title("Aerosol_Optical_Depth_Land_Ocean_Mean_Mean %s %s" %(month_str,year_str), pad=20)

        # save figure
        fig.savefig(fig_dir + "%s.png" %filename.split("/")[-1], format="png", dpi=300)
        
        # close
        fig.clear()
        
        # +++++++++++++
        # interpolation
        # +++++++++++++
        # define filename
        shp_inp_file = os.path.realpath(input_dir + "../INPUT/SHP") + "/gadm36_IDN_kabupaten.xlsx"
        out_file = output_dir + "output_%s%s.xlsx" %(year_str,month_str2)
                
        # read input shp
        df = pd.read_excel(shp_inp_file, sheet_name='Sheet1', header=0, skiprows=[1])
        
        # parse data
        prov_name = df["provname"]
        kab_name = df["kabname"]
        kab_id = df["kabid"]
        bb_ordinates = df["bb_ordinates_2"]

        # prepare output file and write header
        workbook = xlsxwriter.Workbook(out_file)
        worksheet = workbook.add_worksheet("Sheet1")
        worksheet.write(0, 0, "provname")
        worksheet.write(0, 1, "kabname")
        worksheet.write(0, 2, "kabid")
        worksheet.write(0, 3, "bb_ordinates_2")
        worksheet.write(0, 4, "mean_AOD")                     
        
        # define dimension
        nkab = len(kab_name)
        
        # define fill value
        fill_value = -99999.0
        
        # flaten modis data
        lon_1d = np.ravel(lon)
        lat_1d = np.ravel(lat)
        aod_1d = np.ravel(data)

        # loop over kab
        for i in range(nkab):
            # define boundary
            boundary = bb_ordinates[i].split(",")
            lon_min = float(boundary[0])
            lat_min = float(boundary[1]) 
            lon_max = float(boundary[2]) 
            lat_max = float(boundary[3])
            
            # indexing
            index = np.argwhere((lon_1d >= lon_min) &\
                                (lon_1d <= lon_max) &\
                                (lat_1d >= lat_min) &\
                                (lat_1d <= lat_max))[:,0]
            
            # check index 
            if not len(index) == 0:
                # define mean value
                aod_mean = np.nanmean(aod_1d[index])
                
                # assign to output file
                worksheet.write(i+1, 0, prov_name[i])
                worksheet.write(i+1, 1, kab_name[i])
                
                # check kab id (sometimes it has nan)
                if np.isnan(kab_id[i]): 
                    worksheet.write(i+1, 2, fill_value)
                else:
                    worksheet.write(i+1, 2, kab_id[i])
                    
                worksheet.write(i+1, 3, bb_ordinates[i])

                # check aod_mean (sometimes it returns nan)
                if np.isnan(aod_mean): 
                    worksheet.write(i+1, 4, fill_value)
                else:
                    worksheet.write(i+1, 4, aod_mean)
                
            else:
                # assign to output file
                worksheet.write(i+1, 0, prov_name[i])
                worksheet.write(i+1, 1, kab_name[i])
                
                # check kab id (sometimes it has nan)
                if np.isnan(kab_id[i]): 
                    worksheet.write(i+1, 2, fill_value)
                else:
                    worksheet.write(i+1, 2, kab_id[i])
                
                worksheet.write(i+1, 3, bb_ordinates[i])
                worksheet.write(i+1, 4, fill_value)
        
        # close output file
        workbook.close()
        