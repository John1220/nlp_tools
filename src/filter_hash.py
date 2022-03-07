# -*- coding: utf-8 -*-
import os
import re
from collections import defaultdict
import itertools
import numpy as np
from tqdm import tqdm

from Utils.io_utils import IO_Utils
from Utils.timer_utils import timer
from segmenter import hanlpsegmenter as segmenter

from simhash_ import Simhash


def read_texts(data_path, num=None):
    """
    读取原始文本
    """
    with open(data_path, encoding='utf-8') as fr:
        if num is None:
            texts = fr.readlines()
        else:
            texts = fr.readlines()[:num]
    print(f"origin data {len(texts)}")
    return texts


class HashFilter():
    """
    使用simhash方法对原始数据分桶，桶内去重，结果合并
    """

    def __init__(self):
        """
            `f` is the dimensions of fingerprints, in bits. Must be a multiple of 8.
        """
        self.f = 64
        self.savedir = 'simhash'
        if not os.path.exists(os.path.join(os.getcwd(), self.savedir)):
            os.makedirs(os.path.join(os.getcwd(), self.savedir))

    def bits2int(self, array):
        b = np.packbits(array).tobytes()
        return int.from_bytes(b, 'big')

    def hammingdistance(self, val_a, val_b):
        f = self.f
        x = (val_a ^ val_b) & ((1 << f) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans

    def split_simhash(self, hashval, seglen=16):
        """
        分段simhash值作为hashdict的key
        :param hashval: hash值
        :param seglen: 分段长度
        :return:
        """
        hashbytes = '{:064b}'.format(hashval)
        slices = [slice(i * seglen, (i + 1) * seglen) for i in range(self.f // seglen)]
        segbytes = [hashbytes[s] for s in slices]
        return segbytes

    def if_dup(self, index, k, hmhold=3):
        """
        判断hash段 k 是否在hashdict中
        :param index: 文本id
        :param k: 切分后的hash段
        :param hmhold: hammingdistance 阈值，调大阈值保留更少的样本
        :return:
        """
        if k not in self.hashdic.keys():
            return False
        for code in self.hashdic[k]:
            if self.hammingdistance(self.simhashs[index], self.simhashs[code]) <= hmhold:
                return True
        return False

    @timer
    def _hashdict(self, texts_w):
        """
        输入分词词组，生成simhash dict
        """
        simhash_func = Simhash().build_by_features
        simhashs = map(simhash_func, texts_w)
        self.simhashs = {}
        self.hashdic = defaultdict(list)
        error_texts = []
        for index, key in tqdm(enumerate(simhashs)):
            try:
                self.simhashs[index] = key
                for k in self.split_simhash(key):
                    if_dup = self.if_dup(index, k)
                    if if_dup:
                        pass
                    else:
                        self.hashdic[k].append(index)
            except Exception as e:
                print(e)
                error_texts.append(index)
        error_texts = [self.texts_raw[i] for i in error_texts]
        IO_Utils.write_texts(error_texts, os.path.join(os.getcwd(), self.savedir, 'error_hash.txt'))
        return

    def drop_dup(self, text_indexs, threshold=0.8, hmhold=14):
        duplicates = []
        for i, index in enumerate(text_indexs):
            add = True
            for dup in duplicates:
                if self.hammingdistance(self.simhashs[index], self.simhashs[dup]) <= hmhold:
                    # if Levenshtein.ratio(self.texts_raw[index], self.texts_raw[dup]) >= threshold:
                    add = False
                    break
            if add:
                duplicates.append(index)
        return duplicates

    @timer
    def filter(self, texts, cpus=4):
        print("start filtering...")
        suffix = len(texts) // 10000
        self.texts_raw = texts
        texts = (self.parse_content(t) for t in texts)
        texts_w = (segmenter.cut_words(text) for text in texts)
        self._hashdict(texts_w)
        drop_dup_result = set(itertools.chain.from_iterable(self.hashdic.values()))
        droped_text = [self.texts_raw[i] for i in drop_dup_result]
        IO_Utils.write_texts(droped_text, os.path.join(os.getcwd(), self.savedir, f'dropedtext-{suffix}w-v2.txt'))
        return


if __name__ == '__main__':
    data_path = os.path.join(os.getcwd(), 'data', '')
    texts = read_texts(data_path)
    h_filter = HashFilter()
    result = h_filter.filter(texts)
    print('done')
