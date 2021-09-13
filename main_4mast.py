# -*- coding: utf-8 -*-
"""
@author: luqi
@Created on： 2020.3.9
@instruction：
@Version update log: 该脚本处理4塔综合的情况
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
filenames = ['mast1_result.csv', 'mast2_result.csv', 'mast3_result.csv', 'mast4_result.csv', 'mast_info.csv']
sav_path = 'output'
factor = 2  # 权重计算方法，默认2就是距离的平方权重，修改为1就是距离权重
tur_id_list = ' Site ID '  # 指定风机id编号列名称
mast_id_list = 'LABEL'  # 指定测风塔id编号列名称
x_list = ' X [m] '
y_list = ' Y [m] '
C = [1, 1, 1, 1]  # 两座测风塔置信系数，默认置信系数均为1

# 1. 读取计算结果
mast1_result = pd.read_csv(os.path.join(filepath, filenames[0]), index_col=tur_id_list, encoding='gbk')
mast2_result = pd.read_csv(os.path.join(filepath, filenames[1]), index_col=tur_id_list, encoding='gbk')
mast3_result = pd.read_csv(os.path.join(filepath, filenames[2]), index_col=tur_id_list, encoding='gbk')
mast4_result = pd.read_csv(os.path.join(filepath, filenames[3]), index_col=tur_id_list, encoding='gbk')
mast_info = pd.read_csv(os.path.join(filepath, filenames[4]), index_col=mast_id_list, encoding='gbk')

# 2. 计算风机机位点与对应测风点距离，其中机位坐标点在各个计算结果里都是一致的
mast1_result.loc[:, 'distance'] = (((mast1_result[x_list] - mast_info.iloc[0][0]) ** 2 + (
        mast1_result[y_list] - mast_info.iloc[0][1]) ** 2) ** 0.5).round(2)
mast2_result.loc[:, 'distance'] = (((mast1_result[x_list] - mast_info.iloc[1][0]) ** 2 + (
        mast1_result[y_list] - mast_info.iloc[1][1]) ** 2) ** 0.5).round(2)
mast3_result.loc[:, 'distance'] = (((mast1_result[x_list] - mast_info.iloc[2][0]) ** 2 + (
        mast1_result[y_list] - mast_info.iloc[2][1]) ** 2) ** 0.5).round(2)
mast4_result.loc[:, 'distance'] = (((mast1_result[x_list] - mast_info.iloc[3][0]) ** 2 + (
        mast1_result[y_list] - mast_info.iloc[3][1]) ** 2) ** 0.5).round(2)
multi_mast_result1 = mast1_result.merge(mast2_result, how='inner', left_index=True, right_index=True,
                                        suffixes=('_Mast1', '_Mast2'))
multi_mast_result2 = mast3_result.merge(mast4_result, how='inner', left_index=True, right_index=True,
                                        suffixes=('_Mast3', '_Mast4'))
multi_mast_result = multi_mast_result1.merge(multi_mast_result2, how='inner', left_index=True, right_index=True)

# 3. 权重系数计算，方法参考WT
a1 = C[0] / (multi_mast_result['distance_Mast1'] ** factor + 1)
a2 = C[1] / (multi_mast_result['distance_Mast2'] ** factor + 1)
a3 = C[2] / (multi_mast_result['distance_Mast3'] ** factor + 1)
a4 = C[3] / (multi_mast_result['distance_Mast4'] ** factor + 1)
multi_mast_result.loc[:, 'Mast1_Weight'] = a1 / (a1 + a2 + a3 + a4)
multi_mast_result.loc[:, 'Mast2_Weight'] = a2 / (a1 + a2 + a3 + a4)
multi_mast_result.loc[:, 'Mast3_Weight'] = a3 / (a1 + a2 + a3 + a4)
multi_mast_result.loc[:, 'Mast4_Weight'] = a4 / (a1 + a2 + a3 + a4)

# 4. 计算最终多塔综合结果
multi_mast_result['U_multi'] = multi_mast_result['U_Mast1'] * multi_mast_result['Mast1_Weight'] + \
                               multi_mast_result['U_Mast2'] * multi_mast_result['Mast2_Weight'] + \
                               multi_mast_result['U_Mast3'] * multi_mast_result['Mast3_Weight'] + \
                               multi_mast_result['U_Mast4'] * multi_mast_result['Mast4_Weight']

multi_mast_result['U(w)_multi'] = multi_mast_result['U(w)_Mast1'] * multi_mast_result['Mast1_Weight'] + \
                                  multi_mast_result['U(w)_Mast2'] * multi_mast_result['Mast2_Weight'] + \
                                  multi_mast_result['U(w)_Mast3'] * multi_mast_result['Mast3_Weight'] + \
                                  multi_mast_result['U(w)_Mast4'] * multi_mast_result['Mast4_Weight']

multi_mast_result['Grs_multi'] = multi_mast_result['Grs_Mast1'] * multi_mast_result['Mast1_Weight'] + \
                                 multi_mast_result['Grs_Mast2'] * multi_mast_result['Mast2_Weight'] + \
                                 multi_mast_result['Grs_Mast3'] * multi_mast_result['Mast3_Weight'] + \
                                 multi_mast_result['Grs_Mast4'] * multi_mast_result['Mast4_Weight']

multi_mast_result['Net_multi'] = multi_mast_result['Net_Mast1'] * multi_mast_result['Mast1_Weight'] + \
                                 multi_mast_result['Net_Mast2'] * multi_mast_result['Mast2_Weight'] + \
                                 multi_mast_result['Net_Mast3'] * multi_mast_result['Mast3_Weight'] + \
                                 multi_mast_result['Net_Mast4'] * multi_mast_result['Mast4_Weight']

multi_mast_result['Wk_multi'] = (1 - multi_mast_result['Net_multi'] / multi_mast_result['Grs_multi']) * 100

multi_mast_result[['U_multi', 'U(w)_multi', 'Grs_multi', 'Net_multi', 'Wk_multi']].to_csv(
    os.path.join(sav_path, '双塔综合结论[距离权重{}]_{}.csv'.format(factor, time)), encoding='gbk')

end = timeit.default_timer()
print('Running machine time: %s Seconds' % (end - start))
print('\n Operation complete！')
