from app.services.llm_client import chat_completion

def test_llm_client():
    """Test the LLM client with aviation-related content"""
    try:
        messages = [
            {
                "role": "system", 
                "content": "You are an aviation expert AI assistant. Provide helpful, accurate information about aviation topics."
            },
            {
                "role": "user", 
                "content": "What are the key factors to consider when planning a flight route?"
            }
        ]
        
        response = chat_completion(messages)
        print("✅ LLM Client Test Successful!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ LLM Client Test Failed: {e}")
        return False

if __name__ == "__main__":
    test_llm_client()
