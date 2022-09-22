import pickle
from recommend import get_recom_result
from manip_data import get_tech_token_by_id

def run_recommend():
    tfidf_fp = pickle.load(open('./semi_data/recom_dict_20220922-103812.pkl', 'rb'))

    #輸入要待推薦的文本 須為段好的詞 string
    #target_str 會放user的技術足跡,
    # 用 get_tech_token_by_id() 取得斷好詞的 string 放入
    # 要將技術足跡的 id 放入下面的 exclude_ids

    target_str= '專利 技術 監測 系統 智慧照顧 醫療人員 專利 人員 醫療'

    target_str_2=get_tech_token_by_id('5100')

    #要排除的 tech id list
    exclude_ids=['5100']

    out_1 = get_recom_result(tfidf_fp, target_str, 5)
    out_2 = get_recom_result(tfidf_fp, target_str_2, 5, exclude_ids)

    print(out_1)
    print(out_2)

if __name__ == '__main__':
    run_recommend()


