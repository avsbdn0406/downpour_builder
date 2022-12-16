import os
from PIL import Image
from pathlib import Path

import pandas as pd
import streamlit as st

import geopandas as gpd
from shapely import wkt

from preprocessing import make_life, main_life, save_and_processing, show_button, \
    make_traffic, classify_traffic, run_traffic, make_arch, make_livestock, make_buld_emd, run_livestock,\
    run_facil, make_people, make_tot_sido, run_people



def grid_ndra(grid_file, ndra_file, km_param=1000000):
    placeholder = st.empty()
    placeholder.success('전국격자지도 읽는 중...')
    grid = gpd.read_file(grid_file).to_crs(epsg=5179)
    placeholder.success('자연재해위험지구 읽는 중...')
    ndra = gpd.read_file(ndra_file, encoding='CP949').to_crs(epsg=5179)

    ndra = ndra[['ALIAS', 'SGG_OID', 'COL_ADM_SE', 'geometry']]
    placeholder.success('전국격자지도 X 자연재해위험지구 ...')
    grid_ndra = gpd.overlay(ndra, grid, how='union')
    grid_ndra = grid_ndra.loc[((grid_ndra["SGG_OID"] >= 0) & (grid_ndra["gid"].notnull()))]
    grid_ndra['area'] = grid_ndra.area
    grid_ndra = grid_ndra.groupby('gid')['area'].sum().reset_index()
    grid_ndra['prop'] = grid_ndra['area'] / km_param
    grid_ndra = grid_ndra[['gid', 'prop']]
    placeholder.success('데이터 읽기 완료')

    return grid, grid_ndra


if __name__ == "__main__":

    st.markdown("""<div style="background-color:#464e5f;padding:1px;border-radius:5px">
<h3 style="color:white;text-align:center;">호우영향예보</h3></div>""", unsafe_allow_html=True)
    st.write(' ')
    st.write(' ')
    st.write(' ')



    st.subheader('대상체를 선택해주세요.')
    categories = ['01. 전국인구',
                                 '02. 생활인구',
                                 '03. 도로',
                                 '04. 농업',
                                 '05. 시설',
                                 '06. 축산업']
    category = st.selectbox('', categories)

    c_idx = categories.index(category)

    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.subheader('데이터를 입력해주세요.')

    if c_idx == 0:
        dataset = []
        st.session_state.category = '전국_인구'

        st.write('총 인구 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='0')
        if tmp is not None and len(tmp) !=0 and 'data_01' not in st.session_state:
            bar_tot = st.progress(0)
            st.session_state.data_01 = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_tot.progress(int(100/len(tmp) * (idx+1)))
                if uploaded_file.name.split('.')[-1]=='dbf':
                    s = str(uploaded_file.getvalue()[120:],'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    st.session_state.data_01.append(df)

            st.session_state.data_01 = pd.concat(st.session_state.data_01, ignore_index=True)
            placeholder.success('총인구 데이터 읽기 완료')

        st.write('유아 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='1')
        if tmp is not None and len(tmp) != 0 and 'data_02' not in st.session_state:
            bar_child = st.progress(0)
            st.session_state.data_02 = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_child.progress(int(100 / len(tmp) * (idx + 1)))
                if uploaded_file.name.split('.')[-1] == 'dbf':
                    s = str(uploaded_file.getvalue()[120:], 'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    st.session_state.data_02.append(df)

            st.session_state.data_02 = pd.concat(st.session_state.data_02, ignore_index=True)
            placeholder.success('유아 데이터 읽기 완료')

        st.write('고령 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='2')
        if tmp is not None and len(tmp) != 0 and 'data_03' not in st.session_state:
            bar_elder = st.progress(0)
            st.session_state.data_03 = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_elder.progress(int(100 / len(tmp) * (idx + 1)))
                if uploaded_file.name.split('.')[-1] == 'dbf':
                    s = str(uploaded_file.getvalue()[120:], 'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    st.session_state.data_03.append(df)
            st.session_state.data_03 = pd.concat(st.session_state.data_03, ignore_index=True)
            placeholder.success('고령 데이터 읽기 완료')

        if 'data_01' in st.session_state and 'data_02' in st.session_state and 'data_03' in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'

            if 'levels' not in st.session_state:
                st.session_state.grid = gpd.read_file(grid_path).to_crs(epsg=5179)
                placeholder = st.empty()

                st.session_state.df = main_life(st.session_state.data_01, st.session_state.data_02, st.session_state.data_03)
                st.session_state.save_path = './results/'
                if not os.path.isdir(st.session_state.save_path):
                    os.makedirs(st.session_state.save_path)
                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,st.session_state.grid, st.session_state.df, st.session_state.category,st.session_state.category)
                st.session_state.img = Image.open(st.session_state.save_path + 'grid_' + st.session_state.category + '.png')

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                show_button(st.session_state.save_path, st.session_state.levels,st.session_state.img,
                            st.session_state.library, st.session_state.category)

    elif c_idx == 1:
        st.session_state.category = '생활인구'

        st.write('생활 인구 데이터')

        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='csv', key='0')
        if tmp is not None and len(tmp) !=0 and 'dataset' not in st.session_state:
            bar_people = st.progress(0)
            dataset = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                st.session_state.y = uploaded_file.name.split('_')[2][:4]
                st.session_state.m = uploaded_file.name.split('_')[2][4:6]
                d = uploaded_file.name.split('_')[2][6:8]
                placeholder.success(st.session_state.y+'년 '+st.session_state.m+'월 '+d+'일 데이터 읽는 중...')
                bar_people.progress(int(100/len(tmp) * (idx+1)))
                if uploaded_file.name.split('.')[-1] == 'csv':
                    df = make_people(uploaded_file)
                    dataset.append(df)
            placeholder.success('데이터 읽기 완료.')
            st.session_state.dataset = pd.concat(dataset,ignore_index=True)

        st.write('총 인구 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='1')
        if tmp is not None and len(tmp) !=0 and 'data_01' not in st.session_state:
            bar_tot = st.progress(0)
            df_tot = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_tot.progress(int(100/len(tmp) * (idx+1)))
                if uploaded_file.name.split('.')[-1]=='dbf':
                    s = str(uploaded_file.getvalue()[120:],'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    df_tot.append(df)

            df_tot = pd.concat(df_tot, ignore_index=True)
            df_tot = df_tot[['gid', 'val']].groupby('gid')['val'].sum().reset_index()
            df_tot.columns = ['gid', '총인구']
            st.session_state.data_01 = df_tot
            placeholder.success('총인구 데이터 읽기 완료')

        st.write('유아 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='2')
        if tmp is not None and len(tmp) != 0 and 'data_02' not in st.session_state:
            bar_child = st.progress(0)
            df_child = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_child.progress(int(100 / len(tmp) * (idx + 1)))
                if uploaded_file.name.split('.')[-1] == 'dbf':
                    s = str(uploaded_file.getvalue()[120:], 'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    df_child.append(df)

            df_child = pd.concat(df_child, axis=0, ignore_index=True)
            df_child = df_child[['gid', 'val']].groupby('gid')['val'].sum().reset_index()
            df_child.columns = ['gid', '유아']
            st.session_state.data_02 = df_child
            placeholder.success('유아 데이터 읽기 완료')

        st.write('고령 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='3')
        if tmp is not None and len(tmp) != 0 and 'data_03' not in st.session_state:
            bar_elder = st.progress(0)
            df_elder = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_elder.progress(int(100 / len(tmp) * (idx + 1)))
                if uploaded_file.name.split('.')[-1] == 'dbf':
                    s = str(uploaded_file.getvalue()[120:], 'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    df_elder.append(df)
            df_elder = pd.concat(df_elder, ignore_index=True)
            df_elder = df_elder[['gid', 'val']].groupby('gid')['val'].sum().reset_index()
            df_elder.columns = ['gid', '고령']
            st.session_state.data_03 = df_elder

            placeholder.success('고령 데이터 읽기 완료')

        if 'dataset' in st.session_state and 'data_01' in st.session_state and 'data_02' in st.session_state and 'data_03' in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'
            seoul_path = root_path + '서울시_격자.shp'
            base_path = root_path + '서울시_base.shp'

            if 'levels' not in st.session_state:
                placeholder = st.empty()
                placeholder.success('전국격자지도 데이터셋 읽는 중...')
                st.session_state.grid = gpd.read_file(grid_path).to_crs(epsg=5179)

                placeholder.success('서울시 격자 데이터셋 읽는 중...')
                st.session_state.seoul_grid = gpd.read_file(seoul_path,encoding='utf-8')
                st.session_state.seoul_grid = st.session_state.seoul_grid.set_crs(epsg=5179, allow_override=True)

                placeholder.success('서울시 base 데이터셋 읽는 중...')
                st.session_state.base_grid = gpd.read_file(base_path, encoding='cp949')
                st.session_state.base_grid = st.session_state.base_grid.set_crs(epsg=5179, allow_override=True)

                placeholder.success('유아 및 고령 데이터 지표 구성...')
                st.session_state.sido_df = make_tot_sido(st.session_state.data_01, st.session_state.data_02, st.session_state.data_03)

                st.session_state.results,st.session_state.time_nm, st.session_state.df_list = run_people(st.session_state.dataset, st.session_state.base_grid, st.session_state.seoul_grid, st.session_state.sido_df)

                st.session_state.libraries = []
                st.session_state.images = []
                st.session_state.levels = []
                st.session_state.save_files = []
                st.session_state.save_path = os.path.join('./results/', st.session_state.category, st.session_state.m)

                for res, day in zip(st.session_state.results, st.session_state.df_list):
                    for times in range(1,len(st.session_state.time_nm)+1):
                        save_file = day+'_' + st.session_state.category + '_' + st.session_state.time_nm[times]
                        st.session_state.library, st.session_state.level = save_and_processing(st.session_state.save_path, st.session_state.grid, res, st.session_state.category, save_file)
                        st.session_state.img = Image.open(st.session_state.save_path + '/grid_' + save_file + '.png')

                        st.session_state.libraries.append(st.session_state.library)
                        st.session_state.levels.append(st.session_state.level)
                        st.session_state.images.append(st.session_state.img)
                        st.session_state.save_files.append(save_file)

            if 'images' in st.session_state and 'libraries' in st.session_state and 'levels' in st.session_state:
                for f_name, level, library, img in zip(st.session_state.save_files, st.session_state.levels,
                                                  st.session_state.libraries, st.session_state.images):
                    show_button(st.session_state.save_path, level, img, library, f_name)

    elif c_idx == 2:
        st.session_state.category = '도로'

        st.write('도로 데이터')

        uploaded_file = st.file_uploader('Please choose a file.', accept_multiple_files=False, type='csv', key='0')

        if uploaded_file is not None and 'dataset' not in st.session_state:
            placeholder = st.empty()
            placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')

            if uploaded_file.name.split('.')[-1] == 'csv':
                df = pd.read_csv(uploaded_file,encoding='cp949')
                df['geometry'] = df['WKT'].apply(wkt.loads)
                del df['WKT']
                df = gpd.GeoDataFrame(df, crs='epsg:5179')

            st.session_state.dataset = df
            placeholder.success('도로 데이터 읽기 완료')

        if 'dataset' in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'

            if 'levels' not in st.session_state:
                placeholder = st.empty()
                placeholder.success('전국격자지도 데이터셋 읽는 중...')
                st.session_state.grid = gpd.read_file(grid_path).to_crs(epsg=5179)
                placeholder.success('도로 데이터 X 전국격자지도 데이터셋 오버레이 중...')
                road_overlay = gpd.overlay(st.session_state.dataset, st.session_state.grid, how='union')

                road_overlay['length_union'] = road_overlay.length / 1000

                st.session_state.df = make_traffic(road_overlay)
                st.session_state.df = classify_traffic(st.session_state.df)
                st.session_state.df = run_traffic(st.session_state.df)

                st.session_state.save_path = './results/'
                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,st.session_state.grid, st.session_state.df, st.session_state.category, st.session_state.category)
                st.session_state.img = Image.open(st.session_state.save_path + 'grid_' + st.session_state.category + '.png')

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                show_button(st.session_state.save_path, st.session_state.levels,st.session_state.img,
                            st.session_state.library, st.session_state.category)

    elif c_idx == 3:
        st.session_state.category = '농업'

        st.write('농업 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='csv', key='0')

        if tmp is not None and len(tmp) !=0 and 'arch' not in st.session_state:
            dataset = []
            placeholder = st.empty()
            bar_arch = st.progress(0)
            for idx, uploaded_file in enumerate(tmp):
                if uploaded_file.name.split('.')[-1] == 'csv':
                    bar_arch.progress(int(100 / len(tmp) * (idx + 1)))
                    placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                    df = pd.read_csv(uploaded_file, encoding='cp949')
                    df['geometry'] = df['geometry'].apply(wkt.loads)
                    df = gpd.GeoDataFrame(df, crs='epsg:5179')
                    df = df[['INTPR_NM','geometry']]
                    dataset.append(df)
            df = pd.concat(dataset, axis=0, ignore_index=True)
            st.session_state.arch = df
            placeholder.success('농업 데이터 읽기 완료')

        if 'arch' in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'
            ndra_path = root_path + '자연재해위험지구.shp'

            if 'levels' not in st.session_state:
                st.session_state.grid, st.session_state.grid_ndra = grid_ndra(grid_path, ndra_path)

                placeholder = st.empty()
                placeholder.success('전국격자지도 X 농업 격자 데이터...')
                st.session_state.arch_overlay = gpd.overlay(st.session_state.grid, st.session_state.arch, how = 'intersection')

                st.session_state.df = make_arch(st.session_state.arch_overlay, st.session_state.grid_ndra)
                st.session_state.save_path = './results/'
                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,
                                                                                        st.session_state.grid,
                                                                                        st.session_state.df,
                                                                                        st.session_state.category,
                                                                                        st.session_state.category)
                st.session_state.img = Image.open(
                    st.session_state.save_path + 'grid_' + st.session_state.category + '.png')

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                show_button(st.session_state.save_path, st.session_state.levels, st.session_state.img,
                            st.session_state.library, st.session_state.category)

    elif c_idx == 4:
        st.session_state.category = '시설'
        st.markdown('시설은 **공용, 공업, 교육연구, 의료복지, 편의** 총 **5개의 카테고리**로 이뤄져있습니다.', unsafe_allow_html=False)
        st.write('공통적으로 전국격자지도가 필요하여 데이터를 먼저 읽습니다.')
        st.session_state.c_list = ['공업','공용','교육연구','의료복지','편의']
        st.session_state.c_list.sort()
        if 'grid' not in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'
            placeholder = st.empty()
            placeholder.success('전국격자지도 읽는 중 ...')
            st.session_state.grid = gpd.read_file(grid_path).to_crs(epsg=5179)
            placeholder.success('전국격자지도 read 완료')

        st.write('BULD 파일')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='csv', key='0')

        if tmp is not None and len(tmp)!=0 and 'buld' not in st.session_state:
            st.session_state.list_name = []
            bar_buld = st.progress(0)
            dataset = []
            st.session_state.buld = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_buld.progress(int(100/len(tmp) * (idx+1)))
                if uploaded_file.name.split('.')[-1]=='csv':
                    df = pd.read_csv(uploaded_file, encoding='cp949')
                    df['BDTYP_CD'] = df['BDTYP_CD'].astype('str')
                    for i, b in enumerate(df['BDTYP_CD']):
                        if len(b)<5:
                            df['BDTYP_CD'].loc[i] = '0'+b

                    df['geometry'] = df['geometry'].apply(wkt.loads)
                    df = gpd.GeoDataFrame(df, crs='epsg:5179')
                    dataset.append(df)
                    st.session_state.list_name.append(uploaded_file.name)

            st.session_state.buld = dataset
            placeholder.success('BULD 데이터 읽기 완료')

        if 'buld' in st.session_state:
            st.subheader('시설의 세부 카테고리를 선택해주세요.')

            sub_category = st.selectbox('', st.session_state.c_list)
            sub_cidx = st.session_state.c_list.index(sub_category)

            st.session_state.save_path = './results/'
            st.session_state.sub_cidx = sub_category
            st.session_state.library, st.session_state.level, st.session_state.img = run_facil(st.session_state.sub_cidx, st.session_state.buld,
                                            st.session_state.list_name, st.session_state.grid)

            if 'img' in st.session_state and 'library' in st.session_state and 'level' in st.session_state:
                show_button(st.session_state.save_path, st.session_state.level, st.session_state.img,
                            st.session_state.library, st.session_state.sub_cidx)

    elif c_idx == 5:
        st.session_state.category = '축산업'
        list_dict = {'11000':'서울특별시', '36000':'세종특별자치시', '30000':'대전광역시',
                     '29000':'광주광역시', '26000':'부산광역시', '27000':'대구광역시',
                     '31000': '울산광역시', '28000':'인천광역시', '50000':'제주특별자치도',
                     '46000':'전라남도', '45000':'전라북도', '44000':'충청남도',
                     '43000':'충청북도', '41000':'경기도', '42000':'강원도',
                     '48000':'경상남도', '47000':'경상북도'}

        st.write('축산업 데이터')
        uploaded_file = st.file_uploader('Please choose a file.', accept_multiple_files=False, type='xlsx', key='0')
        list_name = []

        if uploaded_file is not None and 'livestock' not in st.session_state:
            placeholder = st.empty()
            placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')

            if uploaded_file.name.split('.')[-1] == 'xlsx':
                df = pd.read_excel(uploaded_file, header=2)
                st.session_state.livestock = make_livestock(df)

            placeholder.success(uploaded_file.name + ' 데이터 읽기 완료.')

        st.write('BULD 파일')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='csv', key='1')

        if tmp is not None and len(tmp)!=0 and 'buld' not in st.session_state:
            bar_buld = st.progress(0)
            dataset = []
            st.session_state.buld = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_buld.progress(int(100/len(tmp) * (idx+1)))
                if uploaded_file.name.split('.')[-1]=='csv':
                    df = pd.read_csv(uploaded_file, encoding='cp949')
                    df['BDTYP_CD'] = df['BDTYP_CD'].astype('str')
                    df = df[df['BDTYP_CD'] == '17101']
                    df = df.reset_index()
                    df['geometry'] = df['geometry'].apply(wkt.loads)
                    df = gpd.GeoDataFrame(df, crs='epsg:5179')
                    dataset.append(df)
            st.session_state.buld = dataset
            placeholder.success('BULD 데이터 읽기 완료')

        st.write('EMD 파일')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='csv', key='2')

        if tmp is not None and len(tmp) !=0 and 'emd' not in st.session_state:
            bar_emd = st.progress(0)
            dataset = []
            st.session_state.emd = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_emd.progress(int(100/len(tmp) * (idx+1)))
                if uploaded_file.name.split('.')[-1]=='csv':
                    df = pd.read_csv(uploaded_file,encoding='cp949')
                    df['geometry'] = df['geometry'].apply(wkt.loads)
                    df = gpd.GeoDataFrame(df, crs='epsg:5179')
                    dataset.append(df)
                    emd_c = df['EMD_CD'][0]

                for country in list(list_dict.keys()):
                    if country[:2] == str(emd_c)[:2]:
                        list_name.append(list_dict[country])
                        break

            st.session_state.list_name = list_name
            st.session_state.emd = dataset
            placeholder.success('EMD 데이터 읽기 완료')

        if 'livestock' in st.session_state and 'buld' in st.session_state and 'emd' in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'

            if 'levels' not in st.session_state:
                placeholder = st.empty()
                placeholder.success('전국격자지도 읽는 중 ...')
                st.session_state.grid = gpd.read_file(grid_path,encoding='cp949').to_crs(epsg=5179)
                placeholder.success('전국격자지도 read 완료')

                st.session_state.farm, st.session_state.emd = make_buld_emd(st.session_state.buld, st.session_state.emd, st.session_state.grid, st.session_state.list_name)
                st.session_state.df = run_livestock(st.session_state.livestock, st.session_state.emd, st.session_state.farm)

                st.session_state.save_path = './results/'
                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,
                                                                                        st.session_state.grid,
                                                                                        st.session_state.df,
                                                                                        st.session_state.category,
                                                                                        st.session_state.category)
                st.session_state.img = Image.open(
                    st.session_state.save_path + 'grid_' + st.session_state.category + '.png')

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                show_button(st.session_state.save_path, st.session_state.levels, st.session_state.img,
                            st.session_state.library, st.session_state.category)










