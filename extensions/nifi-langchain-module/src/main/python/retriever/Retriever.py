from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators

RETRIEVER_PARAM_PREFIX = 'langchain.retriever.'
EMBEDDING_PARAM_PREFIX = 'langchain.embedding.'

def parse_or_keep_string(input_string):
    import json
    try:
        return json.loads(input_string)
    except json.JSONDecodeError:
        return input_string
   
class Retriever(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']
    class ProcessorDetails:
        version = '0.0.2-SNAPSHOT'
        description = "Retriever for RAG"
        tags = ["LangChain", "LCEL", "retriever", "RAG", "LLMs"]
        dependencies = ['langchain==0.1.4', 'langchain-core==0.1.16', 'langchain_openai==0.0.5', 'langchain-community==0.0.17', 'pgvector==0.2.5', 'psycopg2-binary==2.9.9', 'faiss-cpu==1.7.4']

    RETRIEVER = PropertyDescriptor(
        name="Retriever",
        description="The document retriever to use",
        allowable_values=["PGVector", "FAISS"],
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        required=True
    )

    EMBEDDING = PropertyDescriptor(
        name="Embedding",
        description="The embedding to use",
        allowable_values=["OpenAIEmbeddings"],
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        required=True
    )

    property_descriptors = [
        RETRIEVER,
        EMBEDDING,
    ]

    def __init__(self, **kwargs):
        pass
    
    def getPropertyDescriptors(self):
        return self.property_descriptors
    
    def getDynamicPropertyDescriptor(self, propertyname):
        return PropertyDescriptor(name=propertyname,
            description="A user-defined property",
            validators=[StandardValidators.NON_EMPTY_VALIDATOR],
            dynamic=True) 

    def transform(self, context, flowFile):
        from embeddings import load_embedding
        from retrievers import load_retriever
        from langchain_core.load import dumps

        input = flowFile.getContentsAsBytes().decode()
        # Load embedding
        embedding_name = context.getProperty(self.EMBEDDING).evaluateAttributeExpressions(flowFile).getValue()
        embedding_params = { k.name[len(EMBEDDING_PARAM_PREFIX):]: parse_or_keep_string(v) for k, v in context.getProperties().items() if k.name.startswith(EMBEDDING_PARAM_PREFIX)}
        embedding_function = load_embedding(embedding_name, embedding_params)

        # Load retriever
        retriever_name = context.getProperty(self.RETRIEVER).evaluateAttributeExpressions(flowFile).getValue()
        retriever_params = { k.name[len(RETRIEVER_PARAM_PREFIX):]: parse_or_keep_string(v) for k, v in context.getProperties().items() if k.name.startswith(RETRIEVER_PARAM_PREFIX)}
        retriever = load_retriever(retriever_name, embedding_function, retriever_params)
        output = retriever.invoke(input)

        return FlowFileTransformResult(relationship = "success", contents = dumps(output), attributes = {"mime.type": 'application/json'})