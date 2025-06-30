import time

# Simulated route data
route_steps = [
    {"location": "Start", "instruction": "Head north"},
    {"location": "Junction", "instruction": "Turn right"},
    {"location": "School Zone", "instruction": "Slow down"},
    {"location": "Traffic Light", "instruction": "Prepare to stop"},
    {"location": "Destination", "instruction": "You have arrived"}
]

def simulate_navigation():
    print("Starting mobile-style navigation...")
    for step in route_steps:
        print(f"[{step['location']}] ➤ {step['instruction']}")
        time.sleep(3)  # simulate time delay
    print("Navigation complete.")

if __name__ == "__main__":
    simulate_navigation()
