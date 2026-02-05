# Voice Cloning with Qwen3-TTS

Professional voice cloning application for Apple Silicon using MLX.

## Features

- 🎙️ **Recording Studio**: Record voice samples with real-time validation
- 🎵 **Voice Library**: Save and manage multiple voice profiles
- 🎬 **Generation Studio**: Generate speech in any saved voice
- ⚡ **Quick Test Mode**: Try voice cloning without saving
- 🌍 **Multi-language**: Support for English and French
- 🎨 **Professional UI**: Clean, accessible interface with keyboard shortcuts

## Quick Start

1. **Select or Record a Voice**
   - Choose "Quick Test" to try without saving
   - Or click "➕ New Voice" to create a saved voice

2. **Record Voice Sample** (Quick Test mode)
   - Read the provided script into your microphone
   - Record at least 10 seconds for best quality
   - System will validate recording quality

3. **Generate Speech**
   - Enter any text in the Generation Studio
   - Click "Generate Voice" or press ⌘+Enter
   - Play or download the generated audio

## Keyboard Shortcuts

- **⌘/Ctrl + Enter**: Generate voice
- **Space**: Start/stop recording (when audio focused)
- **Tab**: Navigate controls

## Voice Recording Tips

- Speak naturally at normal pace
- Keep consistent distance from microphone
- Avoid background noise
- Don't clip audio (keep peak < 0.95)
- Record at least 10 seconds for best results

## Requirements

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10+
- Xcode Command Line Tools (`xcode-select --install`)
- 16GB RAM (for the 0.6B model)

## Setup

### Quick Setup (Recommended)

Run the installation script:
```bash
./install.sh
```

This will automatically:
- Verify system requirements (macOS, Apple Silicon, Python 3.10+)
- Create and configure the virtual environment
- Install all dependencies
- Verify the installation

### Manual Setup

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

2. Open your browser to `http://127.0.0.1:7860`

## Technical Details

- Models: Qwen3-TTS (0.6B-4bit, 0.6B-bf16, 1.7B-4bit)
- Sample Rate: 24kHz
- Framework: MLX for Apple Silicon
- UI: Gradio 4.x

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

**Port already in use:**
- See [RESTART.md](RESTART.md) for instructions on restarting the app
