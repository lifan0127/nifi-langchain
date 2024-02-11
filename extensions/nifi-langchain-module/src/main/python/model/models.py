def load_model(name, kwargs):
    if name == 'ChatOpenAI':
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(**kwargs)
    else:
        raise Exception("Unknown model: " + name)