# AviaGenAI

A focused aviation technical assistant powered by LLMs.
Stack: FastAPI, Google AI Studio (Gemini)

## Quickstart

1) Create a virtual environment and install requirements
2) Create a `.env` at project root based on `.env.example`, then set GOOGLE_API_KEY
3) Run the API:
   uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs to try the API.

## Development

This project uses FastAPI for the web framework and uvicorn as the ASGI server.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
