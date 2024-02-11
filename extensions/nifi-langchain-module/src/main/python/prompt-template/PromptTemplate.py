from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators
 
class PromptTemplate(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']
    class ProcessorDetails:
        version = '0.0.2-SNAPSHOT'
        description = "Create a prompt based on a prompt template and input variables."
        tags = ["LangChain", "LCEL", "prompt template", "LLMs"]
        dependencies = ['langchain==0.1.4', 'langchain-core==0.1.16', 'langchain_openai==0.0.5']

    TEMPLATE = PropertyDescriptor(
        name="Template",
        description="The prompt template string",
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        required=True
    )

    property_descriptors = [
      TEMPLATE
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
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.load import dumps, loads

        flow_content = flowFile.getContentsAsBytes().decode()
        try:
          input = loads(flow_content)
        except:
          input = { 'input': flow_content }
        template = context.getProperty(self.TEMPLATE).evaluateAttributeExpressions(flowFile).getValue()
        prompt = ChatPromptTemplate.from_template(template)
        output = prompt.invoke(input)

        return FlowFileTransformResult(relationship = "success", contents = dumps(output), attributes = {"mime.type": "application/json"})