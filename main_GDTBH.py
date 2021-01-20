# -*- coding: utf-8 -*-
"""
@author: luqi
@Created on： 2020.3.9
@instruction：
@Version update log: 该脚本暂时只能处理两塔综合的情况
"""

import os
import datetime
import timeit
import warnings
import pandas as pd

start = timeit.default_timer()
warnings.filterwarnings('ignore')
time = datetime.datetime.now().strftime('%Y%m%d-%H%M')

filepath = r'D:\luqid\Pyproject\WAsP_multimast_AEP_calculator\input'
filenames = ['mast1_result.csv', 'mast2_result.csv', 'mast_info.csv']  # 文件顺序：先单塔综合结果输出，再测风塔坐标，测风塔坐标先后顺序与输出文件先后一致
sav_path = 'output'
factor = 2  # 权重计算方法，默认2就是距离的平方权重，修改为1就是距离权重
tur_id_list = ' Site ID '  # 指定风机id编号列名称
mast_id_list = 'LABEL'  # 指定测风塔id编号列名称
x_list = ' X [m] '
y_list = ' Y [m] '
C = [1, 1]  # 两座测风塔置信系数，默认置信系数均为1

mast1_result = pd.read_csv(os.path.join(filepath, filenames[0]), index_col=tur_id_list, encoding='gbk')
mast2_result = pd.read_csv(os.path.join(filepath, filenames[1]), index_col=tur_id_list, encoding='gbk')
mast_info = pd.read_csv(os.path.join(filepath, filenames[2]), index_col=mast_id_list, encoding='gbk')

mast1_result.loc[:, 'distance'] = (((mast1_result[x_list] - mast_info.iloc[0][0]) ** 2 + (
        mast1_result[y_list] - mast_info.iloc[0][1]) ** 2) ** 0.5).round(2)
mast2_result.loc[:, 'distance'] = (((mast1_result[x_list] - mast_info.iloc[1][0]) ** 2 + (
        mast1_result[y_list] - mast_info.iloc[1][1]) ** 2) ** 0.5).round(2)
multi_mast_result = mast1_result.merge(mast2_result, how='inner', left_index=True, right_index=True,
                                       suffixes=('_Mast1', '_Mast2'))
a1 = C[0] / (multi_mast_result['distance_Mast1'] ** factor + 1)
a2 = C[1] / (multi_mast_result['distance_Mast2'] ** factor + 1)
multi_mast_result.loc[:, 'Mast1_Weight'] = a1 / (a1 + a2)
multi_mast_result.loc[:, 'Mast2_Weight'] = a2 / (a1 + a2)

multi_mast_result['U_multi'] = multi_mast_result['U_Mast1'] * multi_mast_result['Mast1_Weight'] + multi_mast_result[
    'U_Mast2'] * multi_mast_result['Mast2_Weight']
multi_mast_result['U(w)_multi'] = multi_mast_result['U(w)_Mast1'] * multi_mast_result['Mast1_Weight'] + \
                                  multi_mast_result['U(w)_Mast2'] * multi_mast_result['Mast2_Weight']
multi_mast_result['Grs_multi'] = multi_mast_result['Grs_Mast1'] * multi_mast_result['Mast1_Weight'] + multi_mast_result[
    'Grs_Mast2'] * multi_mast_result['Mast2_Weight']
multi_mast_result['Net_multi'] = multi_mast_result['Net_Mast1'] * multi_mast_result['Mast1_Weight'] + multi_mast_result[
    'Net_Mast2'] * multi_mast_result['Mast2_Weight']
multi_mast_result['Wk_multi'] = (1 - multi_mast_result['Net_multi'] / multi_mast_result['Grs_multi']) * 100

multi_mast_result[['U_multi', 'U(w)_multi', 'Grs_multi', 'Net_multi', 'Wk_multi']].to_csv(
    os.path.join(sav_path, '双塔综合结论[距离权重{}]_{}.csv'.format(factor, time)), encoding='gbk')

end = timeit.default_timer()
print('Running machine time: %s Seconds' % (end - start))
print('\n Operation complete！')
