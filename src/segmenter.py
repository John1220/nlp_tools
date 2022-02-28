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


hanlpsegmenter = HanlpSegmenter()

if __name__ == '__main__':
    print(hanlpsegmenter.cut_words(""))
