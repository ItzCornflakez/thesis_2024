import os
import openai
openai.timeout = 300
import time
import nest_asyncio
import json
nest_asyncio.apply()
from tabulate import tabulate
from elasticsearch import Elasticsearch
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)


# This code is part of an Elastic Blog showing how to combine
# Elasticsearch's search relevancy power with 
# OpenAI's GPT's Question Answering power
# https://www.elastic.co/blog/chatgpt-elasticsearch-openai-meets-private-data

# Code is presented for demo purposes but should not be used in production
# You may encounter exceptions which are not handled in the code


# Required Environment Variables
# openai_api - OpenAI API Key
# cloud_id - Elastic Cloud Deployment ID
# cloud_user - Elasticsearch Cluster User
# cloud_pass - Elasticsearch User Password

openai.api_key = os.environ['openai_api']
# model = "gpt-3.5-turbo-0301"
model = "gpt-4"

# Connect to Elastic Cloud cluster
def es_connect(cid, user, passwd):
    es = Elasticsearch(cloud_id=cid, http_auth=(user, passwd))
    return es

# Search ElasticSearch index and return body and URL of the result
def search(query_text):
    cid = os.environ['cloud_id']
    cp = os.environ['cloud_pass']
    cu = os.environ['cloud_user']
    es = es_connect(cid, cu, cp)

    # Elasticsearch query (BM25) and kNN configuration for hybrid search
    query = {
        "bool": {
            "must": [{
                "match": {
                    "search_text": {
                        "query": query_text,
                        "boost": 1
                    }
                }
            }],
            "filter": [{
                "exists": {
                    "field": "ml.inference.search_text_vector.predicted_value"
                }
            }]
        }
    }

    knn = {
        "field": "ml.inference.search_text_vector.predicted_value",
        "k": 1,
        "num_candidates": 20,
        "query_vector_builder": {
            "text_embedding": {
                "model_id": "sentence-transformers__all-distilroberta-v1",
                "model_text": query_text
            }
        },
        "boost": 24
    }

    fields = ["village",
          "yard",
          "street",
          "municipality",
          "postal_code",
          "postal_area",
          "type",
          "location",
          "search_text"
          ]
    index = 'search-elastic-docs'
    resp = es.search(index=index,
                     query=query,
                     knn=knn,
                     fields=fields,
                     size=1,
                     source=False)

    #body = resp['hits']['hits'][0]['fields']['body_content'][0]
    body = resp['hits']['hits'][0]['fields']
    #url = resp['hits']['hits'][0]['fields']['url'][0]
    url = "url"

    return body, url

def truncate_text(text, max_tokens):
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text

    return ' '.join(tokens[:max_tokens])

# Generate a response from ChatGPT based on the given prompt
def chat_gpt(prompt, model="gpt-3.5-turbo", max_tokens=1024, max_context_tokens=4000, safety_margin=5):
    # Truncate the prompt content to fit within the model's context length
    truncated_prompt = truncate_text(prompt, max_context_tokens - max_tokens - safety_margin)

    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(model=model,
                                            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": truncated_prompt}])

    return response.choices[0].message.content

questions = ["Give me the most relevant location to the following location string: Delfingatan, Göteborg?", 
             "Give me the most relevant location to the following location string: Storgatan, Solna?",
             "Give me the most relevant location to the following location string: Professorsvägen, Lomma?",
             "Give me the most relevant location to the following location string: Delfingatan, Vetlanda?",
             "Give me the most relevant location to the following location string: Dikesvägen, Falkenberg?",
            ]
ground_truths = [
                ["The most relevant location to the given location string is: Delfingatan, Göteborg with location coordinates: 11.930303908132151, 57.67692813261036."],
                ["The most relevant location to the given location string is: Storgatan, Solna with location coordinates: 17.996349055480334, 59.35364435598511."],
                ["The most relevant location to the given location string is: Professorsvägen, Lomma with location coordinates: 13.02112319153484, 55.72809292720763."],
                ["The most relevant location to the given location string is: Delfingatan, Vetlanda with location coordinates: 15.085171477793446, 57.4258016877945."],
                ["The most relevant location to the given location string is: Dikesvägen, Falkenberg with location coordinates: 12.468623701096506, 56.907325694304966.]"],
]
answers = []
contexts = []

for query in questions:
    negResponse = "I'm unable to answer the question based on the returned response from database."
    resp, url = search(query)
    #prompt =  f"Please refer to anything refered to as strings as location data and do not mention any of the source data fields that you use as source information. Also give a minimal direct answer to the question. The location cordinates are using coordinate system WGS-84. Return relative locations returned as strings to the following query: {query}\nUsing only the information from this location data as a string from elastic: {resp}\nIf the location string searched for is not a part of the string in the supplied string reply '{negResponse}' and a reason for why no answer was returned. Also on a new line give a google maps link to the coordinate location provided if there is a valid location."
    #prompt = f"Refer to anything described as strings as location data and refrain from mentioning source data fields. Provide a concise response to the query. Return relative locations as strings based on the query: {query}\nUsing only the information from this location data as a string from elastic: {resp}\nIf the location string queried isn't found in the supplied string, respond with '{negResponse}' and specify the reason for no answer. Additionally, include a Google Maps link to the coordinate location provided, if it's a valid location."
    prompt = f"""
    You are an AI assistant that formats data into easy-to-understand text. I will provide you with a human query and data retrieved from a database, and I need you to present this data clearly and concisely. Do not add any information that is not provided in the data. Your task is to format the data in a human-readable and understandable way.

    Human query: "{query}"

    Here is the data:
    {resp}

    Please format this data into an easy-to-understand format.
    """
    answers.append(chat_gpt(prompt))
    list = [json.dumps(resp)]
    contexts.append(list)

# To dict
data = {
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truths": ground_truths
}


# To dict
data = {
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "ground_truths": ground_truths
}

# Convert dict to dataset
dataset = Dataset.from_dict(data)

result = evaluate(
    dataset = dataset, 
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
    ],
)

df = result.to_pandas()

print(df)

# Print the DataFrame as a pretty table
print(tabulate(df, headers='keys', tablefmt='pretty'))

html = df.style.set_table_attributes('class="table"').set_caption("Evaluation Results").to_html()
with open("evaluation_results.html", "w") as f:
    f.write(html)
