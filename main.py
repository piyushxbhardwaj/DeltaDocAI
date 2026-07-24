import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 10000))

    print(f"[INFO] Starting DeltaDoc AI Server on {host}:{port}")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=False
    )
