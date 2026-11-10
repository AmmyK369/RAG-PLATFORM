# Learning Log

## Day 1
- What I set up: I set up LLM call and made a repo
- What my code does: it makes an api call to groq and prints response
- One thing that confused me: model 20b and 120b diff is the speed. 20b is faster, 120b handles complex tasks efficiently.
- What RAG means (my own words):system taking latest piece of document related to asked topic and answering citing them
- what is groq: it is Ai infrastructure which handles the AI api calls like of openai.Runs AI models fast.
-what is cohere: An AI company that makes AI models for business. performs semantic searches, reranker, embeddigns,RAG
-what is langsmith: it manages agentic AI development lifecycle

#Day-2
Why does an AI model need RAG?
Ans- AI needs the doc inout beaucse it doesnt know us. So we prepare vector db and pass to our llm and then llm conerts the quesry to vector and performs semantic search to retrieve top k chunks and then usues that data to answer our personal questions.

What are the steps from question to answer?
Ans- 
Prepare (once): documents → split into text chunks → each chunk turned into a vector → stored in the vector DB
Each question: question → turned into a vector → search finds the top-k similar chunks → (reranker re-sorts them) → chunks plus question go to the LLM → answer with citations

What is an embedding, in one sentence?
Ans- it is the data in vector form containing numeric values 