######################################################
#    file name    : industrial_code.py
#    author       : Yubin Lee
#    written date : Feb.13.2023
#    parameter    : None
#    description  : preprocess 
######################################################

import xlrd
import numpy as np
import pandas as pd
import geopandas as gpd
import mapclassify as mc
import matplotlib.pyplot as plt


# 지도 만들기 위한 한글 폰트 지정
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['figure.figsize'] = (10, 10)

# 작업 경로 설정
file_path = 'file_path/'
file_path_date = file_path + '0226/' # (***날짜 폴더명 변경 필요***)
code_save_name = '14499포함' #(*** 변경 필요***)

# 사업체조사결과 raw data 불러오기(미리 csv 파일로 변환)
df_2010 = pd.read_csv(file_path + '원본/2010년 서울시 사업체조사결과.csv')
df_2015 = pd.read_csv(file_path + '원본/2015년 서울시 사업체조사결과.csv')
df_2020 = pd.read_csv(file_path + '원본/2020사업체조사결과_1.csv')

# 년도별 행정동 코드 및 이름 리스트 불러오기
df_2010_name = pd.read_csv(file_path + '0222/2010코드.csv', encoding='euc-kr')
df_2015_name = pd.read_csv(file_path + '0222/2015코드.csv', encoding='euc-kr')
df_2020_name = pd.read_csv(file_path + '0222/2020코드.csv', encoding='euc-kr')

# 사업체조사결과에 행정동 코드를 기준으로 행정동명 조인
df_2010_join = df_2010.join(df_2010_name.set_index('코드')['행정동명'], on='ZONE_DONG')
df_2015_join = df_2015.join(df_2015_name.set_index('코드')['행정동명'], on='AD_CD')
df_2020_join = df_2020.join(df_2020_name.set_index('코드')['행정동명'], on='AD_CD')


# 코드, 1인 사업체, 종업원 5인 이하 조건으로 추출 (***코드 변경 필요***)
indst_cd_2010 = [14499, 15121, 15129, 16292, 16293, 32022, 33110, 33120, 33401]
indst_cd_2020 = [14499, 15121, 15129, 16291, 16292, 33110, 33120, 33401]

df_2010_ext = df_2010_join[df_2010_join['SN_SESE'].isin(indst_cd_2010)]
df_2010_ext = df_2010_ext.loc[(df_2010_ext['JOSIC'] == 1) & (df_2010_ext['EMP_TO_T'] <= 5)]

df_2015_ext = df_2015_join[df_2015_join['MBZ_INDST_CLS_CD'].isin(indst_cd_2010)]
df_2015_ext = df_2015_ext.loc[(df_2015_ext['ORGFM_DIV_CD'] == 1) & (df_2015_ext['WOKE_ALL_SUM'] <= 5)]

df_2020_ext = df_2020_join[df_2020_join['MBZ_INDST_CLS_CD'].isin(indst_cd_2020)]
df_2020_ext = df_2020_ext.loc[(df_2020_ext['ORGFM_DIV_CD'] == 1) & (df_2020_ext['WOKE_ALL_SUM'] <= 5)]

# 추출한 결과 csv 파일로 저장 os.path.join(file_path_date, code_save_name)
df_2010_ext.to_csv(file_path_date + code_save_name + '_2010_사업체.csv', encoding='euc-kr', index=False)
df_2015_ext.to_csv(file_path_date + code_save_name + '_2015_사업체.csv', encoding='euc-kr', index=False)
df_2020_ext.to_csv(file_path_date + code_save_name + '_2020_사업체.csv', encoding='euc-kr', index=False)

# 피벗 테이블 생성 및 저장
pv_2010 = pd.pivot_table(df_2010_ext, index='행정동명', values='ZONE_DONG', aggfunc='count')
pv_2015 = pd.pivot_table(df_2015_ext, index='행정동명', values='AD_CD', aggfunc='count')
pv_2020 = pd.pivot_table(df_2020_ext, index='행정동명', values='AD_CD', aggfunc='count')

# 피벗 테이블 행정동명 인덱스 리셋
pv_2010 = pv_2010.reset_index()
pv_2015 = pv_2015.reset_index()
pv_2020 = pv_2020.reset_index()

# 피벗 테이블에 행정동명을 기준으로 행정동코드 join
pv_2010 = pv_2010.join(df_2010_name.set_index('행정동명')['행정동코드'], on='행정동명')
pv_2015 = pv_2015.join(df_2015_name.set_index('행정동명')['행정동코드'], on='행정동명')
pv_2020 = pv_2020.join(df_2020_name.set_index('행정동명')['행정동코드'], on='행정동명')

# 피벗 테이블 사업체수 이름 변경
pv_2010 = pv_2010.rename(columns={'ZONE_DONG':'2010사업체수'})
pv_2015 = pv_2015.rename(columns={'AD_CD':'2015사업체수'})
pv_2020 = pv_2020.rename(columns={'AD_CD':'2020사업체수'})

# 피벗 테이블 행정동코드 이름 변경
pv_2010 = pv_2010.rename(columns={'행정동코드':'ADM_DR_CD'})
pv_2015 = pv_2015.rename(columns={'행정동코드':'ADM_DR_CD'})
pv_2020 = pv_2020.rename(columns={'행정동코드':'ADM_DR_CD'})

pv_2010.to_csv(file_path + code_save_name + '_2010_사업체수.csv', encoding='euc-kr', index=False)
pv_2015.to_csv(file_path + code_save_name + '_2015_사업체수.csv', encoding='euc-kr', index=False)
pv_2020.to_csv(file_path + code_save_name + '_2020_사업체수.csv', encoding='euc-kr', index=False)

# shp file 불러오기
seoul_root = file_path + '0222/서울행정동.shp'
seoul = gpd.read_file(seoul_root, encoding='utf-8')

# 행정동코드를 numeric 타입으로 변경
seoul['ADM_DR_CD'] = pd.to_numeric(seoul['ADM_DR_CD'])

# shp 파일에 읍면동 코드를 기준으로 피벗 테이블 조인
seoul_join = pd.merge(seoul, pv_2010, how='left', on='ADM_DR_CD')
seoul_join = pd.merge(seoul_join, pv_2015, how='left', on='ADM_DR_CD')
seoul_join = pd.merge(seoul_join, pv_2020, how='left', on='ADM_DR_CD')

# 필요없는 열 삭제
seoul_join = seoul_join.drop(labels=['행정동명_x', '행정동명_y', '행정동명', 'OBJECTID'], axis=1)

# shp file로 저장 (***코드 변경 필요***)
seoul_join.to_file(file_path_date + code_save_name + ".shp", driver='ESRI Shapefile', encoding='utf-8')

#test_root = file_path_date + code_save_name + '.shp'
#test = gpd.read_file(test_root, encoding='utf-8')
