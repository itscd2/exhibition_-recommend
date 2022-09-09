import pickle
from configparser import ConfigParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import numpy as np
import jieba
import time
import manip_data

#------設定值--------#
config = ConfigParser()
config.read('./setting.cfg')
recom_corpus_file_path = config.get('file_path','recom_corpus')
techs_file_path = config.get('file_path','techs')

ref_item = 'company'
main_item = 'tech' #推薦item

def trim_all_columns(df):
    """
    Trim whitespace from ends of each value across all series in dataframe
    Arguments:
        df: dataframe
    Returns:
        dataframe
    """
    trim_strings = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trim_strings)

def gen_tfidf_mt(sw_path, cut_corpus, main_idx, output_name = 'tfidf'):
    """
    產生 tfidf matrix (建立dict)
    Arguments:
        sw_path: path of stopwords
        cut_corpus:['term term term .....']
        main_idx:被推薦的 index list
        output_name: 輸出檔名
    Returns:
        {'dict':file_path_dict,'mtx':file_path_mtx}
        'dict':dict 的檔案路徑
        'mtx': tfidf matrix 檔案路徑
        放在 semi_data 資料夾內
    """
    with open(sw_path, encoding='utf-8') as f:
        stop_word = f.read()
    sw = stop_word.split('\n')
    tfidf_v = TfidfVectorizer(stop_words=sw)
    tfidf_matrix = tfidf_v.fit_transform(cut_corpus)

    file_path_dict = "".join (['./semi_data/',output_name, '_dict.pkl'])
    file_path_mtx = "".join (['./semi_data/',output_name, '_mtx.pkl'])
    pickle.dump(tfidf_v, open(file_path_dict, "wb"))
    pickle.dump(tfidf_matrix, open(file_path_mtx, "wb"))

    file_path_mainidx_list = "".join (['./semi_data/',output_name, '_mainidx.npy'])
    np.save(file_path_mainidx_list, main_idx)

    return {'dict':file_path_dict,'mtx':file_path_mtx, 'main_idx':file_path_mainidx_list}

def gen_sim_order(sim_slice):
    """
    將 similarity list 回傳相似度分數高->低的index
    """
    order_list=[i[0] for i in sorted(enumerate(sim_slice), key=lambda x:x[1])]
    return order_list

def get_recom_result(tfidf_fp, target_str, recom_num, exclude_mainid_ls=[]):
    """
    取得推薦的結果
    Arguments:
        tfidf_fp: dict- {'dict':檔案路徑, 'mtx':檔案路徑, 'main_idx':推薦item的index}
                  這個 dict 用 gen_tfidf_mt() 產生, 存成檔案 semi_data/recom_dict_xxxx.pkl 用讀的
        target_str: 'term term ...' 目標要被推薦的文本 已斷好的詞
        recom_num: int 推薦數量
        exclude_mainid_ls: [] 要被排除的 main id list
    Returns:
        推薦item的 id list
    """
    tf_dict = pickle.load(open(tfidf_fp['dict'], 'rb'))# 詞庫
    tf_mtx = pickle.load(open(tfidf_fp['mtx'], 'rb'))# 矩陣
    main_idx = np.load(tfidf_fp['main_idx']).tolist()#tech idx

    # Create new tfidfVectorizer with old vocabulary
    tf_vec = TfidfVectorizer(vocabulary = tf_dict.vocabulary_)
    target_list = [target_str]
    tf_fit_matrix = tf_vec.fit_transform(target_list)

    cosine_sim = linear_kernel(tf_mtx, tf_fit_matrix)

    recom_result = list(map(gen_sim_order, cosine_sim.transpose()))
    recom_result.reverse() # 因index 0 的 item 會被推到最後一個, 要倒過來

    recom_result_new = []
    for re in recom_result:
        add = [r for r in re if r in main_idx] #只要技術 別的不要
        id = [manip_data.get_tech_id_by_idx(idx) for idx in add] #用idx換成tech id
        id_save = [i for i in id if i not in exclude_mainid_ls] #排除 tech_id

        recom_result_new.append(id_save)

    output = [ i[0:recom_num] if len(i)>recom_num else i[0:len(i)] for i in recom_result_new][0]
    return output


def generate_semi_data():
    """
    需預先跑的 generate semi data function
    """
    df = pd.read_csv(recom_corpus_file_path, dtype={'id':str})
    new_df = df.dropna(subset='id')
    input_data = trim_all_columns(df)

    collect_corpus = input_data["content"].tolist()

    ref_ids = input_data.index[input_data["cate"] == ref_item].tolist()#以ref_ids推薦main_ids
    main_ids = input_data.index[input_data["cate"] == main_item].tolist()

    ### step 1: 斷詞
    # 載入詞庫
    jieba.set_dictionary(r'./dict/dict.txt.big') #使用繁中詞庫
    jieba.load_userdict(r'./dict/itri.dict.txt.big')  #使用院內技術詞詞庫
    jieba.load_userdict(r'./dict/userdict.txt') #載入自定義辭庫

    #斷詞
    start_time = time.time()
    word_segment = list(map(lambda x: jieba.lcut(x), collect_corpus))
    end_time = time.time()
    print("word_segment:", end_time-start_time)
    #去除空白字串+把斷詞串起來
    word_segment = [list(filter(str.strip, i))for i in word_segment] # 去除空白字串
    cut_corpus = [' '.join(i) for i in word_segment]
    #把斷好的技術存起來
    tech_tokenize =[{'main_id':manip_data.get_tech_id_by_idx(idx),'token':cut_corpus[i]} for idx,i in enumerate(main_ids)]
    fp_main_token = "".join (['./semi_data/main_token_ls.pkl'])
    pickle.dump(tech_tokenize, open(fp_main_token, "wb"))

    ### step 2: 建立詞庫&矩陣
    tfidf_fp= gen_tfidf_mt('./dict/stop_word.txt', cut_corpus, main_ids, output_name = 'tfidf')
    ### step 3: save
    timestr = time.strftime("%Y%m%d-%H%M%S")
    fp_recom_dict = "".join (['./semi_data/recom_dict_',timestr, '.pkl'])
    pickle.dump(tfidf_fp, open(fp_recom_dict, "wb"))



