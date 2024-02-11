def load_parser(name, kwargs):
    if name == 'StrOutputParser':
        from langchain_core.output_parsers import StrOutputParser
        return StrOutputParser(**kwargs), 'text/plain'
    elif name == 'JsonOutputParser':
        from langchain_core.output_parsers import JsonOutputParser
        return JsonOutputParser(**kwargs), 'application/json'
    else:
        raise Exception("Unknown output parser: " + name)