# simhash

> 使用simhash方法对大量短文本模糊去重
> 
> - 对每条文本编码得到 simhash_fingerprint(64bit)
> - 维护 hashdict: key-value 字典（或redis）。key为simhash_fingerprint切分块(16bit)
> - 全量文本遍历完成，输出 hashdict values 为去重后文本
> - (可选)：输出重复记录文本对
> 
> simhash简介：https://zhuanlan.zhihu.com/p/71488127

> [filter_hash.py]参数描述
> - filename 原文本，位于data目录下
> - seg 采用分词切分句子或采用滑窗方法切分句子
> - hm hamming距离参数，默认3，增大参数可增大模糊程度
> - len simhash_fingerprint 切分长度，减小参数可增大模糊程度

