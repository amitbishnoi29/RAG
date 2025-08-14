# RAG Chatbot with Voice Support

A modern Retrieval-Augmented Generation (RAG) chatbot built with Azure OpenAI, Weaviate, React.js, and HeyGen Avatar SDK. This application allows users to upload documents and have natural conversations with an interactive AI avatar that can see, hear, and respond in real-time.

## 🎯 Features

- **RAG Capability**: Upload and query documents using semantic search
- **Streaming Responses**: Real-time response streaming from Azure OpenAI
- **Interactive Avatar**: Real-time video avatar with voice conversation using HeyGen
- **Document Support**: PDF, Markdown, Text file ingestion
- **Modern UI**: Responsive design with Tailwind CSS
- **Source Citations**: Displays source documents for answers
- **Real-time Status**: Live API health monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │    FastAPI      │    │   Weaviate      │
│   Frontend      │────│    Backend      │────│  Vector DB      │
│   (Port 3000)   │    │   (Port 8000)   │    │  (Port 8080)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │  Azure OpenAI   │
                       │   Embeddings    │
                       │   & Chat API    │
                       └─────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React.js, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python |
| Vector DB | Weaviate (local) |
| Embeddings | Azure OpenAI (text-embedding-ada-002) |
| LLM | Azure OpenAI (GPT-3.5/GPT-4) |
| Document Processing | LangChain |
| Voice & Avatar | HeyGen Streaming Avatar SDK |

## 📋 Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.8+
- **Docker** (for Weaviate)
- **Azure OpenAI** account with deployed models
- **HeyGen** account with API access

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd RAG
```

### 2. Start Weaviate

```bash
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  semitechnologies/weaviate:latest
```

### 3. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Start the backend
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend
npm start
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080

# HeyGen Configuration
HEYGEN_API_KEY=your_heygen_api_key_here
HEYGEN_AVATAR_ID=default
HEYGEN_VOICE_ID=default

# Application Configuration
DEBUG=false
```

### Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy the following models:
   - **Chat**: `gpt-35-turbo` or `gpt-4`
   - **Embeddings**: `text-embedding-ada-002`
3. Get your API key and endpoint
4. Update the `.env` file

### HeyGen Setup

1. Sign up for HeyGen at [app.heygen.com](https://app.heygen.com)
2. Navigate to Settings → API to get your API key
3. (Optional) Create custom avatars at [labs.heygen.com](https://labs.heygen.com/interactive-avatar)
4. Update the `.env` file with your HeyGen credentials

## 📚 Usage

### Document Ingestion

#### Using the UI
1. Click the upload button in the top-right
2. Drag and drop files or click to browse
3. Supported formats: PDF, TXT, MD, DOCX (max 10MB)

#### Using the CLI Script
```bash
cd backend

# Ingest a single file
python scripts/ingest.py path/to/document.pdf

# Ingest a directory
python scripts/ingest.py path/to/docs --directory

# Ingest text content
python scripts/ingest.py --text "Your text content here" --filename "my_content"

# View knowledge base stats
python scripts/ingest.py --stats

# Clear all documents
python scripts/ingest.py --clear
```

### Chat Interface

1. **Text Chat**: Type questions in the chat input
2. **Voice Input**: Click the microphone button to use speech recognition
3. **Sources**: View cited source documents below responses
4. **Streaming**: Watch responses appear in real-time

### HeyGen Avatar Features

- **Interactive Avatar**: Real-time video avatar with natural movements
- **Voice Conversation**: Bidirectional voice chat with avatar
- **Visual Feedback**: See when avatar is speaking or listening
- **Advanced AI**: Powered by HeyGen's cutting-edge avatar technology

## 🚀 API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "What is machine learning?",
  "conversation_history": [],
  "stream": true
}
```

### Document Ingestion
```http
POST /ingest/file
Content-Type: multipart/form-data

file: <binary-file-data>
```

```http
POST /ingest/text
Content-Type: application/json

{
  "text_content": "Your text here",
  "filename": "optional-name"
}
```

### Health Check
```http
GET /health
```

### Management
```http
GET /documents/count
DELETE /documents
```

## 🔍 How It Works

1. **Document Processing**:
   - Files are loaded using LangChain document loaders
   - Text is split into semantic chunks (1000 chars, 200 overlap)
   - Chunks are embedded using Azure OpenAI
   - Embeddings stored in Weaviate vector database

2. **Query Processing**:
   - User query is embedded using same model
   - Similarity search retrieves relevant document chunks
   - Context is provided to Azure OpenAI for response generation
   - Response is streamed back to the user

3. **RAG Pipeline**:
   ```
   Query → Embed → Search → Context → LLM → Stream → User
   ```

## 🧪 Development

### Backend Development

```bash
cd backend

# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
python -m uvicorn app.main:app --reload

# Run tests (if available)
pytest

# Format code
black .
isort .
```

### Frontend Development

```bash
cd frontend

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Project Structure

```
RAG/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   └── config.py        # Configuration
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── azure_openai_client.py
│   │   ├── weaviate_client.py
│   │   └── document_service.py
│   ├── scripts/
│   │   └── ingest.py        # CLI ingestion script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBox.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   └── VoiceInput.tsx
│   │   ├── types/
│   │   │   └── speech.d.ts
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🐛 Troubleshooting

### Common Issues

**Weaviate Connection Failed**
```bash
# Check if Weaviate is running
docker ps | grep weaviate

# Restart Weaviate
docker restart weaviate
```

**Azure OpenAI Authentication**
- Verify API key and endpoint in `.env`
- Check Azure OpenAI resource is active
- Ensure models are deployed

**Avatar Not Working**
- Verify HeyGen API key in `.env`
- Check HeyGen account has API access enabled
- Allow microphone and camera permissions
- Check browser console for WebRTC errors

**CORS Issues**
- Ensure backend CORS settings include frontend URL
- Check if both frontend and backend are running

### Logs and Debugging

```bash
# Backend logs
cd backend
python -m uvicorn app.main:app --log-level debug

# Check Weaviate logs
docker logs weaviate

# Frontend console
# Open browser developer tools → Console
```

## 📈 Performance Optimization

- **Chunking**: Adjust `chunk_size` and `chunk_overlap` in config
- **Retrieval**: Modify `max_retrieved_docs` for context vs. speed
- **Caching**: Consider Redis for embedding cache
- **Scaling**: Use Weaviate Cloud for production

## 🔐 Security Considerations

- Store Azure OpenAI keys securely
- Implement authentication for production
- Validate file uploads and content
- Rate limit API endpoints
- Use HTTPS in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Open an issue on GitHub

---

**Built with ❤️ using Azure OpenAI, Weaviate, and React.js** 