from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import traceback
import uvicorn
import os

app = FastAPI()

# Allow your Vercel frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your vercel URL for security later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "YTDL API is running on Render!"}

@app.post("/download")
async def download(request: Request):
    try:
        data = await request.json()
        url = data.get("url")

        if not url:
            return {"error": "URL is required"}

        # Advanced yt-dlp config to bypass common datacenter blocks
        ydl_opts = {
            'format': 'best',
            'dump_single_json': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            # Workarounds for Datacenter IPs
            'source_address': '0.0.0.0', 
            'force_ipv4': True,
            'legacyserverconnect': True,
            # Bypassing Youtube Bot checks
            'cookiefile': None,
            'nocheckcertificate': True,
            # Extremely important: Force YouTube to think this is an Android phone to bypass the "Sign in" web bot checker
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # If standard yt-dlp fails to return formats array, handle gracefuly
            if 'formats' not in info:
                info['formats'] = [{'url': info.get('url'), 'format_id': 'default'}]
                
            return info

    except Exception as e:
        print("Error:")
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

