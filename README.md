# Saturn Wikipedia Chatbot

A Streamlit chatbot that answers questions using Wikipedia and suggests YouTube videos for any topic. Supports spelling correction and multi-language Wikipedia answers.

## Features
- Wikipedia Q&A with paragraph gaps
- YouTube video search for any topic (just include 'video' in your prompt)
- Spelling correction for queries
- Multi-language support (e.g., 'in Hindi')
- Modern chat UI with fixed input at the bottom

## Deploy on Render
1. Push all files to your GitHub repository.
2. On Render, create a new Web Service:
   - Build Command: `sh setup.sh`
   - Start Command: `streamlit run wikipedia_chatbot.py --server.port=$PORT --server.address=0.0.0.0`
3. Make sure your repo includes:
   - `wikipedia_chatbot.py`
   - `requirements.txt`
   - `Procfile`
   - `setup.sh`

## Environment Variables
- No special environment variables are required unless you want to hide your YouTube API key.

## Example Usage
- "Who is elonn mussk?"
- "Suggest me some quantum computing video"
- "Who is Sundar Pichai in Hindi?"

---

Made with ❤️ using Streamlit, Wikipedia, and YouTube Data API.
