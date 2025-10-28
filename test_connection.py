from app.core.config import settings
from openai import OpenAI

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "user", "content": "Hello! Are you working? Respond with 'AviaGenAI connection successful!'"}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI Connection Successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Connection Failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_connection()
