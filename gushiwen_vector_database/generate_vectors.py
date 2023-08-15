# -*- coding: utf-8 -*-
#!/usr/bin/env python3

# Based on: 
# 代码注释使用中文 - 英文
# Code comments use Chinese - English

# 将文本转化为向量并存储为文件 - Convert text to vector and store it as a file
# 使用方法：text

import torch
from transformers import AutoTokenizer, AutoModel
import json

# 加载模型 - Load model
tokenizer = AutoTokenizer.from_pretrained("./embedding_model/models--sentence-transformers--all-mpnet-base-v2/snapshots/bd44305fd6a1b43c16baf96765e2ecb20bca8e1d")
model = AutoModel.from_pretrained("./embedding_model/models--sentence-transformers--all-mpnet-base-v2/snapshots/bd44305fd6a1b43c16baf96765e2ecb20bca8e1d")

# 平均池化 - Average pooling
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# # 获取文本的向量 - Get the vector of the text
def get_vector(text):
    encoded_input = tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
    # 使用平均池化获取文本向量 - Use average pooling to get text vectors
    input_ids = mean_pooling(model_output, encoded_input['attention_mask'])
    return input_ids

# 读取本地数据库并转换为二维向量存储 - Read the local database and convert it to a two-dimensional vector storage
def read_and_save(file):
    file = json.load(open(file, 'r', encoding='utf-8'))
    vectors = []
    for i in range(len(file)):
        line = str(file[i])
        vector = get_vector(line)
        vectors.append(vector)
    vectors = torch.cat(vectors, dim=0)
    torch.save(vectors, './local_vectors/vectors.pt') # 保存向量的路径及文件名
    print('generate vectors successfully!')

if __name__ == '__main__':
    read_and_save('gushiwen.json')
    