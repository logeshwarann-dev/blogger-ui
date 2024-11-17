import json
import boto3
import base64
import concurrent.futures
from io import BytesIO

# Initialize clients
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
s3_client = boto3.client("s3")

# S3 bucket details
BUCKET_NAME = "blog-generator-bucket-v5"  # Replace with bucket name

def generate_text(prompt):
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-text-express-v1",
        contentType="application/json",
        body=json.dumps({
            "inputText": f"Assume that you are a blog generator. Your output must be within 250 words and no more than that.Generate a blog with this given topic: {prompt}",
            "textGenerationConfig": {
                "maxTokenCount": 400,
                "temperature": 0.5,
                "topP": 1
            }
        })
    )
    final_output = json.loads(response['body'].read().decode("utf-8"))['results'][0]['outputText']
    print(f"TEXT: {final_output}\n")
    return final_output

def summarize_text(text):
    native_request = {
        "messages": [{
            "role": "user",
            "content": f"Summarize the given content in 2 sentences. Content: {text}"
        }],
        "max_tokens": 50,
        "temperature": 0.5
    }
    response = bedrock_client.invoke_model(
        modelId="ai21.jamba-1-5-large-v1:0",
        contentType="application/json",
        body=json.dumps(native_request)
    )
    summary_text = json.loads(response['body'].read().decode("utf-8"))['choices'][0]['message']['content']
    print(f"SUMMARY: {summary_text}\n")
    return summary_text

def analyze_sentiment(text):
    native_request = {
        "prompt": f"<s>[INST] Provide the sentiment analysis output of the following content in one line within 10 words : {text} [INST]", 
        "max_tokens": 40,
        "temperature": 0.5
    }
    response = bedrock_client.invoke_model(
        modelId="mistral.mistral-7b-instruct-v0:2",
        body=json.dumps(native_request),
        contentType="application/json"
    )
    sentiment_output = json.loads(response['body'].read().decode("utf-8"))['outputs'][0]['text']
    #print(f"SENTIMENT: {sentiment_output}\n")

    return sentiment_output

def generate_image(prompt):
    response = bedrock_client.invoke_model(
        modelId="stability.stable-diffusion-xl-v1",
        contentType="application/json",
        body=json.dumps({
            "text_prompts": [{"text": f"I want you to generate a photograpic colorful image for the following blog. \"{prompt}\"","weight":1}],
            "cfg_scale":12,
            "seed":0,
            "steps":75,
            "width":512,
            "height":512
        })
    )
    # Decode the base64 image from the response
    image_base64 = json.loads(response['body'].read())["artifacts"][0]["base64"]
    image_data = base64.b64decode(image_base64)

    # Save the image to S3
    prompt=prompt.strip()
    image_key = f"{prompt.replace(' ', '_')}.png"  # Use prompt as part of the filename
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=image_key,
        Body=BytesIO(image_data),
        ContentType="image/png"
    )

    # Generate the S3 URL
    s3_url = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{image_key}"
    print(f"IMAGE: {s3_url}\n")
    return s3_url

def classify_text(text):
    blog_categories = [
    "Technology",
    "Health",
    "Finance",
    "Travel",
    "Lifestyle",
    "Food",
    "Education",
    "Business",
    "Entertainment",
    "Fashion"
        ]
    native_request = {
        "prompt": f"From this list,{blog_categories}.Pick the right category for the following content in one word. Content: {text}",
        "maxTokens": 10,
        "temperature": 0.5,
    }

    response = bedrock_client.invoke_model(
        modelId="ai21.j2-mid-v1",
        body=json.dumps(native_request),
        contentType="application/json"
    )
    classified_output = json.loads(response['body'].read().decode("utf-8"))["completions"][0]["data"]["text"]
    print(f"CLASSIFY: {classified_output}\n")
    return classified_output

def lambda_handler(event, context):
    user_prompt = json.loads(event['body'])['prompt']

    generated_text = generate_text(user_prompt)

    # Execute tasks concurrently to reduce Lambda runtime
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_summary = executor.submit(summarize_text, generated_text)
        future_sentiment = executor.submit(analyze_sentiment, generated_text)
        future_category = executor.submit(classify_text, generated_text)
        future_image = executor.submit(generate_image, user_prompt)  # Pass the prompt to generate image
        

        # Retrieve results
        summary = future_summary.result()
        sentiment = future_sentiment.result()
        category = future_category.result()
        image_url = future_image.result()  # S3 URL of generated image
        

    # Construct the response
    response = {
        "generated_text": generated_text,
        "summary": summary,
        "sentiment": sentiment,
        "image_url": image_url,
        "category": category
    }

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(response)
    }