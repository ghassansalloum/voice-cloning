# Voice Cloning with Qwen3-TTS

A local voice cloning application using Qwen3-TTS via MLX-Audio with a Gradio web interface. Runs entirely on your Mac with Apple Silicon.

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.10+
- 16GB RAM (for the 0.6B model)

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser to `http://localhost:7860`

3. Follow the steps in the UI:
   - Read the reference script aloud and record your voice
   - Enter the text you want spoken in your cloned voice
   - Click "Generate Cloned Voice"
   - Play or download the generated audio

## Notes

- **First run:** The model (~1.2GB) will be downloaded and cached automatically
- **Model:** Uses `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16`
- **Sample rate:** 24000 Hz
- **Recording tips:** Speak clearly in a quiet environment for best results

## Troubleshooting

**Microphone not working:**
- Ensure your browser has permission to access the microphone
- Try using Chrome or Safari

**Out of memory:**
- Close other applications to free up RAM
- The model requires approximately 2-3GB of RAM

**Generation is slow:**
- First generation loads the model (takes longer)
- Subsequent generations are faster
