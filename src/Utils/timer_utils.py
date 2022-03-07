import time


# 装饰器，用于统计函数运行时间
def timer(func):
    def deco(*args, **kwargs):
        time_start = time.time()
        value = func(*args, **kwargs)  # 返回所装饰函数的返回值
        time_end = time.time()
        print("function %s costs %f seconds" % (func.__name__, (time_end - time_start)))
        return value
    return deco
