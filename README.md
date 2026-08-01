# LighteningHub Team - Healthcare Track

## Setup

Requires `ffmpeg` on `PATH` (system package, not pip-installable — used by Whisper for audio decoding):

```bash
brew install ffmpeg        # macOS
sudo apt-get install ffmpeg  # Debian/Ubuntu
```

```bash
pip install -r requirements.txt
cp .env.example .env  # then fill in your Gemma API key
python app.py
```

See `AGENTS.md` for full architecture/setup details and `.steering/` for the project plan.
