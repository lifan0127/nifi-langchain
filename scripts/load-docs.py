from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
import re
from dotenv import load_dotenv

load_dotenv()

# Split text by chapters
book_metadata = {
  'title': 'Around the World in 80 Days',
  'author': 'Jules Verne',
  'url': 'https://www.gutenberg.org/ebooks/103',
}
with open('data/samples/around-world-in-80-days.txt', 'r') as file:
    text = file.read()

content = re.split('\*\*\*.*\*\*\*', text)[1]
splits = re.split('CHAPTER [IXV]+\.', content)
toc = splits[1: 38]
chapters = splits[38:]
documents = [Document(page_content=c.strip(), metadata={**book_metadata, 'chapter_num': i+1, 'chapter_title': t.strip()}) for i, (t, c) in enumerate(zip(toc, chapters))]

store = PGVector(
  collection_name="around-the-world-in-80-days",
  connection_string="postgresql+psycopg2://postgres:postgres@db:5432/postgres",
  embedding_function=OpenAIEmbeddings(),
  pre_delete_collection=True
)

store.add_documents(documents)

