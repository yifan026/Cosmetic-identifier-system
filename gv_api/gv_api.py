#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2017/9/26 下午 2:40

@author: YFC
"""

import io
from google.cloud import vision
from google.cloud.vision import types
# import re
# import copy
import time
from modules.ToolKit import *
# import Levenshtein
import operator
import pandas as pd
from datetime import datetime
import requests
import json
from base64 import b64encode

isLocalHost = 0
# index_name = 'crawler2_prd'
index_name = kit.config.get('ESdb', 'index')

doct_type = 'Amazon'

es, ho = kit.get_elasticsearch(isLocalHost)

docTypeSelection = [doct_type]

today = datetime.fromtimestamp(datetime.utcnow().timestamp())

now = int((today - datetime(1970, 1, 1)).total_seconds())

client = vision.ImageAnnotatorClient()

result_list_for_web = []
result_title_list = []
result_url_list = []
amazon_pic_list = []

feature_data_dict = {}

tmp_data_dict = {}

result_word_for_web = ''
keyword_text = ''

make_feature = need_to_use = ''

es_title_string = ''

ELASTIC_SEARCH_RANK = 'ES Rank'
LCS = 'LCS'
LEVENSHTEIN = 'LD'
LCS_RANK = 'LCS Rank'
LEVENSHTEIN_RANK = 'LD Rank'
SUBSTRING_RATE = 'STr'
WORD_HIT_RATE = 'WHr'
SUBSTRING_RATE_RANK = 'STr Rank'
WORD_HIT_RATE_RANK = 'WHr Rank'

result_label = []

size = 30
hit_top3_product_count = 0

# ---------可調整的參數------------

TOP_ES_RANK = 30
TOP_N_PRODUCT = 30
STr_rank_range = 30
substring_rate_decision_point = 0.15
word_hit_rate_decision_point = 0.24

# ---------可調整的參數------------

API_key = kit.config.get('google', 'gv_api_key_himirror')
ENDPOINT_URL = kit.config.get('google', 'endpoint_url')


class Get_GV():
    def make_image_data_list(self, image_file_names):
        """
        image_filenames is a list of filename strings
        Returns a list of dicts formatted as the Vision API
            needs them to be
        """
        img_requests = []

        # for img_name in image_file_names:
        with open(image_file_names, 'rb') as f:
            ctxt = b64encode(f.read()).decode()

            img_requests.append({
                'image': {'content': ctxt},
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }, {
                    "type": "LOGO_DETECTION",
                    "maxResults": 1
                }]
            })
            # print(img_requests)
        return json.dumps({"requests": img_requests}).encode()

    def request_ocr(self, image_file_names):
        response = requests.post(ENDPOINT_URL,
                                 data=self.make_image_data_list(image_file_names),
                                 params={'key': API_key},
                                 headers={'Content-Type': 'application/json'})
        return response

    def response_image(self, img_path, type_feature):

        req_body = {
            "requests": [
                {
                    "image": {
                        "source": {
                            "imageUri": img_path
                        }
                    },
                    "features": [
                        {
                            "type": type_feature,
                            "maxResults": 1
                        }
                    ]
                }
            ]
        }

        return req_body

    def load_img_by_path(self, path):
        """load local img file"""

        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

        return content

    def load_img_by_uri(self, uri):
        """load cloud img file"""

        image = types.Image()
        image.source.image_uri = uri

        return image

    def get_data_from_es(self, title_string):
        # que = "Title:" + title_string

        body = {
            "query": {
                "match": {
                    "Title": title_string}

            },

            "_source": ["Title", 'Source_URL', 'Img_URLs'],
            "size": size

        }

        # print(docTypeSelection)

        res = es.search(index=index_name, body=body)

        res_output = res['hits']['hits']

        title_dict = dict()

        for titleDictCount, dict_content in enumerate(res_output):
            title_dict[titleDictCount] = {'Title': dict_content['_source']['Title'],
                                          'SrcURL': dict_content['_source']['Source_URL'],
                                          'ImgURL': dict_content['_source']['Img_URLs']}

        return title_dict

    def lcs_dp(self, x, y):
        # y as column, x as row
        dp = [([0] * len(y)) for i in range(len(x))]
        max_length = max_index = 0
        for i in range(0, len(x)):
            for j in range(0, len(y)):
                if x[i] == y[j]:
                    if i != 0 and j != 0:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                    if i == 0 or j == 0:
                        dp[i][j] = 1
                    if dp[i][j] > max_length:
                        max_length = dp[i][j]
                        max_index = i + 1 - max_length
                        # print('length of LCS :%s' % max_length)
                        # print('substring of LCS :%s' % x[max_index:max_index + max_length])
        return x[max_index:max_index + max_length]

    def method_round(self, num):
        return round(num, 2)

    def except_word_method(self, except_word):
        global result_word_for_web

        result_word_for_web = result_word_for_web + except_word + '<br>'
        print(except_word)

    def re_sub_string(self, text, blank_select=0):
        keyword_after_re = re.sub('[\\\\/\-\':*,?;!%$@"<>|~&()+®.●_]', ' ', text)

        if blank_select == 1:
            text_tmp = ' '.join(keyword_after_re.split())
        else:
            text_tmp = ''.join(keyword_after_re.split(' '))

        text_tmp = text_tmp.lower()

        return text_tmp

    def unzip_dict(self, dict_unzip, ori_text, af_text_with_blank):
        global result_word_for_web
        global result_title_list
        global result_url_list
        global amazon_pic_list
        es_score_dict = copy.deepcopy(dict_unzip)

        {t: r[1].update({LCS: len(self.lcs_dp(self.re_sub_string(r[1]['Title']), ori_text)),
                         SUBSTRING_RATE: self.method_round(
                             len(self.lcs_dp(self.re_sub_string(r[1]['Title']), ori_text)) / len(ori_text)),
                         WORD_HIT_RATE: self.method_round(
                             [k in self.re_sub_string(r[1]['Title'], blank_select=1) for k in
                              af_text_with_blank.split()].count(True) / len(
                                 af_text_with_blank.split()))
                         # ,LEVENSHTEIN: self.method_round(Levenshtein.jaro(self.re_sub_string(r[1]['Title']), ori_text)),
                         }) for t, r in
         enumerate(es_score_dict.items())}

        sorted_dict_by_es = sorted(es_score_dict.items(), key=operator.itemgetter(0))

        {t: r[1].update({ELASTIC_SEARCH_RANK: t}) for t, r in enumerate(sorted_dict_by_es, 1)}

        sorted_dict_by_lcs = sorted(es_score_dict.items(), key=lambda x: x[1][LCS], reverse=True)

        {t: r[1].update({LCS_RANK: t}) for t, r in enumerate(sorted_dict_by_lcs, 1)}

        # sorted_dict_by_levenshtein = sorted(es_score_dict.items(), key=lambda x: x[1][LEVENSHTEIN],
        #                                     reverse=True)

        # {t: r[1].update({LEVENSHTEIN_RANK: t}) for t, r in enumerate(sorted_dict_by_levenshtein, 1)}

        sorted_dict_by_substring_rate = sorted(es_score_dict.items(), key=lambda x: x[1][SUBSTRING_RATE],
                                               reverse=True)

        {t: r[1].update({SUBSTRING_RATE_RANK: t}) for t, r in enumerate(sorted_dict_by_substring_rate, 1)}

        sorted_dict_by_word_hit_rate = sorted(es_score_dict.items(), key=lambda x: x[1][WORD_HIT_RATE],
                                              reverse=True)

        {t: r[1].update({WORD_HIT_RATE_RANK: t}) for t, r in enumerate(sorted_dict_by_word_hit_rate, 1)}

        if [s[1][SUBSTRING_RATE] <= substring_rate_decision_point for s in sorted_dict_by_es].count(True) > 0 and [
            s[1][SUBSTRING_RATE] <= substring_rate_decision_point for s in sorted_dict_by_es].index(
            True) + 1 <= STr_rank_range:
            for str_rank, str_content_dict in enumerate(sorted_dict_by_substring_rate, 1):

                if str_rank <= TOP_N_PRODUCT:
                    result_title_list.append(str_content_dict[1]['Title'])
                    result_url_list.append(str_content_dict[1]['SrcURL'])
                    amazon_pic_list.append(str_content_dict[1]['ImgURL'][0:3])

        else:
            for es_rank, content_dict in enumerate(sorted_dict_by_es, 1):

                if es_rank <= TOP_N_PRODUCT:
                    result_title_list.append(content_dict[1]['Title'])
                    result_url_list.append(content_dict[1]['SrcURL'])
                    amazon_pic_list.append(content_dict[1]['ImgURL'][0:3])

    def gv_text(self, file):
        response_image = self.load_img_by_path(file)
        text_response = client.text_detection(image=response_image)
        texts = text_response.text_annotations

        # print(texts)

        return texts[0].description

    def get_gv(self, file):
        global result_title_list
        global result_url_list
        global amazon_pic_list
        # global result_word_for_web

        # color_logo_word_1 = '<div><font color="green">'
        # color_word_2 = '</font>'

        # response_image = self.load_img_by_path(file)
        # print(response_image)
        # 先以logo去搜尋
        start_time = time.time()

        # logo_response = client.logo_detection(image=response_image)
        #
        # if logo_response.logo_annotations:
        #     logos = logo_response.logo_annotations
        #     keyword_logo = logos[0].description
        #     except_word_method(color_logo_word_1 + 'Logo:' + keyword_logo + color_word_2 + '</div>')
        # else:
        #     print('此商品無法辨識出Logo!!!')
        # keyword_logo = ''

        # 再以text去搜尋
        # text_response = client.text_detection(image=response_image)

        text_response = self.request_ocr(file)
        # print('logoAnnotations')
        # print(text_response.json()['responses'][0]['logoAnnotations'][0])
        # print(text_response.json()['responses'][0]['textAnnotations'][0]['description'])

        try:
            keyword_text_unclean = text_response.json()['responses'][0]['textAnnotations'][0]['description']
            text_logo_json = text_response.json()['responses'][0]
        except Exception as e:
            print('此商品無法辨識!!!', e)
            text_logo_json = ''
            # result_list_for_web.append(result_word_for_web)
            # result_word_for_web = ''
            return '', [], '', ''

        # print(text_logo_json)

        keyword_final_string = ' '.join(keyword_text_unclean.split('\n'))

        keyword_final_string_backup = copy.deepcopy(keyword_final_string)

        after_filter_text_without_blank = self.re_sub_string(keyword_final_string)

        after_filter_text_with_blank = self.re_sub_string(keyword_final_string, blank_select=1)

        res_dict = self.get_data_from_es(keyword_final_string)

        print('原始text: ' + keyword_final_string_backup)
        print()
        print('過濾雜訊後的text: ' + after_filter_text_without_blank)

        self.unzip_dict(res_dict, after_filter_text_without_blank,
                        after_filter_text_with_blank)

        tables_all = []

        counts = [x for x in range(1, len(result_title_list) + 1)]

        df = pd.DataFrame([counts, amazon_pic_list, result_title_list, result_url_list]).T

        df.columns = ["number", "amazon_pic", "result_title", "result_url"]

        tables_all.append(df.to_html(index=False))

        tables_all = df.to_dict(orient="records")
        spend_time = str(self.method_round(time.time() - start_time))
        print("\n--- %s seconds ---" % spend_time)

        result_title_list = []
        result_url_list = []
        amazon_pic_list = []

        return keyword_final_string_backup, tables_all, spend_time, text_logo_json


get_gv_file = Get_GV()
