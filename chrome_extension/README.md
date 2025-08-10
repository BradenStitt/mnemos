# Memory Service Chrome Extension

This Chrome extension has been modified to work with your own memory service instead of mem0.ai. It removes all authentication requirements and routes API calls to your local service.

## Features

- **No Authentication Required**: The extension works without any login or API keys
- **Memory Storage**: Automatically stores messages when you send them
- **Memory Retrieval**: Searches for relevant memories when you click the memory button
- **Memory Integration**: Adds relevant memories to your prompts
- **Floating Button**: Easy access to memory features with a floating button
- **Keyboard Shortcut**: Use Ctrl+M to open the memory modal

## Setup

### 1. Configure Your Service URL

Edit `chrome_extension/mem0/config.js` to point to your memory service:

```javascript
const CONFIG = {
  SERVICE_BASE_URL: 'http://localhost:8000', // Change this to your service URL
  // ... other config
};
```

### 2. Required API Endpoints

Your service needs to provide these endpoints:

#### GET `/api/cascading-retrieval`
- **Query Parameter**: `text_query` (string)
- **Response**: 
```json
{
  "results": [
    {
      "id": "memory-id",
      "chunk_text": "Memory content",
      "score": 0.95
    }
  ]
}
```

#### POST `/api/store-memory`
- **Request Body**:
```json
{
  "message": "Text to store",
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "extension"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Memory stored successfully",
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "extension"
}
```

### 3. Install the Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome_extension/mem0` folder

## Usage

1. **Automatic Memory Storage**: When you send a message, it's automatically stored in your memory service
2. **Memory Retrieval**: Click the floating memory button (bottom-left) or press Ctrl+M to search for relevant memories
3. **Add Memories to Prompt**: Click "Add to Prompt" to include relevant memories in your message
4. **Individual Memory Addition**: Click the + button on individual memories to add them one by one

## Configuration

### Service Configuration (`config.js`)

- `SERVICE_BASE_URL`: Your memory service URL
- `ENDPOINTS`: API endpoint paths
- `UI`: Visual customization options
- `FEATURES`: Enable/disable specific features

### Features

- **Auto Store Messages**: Automatically stores sent messages
- **Notification Dot**: Shows a green dot when there's text in the input
- **Keyboard Shortcut**: Ctrl+M to open memory modal

## Troubleshooting

1. **Service Not Found**: Make sure your memory service is running and accessible
2. **CORS Issues**: Ensure your service allows requests from the extension
3. **No Memories Found**: Check that your search endpoint is working correctly
4. **Memory Not Stored**: Verify your store endpoint is functioning

## Development

### File Structure

```
chrome_extension/mem0/
├── manifest.json          # Extension configuration
├── config.js              # Service configuration
├── background.js          # Background script (no auth needed)
├── popup.html             # Extension popup (service status)
├── popup.js               # Popup logic
├── content.js             # Main content script
├── chatgpt/
│   └── content.js         # ChatGPT-specific content script
├── sidebar.js             # Sidebar functionality
└── icons/                 # Extension icons
```

### Key Changes Made

1. **Removed Authentication**: No more API keys or login required
2. **Updated API Endpoints**: Routes to your service instead of mem0.ai
3. **Simplified UI**: Removed login popups and auth checks
4. **Configuration File**: Easy service URL management
5. **Error Handling**: Better error handling for service connectivity

## API Integration

The extension expects your service to handle:

1. **Memory Storage**: Store text with metadata
2. **Memory Search**: Find relevant memories based on query
3. **Response Format**: Consistent JSON responses

Make sure your service implements the required endpoints and response formats as specified above. 