# AviaGenAI

A FastAPI-based AI application for aviation-related content generation.

## Project Structure

```
AviaGenAI/
├── app/
│   └── main.py          # FastAPI application
├── data/
│   └── raw/             # Raw data storage
├── docs/                # Documentation
├── tests/               # Test files
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── LICENSE             # MIT License
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/shahfsaifi1-lang/AviaGenAI.git
cd AviaGenAI
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### API Endpoints

- `GET /` - Health check endpoint
  - Returns: `{"message": "AviaGenAI API is running ✅"}`

## Development

This project uses FastAPI for the web framework and uvicorn as the ASGI server.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
