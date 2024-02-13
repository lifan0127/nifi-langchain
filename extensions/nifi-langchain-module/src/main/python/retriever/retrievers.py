def load_retriever(name, embedding_function, kwargs):
    if name == 'PGVector':
      from langchain_community.vectorstores.pgvector import PGVector
      return PGVector(embedding_function=embedding_function, **kwargs).as_retriever()
    elif name == 'FAISS':
      from langchain_community.vectorstores import FAISS
      index_path = kwargs.pop('index_path')
      return FAISS.load_local(index_path, embedding_function).as_retriever()
    else:
        raise Exception("Unknown model: " + name)