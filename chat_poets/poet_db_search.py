import torch
import faiss

from transformers import AutoTokenizer, AutoModel


def poet_db_search(txt):
    # 检查GPU可用性并设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 加载模型 - Load model
    tokenizer = AutoTokenizer.from_pretrained("shibing624/text2vec-bge-large-chinese", cache_dir='embedding_model',
                                              model_max_length=512)
    model = AutoModel.from_pretrained("shibing624/text2vec-bge-large-chinese", cache_dir='embedding_model').to(device)

    def read_local_data_and_vectors():
        processed_data, vectors = torch.load('./local_vectors/data_and_vectors.pt')
        return processed_data, vectors

    # 平均池化 - Average pooling
    def mean_pooling(model_output, attention_mask):
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    # 获取文本的向量 - Get the vector of the text
    def get_vector(text):
        # 将文本分为512字的块
        text_chunks = [text[i:i + 512] for i in range(0, len(text), 512)]
        vectors = []
        for chunk in text_chunks:
            encoded_input = tokenizer(chunk, padding=True, truncation=True, max_length=512, return_tensors='pt').to(
                device)
            with torch.no_grad():
                model_output = model(**encoded_input)
            # 使用平均池化获取文本向量 - Use average pooling to get text vectors
            vector = mean_pooling(model_output, encoded_input['attention_mask'])
            vectors.append(vector)
        # 如果有多个块，将其向量表示平均
        if len(vectors) > 1:
            vectors = torch.stack(vectors, dim=0)
            vector = vectors.mean(dim=0)
        else:
            vector = vectors[0]
        return vector.cpu()  # 将结果移回CPU以便于后续处理和保存

    def build_faiss_index(vectors):
        dimension = vectors.shape[1]  # 获取向量的维度
        index = faiss.IndexFlatL2(dimension)  # 使用L2距离创建一个平面索引
        faiss.normalize_L2(vectors)  # L2归一化向量
        index.add(vectors)  # 将向量添加到索引中
        return index

    def get_domain_knowledge(text, n):
        processed_data, vectors = read_local_data_and_vectors()
        input_vector = get_vector(text)
        input_vector = input_vector.detach().numpy()
        vectors = vectors.detach().numpy()

        # 构建FAISS索引并执行搜索
        index = build_faiss_index(vectors)
        faiss.normalize_L2(input_vector)  # L2归一化输入向量
        D, I = index.search(input_vector, n)  # 执行搜索，D是距离，I是索引

        if max(I[0]) >= len(processed_data):
            raise ValueError("Invalid index returned by FAISS")
        selected_records = [processed_data[i] for i in I[0]]  # 直接从索引中选择数据记录
        return selected_records

    knowledges = get_domain_knowledge(txt, 1)
    return knowledges


if __name__ == '__main__':
    knowledge = poet_db_search("苏轼的定风波真的好看吗")
    print((knowledge[0]["content"]).strip())

