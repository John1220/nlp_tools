# -*- coding: utf-8 -*-

import json
import os


class IO_Utils(object):
    def __init__(self):
        pass

    @staticmethod
    def read_texts(file_path):
        """读 txt 或 csv 文件"""
        with open(file_path, encoding='utf8') as fr:
            text_lines = fr.readlines()
        return text_lines

    @staticmethod
    def write_texts(text_lines, file_path):
        """写 txt 或 csv 文件"""
        text_lines = [text_line.strip() + "\n" for text_line in text_lines]
        with open(file_path, "w", encoding="utf-8") as fw:
            fw.writelines(text_lines)

    @staticmethod
    def load_json(json_path):
        """读json文件"""
        with open(json_path,encoding="utf-8") as fr:
            json_dict = json.load(fr)
        return json_dict

    @staticmethod
    def write_json(json_dict, json_path):
        """写json文件"""
        with open(json_path, 'w', encoding="utf-8") as fw:
            json.dump(json_dict, fw, ensure_ascii=False)