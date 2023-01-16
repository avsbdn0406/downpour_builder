import os
from PIL import Image
from pathlib import Path

import pandas as pd
import streamlit as st

import geopandas as gpd
from shapely import wkt
import calendar

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
    overlay_ndra = gpd.overlay(ndra, grid, how='union')
    overlay_ndra = overlay_ndra.loc[((overlay_ndra["SGG_OID"] >= 0) & (overlay_ndra["gid"].notnull()))]
    overlay_ndra['area'] = overlay_ndra.area
    overlay_ndra = overlay_ndra.groupby('gid')['area'].sum().reset_index()
    overlay_ndra['prop'] = overlay_ndra['area'] / km_param
    overlay_ndra = overlay_ndra[['gid', 'prop']]
    placeholder.success('데이터 읽기 완료')

    return grid, overlay_ndra


if __name__ == "__main__":

    st.markdown("""<div style="background-color:#464e5f;padding:1px;border-radius:5px">
<h3 style="color:white;text-align:center;">호우영향예보</h3></div>""", unsafe_allow_html=True)
    st.write(' ')
    st.write(' ')
    st.write(' ')

    st.subheader('대상체를 선택해주세요.')
    categories = ['01. 생활','02. 생활인구','03. 도로','04. 농업','05. 시설','06. 축산업']
    category = st.selectbox('', categories)

    c_idx = categories.index(category)
    server_dir = './tmp/IRIS/'

    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.subheader('데이터를 입력해주세요.')

    if c_idx == 0:
        dataset = []
        st.session_state.category = '생활'
        st.session_state.category_eng = 'life'

        st.write('총 인구 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='0')
        if tmp is not None and len(tmp) !=0 and 'data_tot' not in st.session_state:
            bar_tot = st.progress(0)
            data_tot = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_tot.progress(int(100/len(tmp) * (idx+1)))
                if uploaded_file.name.split('.')[-1]=='dbf':
                    try:
                        s = str(uploaded_file.getvalue()[120:], 'utf-8')
                        s = ' '.join(s.split())
                        txt_list = s.split(' ')
                        df = make_life(txt_list)
                        data_tot.append(df)
                    except UnicodeDecodeError as e:
                        warns = st.empty()
                        warns.warning('데이터 구성 형식이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램을 종료합니다.')
                        st.stop()

                else:
                    warns = st.empty()
                    warns.warning(uploaded_file.name+' 파일은 dbf 확장자가 아니므로 제외됩니다.')

            st.session_state.data_tot = pd.concat(data_tot, ignore_index=True)
            placeholder.success('총인구 데이터 읽기 완료')

        st.write('유아 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='1')
        if tmp is not None and len(tmp) != 0 and 'data_child' not in st.session_state:
            bar_child = st.progress(0)
            data_child = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_child.progress(int(100 / len(tmp) * (idx + 1)))
                if uploaded_file.name.split('.')[-1] == 'dbf':
                    try:
                        s = str(uploaded_file.getvalue()[120:], 'utf-8')
                        s = ' '.join(s.split())
                        txt_list = s.split(' ')
                        df = make_life(txt_list)
                        data_child.append(df)
                    except UnicodeDecodeError as e:
                        warns = st.empty()
                        warns.warning('데이터 구성 형식이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램을 종료합니다.')
                        st.stop()
                else:
                    warns = st.empty()
                    warns.warning(uploaded_file.name+' 파일은 dbf 확장자가 아니므로 제외됩니다.')

            st.session_state.data_child = pd.concat(data_child, ignore_index=True)
            placeholder.success('유아 데이터 읽기 완료')

        st.write('고령 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='dbf', key='2')
        if tmp is not None and len(tmp) != 0 and 'data_elder' not in st.session_state:
            bar_elder = st.progress(0)
            data_elder = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                placeholder.success(uploaded_file.name + ' 데이터 읽는 중...')
                bar_elder.progress(int(100 / len(tmp) * (idx + 1)))
                if uploaded_file.name.split('.')[-1] == 'dbf':
                    try:
                        s = str(uploaded_file.getvalue()[120:], 'utf-8')
                        s = ' '.join(s.split())
                        txt_list = s.split(' ')
                        df = make_life(txt_list)
                        data_elder.append(df)
                    except UnicodeDecodeError as e:
                        warns = st.empty()
                        warns.warning('데이터 구성 형식이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램을 종료합니다.')
                        st.stop()
                else:
                    warns = st.empty()
                    warns.warning(uploaded_file.name+' 파일은 dbf 확장자가 아니므로 제외됩니다.')

            st.session_state.data_elder = pd.concat(data_elder, ignore_index=True)
            placeholder.success('고령 데이터 읽기 완료')

        if 'data_tot' in st.session_state and 'data_child' in st.session_state and 'data_elder' in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'

            if 'levels' not in st.session_state:
                st.session_state.grid = gpd.read_file(grid_path).to_crs(epsg=5179)
                placeholder = st.empty()

                st.session_state.df = main_life(st.session_state.data_tot, st.session_state.data_child, st.session_state.data_elder,st.session_state.category)
                st.session_state.save_path = server_dir

                if not os.path.isdir(st.session_state.save_path):
                    save_warns = st.empty()
                    save_warns.warning('저장 경로가 존재하지 않습니다. 관리자에게 문의하세요.')
                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,st.session_state.grid, st.session_state.df, st.session_state.category,st.session_state.category_eng)
                del st.session_state.library['LEVEL']
                st.session_state.img_filename = 'grid_'+st.session_state.category_eng+'.png'
                st.session_state.img = Image.open(st.session_state.save_path + st.session_state.img_filename)

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                st.header(st.session_state.category)
                show_button(st.session_state.save_path, st.session_state.levels,st.session_state.img,
                            st.session_state.library, st.session_state.category_eng, st.session_state.img_filename)

    elif c_idx == 1:
        st.session_state.category = '생활인구'
        st.session_state.category_eng = 'lifeman'

        st.write('서울시 생활 인구 데이터')

        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=True, type='csv', key='0')
        if tmp is not None and len(tmp) !=0 and 'dataset' not in st.session_state:
            bar_people = st.progress(0)
            dataset = []
            placeholder = st.empty()

            for idx, uploaded_file in enumerate(tmp):
                if len(uploaded_file.name)!=25:
                    warns = st.empty()
                    warns.warning(uploaded_file.name + ' : 잘못된 형식의 파일명입니다. 매뉴얼을 참고하세요. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램이 종료됩니다.')
                    st.stop()
                else:
                    y = uploaded_file.name.split('_')[2][:4]
                    m = uploaded_file.name.split('_')[2][4:6]
                    st.session_state.m = calendar.month_abbr[int(m)]
                    d = uploaded_file.name.split('_')[2][6:8]
                    placeholder.success(y+'년 '+m+'월 '+d+'일 데이터 읽는 중...')
                    bar_people.progress(int(100/len(tmp) * (idx+1)))

                    if uploaded_file.name.split('.')[-1] == 'csv':
                        try:
                            df = make_people(uploaded_file)
                            dataset.append(df)
                        except UnicodeDecodeError as e:
                            warns = st.empty()
                            warns.warning('데이터 구성 형식이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램을 종료합니다.')
                            st.stop()

            placeholder.success('데이터 읽기 완료.')
            st.session_state.dataset = pd.concat(dataset,ignore_index=True)

        st.write('서울시 총 인구 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=False, type='dbf', key='1')
        if tmp is not None and 'data_tot' not in st.session_state:
            bar_tot = st.progress(0)
            df_tot = []
            placeholder = st.empty()
            placeholder.success(tmp.name + ' 데이터 읽는 중...')

            if tmp.name.split('.')[-1] == 'dbf':
                try:
                    s = str(tmp.getvalue()[120:], 'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    df_tot.append(df)

                    st.session_state.data_tot = pd.concat(df_tot, ignore_index=True)
                    del df_tot
                    placeholder.success('총인구 데이터 읽기 완료')

                except UnicodeDecodeError as e:
                    warns = st.empty()
                    warns.warning('데이터 구성 형식이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램을 종료합니다.')
                    st.stop()
            else:
                warns = st.empty()
                warns.warning(tmp.name+' 파일은 dbf 확장자가 아니므로 제외됩니다.')

        st.write('서울시 유아 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=False, type='dbf', key='2')
        if tmp is not None and 'data_child' not in st.session_state:
            bar_child = st.progress(0)
            df_child = []
            placeholder = st.empty()
            placeholder.success(tmp.name + ' 데이터 읽는 중...')

            if tmp.name.split('.')[-1] == 'dbf':
                try:
                    s = str(tmp.getvalue()[120:], 'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    df_child.append(df)
                    st.session_state.data_child = pd.concat(df_child, axis=0, ignore_index=True)
                    del df_child
                    placeholder.success('유아 데이터 읽기 완료')

                except UnicodeDecodeError as e:
                    warns = st.empty()
                    warns.warning('데이터 구성 형식이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램을 종료합니다.')
                    st.stop()
            else:
                warns = st.empty()
                warns.warning(tmp.name + ' 파일은 dbf 확장자가 아니므로 제외됩니다.')

        st.write('서울시 고령 데이터')
        tmp = st.file_uploader('Please choose a file.', accept_multiple_files=False, type='dbf', key='3')
        if tmp is not None and 'data_elder' not in st.session_state:
            bar_elder = st.progress(0)
            df_elder = []
            placeholder = st.empty()
            placeholder.success(tmp.name + ' 데이터 읽는 중...')

            if tmp.name.split('.')[-1] == 'dbf':
                try:
                    s = str(tmp.getvalue()[120:], 'utf-8')
                    s = ' '.join(s.split())
                    txt_list = s.split(' ')
                    df = make_life(txt_list)
                    df_elder.append(df)
                    st.session_state.data_elder = pd.concat(df_elder, ignore_index=True)

                    placeholder.success('고령 데이터 읽기 완료')
                    del df_elder

                except UnicodeDecodeError as e:
                    warns = st.empty()
                    warns.warning('데이터 구성 형식이 올바르지 않습니다. 새로고침 후 올바른 데이터를 입력해주세요. 프로그램을 종료합니다.')
                    st.stop()
            else:
                warns = st.empty()
                warns.warning(tmp.name + ' 파일은 dbf 확장자가 아니므로 제외됩니다.')

        if 'dataset' in st.session_state and 'data_tot' in st.session_state and 'data_child' in st.session_state and 'data_elder' in st.session_state:
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

                st.session_state.sido_df = make_tot_sido(st.session_state.data_tot, st.session_state.data_child, st.session_state.data_elder)

                st.session_state.results, st.session_state.time_nm, st.session_state.df_list = run_people(st.session_state.dataset, st.session_state.base_grid, st.session_state.seoul_grid, st.session_state.sido_df)

                st.session_state.libraries = []
                st.session_state.images = []
                st.session_state.levels = []
                st.session_state.filenames = []
                st.session_state.sub_headers = []
                st.session_state.save_path = server_dir

                st.session_state.time_eng = {1: 'morning', 2: 'afternoon', 3: 'dinner', 4: 'nighttime'}
                day_eng = {'평일':'week', '주말':'weekend'}

                for res, day, day_kor in zip(st.session_state.results, day_eng.values(),day_eng):
                    for times in range(1,len(st.session_state.time_nm)+1):
                        # Define filename
                        save_file = st.session_state.category_eng + '_' + st.session_state.m+'_'+ day + '_' + st.session_state.time_eng[times]
                        st.session_state.library, st.session_state.level = save_and_processing(
                            st.session_state.save_path, st.session_state.grid, res,
                            st.session_state.category, save_file)
                        st.session_state.img_filename = 'grid_' + save_file + '.png'
                        st.session_state.img = Image.open(st.session_state.save_path + st.session_state.img_filename)

                        st.session_state.libraries.append(st.session_state.library)
                        st.session_state.levels.append(st.session_state.level)
                        st.session_state.images.append(st.session_state.img)
                        st.session_state.filenames.append(save_file)
                        st.session_state.sub_headers.append(day_kor+' '+st.session_state.time_nm[times])

            if 'images' in st.session_state and 'libraries' in st.session_state and 'levels' in st.session_state:
                for f_name, level, library, img, sub_header in zip(st.session_state.filenames, st.session_state.levels,
                                                  st.session_state.libraries, st.session_state.images,st.session_state.sub_headers):
                    st.header(sub_header)
                    show_button(st.session_state.save_path, level, img, library, f_name, 'grid_'+f_name+'.png')

    elif c_idx == 2:
        st.session_state.category = '도로'
        st.session_state.category_eng = 'road'

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
                del df

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

                st.session_state.save_path = server_dir
                if not os.path.isdir(st.session_state.save_path):
                    save_warns = st.empty()
                    save_warns.warning('저장 경로가 존재하지 않습니다. 관리자에게 문의하세요.')

                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,
                                                                                        st.session_state.grid,
                                                                                        st.session_state.df,
                                                                                        st.session_state.category,
                                                                                        st.session_state.category_eng)
                st.session_state.img_filename = 'grid_' + st.session_state.category_eng + '.png'
                st.session_state.img = Image.open(st.session_state.save_path + st.session_state.img_filename)

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                st.header(st.session_state.category)
                show_button(st.session_state.save_path, st.session_state.levels,st.session_state.img,
                            st.session_state.library, st.session_state.category_eng, st.session_state.img_filename)

    elif c_idx == 3:
        st.session_state.category = '농업'
        st.session_state.category_eng = 'farm'

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
                st.session_state.grid, st.session_state.ndra = grid_ndra(grid_path, ndra_path)
                st.session_state.ndra['prop'] += 1
                st.session_state.ndra = st.session_state.ndra.rename(columns={'prop': 'prop_ndra'})

                placeholder = st.empty()
                placeholder.success('전국격자지도 X 농업 격자 데이터...')
                st.session_state.arch_overlay = gpd.overlay(st.session_state.grid, st.session_state.arch, how = 'intersection')

                st.session_state.df = make_arch(st.session_state.arch_overlay, st.session_state.grid_ndra)
                st.session_state.save_path = server_dir
                if not os.path.isdir(st.session_state.save_path):
                    save_warns = st.empty()
                    save_warns.warning('저장 경로가 존재하지 않습니다. 관리자에게 문의하세요.')

                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,
                                                                                        st.session_state.grid,
                                                                                        st.session_state.df,
                                                                                        st.session_state.category,
                                                                                        st.session_state.category_eng)
                st.session_state.img_filename = 'grid_' + st.session_state.category_eng + '.png'
                st.session_state.img = Image.open(st.session_state.save_path + st.session_state.img_filename)

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                st.header(st.session_state.category)
                show_button(st.session_state.save_path, st.session_state.levels, st.session_state.img,
                            st.session_state.library, st.session_state.category_eng, st.session_state.img_filename)

    elif c_idx == 4:
        st.session_state.category = '시설'
        st.markdown('시설은 **공용, 공업, 교육연구, 의료복지, 편의** 총 **5개의 카테고리**로 이뤄져있습니다.', unsafe_allow_html=False)
        st.write('공통적으로 전국격자지도가 필요하여 데이터를 먼저 읽습니다.')
        st.session_state.c_list = ['공업','공용','교육연구','의료복지','편의']
        st.session_state.c_eng_list = ['indust','public','edu','medi','convin']
        st.session_state.c_list.sort()
        if 'grid' not in st.session_state:
            root_path = str(Path(__file__).parent)+'/dataset/'
            grid_path = root_path + 'grid_test.shp'
            ndra_path = root_path + '자연재해위험지구.shp'

            placeholder = st.empty()
            st.session_state.grid, st.session_state.ndra = grid_ndra(grid_path, ndra_path)
            st.session_state.ndra['prop'] += 1
            st.session_state.ndra = st.session_state.ndra.rename(columns={'prop': 'prop_ndra'})

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
            sub_ceng = st.session_state.c_eng_list[sub_cidx]

            st.session_state.save_path = server_dir
            st.session_state.sub_category = sub_category
            st.session_state.sub_cidx = sub_cidx
            st.session_state.sub_c_eng = sub_ceng
            st.session_state.df = run_facil(st.session_state.sub_category, st.session_state.buld,
                                            st.session_state.list_name, st.session_state.grid,st.session_state.ndra)

            st.session_state.save_path = server_dir
            if not os.path.isdir(st.session_state.save_path):
                save_warns = st.empty()
                save_warns.warning('저장 경로가 존재하지 않습니다. 관리자에게 문의하세요.')

            st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,
                                                                                    st.session_state.grid,
                                                                                    st.session_state.df,
                                                                                    st.session_state.sub_category,                                                                                    st.session_state.sub_c_eng)
            st.session_state.img_filename = 'grid_' + st.session_state.sub_c_eng + '.png'
            st.session_state.img = Image.open(st.session_state.save_path + st.session_state.img_filename)

        if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
            st.header(st.session_state.sub_category)
            show_button(st.session_state.save_path, st.session_state.levels, st.session_state.img,
                        st.session_state.library, st.session_state.sub_c_eng, st.session_state.img_filename)

    elif c_idx == 5:
        st.session_state.category = '축산'
        st.session_state.category_eng = 'listock'
        list_dict = {'11000':'서울특별시', '36000':'세종특별자치시', '30000':'대전광역시',
                     '29000':'광주광역시', '26000':'부산광역시', '27000':'대구광역시',
                     '31000': '울산광역시', '28000':'인천광역시', '50000':'제주특별자치도',
                     '46000':'전라남도', '45000':'전라북도', '44000':'충청남도',
                     '43000':'충청북도', '41000':'경기도', '42000':'강원도',
                     '48000':'경상남도', '47000':'경상북도'}

        st.write('축산 데이터')
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
            ndra_path = root_path + '자연재해위험지구.shp'

            placeholder = st.empty()
            st.session_state.grid, st.session_state.ndra = grid_ndra(grid_path, ndra_path)
            st.session_state.ndra['prop'] += 1
            st.session_state.ndra = st.session_state.ndra.rename(columns={'prop': 'prop_ndra'})

            placeholder.success('전국격자지도 read 완료')

            if 'levels' not in st.session_state:
                placeholder = st.empty()
                placeholder.success('전국격자지도 읽는 중 ...')
                st.session_state.grid = gpd.read_file(grid_path,encoding='cp949').to_crs(epsg=5179)
                placeholder.success('전국격자지도 read 완료')

                st.session_state.farm, st.session_state.emd = make_buld_emd(st.session_state.buld, st.session_state.emd, st.session_state.grid, st.session_state.list_name)
                st.session_state.df = run_livestock(st.session_state.livestock, st.session_state.emd, st.session_state.farm,st.session_state.ndra)

                st.session_state.save_path = server_dir
                if not os.path.isdir(st.session_state.save_path):
                    save_warns = st.empty()
                    save_warns.warning('저장 경로가 존재하지 않습니다. 관리자에게 문의하세요.')

                st.session_state.library, st.session_state.levels = save_and_processing(st.session_state.save_path,
                                                                                        st.session_state.grid,
                                                                                        st.session_state.df,
                                                                                        st.session_state.category,
                                                                                        st.session_state.category_eng)
                st.session_state.img_filename = 'grid_' + st.session_state.category_eng + '.png'
                st.session_state.img = Image.open(st.session_state.save_path + st.session_state.img_filename)

            if 'img' in st.session_state and 'library' in st.session_state and 'levels' in st.session_state:
                st.header(st.session_state.category)
                show_button(st.session_state.save_path, st.session_state.levels, st.session_state.img,
                            st.session_state.library, st.session_state.category_eng, st.session_state.img_filename)










