#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import mapclassify as mc
import matplotlib.patches as mpatches
from PIL import ImageColor

plt.rc('font', family='NanumGothic')

def grid_ndra(grid_file, ndra_file, km_param=1000000):
    grid = gpd.read_file(grid_file).to_crs(epsg=5179)
    ndra = gpd.read_file(ndra_file, encoding='CP949').to_crs(epsg=5179)

    ndra = ndra[['ALIAS', 'SGG_OID', 'COL_ADM_SE', 'geometry']]

    grid_ndra = gpd.overlay(ndra, grid, how='union')
    grid_ndra = grid_ndra.loc[((grid_ndra["SGG_OID"] >= 0) & (grid_ndra["gid"].notnull()))]
    grid_ndra['area'] = grid_ndra.area
    grid_ndra = grid_ndra.groupby('gid')['area'].sum().reset_index()
    grid_ndra['prop'] = grid_ndra['area'] / km_param
    grid_ndra = grid_ndra[['gid', 'prop']]

    return grid, grid_ndra


def natural_breaks(df, columns, folder, filename):
    classifier = mc.NaturalBreaks.make(k=4)
    print(folder+'/'+filename+'.csv')
    df.to_csv(f'{folder}/{filename}.csv', encoding='cp949', index=False)

    df['LEVEL'] = df[[columns]].apply(classifier)
    df['LEVEL'] = df['LEVEL'] + 1
    df['LEVEL'] = df['LEVEL'].astype(int)

    return df


def levels_to_csv(df, columns, folder, filename):
    level_1 = df[df['LEVEL'] == 1][columns].max()
    level_2 = df[df['LEVEL'] == 2][columns].max()
    level_3 = df[df['LEVEL'] == 3][columns].max()

    levels = pd.DataFrame([[df[df['LEVEL'] == 1][columns].min(), level_1], [level_1, level_2], [level_2, level_3], [level_3,df[columns].max()]], columns=['from', 'to'])
    if columns=='농업' or columns=='도로':
        levels = levels.astype('float')
    else:
        levels = levels.astype('int')

    levels.to_csv(f'{folder}/{filename}.csv', encoding='cp949', index=False)

    return levels


def draw_grid(grid, df, folder, category, filename, mode=1):
    if mode == 1:
        test = pd.merge(grid, df, on='gid')  # 5km --> on = 'id'
    elif mode == 5:
        test = pd.merge(grid, df, on='id')
    else:
        print('Mode error!')

    colors = {0: '#ebebeb',
              1: '#50a1be',
              2: '#fdd232',
              3: '#e65f25',
              4: '#b8191f'}

    colors_rgb = []

    for c in colors:
        r, g, b, a = ImageColor.getcolor(colors[c], "RGBA")
        colors_rgb.append((r / 255.0, g / 255.0, b / 255.0, a / 255.0,))

    values = ['Minimal', 'Minor', 'Significant', 'Severe']

    fig, ax = plt.subplots(figsize=(12, 16))
    grid.plot(ax=ax, color='#ebebeb')
    for ctype, data in test.groupby('LEVEL'):
        color = colors[ctype]
        data.plot(ax=ax, legend=True, categorical=True, color=color, label=ctype)
    patches = [mpatches.Patch(color=colors_rgb[i + 1], label="{l}".format(l=values[i])) for i in range(len(values))]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,
               fontsize='xx-large')
    # plt.title(category, fontsize=20)
    ax.set_axis_off()
    plt.tight_layout()

    plt.show()

    plt.savefig(folder + '/grid_' + filename + '.png', dpi=300)
