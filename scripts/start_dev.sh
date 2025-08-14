#!/bin/bash

echo "🚀 Starting RAG Chatbot with HeyGen Avatar..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

# Check dependencies
echo "📋 Checking dependencies..."

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Backend .env file not found. Creating from example..."
    if [ -f "docs/env-example.txt" ]; then
        cp docs/env-example.txt backend/.env
        echo "📝 Please edit backend/.env with your API keys before continuing."
        echo "Required: AZURE_OPENAI_API_KEY, HEYGEN_API_KEY"
        read -p "Press Enter when you've updated the .env file..."
    else
        echo "❌ env-example.txt not found. Please create backend/.env manually."
        exit 1
    fi
fi

# Start Weaviate
echo "🗄️  Starting Weaviate..."
if port_in_use 8080; then
    echo "✅ Weaviate already running on port 8080"
else
    docker run -d \
        --name weaviate-rag \
        -p 8080:8080 \
        -e QUERY_DEFAULTS_LIMIT=25 \
        -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
        -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
        semitechnologies/weaviate:latest
    
    echo "⏳ Waiting for Weaviate to start..."
    sleep 10
    
    if port_in_use 8080; then
        echo "✅ Weaviate started successfully"
    else
        echo "❌ Failed to start Weaviate"
        exit 1
    fi
fi

# Start Backend
echo "🔧 Starting FastAPI backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "🚀 Starting backend server..."
python run.py &
BACKEND_PID=$!

cd ..

# Start Frontend
echo "⚛️  Starting React frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo "🚀 Starting frontend server..."
npm start &
FRONTEND_PID=$!

cd ..

# Wait a moment for servers to start
sleep 5

echo ""
echo "🎉 RAG Chatbot with HeyGen Avatar is starting!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🗄️  Weaviate: http://localhost:8080"
echo ""
echo "💡 To test the system:"
echo "1. Upload some documents using the UI or CLI:"
echo "   cd backend && python scripts/ingest.py ../docs/sample_document.md"
echo "2. Click the video icon to start the HeyGen avatar"
echo "3. Ask questions about your documents!"
echo ""
echo "⏹️  To stop all services, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    docker stop weaviate-rag 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for user to stop
wait 