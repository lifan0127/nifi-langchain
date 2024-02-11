def load_retriever(name, embedding_function, kwargs):
    if name == 'PGVector':
      from langchain_community.vectorstores.pgvector import PGVector
      return PGVector(embedding_function=embedding_function, **kwargs).as_retriever()
    else:
        raise Exception("Unknown model: " + name)