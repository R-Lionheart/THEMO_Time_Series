#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 09:05:03 2018

@author: regina
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn; seaborn.set()
from datetime import datetime
#from dateutil import parser

parser = argparse.ArgumentParser(description='This program creates time series of several sensors on the moored THEMO buoy.', 
                                 epilog='Regina Lionheart, CROSSMAR Lab, University of Haifa')
parser.add_argument('file', help='concatenated dataset of all THEMO sensor data')
parser.add_argument('--start-date', help="the start date - 'format YYYY-MM-DD'", 
                    type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                    default=pd.Timestamp.min.to_pydatetime())

parser.add_argument('--end-date', help ="the end date - 'format YYYY-MM-DD'",
                    type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                    default=pd.Timestamp.max.to_pydatetime())
parser.add_argument('--SST', action='store_true', default=False, 
                    help='time series of sea surface temperature (in C) from the top 20m')
parser.add_argument('--fluorescence', action='store_true', default=False, 
                    help='time series of fluorescence at 1m depth')
parser.add_argument('--air-temp', action='store_true', default=False, 
                    help='time series of atmospheric temperature (in C), 3m above sea level')
parser.add_argument('--windspeed', action='store_true', default=False, 
                    help='time series of wind velocity (in m/s), 3m above sea level')
parser.add_argument('--wind-direction', action='store_true', default=False, 
                    help='time series of wind direction, measured in degrees')
parser.add_argument('--pressure', action='store_true', default=False, 
                    help='time series of atmospheric pressure (in mb), 3m above sea level')
parser.add_argument('--humidity', action='store_true', default=False, 
                    help='time series of relative humidity (RH percent), 3m above sea level')
parser.add_argument('--dewpoint', action='store_true', default=False, 
                    help='time series of atmospheric dewpoint (in C), 3m above sea level')
args = parser.parse_args()

## Data import from THEMO
## Weather station, Sea Surface Temperature (SST), and chlorophyll fluorescence.

weather = pd.read_csv('/Users/regina/university_projects/Themo_Data/Weather0717-0618.csv', 
                      parse_dates=[[0,1]], index_col=0)
weather = weather.drop(columns=['threshold', 'const_err'])
weather = weather.rename(columns={'temperature':'air_temperature'})
weather_avg = weather.resample('D').mean()

SST = pd.read_csv('/Users/regina/university_projects/Themo_Data/SST0717-0618.csv',
                   parse_dates=[[0, 1]], index_col=0)
SST = SST.drop(columns=['s9_id', 'threshold', 'const_err'])
SST = SST[(SST.temperature < 31) & (SST.temperature > 20)]
SST = SST[SST.depth < 20].rename(columns={"temperature": "sst_upper_zone"})
SST = SST.drop(columns=['depth'])
SST_avg = SST.sst_upper_zone.resample('D').mean()


chl = pd.read_csv('/Users/regina/university_projects/Themo_Data/chlorophyll0717-0618.csv', 
                 parse_dates=[[0,1]], index_col=0)
chl = chl.drop(columns=['turbidity_units', 'threshold', 'const_err'])
chl = chl[(chl.chlorophyll_concentration < 1.0) & (chl.chlorophyll_concentration > 0)]


sets = [weather, SST, chl]
pd.concat(sets, axis=0, join='outer', join_axes=None, ignore_index=False,
          keys=None, levels=None, names=None, verify_integrity=False,
          copy=True, sort=False).to_csv('~/university_projects/Themo_Data/Full_Themo.csv')

ds = pd.read_csv('~/university_projects/Themo_data/Full_Themo.csv', parse_dates=[0])
ds.index = pd.to_datetime(ds.index, unit='s')

#ds['d_stamp_t_stamp'] = pd.to_datetime(ds['d_stamp_t_stamp']).apply(lambda x: x.replace(minute=0, second=0))
#ds['d_stamp_t_stamp'].dt.date

# =============================================================================
# NEED TO FIGURE OUT HOW TO SORT WITHIN THE CSV BY DATES 

#ds = pd.read_csv(args.file, parse_dates=[0])#, index_col=0)
ds = ds[(ds.d_stamp_t_stamp >= args.start_date)]
ds = ds[(ds.d_stamp_t_stamp <= args.end_date)]

 
if args.SST:
    SST_plot = plt.figure(figsize=(14,10))
    SST_plot.suptitle('Sea Surface Temperature', fontsize=20)
    SST_fig = SST_plot.add_subplot(111)
    SST_fig.plot(ds['sst_upper_zone'], color='turquoise', alpha=0.4)
    SST_fig.plot(ds['sst_upper_zone'].resample('D').mean(), color='darkblue', marker='o', 
                 markersize=5)
    SST_fig.set_ylabel('SST in C', color='darkblue', fontsize=15)
    SST_fig.legend(['Raw SST Data', 'SST Daily Average'], fontsize=15, loc=0)


if args.fluorescence:
    chl_plot = plt.figure(figsize=(14,10))
    chl_plot.suptitle('Chlorophyll', fontsize=20)
    chl_fig = chl_plot.add_subplot(111)
    chl_fig.plot(ds['chlorophyll_concentration'], alpha=0.4)
    chl_fig.plot(ds['chlorophyll_concentration'].resample('D').mean(), color='darkorange', 
                 marker='o', markersize=5)
    chl_fig.set_xlabel("Date"),chl_fig.set_ylabel("Chlorophyll Concentration in uG/L") 
    chl_fig.legend(['Raw chlorophyll data', 'Chlorophyll daily average'], fontsize=15, loc=0)
 
    
if args.air_temp:
    air_plot = plt.figure(figsize=(14,10))
    air_plot.suptitle('Air Temperature', fontsize=20)
    air_fig = air_plot.add_subplot(111)
    air_fig.plot(ds['air_temperature'], color='blue', alpha=0.4)
    air_fig.plot(ds['air_temperature'].resample('D').mean(), color='darkblue', 
                 marker='o', markersize=5)
    air_fig.set_xlabel("Date"),air_fig.set_ylabel("Air Temperature in C") 
    air_fig.legend(['Raw air temperature data', 'Air temperature daily average'], fontsize=15, loc=0)


if args.windspeed:
    windspeed_plot = plt.figure(figsize=(14,10))
    windspeed_plot.suptitle('Wind Speed', fontsize=20)
    windspeed_fig = windspeed_plot.add_subplot(111)
    windspeed_fig.plot(ds['wind_speed'], color='darkblue', alpha=0.5)
    windspeed_fig.set_xlabel("Date"),chl_fig.set_ylabel("Wind Speed in m/s") 
    windspeed_fig.legend(['Raw wind speed data', 'Wind speed daily average'], fontsize=15, loc=0)


if args.wind_direction:
    winddirection_plot = plt.figure(figsize=(14,10))
    winddirection_plot.suptitle('Wind Direction', fontsize=20)
    winddirection_fig = winddirection_plot.add_subplot(111)
    winddirection_fig.plot(ds['wind_direction'], color='magenta', alpha=0.5)
    winddirection_fig.set_xlabel("Date"),chl_fig.set_ylabel("Wind direction in degrees") 
    winddirection_fig.legend(['Raw wind direction data', 'Wind direction daily average'], fontsize=15, loc=0)

if args.pressure:
    pressure_plot = plt.figure(figsize=(14,10))
    pressure_plot.suptitle('Pressure', fontsize=20)
    pressure_fig = pressure_plot.add_subplot(111)
    pressure_fig.plot(ds['pressure'], color='palegreen', alpha=0.5)
    pressure_fig.set_xlabel("Date"), chl_fig.set_ylabel("Pressure in MB") 
    pressure_fig.legend(['Raw pressure data', 'Pressure daily average'], fontsize=15, loc=0)
    
if args.humidity:
    humidity_plot = plt.figure(figsize=(14,10))
    humidity_plot.suptitle('Humidity', fontsize=20)
    humidity_fig = humidity_plot.add_subplot(111)
    humidity_fig.plot(ds['humidity'], color='darkolivegreen', alpha=0.5)
    humidity_fig.set_xlabel("Date"), chl_fig.set_ylabel("Humidity in MB") 
    humidity_fig.legend(['Raw humidity data', 'Humidity average'], fontsize=15, loc=0)

if args.dewpoint:
    dewpoint_plot = plt.figure(figsize=(14,10))
    dewpoint_plot.suptitle('Dewpoint', fontsize=20)
    dewpoint_fig = dewpoint_plot.add_subplot(111)
    dewpoint_fig.plot(ds['dewpoint'], color='red', alpha=0.5)
    dewpoint_fig.set_xlabel("Date"), chl_fig.set_ylabel("Dewpoint in C") 
    dewpoint_fig.legend(['Raw dewpoint data', 'Dewpoint average'], fontsize=15, loc=0)    


plt.show()
