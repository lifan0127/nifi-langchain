from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators

PARAM_PREFIX = 'langchain.output_parser.'
def parse_or_keep_string(input_string):
    import json
    try:
        return json.loads(input_string)
    except json.JSONDecodeError:
        return input_string
   
class OutputParser(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']
    class ProcessorDetails:
        version = '0.0.2-SNAPSHOT'
        description = "Parse output from LLMs"
        tags = ["LangChain", "LCEL", "output parser", "LLMs"]
        dependencies = ['langchain==0.1.4', 'langchain-core==0.1.16', 'langchain_openai==0.0.5']

    PARSER = PropertyDescriptor(
        name="Output Parser",
        description="The output parser to use",
        allowable_values=["StrOutputParser", "JsonOutputParser", "Dummy Parser"],
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        required=True
    )

    property_descriptors = [
        PARSER
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
        from parsers import load_parser
        from langchain_core.load import dumps, loads

        flow_content = flowFile.getContentsAsBytes().decode()
        input = loads(flow_content)
        parser_name = context.getProperty(self.PARSER).evaluateAttributeExpressions(flowFile).getValue()
        parser_params = { k.name[len(PARAM_PREFIX):]: parse_or_keep_string(v) for k, v in context.getProperties().items() if k.name.startswith(PARAM_PREFIX)}
        parser, mime_type = load_parser(parser_name, parser_params)
        output = parser.invoke(input)

        return FlowFileTransformResult(relationship = "success", contents = output if mime_type == 'text/plain' else dumps(output), attributes = {"mime.type": mime_type})