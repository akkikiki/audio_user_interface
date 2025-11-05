curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/gemma-3n-E2B-it-4bit",
    "audio": ["https://d38nvwmjovqyq6.cloudfront.net/va90web25003/companions/Foundations%20of%20Rock/13.01.mp3"],
    "prompt": "Describe what you hear in these audio files",
    "stream": false,
    "max_tokens": 500
  }'
#    "stream": true,
