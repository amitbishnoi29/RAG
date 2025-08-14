# Chat API Examples

This directory contains working examples demonstrating how to use the `/chat` endpoint with different methods and streaming options.

## Files

- **`chat_examples.html`** - Interactive web page with working examples
- **`README.md`** - This file

## Quick Start

1. **Start the backend server:**
   ```bash
   cd backend
   source venv/bin/activate
   python run.py
   ```

2. **Open the examples page:**
   ```bash
   # Open in browser
   open examples/chat_examples.html
   
   # Or serve it locally
   python -m http.server 8080
   # Then visit: http://localhost:8080/examples/chat_examples.html
   ```

3. **Try both streaming and non-streaming examples side by side!**

## What You'll See

- **Left Panel:** Real-time streaming chat (words appear as they're generated)
- **Right Panel:** Complete response chat (full response appears at once)
- **Bottom Panel:** Request logs showing the entire process

## Features

✅ **Working Examples:** Copy-paste ready code  
✅ **Real-time Logs:** See exactly what's happening  
✅ **Side-by-side Comparison:** Streaming vs Non-streaming  
✅ **Error Handling:** Graceful error management  
✅ **Source Display:** Shows document sources used  

## Backend Must Be Running

Make sure your backend is running on `http://localhost:8000` before testing the examples.

Check backend status:
```bash
curl http://localhost:8000/health
```

## Documentation

For complete API documentation, see: `../CHAT_API_DOCUMENTATION.md` 