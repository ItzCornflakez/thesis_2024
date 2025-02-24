from openai import OpenAI
client = OpenAI(api_key="") # Fill in api key here

response = client.images.generate(
  model="dall-e-3",
  prompt="generate a top down topographic map of umeå that would look like a satelite image",
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)