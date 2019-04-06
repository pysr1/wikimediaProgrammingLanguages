#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 17:00:42 2019

@author: bryant
"""

import requests
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

name = 'Python_(programming_language)'
start_date = "2018/01/01"


def wikimedia_request(page_name, start_date, end_date = None):
    '''
    A fucntion that makes requests to the wikimedia pagecveiws API

    Parameters
    ----------
    page_name : string
    A string containing the name of the wikipeida page you would like pageviews for
    
    start_date : string
    a date string YYYY/MM/DD indicating the first date that the request should return
    
    end_date : string
    a date string YYYY/MM/DD indicating the last date that the request should return. defaults to system date
    Returns
    -------
    df : pandas DataFrame
    A dataframe with the article name and the number of pageviews.
    '''
    
    # get rid of the / in the date
    sdate = start_date.split("/")
    # join together the text that was split
    sdate = ''.join(sdate)
    # if an end date is not specified
    if end_date == None:
        #get the current date
        end_date = str(datetime.datetime.now())[0:10].split("-")
        edate = ''.join(end_date)
    else:
        # use date from end_date argument
        edate = end_date.split("/")
        edate = edate[0] + edate[1] + edate[2]
    # use these elements to make an api request
    r = requests.get(
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{}/daily/{}/{}".format(page_name,sdate, edate)
    )
    # get the json
    result = r.json()
    # convert to dateframe
    df = pd.DataFrame(result['items'])
    # the wikimedia api returns 2 extra zeros at the end of the timestamp for some reason
    df['timestamp'] = [i[:-2] for i in df.timestamp]
    # convert to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # set timestamp as index
    df.set_index('timestamp', inplace = True)
    # return the article and views columns
    return df[['article', 'views']]


df = wikimedia_request(name, start_date)

def tsregplot(series, ax = None, days_forward = 10, color = 'C0'):
    '''
    A fucntion that makes requests to the wikimedia pagecveiws API

    Parameters
    ----------
    series : Pandas datetime index Series
    A pandas Series with datetime index
    
    ax : matplotlib axes object
    A matplotlib axes obect
    
    days_forward : int
    An integer indicating how many days to extend the regression line
    
    color : string
    A matplotlib color string 
    
    Returns
    -------
    ax : matplotlib axes object
    returns a matplotlib axes object with regplot
    '''
    
    series = series.reset_index()
    series.columns = ['date', 'value']
    if ax == None:
        series['date_ordinal'] = pd.to_datetime(series['date']).apply(lambda date: date.toordinal())
        ax = sns.regplot(
        data=series,
        x='date_ordinal',
        y='value',
        color = color
        )
        ax.set_xlim(series['date_ordinal'].min() - 2, series['date_ordinal'].max() + days_forward)
        ax.set_ylim(series['value'].min() - 1000, series['value'].max() + 1000)
        ax.set_xlabel('date')
        new_labels = [date.fromordinal(int(item)) for item in ax.get_xticks()]
        ax.set_xticklabels(new_labels)
    else:
        series['date_ordinal'] = pd.to_datetime(series['date']).apply(lambda date: date.toordinal())
        ax = sns.regplot(
        data=series,
        x='date_ordinal',
        y='value',
        ax = ax, 
        color = color
        )
    
        ax.set_xlim(series['date_ordinal'].min() - 5, series['date_ordinal'].max() + days_forward)
        ax.set_ylim(series['value'].min() * 0.9 , series['value'].max()* 1.1)
        ax.set_xlabel('date')
        new_labels = [date.fromordinal(int(item)).strftime("%m/%Y") for item in ax.get_xticks()]
        ax.set_xticklabels(new_labels)
        return ax
names = ['Python (programming language)', 'R (programming language)', 'Java (programming language)', 
         'Scala (programming_language)', 'JavaScript', 'Swift (programming language)', 'C++', 
         'C (programming language)', 'Clojure', 'C Sharp (programming language)', 'F Sharp (programming language)',
        'Julia (programming language)', 'Visual Basic .NET', 'Perl', 'Haskell (programming language)',
        'Go (programming language)', 'Ruby (programming language)', 'PHP', 'Bash (Unix shell)', 'TypeScript']

dfs = pd.concat([wikimedia_request(x, start_date) for x in names])


means = dfs.groupby('article').mean()['views']
means.sort_values(ascending = False).plot(kind = 'barh', color ='C0', figsize = (12,6))
plt.title('Total Wikipedia Page Views')
sns.despine()
plt.xlabel('Count of Page Views')
plt.ylabel("")
plt.tight_layout()
plt.savefig('pageviewsbar.png')


fig, ax = plt.subplots(10,2, figsize = (16, 20))
ax = ax.ravel()
counter = 0
for i, j in zip(dfs.article.unique(), names):
    string = i
    selected = dfs.query("article == '{}'".format(string))
    tsregplot(selected['views'].resample('M').sum()[:-1], ax = ax[counter])
    ax[counter].set_title(j)
    plt.tight_layout()
    counter += 1
plt.savefig('trendplots.png')