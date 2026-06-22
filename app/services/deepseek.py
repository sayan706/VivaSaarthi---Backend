import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.config import Config

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def generate_with_retry(messages, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL", "deepseek-chat"),
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"\nDeepSeek Error (Attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            
            # If all retries fail, fall back to Gemini
            print("DeepSeek API is unreachable. Falling back to Gemini API...")
            try:
                from google import genai
                from google.genai import types
                
                gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                
                # Convert OpenAI messages to Gemini format
                # System prompt usually goes to system_instruction in Gemini 2.0
                system_instruction = None
                gemini_contents = []
                
                for msg in messages:
                    if msg["role"] == "system":
                        system_instruction = msg["content"]
                    elif msg["role"] == "user":
                        gemini_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg["content"])]))
                    elif msg["role"] == "assistant":
                        gemini_contents.append(types.Content(role="model", parts=[types.Part.from_text(text=msg["content"])]))
                        
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=2048
                )
                
                response = gemini_client.models.generate_content(
                    model=Config.GEMINI_MODEL,
                    contents=gemini_contents,
                    config=config
                )
                return response.text
            except Exception as gemini_err:
                print(f"Gemini fallback also failed: {gemini_err}")
                raise Exception("Both DeepSeek and Gemini APIs failed to respond.") from gemini_err

def check_answer_relevance(messages, answer):
    last_question = ""
    for msg in reversed(messages):
        if msg["role"] == "assistant":
            last_question = msg["content"]
            break

    prompt = [
        {"role": "system", "content": "You are an AI evaluating an interview. Determine if the user's answer is an attempt to address the interview question. \nCRITICAL RULES:\n- If the user gives a short, casual, grammatically poor, or vague answer (e.g., 'basically I want to learn so that why', 'I dont know', 'yes'), you MUST answer with 'RELEVANT' because they are participating in the interview context.\n- ONLY answer with 'IRRELEVANT' if the user says something completely off-topic that has absolutely nothing to do with an interview (e.g., 'what is the weather', 'I am fine', 'how do I bake a cake').\nOnly respond with the exact word RELEVANT or IRRELEVANT."},
        {"role": "user", "content": f"Previous Question: {last_question}\n\nUser's input: {answer}"}
    ]
    
    response = generate_with_retry(prompt, retries=2)
    return "IRRELEVANT" not in response.upper()
