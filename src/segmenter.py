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


if __name__ == '__main__':
    print(HanlpSegmenter().cut_words(
        "【交银施罗德基金】尊敬的柯燕卿:您于7月27日提交的定期定额申购阿尔法申请确认成功,确认金额90.00元,确认份额28.25份,成交净值3.181元。微信关注公众号""jysld001"", 基金知识、精彩活动尽在掌握!"))
