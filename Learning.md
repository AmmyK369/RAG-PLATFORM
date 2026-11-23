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

## Challenges

1.Chunks longer than the embedding model's limit. I used 512-token chunks with a 256-token model, so half of each chunk was silently ignored. I spotted it, checked max_seq_length, resized to 200/40, and re-ingested to 1,502 chunks.
2.Cloud connection failed. The connection kept getting cut. The cause turned out to be that I'd never created a cluster, only an account key. I learned the difference between an account, a cluster endpoint, and an API key.
3.Vector search returns results even when nothing is relevant. For unanswerable questions it still returned the "least bad" chunks. That's why I added hybrid search, reranking, and a strict "I don't know" prompt.
4.Qdrant required an index for the role filter. The filter failed with a 400 error until I created a payload index on allowed_roles.
5.Model names change. My reranker choice was outdated, so I checked the provider's current docs and switched to Rerank 5 Fast, with a fallback so a failed call doesn't crash the system.

## day idk
- what is least priveldge?
it means the person should have access to only a part of info required to perfom their job.

-why salary is admin only?
because employees have diff levels and so different pays and them knowing the actual salaries being given makes it harder for managements to negotiate

- what is default deny?
it means that documents or anyhting which have no label should not be automatically meant for public access rather it should be denied by default . this way no imp info gets leaked even by mistake.

## block 2 and 3 

- Why hybrid search (BM25 + vector)? What does the reranker do?
we use exact keyword matching and semantic search for finding similar kewords which results in better retreival of the chunk against the query. combining these 2 methods gives more accirate answers.the reranker then sorts the retrieved chunks to top k chunks most relevant to the query.

- What does the prompt force the AI to do?
the prompt tells the ai to not make answers up and to say i dont know based on the documnets rather than giving false answers. and aslo tells to cite the sources along with answers

- How do roles work, and what did the leak test prove?
there are 3 roles on the company level that is engineer admin and employee. the salary band and board info is only available to the admin and likewise all 3 have diff restrictions to the sources which makes the info leakproof. the leak tets proove that least privilledge is being used actively for each role efficiently.

## block 4
adding fastend api and frontend
starting with the upload the document pipeline - uploader.py
the waiter- api.py

## block 5
evaluation

build_evail.py - is hybrid really good?
results:
Mode	Hit@5	Questions missed (out of 40)
vector	98%	1 (sq1)
hybrid	95%	2 (sq11, sq19)
hybrid + rerank	100%	0

catch here: the language was too easy lexicographically.hit@5 is very lineant.

 On my test set the retrieval was near ceiling. Hybrid alone didn't beat vector, and the reranker recovered the misses. I recognised the questions were too lexically easy, so I added paraphrased questions and ranking-sensitive metrics to separate the methods.

## Fixes

Add paraphrased questions.

improved results:
Mode	Hit@1	Hit@5	MRR
vector	80% (36/45)	96% (43/45)	0.85
hybrid	76% (34/45)	96% (43/45)	0.83
hybrid + rerank	91% (41/45)	100% (45/45)	0.95

I compared vector, hybrid and hybrid plus rerank on 45 questions. Reranking gave the biggest gain: hit@1 went from about 80% to 91%, and MRR from about 0.84 to 0.95. Hybrid alone didn't beat vector overall, but it missed different questions, which is why it's a good candidate pool for the reranker. The sample is small, so I treat the differences as directional.
