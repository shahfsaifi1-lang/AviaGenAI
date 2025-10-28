from app.core.config import settings
import google.generativeai as genai

def list_available_models():
    """List available Google AI models"""
    try:
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        models = genai.list_models()
        
        print("Available models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"- {model.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return False

if __name__ == "__main__":
    list_available_models()
