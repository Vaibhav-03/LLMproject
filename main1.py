import requests
import json
import pandas as pd

def get_ollama_results(product_name, product_description):
    url = 'http://localhost:11434/api/generate'
    headers = {'Content-Type': 'application/json'}

    data = {
        "model": "mistral",
        "stream": False,
        "prompt": f"You are a helpful assistant for online retail product metadata extraction. \
Provide key words or phrases that are important features of the product below, \
especially for someone who might like to buy it. \
Infer attribute:value mappings that categorize or identify the product. \
Do not include the original NAME or DESCRIPTION. \
Avoid nonspecific attributes (keys) like 'attributes' or 'features'. \
Respond in valid JSON format. For example, this would be a good response: \
```json \
{{ \
    'blend': 'wool', \
    'sizes': [8, 9, 10], \
    'material': {{ \
        'outsole': 'rubber', \
        'lining': 'jersey' \
    }}, \
    'benefits': ['odor-resistant', 'easy mobility'] \
}} \
1.don't not leave any attributes keys or values empty \
2.the output must be all in lower case and singular nouns \
3.use standard formatting for values, such as '50ml' instead of '50 ml' \
4.be concise, don’t create repeated answers \
5.dont give anything other than the json output, no explanation \
Here is the Product information: {product_name}, {product_description}",
        'product_name': product_name,
        'product_description': product_description
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data["response"]
        return actual_response
    else:
        print("Error:", response.status_code, response.text)
        return None

def read_sample_data(metadata_file_path, description_file_path):
    metadata_columns = ['external_id', 'name', 'brand', 'categories', 'attributes']
    data_df = pd.read_csv(metadata_file_path, sep='', header=None, names=metadata_columns, usecols=[1, 2, 4, 6, 7])
    
    description_df = pd.read_csv(description_file_path, sep='', header=None, names=['external_id', 'description'])

    # Merge metadata and description dataframes on external_id
    data_df = data_df.merge(description_df, on='external_id', how='left')

    return data_df

data = read_sample_data('./metadata.txt', './description.txt')


all_results = []


first_iteration = True


for index, row in data.iterrows():
    product_name = row['name']
    product_description = row['description']
    print(f"Processing product: {product_name}")
    
 
    if first_iteration:
        first_iteration = False
        continue
    
    # Call the Ollama API
    product_results = get_ollama_results(product_name, product_description)
    if product_results is not None:  # Check if results were obtained successfully
        # Append the result to the list
        all_results.append({'product_name': product_name, 'result': product_results})
        # Save all results to a single JSON file
        with open('mistral_results.json', 'w') as file:
            json.dump(all_results, file, indent=4)
        print("Results appended to 'mistral_results.json'")
    else:
        print(f"Failed to get results for product: {product_name}")
