import langchain
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_text_splitters import CharacterTextSplitter

def spr_summarize(text):
  # Split the text into chunks
  chunks = CharacterTextSplitter().split_text(text, chunk_size=1000)

  map_reduce_chain = MapReduceDocumentsChain(
      map_chain=langchain.chains.summarize.load_summarize_chain(
          llm=langchain_openai.ChatOpenAI(temperature=0),
          chain_type="stuff",
          prompt_template="Summarize this chunk of text: {text}",
      ),
      reduce_chain=ReduceDocumentsChain(
          reduce_function=lambda summaries: "\n".join(summaries)
      ),
  )

  summaries = map_reduce_chain.run(chunks)

  return "\n".join(summaries)
