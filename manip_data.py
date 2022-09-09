from configparser import ConfigParser

import pandas as pd
import csv
import pickle

config = ConfigParser()
config.read('./setting.cfg')
techs_file_path = config.get('file_path','techs')
recom_corpus_file_path = config.get('file_path','recom_corpus')

"""
把原始的展場技術列表, 轉換成跑推薦input資料
"""
def load_initial_data2_input(xlsx_fp_tech, xlsx_fp_com, col=''):
    ### 載入技術資料
    # 編號欄位 # 技術名稱欄位 # 技術文本欄位 的位置 (技術文本有多個欄位要合併)
    id_col,name_col,c_col_1,c_col_2,c_col_3=0,1,1,2,3

    t_df = pd.read_excel(xlsx_fp_tech, usecols=col, converters = {id_col:txt_2_str}) #用converters好處是可以用欄位號, 用dtype需用欄位名
    t_df = t_df.fillna(0)
    # 拼裝 文本(content)要的欄位
    t_df['content'] = t_df[t_df.columns[c_col_1]].astype(str) +','\
                    + t_df[t_df.columns[c_col_2]].astype(str)+','+ \
                      t_df[t_df.columns[c_col_3]].astype(str)

    corpus_df = pd.DataFrame({'id':t_df.iloc[:,id_col], 'content':t_df['content'], 'cate':'tech'})
    tech_list_df = pd.DataFrame({'id':t_df.iloc[:,id_col], 'tech_name':t_df.iloc[:,name_col]})

    # 拿掉 na 被取代成0 的 row
    corpus_df = corpus_df.drop(corpus_df[corpus_df.id ==0].index)
    tech_list_df = tech_list_df.drop(corpus_df[corpus_df.id ==0].index)

    ### 載入廠商資料
    # 編號欄位 # 技術名稱欄位 # 技術文本欄位 的位置
    id_col,name_col,c_col_1=0,1,2
    com_df = pd.read_excel(xlsx_fp_com, converters = {id_col:txt_2_str})
    corpus_com_df = pd.DataFrame({'id':com_df.iloc[:,id_col], 'content':com_df.iloc[:,c_col_1], 'cate':'company'})

    ### 合併
    output_df = pd.concat([corpus_df, corpus_com_df],axis=0, ignore_index=True)

    output_path_dict = techs_file_path
    output_path_corpus = recom_corpus_file_path

    output_df.to_csv(output_path_corpus,index=False)
    tech_list_df.to_csv(output_path_dict,index=False)

"""
用技術id換技術名稱
"""
def get_tech_name_by_id(tech_id):
    tech_dict_path = techs_file_path
    key_list, value_list=[],[]
    with open(tech_dict_path) as csvfile:
        techs_reader = csv.DictReader(csvfile)
        for tech in techs_reader:
            key_list.append(tech['id'])
            value_list.append(tech['tech_name'])
    techs_dict = {k: v for k, v in zip(key_list, value_list)}
    if (tech_id in techs_dict.keys()):
        return techs_dict.get(tech_id)
    else:
        return None

"""
用技術 index 換技術 id
"""
def get_tech_id_by_idx(tech_idx):
    tech_dict_path = techs_file_path
    key_list, value_list=[],[]
    with open(tech_dict_path) as csvfile:
        techs_reader = csv.DictReader(csvfile)
        for tech in techs_reader:
            key_list.append(tech['id'])
            value_list.append(tech['tech_name'])
    techs_dict = {k: v for k, v in zip(key_list, value_list)}
    try:
        tech_id = list(techs_dict.items())[tech_idx][0]
        return tech_id
    except IndexError:
        return None

def txt_2_str(col_txt):
    return str(col_txt)

def get_tech_token_by_id(tech_id):
    main_token_ls = pickle.load(open('./semi_data/main_token_ls.pkl', 'rb'))
    main_ids = [i['main_id'] for i in main_token_ls]
    main_tokens = [i['token'] for i in main_token_ls]
    token_dict = {k: v for k, v in zip(main_ids, main_tokens)}
    if (tech_id in token_dict.keys()):
        return token_dict.get(tech_id)
    else:
        return None




# 提供原始的 公司& 技術清單, 轉換到
xlsx_file_path= './original_data/參展技術清單1202.xlsx'
xlsx_file_path= './original_data/參展技術清單_50.xlsx'


xlsx_fp_com='./original_data/all_data_new_202007.xlsx'
xlsx_fp_com='./original_data/all_data_new_10.xlsx'

#load_initial_data2_input(xlsx_file_path,xlsx_fp_com,col='A,B,H,X')

#tech_name = get_tech_name_by_id('1.0')
