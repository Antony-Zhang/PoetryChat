# -*- coding: utf-8 -*-
#!/usr/bin/env python3

# Based on: 
# 代码注释使用中文 - 英文
# Code comments use Chinese - English

# 介绍 - Introduction
# 本程序用于匹配输入文本与数据库中的相似向量 - This program is used to match the input text with similar vectors in the database
# 具体而言 - Specifically
# 先将输入文本转化为向量，再与数据库中的向量进行比较 - First convert the input text into a vector, and then compare it with the vector in the database
# 使用余弦相似度进行比较 - Use cosine similarity for comparison

from generate_vectors import get_vector
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

# 读取本地数据库 - Read the local database
def read_local_vectors():
    vectors = torch.load('./local_vectors/vectors.pt')
    return vectors

# 将输入文本转化为向量并与数据库中的向量进行比较 - Convert the input text into a vector and compare it with the vector in the database
# 输出相似度最高的前n个文本的序号 - Output the serial number of the top 5 texts with the highest similarity
def get_domain_knowledge(text, n, threshold=0.2):
    # 参数介绍 - Parameter introduction
    # text: 输入文本 - Input text
    # n: 输出相似度最高的前n个文本的序号 - Output the serial number of the top 5 texts with the highest similarity
    # threshold: 概率阈值，小于该阈值的知识将被忽略 - Probability threshold, texts with probability less than this threshold will be ignored
    
    # 读取数据库中的向量 - Read the vector in the database
    vectors = read_local_vectors()
    # 将输入文本转化为向量 - Convert the input text into a vector
    input_vector = get_vector(text)
    # 将输入文本转化为numpy数组 - Convert the input text into a numpy array
    input_vector = input_vector.detach().numpy()
    # 将数据库中的向量转化为numpy数组 - Convert the vector in the database to a numpy array
    vectors = vectors.detach().numpy()
    # 计算每个问题与输入文本的相似度 - Calculate the similarity between each question and the input text
    similarity = cosine_similarity(input_vector, vectors)
    print(similarity)
    similarity_sorted = np.squeeze(similarity)
    # 按照相似度从大到小排序 - Sort by similarity from large to small
    similarity_sorted = np.argsort(-similarity_sorted)
    if n > len(similarity):
        n = len(similarity)
    if len(similarity) > 0:
        # 取出相似度最高的前n个文本的序号 - Take out the serial number of the top n texts with the highest similarity
        knowledges_ids = similarity_sorted[:n].tolist()
        # 读取知识库 - Read the knowledge base
        knowledges = json.load(open('gushiwen.json','r', encoding='utf8').readlines())
        # 去除概率小于阈值的知识 - Remove knowledge with probability less than threshold
        knowledges_ids = [i for i in knowledges_ids if similarity[0][i] > threshold]
        # 直接输出资料文本 - directly output the text
        knowledges = [str(knowledge) for knowledge in knowledges]
        # 取出相似度最高的前n个文本 - Take out the top n texts with the highest similarity
        knowledges = [knowledges[i] for i in knowledges_ids]
        return knowledges
    return ''

# sample:
# if __name__ == '__main__':
#     input_text = '这是一条测试样本'
#     knowledges = get_domain_knowledge(input_text, 5)
#     print(knowledges, len(knowledges))
