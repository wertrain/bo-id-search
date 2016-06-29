# -*- coding: utf-8 -*-
u"""
    PSN 関連ユーティリティ
    __author__ = 'wertrain'
    __version__ = '0.1'
"""
import re

class PSNUtil:
    """PSN 関連ユーティリティ""" 
    def __init__(self):
        self.re_id = re.compile('([a-zA-Z]{1})([a-zA-Z0-9\_-]){3,15}')
        self.re_frequent = re.compile('^(ww+)|^(ll+)|^(ee+)|^(TUEE+)|^(HP[0-9]+)|^(AM([0-9]){1,2}$)|^(PM([0-9]){1,2}$)')
        
    def __is_valid_id(self, id):
        u"""
            有効な PSN ID か判定する
        """
        # 頻出単語BL
        list = [
            'wiki', 'twitter', 'href', 'target', 'blank', 
            'border', 'exam', 'youtube', 'skype', 'watch',
            'facebook', 'sage', 'line', 'psid', 'psnid', 
            'bb2ch', 'gp01', 'gp02', 'adsl', 'imgur', 'http',
            'psnprofiles', 'atwiki', 'test', 'yomogi', 'test',
            'read'
        ]
        lowerid = id.lower()
        if lowerid in list:
            return False
        # その他正規表現で判定
        return self.re_frequent.search(id) == None
    
    def get_psn_id_list_from_text(self, text):
        u"""
            テキストから ID らしいものを抽出し返す
        """
        ids = []
        iterator = self.re_id.finditer(text)
        for match in iterator:
            id = match.group()
            if self.__is_valid_id(id):
                ids.append(id)
        # 1レス分の投稿にある ID の重複削除
        return list(set(ids))
