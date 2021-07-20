# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 13:46:22 2021

@author: EricTien
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.stats import norm
from datetime import date, timedelta
import numpy as np
import pandas as pd
import os
import glob
os.chdir(r'D:/Drive/work/FCS/全台乾旱指標計算')


# specific historical month to tccip ar5 precip columns in .csv file
def historical_mtocol(year, month):
    return (year-1960)*12+month+1


# specific future month to tccip ar5 precip columns in .csv file
def future_mtocol(year, month):
    return (year-2006)*12+month+1


# %% SPI3 cal
countylist = ['基隆市', '臺北市', '新北市', '桃園市', '新竹市', '新竹縣', '苗栗縣', '臺中市', '彰化縣',
              '南投縣', '雲林縣', '嘉義縣', '嘉義市', '臺南市', '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣']
for county in countylist:
    dfSPImean = pd.DataFrame([])
    dfSPIstd = pd.DataFrame([])
    dfSPIhist = pd.DataFrame([])
    scenariolist = []
    filelist = glob.glob('data/AR5_統計降尺度_月資料_'+county+'_降雨量_historical_*.csv')
    for i in range(len(filelist)):  # use filelist to create scenariolist
        scenariolist.append(filelist[i][38:-4])
    for scenario in scenariolist:
        dtype = 'historical'
        historical = pd.read_csv(
            'data/AR5_統計降尺度_月資料_'+county+'_降雨量_'+dtype+'_'+scenario+'.csv', index_col=False)
        historical = historical.where(historical != -99.9)

        # calculate SPI3 mean and std from historical
        SPI3mean = []
        SPI3std = []
        historicalSPI3 = []
        for month in range(1, 13):
            precipsum = []
            for year in range(1986, 2006):
                col = historical_mtocol(year, month)
                precipsum.append(
                    historical.iloc[:, col-2:col+1].sum(axis=1).mean())
            precipsum = np.array(precipsum)
            SPI3mean.append(precipsum.mean())
            SPI3std.append(precipsum.std())
            cdf = norm.cdf(precipsum, SPI3mean[month-1], SPI3std[month-1])
            SPI3 = norm.ppf(cdf)
            historicalSPI3.append(SPI3)
        historicalSPI3 = pd.DataFrame(
            np.array(historicalSPI3).T.flatten(), columns=[scenario])
        dfSPIhist = pd.concat([dfSPIhist, historicalSPI3], axis=1)
        SPI3mean = pd.DataFrame(SPI3mean, index=range(
            1, 13), columns=[scenario])  # index=month
        dfSPImean = pd.concat([dfSPImean, SPI3mean], axis=1)
        SPI3std = pd.DataFrame(SPI3std, index=range(
            1, 13), columns=[scenario])  # index=month
        dfSPIstd = pd.concat([dfSPIstd, SPI3std], axis=1)
    dfSPIhist.to_csv('result/'+county+'_SPI3hist.csv')
    dfSPImean.to_csv('result/'+county+'_SPI3mean.csv')
    dfSPIstd.to_csv('result/'+county+'_SPI3std.csv')
    print(county+' historical SPI3, mean, std done.')

for county in countylist:
    dfSPI = pd.DataFrame([])
    rcplist = ['rcp26', 'rcp45', 'rcp60', 'rcp85']
    for rcp in rcplist:
        scenariolist = []
        filelist = glob.glob('data/AR5_統計降尺度_月資料_'+county+'_降雨量_'+rcp+'_*.csv')
        for i in range(len(filelist)):  # use filelist to create scenariolist
            scenariolist.append(filelist[i][33:-4])
        for scenario in scenariolist:
            # read SPI3 mean and std file
            SPI3mean = pd.read_csv(
                'result/'+county+'_SPI3mean.csv', index_col=0)[scenario]
            SPI3std = pd.read_csv(
                'result/'+county+'_SPI3std.csv', index_col=0)[scenario]
            # calculate future SPI3
            dtype = rcp
            future = pd.read_csv(
                'data/AR5_統計降尺度_月資料_'+county+'_降雨量_'+dtype+'_'+scenario+'.csv', index_col=False)
            future = future.where(future != -99.9)
            rcpSPI3 = []
            monthlist = []
            for year in range(2021, 2041):
                for month in range(1, 13):
                    col = future_mtocol(year, month)
                    precip = future.iloc[:, col-2:col+1].sum(axis=1).mean()
                    cdf = norm.cdf(precip, SPI3mean[month], SPI3std[month])
                    SPI3 = norm.ppf(cdf)
                    rcpSPI3.append(SPI3)
                    if month < 10:
                        monthlist.append(str(year)+'0'+str(month))
                    else:
                        monthlist.append(str(year)+str(month))
            rcpSPI3 = pd.DataFrame(
                rcpSPI3, index=monthlist, columns=[scenario+'_'+dtype])
            dfSPI = pd.concat([dfSPI, rcpSPI3], axis=1)
            #dfSPIhist=pd.concat([dfSPIhist, historicalSPI3], axis=1)
            print(county+' '+rcp+' '+scenario+' done.')
    dfSPI.to_csv('result/'+county+'_SPI3.csv')
# %% Drought score
countylist = ['基隆市', '臺北市', '新北市', '桃園市', '新竹市', '新竹縣', '苗栗縣', '臺中市', '彰化縣',
              '南投縣', '雲林縣', '嘉義縣', '嘉義市', '臺南市', '高雄市', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣']
droughtscore20022021 = pd.DataFrame([])
yellow = [2, 3, 6, 8, 10, 10, 7, 5, 4, 2, 4, 4, 4, 9, 8, 1, 2, 2, 1, 3]
orange = [1, 2, 3, 4, 4, 4, 3, 2, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1, 0, 2]
red = [0, 1, 2, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
score = np.array(yellow)*1+np.array(orange)*2+np.array(red)*3+1
droughtscore20022021 = pd.concat(
    [droughtscore20022021, pd.DataFrame([yellow, orange, red, score])])
droughtscore20022021.columns = countylist
droughtscore20022021.index = ['Y', 'O', 'R', 'Score']

# %% SPI3 < -1 or -2 ratio from Nov. to Apr.
mode = ["rcp26","rcp85","all"] # rcp26, rcp85, all
droughthist, sdroughthist, drought, sdrought = [], [], [], []
scenariolist=[]
for county in countylist:
    dfSPI1104 = pd.read_csv('result/'+county+'_SPI3.csv', index_col=0)
    dfSPI1104hist = pd.read_csv('result/'+county+'_SPI3hist.csv', index_col=0)
    for i in range(20, -1, -1):
        dfSPI1104 = dfSPI1104.drop(dfSPI1104.index[i*12+4:i*12+10])
        dfSPI1104hist = dfSPI1104hist.drop(dfSPI1104hist.index[i*12+4:i*12+10])
    for i in range(len(dfSPI1104.columns)-1,-1,-1):
        if dfSPI1104.columns[i][-5:] != mode:
            dfSPI1104 = dfSPI1104.drop(dfSPI1104.columns[i],axis=1)
        else:
            scenariolist.insert(0,dfSPI1104.columns[i][:-6])
    dfSPI1104hist = dfSPI1104hist[scenariolist]

    drought.append((dfSPI1104.where(dfSPI1104 < -1).count()/120).mean())
    sdrought.append((dfSPI1104.where(dfSPI1104 < -2).count()/120).mean())
    droughthist.append((dfSPI1104hist.where(
        dfSPI1104hist < -1).count()/120).mean())
    sdroughthist.append((dfSPI1104hist.where(
        dfSPI1104hist < -2).count()/120).mean())
drought = np.array(drought)
droughthist = np.array(droughthist)
# drought change vs drought score plot
fig, ax = plt.subplots(figsize=(12,7))
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False
ax.axvspan(0,8,facecolor='green',zorder=-1,alpha=0.3,label='低危害')
ax.axvspan(8,18,facecolor='orange',zorder=-1,alpha=0.3,label='中危害')
ax.axvspan(18,max(score)+1,facecolor='red',zorder=-1,alpha=0.3,label='高危害')
ax.set_xlim(0,max(score)+1)
ax.set_xlabel('drought score')
ax.set_ylabel('SPI<-1 ratio/SPI<-1 ratio in history')
ax.set_title(mode+' drought ratio change vs drought score')
ax.scatter(score, drought/droughthist)
for i, label in enumerate(countylist):
    ax.text(score[i], drought[i]/droughthist[i], label)
ax.legend()
ax.grid()
plt.show()

#
'''
fig, ax = plt.subplots(figsize=(12,7))
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False
ax.scatter(score, drought, label='future')
ax.set_xlim(0,max(score)+1)
ax.set_xlabel('drought score')
ax.set_ylabel('SPI<-1 ratio')
for i, label in enumerate(countylist):
    ax.text(score[i], drought[i], label)
ax.scatter(score, droughthist, c='orange', label='historical')
for i, label in enumerate(countylist):
    ax.text(score[i], droughthist[i], label)
ax.grid()
ax.legend()
ax.axvspan(0,8,facecolor='green',zorder=-1,alpha=0.3)
ax.axvspan(8,18,facecolor='yellow',zorder=-1,alpha=0.3)
ax.axvspan(18,max(score)+1,facecolor='red',zorder=-1,alpha=0.3)
plt.show()'''

# new drought score = drought score*drought ratio change
nscore = score*drought/droughthist
# %% drought risk matrix with water demand
demand = np.array([48.5, 188.1, 89.1, 120.4, 27.1, 27.1, 20.8, 134.5,
                  39.6, 17, 27.2, 14.6, 14.6, 95.3, 149, 20, 19.3, 10.8, 7.4, 2.5])
# modified drought score vs water demand plot
fig, ax = plt.subplots(figsize=(12,7))
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False
ax.scatter(demand, nscore)
ax.set_xlim(0,max(demand)+20)
ax.set_ylim(0,30)
ax.set_xlabel('water demand')
ax.set_ylabel('modified drought score')
for i, label in enumerate(countylist):
    plt.text(demand[i], nscore[i], label)
ax.grid()
polyg=Polygon([(0,18),(75,18),(75,8),(max(demand)+20,8),(max(demand)+20,0),(0,0)],facecolor='g',alpha=0.3,zorder=-1,label='低風險')
polyo=Polygon([(0,30),(75,30),(75,18),(max(demand)+20,18),(max(demand)+20,8),(75,8),(75,18),(0,18)],facecolor='orange',alpha=0.3,zorder=-1,label='中風險')
polyr=Polygon([(75,30),(max(demand)+20,30),(max(demand)+20,18),(75,18)],facecolor='r',alpha=0.3,zorder=-1,label='高風險')
ax.add_patch(polyg)
ax.add_patch(polyo)
ax.add_patch(polyr)
ax.legend()
plt.show()
