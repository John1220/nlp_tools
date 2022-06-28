# -*- coding: utf-8 -*-
import os
import re

from pyhanlp import DoubleArrayTrieSegment


class HanlpSegmenter(object):
    def __init__(self, seg_dict_path=None):
        self.segmenter = self._init_segmenter(seg_dict_path)

    def _init_segmenter(self, seg_dict_path):
        # segmenter = DoubleArrayTrieSegment([seg_dict_path])
        segmenter = DoubleArrayTrieSegment()
        segmenter.enablePartOfSpeechTagging(True)
        return segmenter

    def cut_words(self, text):
        cuts = self.segmenter.seg(text)
        cuts = [term.word for term in cuts]
        return ' '.join(cuts)


class EngSegmenter(object):
    def __init__(self):
        self.stop_words = set()
        self.url_regex = re.compile(
            "(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#*]*[\w\-\@?^=%&/~\+#])?")

    def cut_words(self, content):
        """清洗、分词和停止词过滤等"""
        cut_words = [word.strip(':,.。！') for word in content.split() if word != '']
        cut_words = self.replace_url(cut_words)
        cut_words = [word.strip(' -').lower() for word in re.split(r'[\s,._:：?\[\]【】!\(\)\/\\]', cut_words) if
                     word != '']
        cut_words = self.drop_stop_words(cut_words)
        return " ".join(cut_words)

    def drop_stop_words(self, cut_words):
        """去除停用词"""
        stopword_regex = re.compile("\*+|\d+")
        return [word for word in cut_words if
                word != '' and word not in self.stop_words and not stopword_regex.search(word)]

    def replace_url(self, cut_words):
        return ' '.join([re.sub(self.url_regex, ' <url> ', word) for word in cut_words])


hanlpsegmenter = HanlpSegmenter()
engsegmenter = EngSegmenter()

if __name__ == '__main__':
    print(hanlpsegmenter.cut_words(""))
