# Chat API Documentation

## Overview

The `/chat` endpoint provides AI-powered responses using Retrieval-Augmented Generation (RAG) with both streaming and non-streaming options.

**Base URL:** `http://localhost:8000`  
**Endpoint:** `POST /chat`  
**Content-Type:** `application/json`

## Request Format

```json
{
  "message": "Your question here",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous user message",
      "timestamp": "2025-01-01T00:00:00Z"
    },
    {
      "role": "assistant", 
      "content": "Previous assistant response",
      "timestamp": "2025-01-01T00:00:01Z"
    }
  ],
  "stream": true  // true for streaming, false for complete response
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | ✅ Yes | The user's question or message |
| `conversation_history` | array | ❌ No | Previous conversation messages (last 10 used) |
| `stream` | boolean | ❌ No | `true` for SSE streaming, `false` for complete response (default: `true`) |

---

## Method 1: Fetch API + ReadableStream (Recommended for POST)

### Streaming Response (`stream: true`)

```javascript
async function streamingChat(message) {
  try {
    console.log('🚀 Sending streaming request...');
    
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get the readable stream
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let completeResponse = '';

    console.log('📖 Reading streaming response...');

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('🏁 Stream completed');
        break;
      }

      // Decode the chunk
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      // Process each complete line
      for (const line of lines) {
        if (line.trim() && line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          console.log('📡 Received SSE:', data);

          if (data === '[DONE]') {
            console.log('✅ Stream finished');
            break;
          }

          try {
            const parsed = JSON.parse(data);
            
            if (parsed.content !== undefined) {
              console.log('💬 Content chunk:', parsed.content);
              completeResponse += parsed.content;
              
              // Update UI here - each chunk appears immediately
              updateUI(completeResponse);
              
            } else if (parsed.sources) {
              console.log('📚 Sources:', parsed.sources);
              displaySources(parsed.sources);
            }
            
          } catch (error) {
            console.error('❌ Parse error:', error, 'Raw data:', data);
          }
        }
      }
    }

    console.log('🎉 Final response:', completeResponse);
    return completeResponse;

  } catch (error) {
    console.error('❌ Streaming error:', error);
    throw error;
  }
}

// Example usage
streamingChat("What is Python programming?")
  .then(response => console.log('Complete response:', response))
  .catch(error => console.error('Error:', error));
```

### Non-Streaming Response (`stream: false`)

```javascript
async function nonStreamingChat(message) {
  try {
    console.log('🚀 Sending non-streaming request...');
    
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        stream: false  // Get complete response at once
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    console.log('✅ Complete response received');
    console.log('💬 Response:', data.response);
    console.log('📚 Sources:', data.sources);
    
    return data;

  } catch (error) {
    console.error('❌ Request error:', error);
    throw error;
  }
}

// Example usage
nonStreamingChat("What is Python programming?")
  .then(data => {
    console.log('Response:', data.response);
    console.log('Sources:', data.sources);
  })
  .catch(error => console.error('Error:', error));
```

---

## Method 2: fetch-event-source Library

For cleaner SSE handling with POST support:

### Installation
```bash
npm install @microsoft/fetch-event-source
```

### Usage
```javascript
import { fetchEventSource } from '@microsoft/fetch-event-source';

async function chatWithEventSource(message) {
  let completeResponse = '';
  let sources = [];

  try {
    await fetchEventSource('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        stream: true
      }),
      
      onmessage(event) {
        console.log('📡 SSE message:', event.data);
        
        if (event.data === '[DONE]') {
          console.log('✅ Stream completed');
          return;
        }

        try {
          const parsed = JSON.parse(event.data);
          
          if (parsed.content !== undefined) {
            console.log('💬 Content:', parsed.content);
            completeResponse += parsed.content;
            updateUI(completeResponse);
            
          } else if (parsed.sources) {
            console.log('📚 Sources:', parsed.sources);
            sources = parsed.sources;
            displaySources(sources);
          }
          
        } catch (error) {
          console.error('❌ Parse error:', error);
        }
      },
      
      onerror(error) {
        console.error('❌ SSE error:', error);
        throw error;
      },
      
      onclose() {
        console.log('🔌 SSE connection closed');
      }
    });

    return { response: completeResponse, sources };

  } catch (error) {
    console.error('❌ EventSource error:', error);
    throw error;
  }
}

// Example usage
chatWithEventSource("What is Python programming?")
  .then(data => console.log('Final result:', data))
  .catch(error => console.error('Error:', error));
```

---

## Method 3: cURL (Command Line)

### Streaming Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python programming?",
    "stream": true
  }' \
  --no-buffer
```

**Expected Output:**
```
data: {"sources": ["python_programming.md", "web_development.md"]}

data: {"content": "Python"}

data: {"content": " is"}

data: {"content": " a"}

data: {"content": " programming"}

data: {"content": " language..."}

data: [DONE]
```

### Non-Streaming Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python programming?",
    "stream": false
  }'
```

**Expected Output:**
```json
{
  "response": "Python is a programming language...",
  "sources": ["python_programming.md", "web_development.md"]
}
```

---

## Method 4: Python requests

### Streaming with Python
```python
import requests
import json

def streaming_chat(message):
    url = "http://localhost:8000/chat"
    payload = {
        "message": message,
        "stream": True
    }
    
    print(f"🚀 Sending streaming request: {message}")
    
    response = requests.post(
        url, 
        json=payload, 
        stream=True,  # Important for streaming
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        raise Exception(f"HTTP error! status: {response.status_code}")
    
    complete_response = ""
    sources = []
    
    print("📖 Reading streaming response...")
    
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith('data: '):
            data = line[6:]  # Remove 'data: ' prefix
            print(f"📡 Received: {data}")
            
            if data == '[DONE]':
                print("✅ Stream completed")
                break
                
            try:
                parsed = json.loads(data)
                
                if 'content' in parsed:
                    content = parsed['content']
                    print(f"💬 Content: {content}")
                    complete_response += content
                    
                elif 'sources' in parsed:
                    sources = parsed['sources']
                    print(f"📚 Sources: {sources}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Parse error: {e}")
    
    return {"response": complete_response, "sources": sources}

# Example usage
try:
    result = streaming_chat("What is Python programming?")
    print("🎉 Final result:", result)
except Exception as e:
    print(f"❌ Error: {e}")
```

### Non-Streaming with Python
```python
import requests

def non_streaming_chat(message):
    url = "http://localhost:8000/chat"
    payload = {
        "message": message,
        "stream": False
    }
    
    print(f"🚀 Sending non-streaming request: {message}")
    
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"HTTP error! status: {response.status_code}")
    
    data = response.json()
    
    print("✅ Complete response received")
    print(f"💬 Response: {data['response']}")
    print(f"📚 Sources: {data['sources']}")
    
    return data

# Example usage
try:
    result = non_streaming_chat("What is Python programming?")
    print("🎉 Result:", result)
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## Response Formats

### Streaming Response (SSE Format)

**Sources First:**
```
data: {"sources": ["filename1.md", "filename2.md"]}
```

**Content Chunks:**
```
data: {"content": "Hello"}
data: {"content": " world"}
data: {"content": "!"}
```

**End Marker:**
```
data: [DONE]
```

### Non-Streaming Response (JSON)

```json
{
  "response": "Complete response text here...",
  "sources": ["filename1.md", "filename2.md"]
}
```

---

## Error Handling

### Streaming Errors
```javascript
// In SSE stream
data: {"error": "Error message here"}
```

### HTTP Errors
- `400` - Bad Request (invalid JSON, missing message)
- `500` - Internal Server Error (AI service error, database error)
- `503` - Service Unavailable (dependencies down)

### Example Error Handling
```javascript
async function robustStreamingChat(message) {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, stream: true })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`HTTP ${response.status}: ${errorData.detail || 'Unknown error'}`);
    }

    // ... streaming logic
    
  } catch (error) {
    if (error.name === 'TypeError') {
      console.error('❌ Network error:', error.message);
    } else if (error.message.includes('HTTP')) {
      console.error('❌ Server error:', error.message);
    } else {
      console.error('❌ Unexpected error:', error);
    }
    throw error;
  }
}
```

---

## Best Practices

### ✅ Do:
- Use `stream: true` for real-time user experiences
- Use `stream: false` for batch processing or when you need the complete response
- Handle errors gracefully
- Include conversation history for context
- Process chunks immediately in streaming mode
- Use `setTimeout(() => {...}, 0)` to prevent React batching issues

### ❌ Don't:
- Mix streaming and non-streaming in the same request
- Ignore the `[DONE]` marker in streaming
- Forget to handle network errors
- Send extremely long messages (max_tokens limit applies)
- Make too many concurrent requests

---

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Examples Repository

All examples above are working code that you can copy and use directly. The backend logs will show real-time streaming progress:

```
INFO - 🌊 Starting SSE response generation
INFO - 📚 Sending sources  
INFO - 📝 SSE: Sending chunk #1: 'Hello'
INFO - 📝 SSE: Sending chunk #2: ' world'
INFO - ✅ SSE: Completed with 67 chunks
```

Choose the method that best fits your use case:
- **Fetch + ReadableStream**: Most flexible, works in all browsers
- **fetch-event-source**: Cleaner code, requires additional dependency
- **cURL**: Great for testing and scripts
- **Python requests**: Perfect for backend integration 