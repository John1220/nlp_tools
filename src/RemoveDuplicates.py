# -*- coding: utf-8 -*-
import os
import time
from concurrent import futures

import numpy as np
import Levenshtein

from segmenter import hanlpsegmenter


def timer(func):
    def deco(*args, **kwargs):
        time_start = time.time()
        value = func(*args, **kwargs)  # 返回所装饰函数的返回值
        time_end = time.time()
        print("function %s costs %f seconds" % (func.__name__, (time_end - time_start)))
        return value

    return deco


def Jaccrad(terms_model, terms_reference):
    grams_reference = list(terms_reference)  # 去重；如果不需要就改为list
    grams_model = list(terms_model)
    temp = 0
    for i in grams_reference:
        if i in grams_model:
            temp = temp + 1
    fenmu = len(grams_model) + len(grams_reference) - temp  # 并集
    jaccard_coefficient = float(temp / fenmu)  # 交集
    return jaccard_coefficient


def read_texts(data_path, num=1000):
    """
    读取原始文本
    """
    with open(data_path, encoding='utf-8') as fr:
        texts = fr.readlines()[:num]
    texts = [line.replace("\n", "") for line in texts]
    return texts[1:]


def cut_merge(texts, bin_size=1000, processor=8):
    """
    切分、合并
    :param texts: 原文本集合
    :param bin_size: bin：切分的单元，用于去重
    :return:
    """
    texts = np.array(texts)
    bins_num = len(texts) // bin_size + 1
    drop_dup_result = []
    with futures.ProcessPoolExecutor(8) as pool:
        for result in pool.map(drop_dup, [texts[i * bin_size: (i + 1) * bin_size] for i in range(bins_num)]):
            drop_dup_result.append(result)
    drop_dup_result = np.concatenate(drop_dup_result)
    np.random.seed(1)
    np.random.shuffle(drop_dup_result)
    return drop_dup_result


# @timer
def drop_dup(texts, threshold=0.66):
    """
    去重
    :param texts:
    :param threshold:
    :return:
    """
    if len(texts) < 1:
        return texts
    tokens = np.array([hanlpsegmenter.cut_words(text.split('|')[-1]).split(' ') for text in texts])
    length = len(tokens)
    sim_matrix = np.array([
        any([Jaccrad(tokens[i], tokens[j]) > threshold for j in range(i + 1, length)])
        for i in range(length)
    ])
    # 对于重复文本，保留后面，去掉前面
    texts = texts[np.where(sim_matrix == 0)]
    return texts


def output(texts, output_dir="output"):
    texts = texts.tolist()
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    with open(os.path.join(output_dir, 'drop_dup_texts.txt'), 'w', encoding='utf8') as w:
        w.write(''.join([x + '\n' for x in texts]))
    print(f"texts write done.")


def main():
    """
    根据相似性去重: 切分、去重、合并; 再切分、去重、合并
    """
    data_path = r""
    texts = read_texts(data_path, 500000)
    droped_len = len(texts)
    count = 1
    while True:
        texts = cut_merge(texts, bin_size=1000)
        print(f"after {count} droped length: {len(texts)}")
        if len(texts) > 0.9 * droped_len:
            break
        droped_len = len(texts)
        count += 1
    output(texts)


if __name__ == '__main__':
    main()
