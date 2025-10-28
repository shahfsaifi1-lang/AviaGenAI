from app.core.config import settings
import google.generativeai as genai

def test_google_ai_connection():
    """Test Google AI Studio API connection"""
    try:
        # Configure the API key
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        
        # Create the model
        model = genai.GenerativeModel(settings.GOOGLE_AI_MODEL)
        
        # Generate content
        response = model.generate_content("Hello! Are you working? Respond with 'AviaGenAI Google AI connection successful!'")
        
        print("✅ Google AI Connection Successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Google AI Connection Failed: {e}")
        return False

if __name__ == "__main__":
    test_google_ai_connection()
