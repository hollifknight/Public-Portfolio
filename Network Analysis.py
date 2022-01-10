#!/usr/bin/env python
# coding: utf-8

# # Network Analysis of Stations
# 
# This analysis serves to show how the county's fire stations interact with one another. More specifically, how often does Station A rely on another station to provide service in A's First Due?
# 
# By analyzing this information, we can see where gaps in the system would be devastating to service; thus enabling us to move resources if pivotal stations are overwhlemed or out of service.

# In[2]:


## Import data and libraries

import pandas as pd
import networkx as nx
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl


# In[3]:


data = pd.read_csv("/Users/holliknight/Desktop/PGFD/FW Data/Demand All/2021/DemandAll_PBI_20210101_20211025.csv")


# In[4]:


data.shape


# ### Pre-Processing

# In[32]:


## Get unit type from unit column in case we want to analyze by capabilities
data['UnitType'] = data['Unit #'].str.extract(r'([A-Z]{1,2})')

## Remove mutual aid calls
data = data.loc[data['Calculated Incident Area'].notna()]
data = data.loc[~data['Calculated Incident Area'].str.startswith('MA')]

## Get incident counts by Station and Incident Area
df = data.groupby(['Station', 'Calculated Incident Area'], as_index=False)['Incident #'].count()

## Formatting
df['Calculated Incident Area'] = df['Calculated Incident Area'].apply(lambda x: x.zfill(2))
df['Calculated Incident Area'] = '8' + df['Calculated Incident Area'].astype(str)

df.columns = ['Station', 'Area', 'Incidents']

df['Station'] = df['Station'].astype(int)
df['Area'] = df['Area'].astype(int)

## Remove admin or incorrect stations
df = df.loc[df['Station'] != 874]
df = df.loc[df['Area'] != 874]
df = df.loc[df['Area'] != 858]

df = df.loc[df['Station'] != 853]
df = df.loc[df['Station'] != 865]
df = df.loc[df['Station'] != 856]
df = df.loc[df['Station'] != 857]
df = df.loc[df['Station'] != 858]

#df = df.loc[df['Station'] != df['Area']]


# In[33]:


df.head()


# ### Build Network

# In[56]:


G = nx.from_pandas_edgelist(df, 
                            source='Station',
                            target='Area',
                            edge_attr='Incidents',
                            create_using=nx.MultiDiGraph())
                            


# In[57]:


print(nx.info(G))


# In[49]:


## Get station coordinates for mapping graph

stations = pd.read_excel("/Users/holliknight/Desktop/PGFD/Lookup Tables/Station Addresses LatLong.xlsx",index_col='Station')

pos_geo = {}
for node in G.nodes():
    pos_geo[node] = (
                    (min(stations.loc[node]['Longitude'],55)),
                    max(stations.loc[node]['Latitude'],25) 
    )


# In[55]:


## Plotting graph

plt.rcParams['figure.figsize'] = [12, 12]
plt.axis('off')
plt.title('Station Network',fontsize = 24)


weighted_degrees = dict(nx.degree(G,weight='Incidents'))
max_degree = max(weighted_degrees.values())

pos = nx.spring_layout(G,weight='Incidents',iterations=20, k = 4)


for node in G.nodes():
    size = 10*weighted_degrees[node]**0.5
    ns = nx.draw_networkx_nodes(G,pos_geo,nodelist=[node], node_size=size, node_color='#009fe3')
    ns.set_edgecolor('#f2f6fa')


nx.draw_networkx_labels(G,pos_geo,font_size=10);


for e in G.edges(data=True):
    if e[2]['Incidents']>0:
        nx.draw_networkx_edges(G,pos_geo,[e],
                               width=e[2]['Incidents']/100,edge_color='indianred')


# In[51]:


G.nodes


# In[52]:


G.edges


# ### Analyzing Results

# In[30]:


top = pd.DataFrame.from_dict(dict(nx.degree(G)),orient='index').sort_values(0,ascending=False)
top.columns = ['Degree']
top['Weighted Degree'] =  pd.DataFrame.from_dict(dict(nx.degree(G,weight='Incidents')),orient='index')
top['PageRank'] = pd.DataFrame.from_dict(dict(nx.pagerank_numpy(G,weight='Incidents')),orient='index')
top['Betweenness'] =  pd.DataFrame.from_dict(dict(nx.betweenness_centrality(G,weight='Incidents')),orient='index')
top['EigenCentrality'] = pd.DataFrame.from_dict(dict(nx.eigenvector_centrality(G,weight='Incidents')),orient='index')


# In[31]:


top.sort_values(by='EigenCentrality', ascending=False)


# A natural extension of degree centrality is eigenvector centrality. In-degree centrality awards one centrality point for every link a node receives. But not all vertices are equivalent: some are more relevant than others, and, reasonably, endorsements from important nodes count more. The eigenvector centrality thesis reads:
# 
# A node is important if it is linked to by other important nodes.
# Eigenvector centrality differs from in-degree centrality: a node receiving many links does not necessarily have a high eigenvector centrality (it might be that all linkers have low or null eigenvector centrality). Moreover, a node with high eigenvector centrality is not necessarily highly linked (the node might have few but important linkers).
# 
# https://www.sci.unich.it/~francesc/teaching/network/eigenvector.html

# Station 829 has a remarkably higher eigenvector centrality than any other station (more than 3 times higher than the next largest value). We know from practical experience that 829 is a very busy station, often producing our busiest units; however, it appears that many other stations "point toward" this station, and therefore the system relies heavily on its ability to produce / maintain operational capabilities.

# In[1]:


import os
current_path = os.getcwd()


# In[3]:


pwd


# In[2]:


current_path


# In[ ]:


'/Users/holliknight/PGFD/Station and Unit Changes/Network Analysis.ipynb'

## very fun - adding new comment
