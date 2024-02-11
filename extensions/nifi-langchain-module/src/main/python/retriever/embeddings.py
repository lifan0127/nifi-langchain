def load_embedding(name, kwargs):
    if name == 'OpenAIEmbeddings':
      from langchain_openai import OpenAIEmbeddings
      return OpenAIEmbeddings(**kwargs)
    else:
        raise Exception("Unknown embedding: " + embedding)
