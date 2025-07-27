import requests
import datetime
import os

# Set up the API endpoint and headers
url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": "Bearer API-KEY_HERE",  # Replace with your actual API key
    "Content-Type": "application/json"
}

# Define the request payload
payload = {
    "model": "sonar-pro",
    "messages": [
        {"role": "user", "content": "top 10 cars in india"}
    ]
}

# Make the API call
response = requests.post(url, headers=headers, json=payload)

# Output directory and unique filename
output_dir = "/Users/chandradhitiya/Documents/vscode/bhothiyum/ouput"
os.makedirs(output_dir, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(output_dir, f"perplexity_output_{timestamp}.md")

# Extract the content and save to markdown file
if response.status_code == 200:
    content = response.json()["choices"][0]['message']['content']
    
    # Save to markdown file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("# Perplexity AI Response\n\n")
        file.write(content)
    
    print(f"Output saved to {output_path}")
else:
    print(f"Error: {response.status_code}")