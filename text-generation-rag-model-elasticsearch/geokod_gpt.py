import os
import streamlit as st
import openai
from elasticsearch import Elasticsearch

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
model = "gpt-3.5-turbo-0301"

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
    body = resp['hits']['hits']
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


st.title("Geosearch GPT - A simple location search service")

# Main chat form
with st.form("chat_form"):
    query = st.text_input("You: ")
    submit_button = st.form_submit_button("Send")

# Generate and display response on form submission
negResponse = "I'm unable to answer the question based on the returned response from database."
if submit_button:
    resp, url = search(query)
    print(resp)
    print(url)
    prompt = """You are a assistant bot returning geografic location data in a simple to understand format.
      The data is json strings. The location cordinates are using coordinate system WGS-84.
        Do not mention any of the source data fields that you use as source information.
          Return relative locations returned as strings to the following query: {query}\nUsing only the information from this location data as a string from elastic: {resp}\nIf the location string searched for is not a part of the string in the supplied string reply '{negResponse}' and a reason for why no answer was returned.
            Also on a new line give a google maps link to the coordinate location provided if there is a valid location."""
    #prompt = f"Please refer to anything refered to as strings as location data and do not mention any of the source data fields that you use as source information.
    #  The location cordinates are using coordinate system WGS-84. Return relative locations returned as strings to the following query: {query}\nUsing only the information from this location data as a string from elastic: {resp}\nIf the location string searched for is not a part of the string in the supplied string reply '{negResponse}' and a reason for why no answer was returned. Also on a new line give a google maps link to the coordinate location provided if there is a valid location."
    answer = chat_gpt(prompt)
    print(answer)
    
    if negResponse in answer:
        st.write(f"ChatGPT: {answer.strip()}")
    else:
        st.write(f"ChatGPT: {answer.strip()}\n")



