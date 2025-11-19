import os
import requests
import json

def get_llm_response(user_input):
    """
    Calls OpenRouter LLaMA model and returns structured JSON response
    that contains action, item, and quantity.
    """

    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    few_shot_examples = [
        {
            "role": "system",
            "content": (
                "You are a restaurant order assistant. "
                "You must always respond in JSON format like:\n"
                "{\"action\": \"add_to_cart\", \"item\": \"dosa\", \"quantity\": 2}\n\n"
                "Actions: add_to_cart, show_cart, confirm_order, cancel_order."
            )
        },
        {"role": "user", "content": "Add 2 dosas"},
        {"role": "assistant", "content": "{\"action\": \"add_to_cart\", \"item\": \"dosa\", \"quantity\": 2}"},
        {"role": "user", "content": "Show my cart"},
        {"role": "assistant", "content": "{\"action\": \"show_cart\"}"},
        {"role": "user", "content": "Confirm my order"},
        {"role": "assistant", "content": "{\"action\": \"confirm_order\"}"}
    ]

    messages = few_shot_examples + [{"role": "user", "content": user_input}]

    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 150
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        reply = data["choices"][0]["message"]["content"].strip()

        try:
            return json.loads(reply)
        except json.JSONDecodeError:
            return {"action": "unknown", "item": "", "quantity": 0, "raw_response": reply}

    except Exception as e:
        return {"action": "error", "error": str(e)}
