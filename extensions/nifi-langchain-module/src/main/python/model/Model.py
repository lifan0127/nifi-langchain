from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators

PARAM_PREFIX = 'langchain.model.'
def parse_or_keep_string(input_string):
    import json
    try:
        return json.loads(input_string)
    except json.JSONDecodeError:
        return input_string
    
class Model(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']
    class ProcessorDetails:
        version = '0.0.2-SNAPSHOT'
        description = "LLM model"
        tags = ["LangChain", "LCEL", "model", "LLMs"]
        dependencies = ['langchain==0.1.4', 'langchain-core==0.1.16', 'langchain_openai==0.0.5']

    MODEL = PropertyDescriptor(
        name="Model",
        description="The LLM model to use",
        allowable_values=["ChatOpenAI", "DummyLLM"],
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        required=True
    )

    property_descriptors = [
        MODEL,
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
        import json
        from models import load_model
        from langchain_core.load import dumps, loads

        flow_content = flowFile.getContentsAsBytes().decode()
        input = loads(flow_content)
        model_name = context.getProperty(self.MODEL).evaluateAttributeExpressions(flowFile).getValue()
        model_params = { k.name[len(PARAM_PREFIX):]: parse_or_keep_string(v) for k, v in context.getProperties().items() if k.name.startswith(PARAM_PREFIX)}
        model = load_model(model_name, model_params)
        output = model.invoke(input)
        return FlowFileTransformResult(relationship = "success", contents = dumps(output), attributes = {"mime.type": "application/json"})