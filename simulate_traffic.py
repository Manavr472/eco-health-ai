import requests
import time
import random

def simulate():
    print("Simulating agent activity to generate logs...")
    print("Check logs/resource_agent.log and logs/prediction_agent.log")
    
    endpoints = [
        "http://localhost:8000/api/recommendations?hospital_id=1&days_ahead=5",
        "http://localhost:8000/api/predictions/surge?hospital_id=1&days_ahead=7",
        "http://localhost:8000/api/recommendations?hospital_id=2&days_ahead=5",
        "http://localhost:8000/api/predictions/surge?hospital_id=2&days_ahead=7"
    ]
    
    # Run for 20 iterations
    for i in range(20):
        url = random.choice(endpoints)
        try:
            print(f"[{i+1}/20] Triggering agent logic...")
            requests.get(url)
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    simulate()
