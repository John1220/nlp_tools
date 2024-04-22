# -*- coding: utf-8 -*-
import json
import multiprocessing
from concurrent import futures

import pandas as pd
import requests


def decode_md5(hashed):
    url = "http://192.168.199.132:31090/mobile/md5/like-new?key="
    # 发起 GET 请求
    response = requests.get(url + hashed)
    if response.text:
        return [json.loads(response.text)]
    return


def parallel_func(func, src: list, num_process: int):
    result = []
    with futures.ProcessPoolExecutor(num_process) as pool:
        for i in pool.map(func, src):
            print(i)
            result.append(i)
    return result


def parallel_func2(func, src: list, num_process: int):
    print(func)
    result = []
    with multiprocessing.Pool(processes=num_process) as pool:
        # 启动10个进程执行worker函数
        results = [pool.apply_async(func, args=(i,)) for i in src]
        # 等待所有进程完成
        output = [p.get() for p in results]
        return output
    print('All tasks completed.')
    return result


def selfc(x):
    return x


def f(i):
    return i * 2


def decode_test():
    # data = pd.read_csv('风豹绿信.csv')
    # data = data.head(20)
    # hasheds = data['mobile'].values
    result = parallel_func(f, list(range(8)), 2)
    print(result)


if __name__ == '__main__':
    decode_test()
# print(list(range(10)))
