import os
import pandas as pd
import streamlit as st
import geopandas as gpd
from PIL import Image
from postprocessing import  natural_breaks, levels_to_csv, draw_grid
import datetime as dt


def convert_df(df):

    return df.to_csv().encode('utf-8')


def make_life(txt_list):
    df = pd.DataFrame(columns=['gid', 'lbl', 'val'])
    cnt = 0
    flag = 0

    w_flag = True
    while w_flag:
        for i in range(1, len(txt_list) * 3, 3):
            if cnt <= 107555*3:
                try:
                    if '*' in txt_list[i + flag] or '*' in txt_list[i + flag + 1] or '*' in txt_list[i + flag + 2]:
                        df.loc[cnt] = [txt_list[i + flag], 0, 0]
                        flag -= 1
                        cnt += 1
                    else:
                        if txt_list[i + 1] == 'N/A' and txt_list[i + 2] == 'N/A':
                            df.loc[cnt] = [txt_list[i], 0, 0]
                        elif txt_list[i + 1] == 'N/A':
                            df.loc[cnt] = [txt_list[i], 0, float(txt_list[i + 2])]
                        elif txt_list[i + 2] == 'N/A':
                            df.loc[cnt] = [txt_list[i], float(txt_list[i + 1]), 0]
                        else:
                            try:
                                df.loc[cnt] = [txt_list[i], float(txt_list[i + 1]), float(txt_list[i + 2])]

                            except ValueError as e:
                                df.loc[cnt] = [txt_list[i], txt_list[i + 1], txt_list[i + 2]]

                        cnt += 1
                except IndexError as error:
                    break
            else:
                w_flag = False
        w_flag = False

    df['lbl'] = df['lbl'].astype(float)
    df['val'] = df['val'].astype(float)

    return df


def run_life(df, category):
    placeholder = st.empty()
    placeholder.success(category+' 데이터를 처리합니다.')
    if 'gid' in df.keys().to_list() and 'val' in df.keys().to_list():
        df = df[['gid', 'val']].groupby('gid')['val'].sum().reset_index()
        df.columns = ['gid', category]
        return df
    elif 'gid' in df.keys().to_list() and 'val' not in df.keys().to_list():
        warns = st.empty()
        warns.warning(category + '데이터의 "val" 값이 존재하지 않습니다. 프로그램이 종료됩니다. 새로고침을 눌러주세요.')
        st.stop()

    elif 'gid' not in df.keys().to_list() and 'val' in df.keys().to_list():
        warns = st.empty()
        warns.warning(category + '데이터의 "gid" 값이 존재하지 않습니다. 프로그램이 종료됩니다. 새로고침을 눌러주세요.')
        st.stop()

    else:
        warns = st.empty()
        warns.warning(category + '데이터의 구성 형식이 올바르지 않습니다. 프로그램이 종료됩니다. 새로고침을 눌러주세요.')
        st.stop()


def main_life(data_tot, data_child, data_elder,category):
    df_total = run_life(data_tot, '총인구')
    df_child = run_life(data_child, '유아')
    df_elder = run_life(data_elder, '고령')
    if len(df_child) !=0 and len(df_total) !=0 and len(df_elder)!=0:
        df = pd.concat([df_total[['gid', '총인구']],
                                         df_child[['유아']],
                                         df_elder[['고령']]], axis=1)

        df['취약인구'] = df['유아'] + df['고령']
        df['취약인구비'] = df['취약인구'] / df['총인구']
        df[category] = df['총인구'] * (df['취약인구비'] + 1)

        df = df[df[category].notnull()]
        df = df[['gid', '총인구', '취약인구', category]]

        return df
    else:
        warns = st.empty()
        warns.warning('데이터의 형태가 올바르지 않거나 빈 데이터가 입력되었습니다. 프로그램이 종료됩니다.')
        st.stop()


def save_and_processing(save_path, grid, df, columns, eng_name,mode=0):

    placeholder = st.empty()
    placeholder.warning('Impact library를 계산합니다.')

    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    """
    6 Jan, Delete
    # fd = dt.datetime.now()
    # filedate = str(fd.year) + str(fd.month) + str(fd.day) + str(fd.hour) + str(fd.minute) + str(fd.second)
    """

    """
    6 Jan, New
    """
    lib_filename = 'icuh_library_'+eng_name
    library = natural_breaks(df, columns, save_path, lib_filename)

    placeholder.empty()
    placeholder.warning('Impact level을 계산합니다.')
    level_filename = 'icuh_level_' + eng_name
    levels = levels_to_csv(library, columns, save_path, level_filename)

    placeholder.empty()
    if mode==0:
        placeholder.warning(columns + ' 결과 이미지를 저장중 입니다.')
    elif mode==1:
        placeholder.warning(columns + ' 결과 이미지를 저장중 입니다. ('+eng_name+')')
    draw_grid(grid, df, save_path, columns, eng_name, mode=1)
    # img_filename = 'grid_'+eng_name+'.png'
    placeholder.warning(columns + ' 결과 이미지 저장 완료.')

    return library, levels


def show_button(save_path, levels, img, library, eng_name, img_filename):
    st.subheader('Impact Levels')
    if type(levels['from'][0]) == 'float':
        st.write(levels.style.format("{:.6}"))
    else:
        st.write(levels)
    st.image(img)


    levels = convert_df(levels)
    st.download_button(
        label="Impact levels 산정 기준 저장하기",
        data=levels,
        file_name= 'icuh_level_'+eng_name + '.csv',
        mime='text/csv',
        key = eng_name+'_0'
    )

    libr = convert_df(library)
    st.download_button(
        label="Impact library 저장하기",
        data=libr,
        file_name= 'icuh_library_'+eng_name + '.csv',
        mime='text/csv',
        key=eng_name + '_1'
    )

    with open(save_path + img_filename,
              'rb') as img_save:
        st.download_button(
            label="이미지 저장하기",
            data=img_save,
            file_name=img_filename,
            mime="image/png",
            key=eng_name + '_2'
        )


def make_people(file):
    df = pd.read_csv(file, encoding='cp949')
    df = df.replace('*', 0)
    df.fillna(0)
    df.iloc[:, 5:] = df.iloc[:, 5:].astype(float).astype(int)
    df['취약인구수'] = df['남자0세부터9세생활인구수'] + df['남자65세부터69세생활인구수'] + df['남자70세이상생활인구수'] + df['여자0세부터9세생활인구수'] + df['여자65세부터69세생활인구수'] + df['여자70세이상생활인구수']
    try:
        df = df[['기준일ID', '시간대구분', '행정동코드', '집계구코드', '총생활인구수', '취약인구수']]
        return df
    except:
        df['기준일ID'] = df['?"기준일ID"']
        df = df[['기준일ID', '시간대구분', '행정동코드', '집계구코드', '총생활인구수', '취약인구수']]
        return df


def make_tot_sido(df_tot, df_child, df_elder):
    try:
        df_tot = run_life(df_tot, '총인구')
        df_child = run_life(df_child, '유아')
        df_elder = run_life(df_elder, '고령')
        tot_child = pd.merge(df_tot,df_child, on='gid')
        sido_df = pd.merge(tot_child,df_elder,on='gid')
        del tot_child

        sido_df['취약인구'] = sido_df['유아'] + sido_df['고령']
        sido_df['취약인구비'] = sido_df['취약인구'] / sido_df['총인구']
        sido_df['생활인구'] = sido_df['총인구'] * (sido_df['취약인구비'] + 1)

        sido_df = sido_df[sido_df['생활인구'].notnull()]
        sido_df = sido_df[['gid', '총인구', '취약인구', '생활인구']]

        return sido_df

    except RuntimeError as e:
        warns = st.empty()
        warns.warning('데이터 내에 gid 행이 존재하지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램이 종료됩니다.')
        st.stop()



def make_df_people(df):
    try:
        df = df.sort_values(by=['기준일ID', '시간대구분'])
        df['기준일ID'] = pd.to_datetime(df['기준일ID'].astype(str))
        df['day_of_week'] = df['기준일ID'].dt.dayofweek

        df.loc[(df['시간대구분'] >= 6) & (df['시간대구분'] < 9), '시제'] = 1
        df.loc[(df['시간대구분'] >= 9) & (df['시간대구분'] < 18), '시제'] = 2
        df.loc[(df['시간대구분'] >= 18) & (df['시간대구분'] < 21), '시제'] = 3
        df.loc[(df['시간대구분'] < 6) | (df['시간대구분'] >= 21), '시제'] = 4

        df.loc[(df['day_of_week'] >= 0) | (df['day_of_week'] < 5), '일별'] = 5
        df.loc[(df['day_of_week'] == 5) | (df['day_of_week'] == 6), '일별'] = 6

        df_weekdays = df[df['일별'] == 5]
        df_weekend = df[df['일별'] == 6]
        return df_weekdays, df_weekend

    except RuntimeError as e:
        warns = st.empty()
        warns.warning('데이터에 기준일ID 혹은 시간대구분 행이 존재하지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램이 종료됩니다.')
        st.stop()



def day_df(times, df, base_grid):
    df_edit = df[df['시제'] == times].copy()
    df_edit['집계구코드'] = df_edit['집계구코드'].astype(int)
    df_edit = df_edit.groupby('집계구코드')[['총생활인구수', '취약인구수']].mean().reset_index()
    df_edit.columns = ['TOT_REG_CD', '총생활인구수', '취약인구수']
    df_edit['TOT_REG_CD'] = df_edit['TOT_REG_CD'].astype(str)

    df_edit = pd.merge(base_grid, df_edit, on='TOT_REG_CD')
    df_edit['총생활인구수'] = df_edit['prop'] * df_edit['총생활인구수']
    df_edit['취약인구수'] = df_edit['prop'] * df_edit['취약인구수']

    df_edit = df_edit.groupby(['gid'])[['총생활인구수', '취약인구수']].sum().reset_index()
    df_edit['취약인구비'] = df_edit['취약인구수'] / df_edit['총생활인구수']

    return df_edit


def run_people(df, base_grid, seoul_grid, sido_df):
    time_nm = {1: '아침', 2: '낮', 3: '저녁', 4: '야간'}
    df_weekdays, df_weekend = make_df_people(df)
    df_list = {'평일': df_weekdays, '주말': df_weekend}

    results = []
    ph = st.empty()

    for d, day in enumerate(df_list):
        df = df_list[day]
        for times in range(1,len(time_nm)+1):
            ph.success(day + ' '+ time_nm[times])
            df_edit = day_df(times, df, base_grid)

            # Seoul
            seoul = pd.merge(seoul_grid, df_edit, on='gid')
            seoul['total'] = seoul['총생활인구수'] * (seoul['취약인구비'] + 1)
            seoul = seoul[['gid', '총생활인구수', '취약인구수', 'total']]
            seoul.columns = ['gid', '총인구', '취약인구', '생활인구']

            res = pd.concat([sido_df, seoul], axis=0)
            res = res.groupby(['gid'])[['총인구', '취약인구', '생활인구']].sum().reset_index()
            res.sort_values(by='gid').reset_index(drop=True)
            results.append(res)

    return results, time_nm, df_list


def make_traffic(road_overlay):
    try:
        df = road_overlay[['gid', 'FACIL_KIND', 'length_union', 'LANES']].copy()
        df['FACIL_KIND'] = df['FACIL_KIND'].astype(int)
        df['length_union'] = df['length_union'].astype(float)
        df['LANES'] = df['LANES'].astype(int)
        return df
    except RuntimeError as e:
        warns = st.empty()
        warns.warning('데이터 구성이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램이 종료됩니다.')
        st.stop()


def classify_traffic(df):
    placeholder = st.empty()
    placeholder.success('도로 종류 분류중... ')
    progress_facil = st.progress(0)

    df['FACIL_KIND'] = df['FACIL_KIND'].astype(str)

    for i, x in enumerate(df['FACIL_KIND']):
        progress_facil.progress(int(100 / len(df) * (i + 1)))
        if x == '0':
            df['FACIL_KIND'][i] = '일반도로'
        elif x == '1':
            df['FACIL_KIND'][i] = '교량'
        elif x == '2':
            df['FACIL_KIND'][i] = '터널'
        elif x == '4':
            df['FACIL_KIND'][i] = '고가도로'
        elif x == '8':
            df['FACIL_KIND'][i] = '지하도로'
    return df


def run_traffic(df):
    placeholder = st.empty()
    placeholder.success('도로 수 x 도로 길이 계산중...')
    df['LANExLENGTH'] = df['length_union'] * df['LANES']
    df = df[['gid', 'FACIL_KIND', 'LANExLENGTH']].dropna()
    df = pd.pivot_table(df,index='gid', columns='FACIL_KIND', values='LANExLENGTH', aggfunc='sum').reset_index()

    placeholder.success('취약 도로 분류중...')

    col_list = df.keys().to_list()

    if '고가도로' in col_list and '교량' in col_list and '터널' in col_list:
        df['지하차도/교량/터널'] = df['고가도로'] + df['교량'] + df['터널']

    elif '고가도로' in col_list and '교량' in col_list:
        df['지하차도/교량/터널'] = df['고가도로'] + df['교량']

    elif '교량' in col_list and '터널' in col_list:
        df['지하차도/교량/터널'] = df['교량'] + df['터널']

    elif '고가도로' in col_list and '터널' in col_list:
        df['지하차도/교량/터널'] = df['고가도로'] + df['터널']

    elif '고가도로' in col_list:
        df['지하차도/교량/터널'] = df['고가도로']

    elif '교량' in col_list:
        df['지하차도/교량/터널'] = df['교량']

    elif '터널' in col_list:
        df['지하차도/교량/터널'] = df['터널']


    df = df[['gid', '일반도로', '지하차도/교량/터널']]

    placeholder.success('취약 도로 계산중...')
    df['prop'] = df['지하차도/교량/터널'] / df['일반도로']
    df['도로'] = df.apply(lambda x: x['일반도로'] * (x['prop'] + 1) if x['prop'] > 0 else x['일반도로'], axis=1)

    df = df[df['일반도로'] > 0]
    df = df.sort_values(by='일반도로').reset_index()
    df = df.rename(columns={'일반도로': '일반도로/고속도로'})
    df = df[['gid', '일반도로/고속도로', '지하차도/교량/터널', '도로']]

    return df


def make_arch(allData_overlay, grid_ndra):
    placeholder = st.empty()
    placeholder.success('면적 계산중...')
    allData_overlay['area'] = allData_overlay.area
    allData_overlay = pd.pivot_table(allData_overlay,
                                     index=['gid'],
                                     columns='INTPR_NM',
                                     values='area',
                                     aggfunc='sum').reset_index()

    allData_overlay['합계'] = allData_overlay.iloc[:, 2:].sum(axis=1)
    allData_overlay['prop'] = allData_overlay['합계'] / 1000000

    ndra = grid_ndra.rename(columns={'prop': 'prop_ndra'})

    placeholder.success('자연재해위험지구 데이터와 계산중...')
    concat_data = pd.concat([allData_overlay, ndra], keys='gid').reset_index()
    concat_data = concat_data[concat_data["합계"] >= 0]

    concat_data['prop_ndra'] = concat_data['prop_ndra'].fillna(1)
    concat_data['prop'] = concat_data['prop'] * concat_data['prop_ndra']
    concat_data = concat_data.drop(columns=['합계'])
    concat_data = concat_data.rename(columns={'prop':'농업'})
    concat_data = concat_data[['gid', '과수', '논', '밭', '시설', '농업']]

    return concat_data


def make_livestock(df):
    df.columns = ['시도', '시군', '읍면동', '축종명', '개수', '시설 없음', '시설 있음', '자영', '임차', '사육규모', '단위']
    livestock = df[['시도', '시군', '읍면동', '축종명', '사육규모']]
    livestock = livestock[livestock['축종명'] != '소계']
    livestock = livestock[livestock['읍면동'] != '소계']
    livestock = livestock[livestock['시군'] != '소계']
    livestock = livestock[livestock['사육규모'] != '소계']
    livestock = livestock[livestock['시도'] != '총계']
    livestock = livestock.reset_index()
    livestock = livestock[['시도', '시군', '읍면동', '축종명', '사육규모']]

    return livestock


def make_buld_emd(bulds, emds, grid, list_name):
    allData = []
    emdData = []

    bar_livestock = st.progress(0)
    ph = st.empty()
    for ls_live, df_emd, i in zip(bulds, emds, list_name):
        ph.success(i + ' 자료 읽는 중...')
        bar_livestock.progress(int(100 / len(bulds) * (list_name.index(i) + 1)))

        ls_live['EMD_CD'] = ls_live['EMD_CD'].astype('str')
        ls_live['SIG_CD'] = ls_live['SIG_CD'].astype('str')
        ls_live['EMD_CD'] = ls_live['SIG_CD'] + ls_live['EMD_CD']
        ls_live = ls_live[['SIG_CD', 'EMD_CD', 'geometry']]

        df_emd['시도'] = str(i)
        df_emd['EMD_CD'] = df_emd['EMD_CD'].astype('str')
        df_emd = df_emd[['EMD_CD', '시도', 'EMD_KOR_NM']].copy()

        ls_live.merge(df_emd, on='EMD_CD')

        farm_sido = gpd.overlay(ls_live, grid, how='union')
        farm_sido['TYPE'] = '축사면적'
        farm_sido = farm_sido.loc[((farm_sido["EMD_CD"].notna()) & (farm_sido["gid"].notna()))]
        farm_sido['area'] = farm_sido.area
        farm_sido = pd.pivot_table(farm_sido, index=['gid', 'EMD_CD'],
                                   columns='TYPE', values='area', aggfunc='sum').reset_index()

        allData.append(farm_sido)
        emdData.append(df_emd)

    ph.success('자료 읽기 완료.')
    placeholder = st.empty()
    placeholder.warning('축사 면적 데이터 병합중...')
    farm = pd.concat(allData, axis=0, ignore_index=True)

    placeholder.warning('시도 데이터 병합중...')
    emd = pd.concat(emdData, axis=0, ignore_index=True)

    return farm, emd


def run_livestock(livestock, emd, farm, ndra):
    livestock['NM'] = livestock['시도'] + livestock['읍면동']

    emd['NM'] = emd['시도'] + emd['EMD_KOR_NM']

    livestocks = livestock.merge(emd, on='NM')

    livestocks = livestocks[['시도_x', '시군', '읍면동', 'EMD_CD', '축종명', '사육규모']]
    livestocks.columns = ['시도', '시군', '읍면동', 'EMD_CD', '축종명', '사육규모']

    livestocks['사육규모'] = livestocks['사육규모'].astype(int)

    livestocks = pd.pivot_table(livestocks,
                                index='EMD_CD',
                                columns='축종명',
                                values='사육규모', aggfunc='sum').reset_index()

    farm_total_area = farm.groupby('EMD_CD')['축사면적'].sum().reset_index()

    farm_total_area.columns = ['EMD_CD', 'total_area']
    farm = farm.merge(farm_total_area, on='EMD_CD')

    farm['prop'] = farm['축사면적'] / farm['total_area']

    merge_frame = farm.merge(livestocks, on='EMD_CD')

    merge_frame['한우'] = merge_frame['prop'] * merge_frame['한우']
    merge_frame['젖소'] = merge_frame['prop'] * merge_frame['젖소']
    merge_frame['돼지'] = merge_frame['prop'] * merge_frame['돼지']
    merge_frame['산란계'] = merge_frame['prop'] * merge_frame['산란계']
    merge_frame['육계'] = merge_frame['prop'] * merge_frame['육계']

    merge_frame.groupby('gid')['한우', '젖소', '돼지', '육계', '산란계'].sum().reset_index()

    merge_frame = merge_frame.fillna(0)

    concat_data = pd.merge(merge_frame, ndra, on='gid', how='left').reset_index()

    concat_data['prop_ndra'] = concat_data['prop_ndra'].fillna(1)

    concat_data['한우'] = concat_data['prop_ndra'] * concat_data['한우']
    concat_data['젖소'] = concat_data['prop_ndra'] * concat_data['젖소']
    concat_data['돼지'] = concat_data['prop_ndra'] * concat_data['돼지']
    concat_data['산란계'] = concat_data['prop_ndra'] * concat_data['산란계']
    concat_data['육계'] = concat_data['prop_ndra'] * concat_data['육계']

    concat_data['축산업'] = concat_data['한우'] + concat_data['젖소'] + concat_data['돼지'] + concat_data['육계'] + concat_data[
        '산란계']

    concat_data.groupby('gid')['한우', '젖소', '돼지', '육계', '산란계'].sum().reset_index()

    concat_data = concat_data[['gid', '한우', '젖소', '돼지', '산란계', '육계', '축산업']]
    concat_data = concat_data[concat_data["축산"] >= 0]

    return concat_data


def building_comm(df) :
    df = df[(df['BDTYP_CD'].str[:2] == '10') |
            (df['BDTYP_CD'].str[:2] == '18') |
            (df['BDTYP_CD'].str[:2] == '19') |
            (df['BDTYP_CD'].str[:2] == '20') |
            (df['BDTYP_CD'].str[:2] == '27')
       ].reset_index(drop=True)
    return df


def building_conv(df) :
    df = df[(df['BDTYP_CD'].str[:2] == '03') |
            (df['BDTYP_CD'].str[:2] == '04') |
            (df['BDTYP_CD'].str[:2] == '05') |
            (df['BDTYP_CD'].str[:2] == '06') |
            (df['BDTYP_CD'].str[:2] == '09') |
            (df['BDTYP_CD'].str[:2] == '11') |
            (df['BDTYP_CD'].str[:2] == '12')
       ].reset_index(drop=True)
    return df


def building_medi(df):
    df = df[(df['BDTYP_CD'].str[:2] == '07') |
            (df['BDTYP_CD'].str[:2] == '03005') |
            (df['BDTYP_CD'].str[:2] == '03108')
           ].reset_index(drop=True)
    return df


def building_edu(df):
    df = df[df['BDTYP_CD'].str[:2] == '08'].reset_index(drop=True)
    return df


def building_indus(df):
    df = df[(df['BDTYP_CD'].str[:2] == '13') |
            (df['BDTYP_CD'].str[:2] == '14') |
            (df['BDTYP_CD'].str[:2] == '15') |
            (df['BDTYP_CD'].str[:2] == '16') |
            (df['BDTYP_CD'].str[:2] == '17')
       ].reset_index(drop=True)
    return df


def run_facil(c_idx, buld, list_name, grid, ndra):
    sub_ph = st.empty()
    allData = []

    for i, k in zip(list_name, buld):
        sub_ph.success(i + ' 데이터셋 읽는 중...')
        if c_idx == '공용':
            allData.append(building_comm(k))
        elif c_idx == '공업':
            allData.append(building_indus(k))
        elif c_idx == '교육연구':
            allData.append(building_edu(k))
        elif c_idx == '의료복지':
            allData.append(building_medi(k))
        elif c_idx == '편의':
            allData.append(building_conv(k))
        else:
            allData = None

    allData = pd.concat(allData, axis=0, ignore_index=True)
    sub_ph.success(c_idx + '취약지표 계산중...')

    if c_idx == '의료복지' or c_idx == '교육연구':
        df_2 = gpd.overlay(grid, allData, how='intersection')
        df_3 = df_2.groupby(['gid'])['BDTYP_CD'].count().reset_index()
        df_3.columns = ['gid', c_idx]

    else:
        if c_idx == '공업':
            allData['BDTYP_CD_'] = allData['BDTYP_CD'].apply(lambda x: "공장"
            if (x.startswith("13"))
            else ("창고시설" if x.startswith("14")
                  else ("위험물저장처리시설" if x.startswith("15")
                        else ("자동차관련시설" if x.startswith("16")
                              else "동식물관련시설"))))
        elif c_idx == '공용':
            allData['BDTYP_CD_'] = allData['BDTYP_CD'].apply(lambda x: "업무시설"
            if (x.startswith("10"))
            else ("분뇨,쓰레기처리시설" if x.startswith("18")
                  else ("공공용시설" if x.startswith("19")
                        else ("묘지관련시설" if x.startswith("20")
                              else "발전시설"))))
        elif c_idx == '편의':
            allData['BDTYP_CD_'] = allData['BDTYP_CD'].apply(lambda x: "제1종근린생활시설"
            if (x.startswith("03"))
            else ("제2종근린생활시설" if x.startswith("04")
                  else ("문화및집회시설" if x.startswith("05")
                        else ("판매및영업시설" if x.startswith("06")
                              else ("운동시설" if x.startswith("09")
                                    else ("숙박시설" if x.startswith("11")
                                          else "위락시설"))))))

        df_2 = gpd.overlay(grid, allData, how='intersection')
        df_3 = pd.pivot_table(df_2,
                              index='gid',
                              columns='BDTYP_CD_',
                              values='BSI_INT_SN', aggfunc='count').reset_index()

        df_3[c_idx] = df_3.sum(axis=1)

    concat_data = pd.merge(df_3, ndra, on='gid', how='left').reset_index()
    concat_data = concat_data[concat_data[c_idx] >= 0]

    concat_data['prop_ndra'] = concat_data['prop_ndra'].fillna(1)
    concat_data[c_idx] = concat_data[c_idx] * concat_data['prop_ndra']


    sub_ph.success('계산 완료')



    return concat_data


