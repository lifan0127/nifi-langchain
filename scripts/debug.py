from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.load import dumps, loads
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# prompt_template = ChatPromptTemplate.from_template("tell me a short joke about {topic}")
# model = ChatOpenAI(model='gpt-4-turbo-preview')

# prompt_invoke = prompt_template.invoke({'topic': 'hello'})
# prompt_invoke_serialized = dumps(prompt_invoke)
# prompt_invoke_deserialized = loads(prompt_invoke_serialized)

# model_invoke = model.invoke(prompt_invoke_deserialized)
# print(model_invoke.to_json())

# store = PGVector(
#   collection_name="around-the-world-in-80-days",
#   connection_string="postgresql+psycopg2://postgres:postgres@db:5432/postgres",
#   embedding_function=OpenAIEmbeddings(),
# )
# query = "Certainly an Englishman, it was more doubtful whether Phileas Fogg was a Londoner."
# docs = store.max_marginal_relevance_search_with_score(query)

# print(docs)

db = FAISS.load_local('data/samples/around-the-world-in-80-days-index', OpenAIEmbeddings())
docs = db.similarity_search("What happened to Mr. Fogg in Hong Kong?")
print(docs)