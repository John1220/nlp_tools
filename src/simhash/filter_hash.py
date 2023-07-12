# -*- coding: utf-8 -*-
import os
import re
import argparse
import time
from collections import defaultdict
import itertools

import Levenshtein
import numpy as np
import pandas as pd
from tqdm import tqdm

from simhash_ import Simhash

from src.Utils.io_utils import IO_Utils
from src.Utils.timer_utils import timer


def read_texts(data_path, num=None):
    """
    读取原始文本
    """
    with open(data_path, encoding='utf-8') as fr:
        if num is None:
            texts = fr.readlines()
        else:
            texts = fr.readlines()[:num]
    print(f"texts size: {len(texts)}")
    return texts


class HashFilter():
    """
    使用simhash方法对原始数据快速去重
    """

    def __init__(self, hmhold=3, keylength=16, f=64, segmenter=False):
        """
            `f` is the dimensions of fingerprints, in bits. Must be a multiple of 8.
        """
        self.segmenter = segmenter
        self.f = f
        self.keylength = keylength
        self.hmhold = hmhold
        self.savedir = 'output'
        if not os.path.exists(os.path.join(os.getcwd(), self.savedir)):
            os.makedirs(os.path.join(os.getcwd(), self.savedir))
        # 重复文本
        self.duptexts = []

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

    def split_simhash(self, hashval):
        """
        切分分段simhash值，切分结果作为hashdict的key
        """
        seglen = self.keylength
        hashbytes = '{:064b}'.format(hashval)
        slices = [slice(i * seglen, (i + 1) * seglen) for i in range(self.f // seglen)]
        segbytes = [hashbytes[s] for s in slices]
        return segbytes

    def update_dict(self, index, key):
        """
        index:  text fingerprint
        key:    16 bits key
        """
        hmhold = self.hmhold
        seghash_keys = self.split_simhash(key)
        for k in seghash_keys:
            for code in self.hashdic.get(k, []):
                if self.hammingdistance(self.simhashs[index], self.simhashs[code]) <= hmhold:
                    self.duptexts.append((code, index))
                    return
        for k in seghash_keys:
            self.hashdic[k].add(index)
        return

    @timer
    def _hashdict(self, texts_w):
        """
        输入分词词组，生成hashdict
        texts_w: 分词后的文本组，每个文本空格间隔
        """
        simhash_func = Simhash().build_by_features
        simhashs = map(simhash_func, texts_w)
        self.simhashs = {}
        self.hashdic = defaultdict(set)
        error_texts = []
        for index, key in tqdm(enumerate(simhashs)):
            try:
                self.simhashs[index] = key
                self.update_dict(index, key)
            except Exception as e:
                print(e)
                error_texts.append(index)
        error_texts = [self.texts_raw[i] for i in error_texts]
        if error_texts:
            IO_Utils.write_texts(error_texts, os.path.join(os.getcwd(), self.savedir, 'error_hash.txt'))
        return

    def drop_dup(self, text_indexs, threshold=0.8, hmhold=14):
        """
        去重，每个key下的文本集合两两之间相似度不高于阈值
        :param text_indexs:
        :param threshold: Levenshtein 距离
        :param hmhold: hamming 距离，计算更快
        :return:
        """
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

    def shingle(self, tokens, window=4):
        '''A generator for a moving window of the provided tokens.'''
        if window <= 0:
            raise ValueError('Window size must be positive')
        its = []
        for number in range(window):
            it = iter(tokens)
            its.append(it)
            for _ in range(number):
                next(it)
        try:
            while True:
                yield [next(it) for it in its]
        except StopIteration:
            pass

    def format(self, text, window=4):
        url_regex = re.compile("(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#*]*[\w\-\@?^=%&/~\+#])?")
        num_regex = re.compile('\d+')
        stop_regex = re.compile('\s')
        text = stop_regex.sub(' ', text)
        text = url_regex.sub('<url>', text)
        text = num_regex.sub('<d>', text)
        if len(text) <= window:
            return text
        text = [''.join(shingle) for shingle in self.shingle(text, window=window)]
        return text

    def filter(self, texts):
        nowtime = time.strftime('%m%d-%H_%M', time.localtime())
        print("start filtering...")
        suffix = len(texts) // 10000
        self.texts_raw = texts
        if self.segmenter:
            from segmenter import HanlpSegmenter as segmenter
            texts_w = (segmenter.cut_words(text) for text in texts)
        else:
            texts_w = (self.format(text) for text in texts)
        self._hashdict(texts_w)
        drop_dup_result = set(itertools.chain.from_iterable(self.hashdic.values()))
        droped_text = [self.texts_raw[i] for i in drop_dup_result]
        print(f"after filter texts size: {len(droped_text)}")

        # 保存去重后文本
        outputfile = os.path.join(os.getcwd(), self.savedir, f'dropedtext-{suffix}w-hm{self.hmhold}-{nowtime}.txt')
        IO_Utils.write_texts(droped_text, outputfile)
        print(f'file saved at {outputfile}')

        # 保存重复记录文本
        duptexts_file = os.path.join(os.getcwd(), self.savedir, f'duptext-{suffix}w-hm{self.hmhold}-{nowtime}.csv')
        duptexts = [(i, j, self.texts_raw[i], self.texts_raw[j]) for i, j in self.duptexts]
        pd.DataFrame(data=duptexts, columns=['i', 'j', 'text_i', 'text_j']).sort_values(by='i').to_csv(duptexts_file,
                                                                                                       index=False)
        return


def main(filename, segmenter=False, hamming_threshold=3, keylength=16):
    data_path = os.path.join('', 'data', filename)
    texts = read_texts(data_path)
    h_filter = HashFilter(segmenter=segmenter, hmhold=hamming_threshold, keylength=keylength)
    h_filter.filter(texts)
    print('done')


def test():
    data_path = ''
    texts = read_texts(data_path)
    h_filter = HashFilter(segmenter=False, hmhold=10)
    h_filter.filter(texts)
    print('done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='simhash filter duplicate texts')
    parser.add_argument('-filename', dest='filename', required=True, help='filename')
    parser.add_argument('-seg', dest='segmenter', default=False, help='use segmenter')
    parser.add_argument('-hm', dest='hmhold', default=3, help='hamming distance threshold')
    parser.add_argument('-len', dest='keylength', default=16, help='segment simhash_code length')
    args = parser.parse_args()

    filename = args.filename
    hamming_threshold = int(args.hmhold)
    keylength = int(args.keylength)
    segmenter = bool(args.segmenter)
    main(filename, segmenter=segmenter, hamming_threshold=hamming_threshold, keylength=keylength)

    # python filter_hash.py -filename dropedtext-100w-hm3-v2.txt -seg True
