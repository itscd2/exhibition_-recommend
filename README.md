# exhibition-recommend


### 跑推薦需要的檔案
```
──── main.py #介紹使用
│
──── manip_data.py #整理資料用
│
──── recommend.py # 推薦用
│
──── ./semi_data
│
│──── recom_dict_yyyymmdd-hhMMss.pkl # 存下面三個路徑
│──── tfidf_dict.pkl #斷好的詞庫
│──── tfidf_mtx.pkl #矩陣
│──── main_token_ls.pkl #main item token(主要被推薦的文本斷詞)
│──── tfidf_mainidx.npy #main item idx(主要被推薦的index)
│
──── ./analysis_data
│──── tech_list.csv #main item list (技術清單)
│
```

### Usage

```
# as main.py
# 讀取檔案
tfidf_fp = pickle.load(open('./semi_data/recom_dict_20220908-231214.pkl', 'rb'))

# ex:target_str
# 輸入要待推薦的文本 須為段好的詞 string 
# target_str 會放 user的技術足跡,

# ex: target_str_2
# 用 get_tech_token_by_id() 取得斷好詞的 string 放入
# 再將技術足跡的 id 放入下面的 exclude_ids

target_str= '專利 技術 監測 系統 智慧照顧 醫療人員 專利 人員 醫療'

target_str_2=get_tech_token_by_id('90')

#要排除的 tech id list
exclude_ids=['90']

# 推薦數量
recom_num = 5
out_1 = get_recom_result(tfidf_fp, target_str, recom_num)
out_2 = get_recom_result(tfidf_fp, target_str_2, recom_num, exclude_ids)

print(out_1)
['92', '95', '96', '98', '99'] #推薦技術的id

print(out_2)
['91', '94', '99', '102', '111']

```
