import pandas as pd
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
from scipy.stats import hypergeom



def load_tsv(path):

    if path.endswith('.tsv'):
        df = pd.read_table(path)
        if 'morph' in df :
            df = df.drop(columns='morph')
    else:
        df = pd.read_table(path + '/' + os.listdir(path)[0])
        if 'morph' in df :
            df = df.drop(columns='morph')
        for filename in os.listdir(path)[1:] :
            if filename.endswith('.tsv') :
                temp_df = pd.read_table(path + '/' + filename)
                if 'morph' in temp_df :                
                    temp_df = temp_df.drop(columns='morph')
                df = pd.concat([df, temp_df], ignore_index=True)

    df['POS'] = df['POS'].str[0:3]

    return df



def select_tokens(df, poslist, drop=True):

    df['POS'] = df['POS'].str[0:3]
    df = df[df['POS'].isin(poslist)]

    if drop == True :
        df = df.reset_index(drop=True)

    return df



def build_freq_df(df, dtype):

    freq_df = df.groupby([dtype,'POS']).size().to_frame(name = 'freq').reset_index()

    return freq_df



def freq_cell_w(freq_df, word1, pos1, word2, pos2, dtype):

    row = freq_df.index[(freq_df[dtype] == word1) & (freq_df['POS'] == pos1)].tolist()[0]
    col = freq_df.index[(freq_df[dtype] == word2) & (freq_df['POS'] == pos2)].tolist()[0]

    return row, col



def build_coocc_list(key, pos, df, n, dtype, coocc_list):

    if dtype == 'lemma':
        arg = 1
    elif dtype == 'form':
        arg = 0

    for i in range(len(df)):
        if (str(df.iloc[i,1]) == key) & (str(df.iloc[i,2]) == pos):
            for k in range(max(0, i - n), min(len(df), i + n + 1)):
                if (df.iloc[k, arg] + ' ' + df.iloc[k,2]) not in coocc_list :
                    coocc_list.append(df.iloc[k, arg] + ' ' + df.iloc[k,2])

    return coocc_list




def build_cofreq_df(coocc_list):

    cofreq_df = pd.DataFrame(0, columns=coocc_list, index=coocc_list)

    return cofreq_df




def cofreq(key1, pos1, key2, pos2, df, n, dtype):

    cofreq = 0

    if (key1==key2) & (pos1==pos2):
        pass
    else :
        if dtype == 'lemma':
            arg = 1
        elif dtype == 'form':
            arg = 0
        for i in range(len(df)):
            if (str(df.iloc[i,arg]) == key1) & (str(df.iloc[i,2]) == pos1):
                for k in range(max(0, i - n), min(len(df), i + n + 1)):
                    if (str(df.iloc[k,arg]) == key2) & (str(df.iloc[k,2]) == pos2):
                        cofreq += 1

    return cofreq





def fill_cofreq_df(key, pos, cofreq_df, df, n, dtype):

    for row in cofreq_df.index:
        cofreq_df.loc[key + ' ' + pos, row] = cofreq(key, pos, row.split()[0], row.split()[1], df, n, dtype)

    return cofreq_df




def stat_link(word1, pos1, word2, pos2, df, freq_df, cofreq_df, n, dtype):

    row, col = freq_cell_w(freq_df, word1, pos1, word2, pos2, dtype)

    obs_freq = cofreq_df.loc[word1 + ' ' + pos1, word2 + ' ' + pos2]
    th_freq = hypergeom.mean(len(df),freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)
    std = hypergeom.std(len(df),freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)
    red_dev = (obs_freq - th_freq)/std
    p_value = 2*hypergeom.sf(obs_freq, len(df), freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)
    fluct_interval = hypergeom.interval(0.95, len(df), freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)

    return obs_freq, p_value, red_dev, fluct_interval





def full_stat_link(keylist, path, poslist, n, dtype):

    word1, pos1 = keylist[0].split()[0], keylist[0].split()[1]
    word2, pos2 = keylist[1].split()[0], keylist[1].split()[1]

    df = load_tsv(path)
    df = select_tokens(df, poslist, drop= True)
    freq_df = build_freq_df(df, dtype)

    row, col = freq_cell_w(freq_df, word1, pos1, word2, pos2, dtype)

    obs_freq = cofreq(word1, pos1, word2, pos2, df, n, dtype)
    th_freq = hypergeom.mean(len(df),freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)
    std = hypergeom.std(len(df),freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)
    red_dev = (obs_freq - th_freq)/std
    p_value = 2*hypergeom.sf(obs_freq, len(df), freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)
    fluct_interval = hypergeom.interval(0.95, len(df), freq_df.iloc[col,2],freq_df.iloc[row,2]*2*n)

    return obs_freq, p_value, red_dev, fluct_interval





def fill_stat_df(df, freq_df, cofreq_df, coocc_list, n, arg, dtype):

    stat_df = build_cofreq_df(coocc_list)
    
    if arg == 'obs_freq':
        for row in stat_df.index:
            for col in stat_df.columns:
                stat_df.loc[row, col] = stat_link(row.split()[0], row.split()[1], col.split()[0], col.split()[1], df, freq_df, cofreq_df, n, dtype)[0]
        
    elif arg == 'red_dev':
        for row in stat_df.index:
            for col in stat_df.columns:
                stat_df.loc[row, col] = stat_link(row.split()[0], row.split()[1], col.split()[0], col.split()[1], df, freq_df, cofreq_df, n, dtype)[2]    
    
    for i in range(len(stat_df)):
        for j in range(len(stat_df)):
            if stat_df.iloc[i,j] > 0 :
                stat_df.iloc[j, i] = min(stat_df.iloc[i,j], stat_df.iloc[j,i])
            if stat_df.iloc[j,i] > 0 :
                stat_df.iloc[i,j] = min(stat_df.iloc[i,j], stat_df.iloc[j,i])
                
    return stat_df




def build_graph(keylist, poslist, stat_df, freq_df, dtype, *args): 

    G = nx.Graph()
    
    attr = {}
    labels = {}
    colors = []
    sizes = []

    for i in range(len(stat_df)):
        for j in range(len(stat_df)):
            if stat_df.iloc[i, j] > 0 :
                if stat_df.index[i] in keylist or stat_df.index[j] in keylist : 
                    G.add_edge(stat_df.index[i], stat_df.index[j], weight = 1/stat_df.iloc[i,j], capacity = 'main')
                elif stat_df.index[i] not in keylist and stat_df.index[j] not in keylist :
                    G.add_edge(stat_df.index[i], stat_df.index[j], weight = 1/stat_df.iloc[i,j], capacity = 'sec')
                attr[i] = stat_df.index[i], freq_df.iloc[freq_df.index[(freq_df[dtype] == stat_df.index[i].split()[0]) & (freq_df['POS'] == stat_df.index[i].split()[1])].tolist()[0], 2]
                attr[j] = stat_df.index[j], freq_df.iloc[freq_df.index[(freq_df[dtype] == stat_df.index[j].split()[0]) & (freq_df['POS'] == stat_df.index[j].split()[1])].tolist()[0], 2]

    for p in attr.values() :
        if p[0].split()[1] == poslist[0]:
            colors.append('#9fc4e4')
        elif p[0].split()[1] == poslist[1]:
            colors.append('#b7addc')
        elif p[0].split()[1] == poslist[2]:
            colors.append('#fcc0f2')
        sizes.append(p[1] * 200)
        
    for node in G.nodes():
        labels[node] = node.split()[0]
        
    emain = [(u,v) for (u,v,d) in G.edges(data=True) if d['capacity'] == 'main']
    esec = [(u,v) for (u,v,d) in G.edges(data=True) if d['capacity'] == 'sec'] 
    
    pos = nx.kamada_kawai_layout(G)
    edges = G.edges()
    weights_main = [G[u][v]['weight'] for u,v in emain]
    weights_sec = [G[u][v]['weight'] for u,v in esec]
    
    widths_main = weights_main

    for n in range(len(widths_main)) :
        widths_main[n] =  1 / widths_main[n]
        
    if 'all' in args : 
        widths_sec = weights_sec
        for n in range(len(widths_sec)) :
            widths_sec[n] =  1 / widths_sec[n]
        
    fig, ax = plt.subplots(figsize=(10,10))
    
    nx.draw_networkx_nodes(G, pos, node_color = colors, node_size = sizes, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist = emain, width = widths_main, edge_color = '#f59c72')

    if 'all' in args :
        nx.draw_networkx_edges(G, pos, edgelist=esec, width = widths_sec, edge_color = '#fbe3d3', style='dashed')

    nx.draw_networkx_labels(G, pos, labels, font_size = 12, font_family = 'sans-serif')
    
    plt.axis('off')
    plt.show()
    
    return G




def lexnet(keylist, path, poslist, n, arg, dtype, method):

    df = load_tsv(path)
    df = select_tokens(df, poslist, drop= True)
    freq_df = build_freq_df(df, dtype)
    coocc_list = []

    for i in range(len(keylist)) :
        coocc_list = build_coocc_list(keylist[i].split()[0], keylist[i].split()[1], df, n, dtype, coocc_list)

    cofreq_df = build_cofreq_df(coocc_list)

    if method == 'all':
        reflist = coocc_list
    else :
        reflist = keylist

    for i in range(len(reflist)) :
        cofreq_df = fill_cofreq_df(reflist[i].split()[0], reflist[i].split()[1], cofreq_df, df, n, dtype)

    stat_df = fill_stat_df(df, freq_df, cofreq_df, coocc_list, n, arg, dtype)

    return build_graph(keylist, poslist, stat_df, freq_df, dtype, method)




def intersection(keylist, G, order):

    inter_list = []
    node_dic = {}
    
    for key in keylist :
        neighbor_dic = {}
        neighbor_list = [node for node in G.neighbors(key)]
        neighbor_list.append(key)
        neighbor_dic[0] = neighbor_list
        for j in range(1,order):
            for neighbor in neighbor_dic[j-1]:
                neighbor_list += [nodebis for nodebis in G.neighbors(neighbor)]
                neighbor_list.append(neighbor)
                neighbor_list = list(set(neighbor_list))
                neighbor_dic[j] = neighbor_list
        node_dic[key] = neighbor_dic[order - 1]
    
    for item in node_dic[keylist[0]]:
        i= 1 
        while item in node_dic[keylist[i]] :
            i += 1
            if i == len(node_dic):
                break
        if i == len(node_dic):
            inter_list.append(item)
                
    ratio = round(len(inter_list)/len(list(G.nodes())),3)
    
    weighted_inter = 0
    weighted_total = 0
    
    for node1 in inter_list:
        for node2 in inter_list :
            if nx.has_path(G, node1, node2):
                nodes = nx.dijkstra_path(G, node1, node2)
                if len (nodes) <= order + 1:
                    while len(nodes) > 1:
                        weighted_inter += 1/G[nodes[0]][nodes[1]]['weight']
                        nodes.pop(0)
                else:
                    pass
                
    for node1 in G.nodes():
        for node2 in G.nodes() :
            if nx.has_path(G, node1, node2):
                nodes = nx.dijkstra_path(G, node1, node2)
                if len(nodes) <= order + 1:
                    while len(nodes) > 1:
                        weighted_total += 1/G[nodes[0]][nodes[1]]['weight']
                        nodes.pop(0)
                else:
                    pass
            
    weighted_ratio = round(weighted_inter/weighted_total, 3)
    
    return inter_list, ratio, weighted_ratio




def full_intersection(keylist, path, poslist, n, arg, dtype, method, order):

    G = lexnet(keylist, path, poslist, n, arg, dtype, method)
        
    inter_list = []
    node_dic = {}
    
    for key in keylist :
        neighbor_dic = {}
        neighbor_list = [node for node in G.neighbors(key)]
        neighbor_list.append(key)
        neighbor_dic[0] = neighbor_list
        for j in range(1,order):
            for neighbor in neighbor_dic[j-1]:
                neighbor_list += [nodebis for nodebis in G.neighbors(neighbor)]
                neighbor_list.append(neighbor)
                neighbor_list = list(set(neighbor_list))
                neighbor_dic[j] = neighbor_list
        node_dic[key] = neighbor_dic[order - 1]
    
    for item in node_dic[keylist[0]]:
        i= 1
        while item in node_dic[keylist[i]] :
            i += 1
            if i == len(node_dic):
                break
        if i == len(node_dic):
            inter_list.append(item)
                
    ratio = round(len(inter_list)/len(list(G.nodes())),3)
    
    weighted_inter = 0
    weighted_total = 0
    
    for node1 in inter_list:
        for node2 in inter_list :
            if nx.has_path(G, node1, node2):
                nodes = nx.dijkstra_path(G, node1, node2)
                if len (nodes) <= order + 1:
                    while len(nodes) > 1:
                        weighted_inter += 1/G[nodes[0]][nodes[1]]['weight']
                        nodes.pop(0)
                else:
                    pass
                
    for node1 in G.nodes():
        for node2 in G.nodes() :
            if nx.has_path(G, node1, node2):
                nodes = nx.dijkstra_path(G, node1, node2)
                if len(nodes) <= order + 1:
                    while len(nodes) > 1:
                        weighted_total += 1/G[nodes[0]][nodes[1]]['weight']
                        nodes.pop(0)
                else:
                    pass
            
    weighted_ratio = round(weighted_inter/weighted_total, 3)
    
    return inter_list, ratio, weighted_ratio




def weighted_degree(G):
    return sorted(G.degree(weight = 'weight'), key = lambda x: x[1], reverse = True)
