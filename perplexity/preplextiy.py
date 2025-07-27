import requests
import time

# API URLs
POST_URL = "https://api.apify.com/v2/actor-runs/2i8atIASOvGQnPcvo/resurrect?token=apify_api_7vRwaaAlsHHoR6CVsuTJIlfKOTjao401V7fE"
GET_URL = "https://api.apify.com/v2/actor-runs/2i8atIASOvGQnPcvo?token=apify_api_7vRwaaAlsHHoR6CVsuTJIlfKOTjao401V7fE"

def send_input_to_apify(input_data):
    """Send input to Apify actor"""
    response = requests.post(POST_URL, json=input_data)
    return response.json()

def get_results_from_apify():
    """Get results from Apify actor"""
    response = requests.get(GET_URL)
    return response.json()

def run_apify_task(input_data, wait_time=5):
    """Send input and wait for results"""
    # Send input
    print("Sending input to Apify...")
    post_result = send_input_to_apify(input_data)
    print(f"Input sent: {post_result}")
    
    # Wait for processing
    time.sleep(wait_time)
    
    # Get results
    print("Getting results...")
    results = get_results_from_apify()
    return results

# Example usage
if __name__ == "__main__":
    # Replace with your actual input data
    my_input = {
        "query": "top 10 cars in indiapip",
        "maxResults": 10
    }
    
    results = run_apify_task(my_input)
    print(results)