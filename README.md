# Voice Cloning with Qwen3-TTS

A local voice cloning application using Qwen3-TTS via MLX-Audio with a Gradio web interface. Runs entirely on your Mac with Apple Silicon.

## Features

- **Voice Profiles**: Save and manage multiple voice profiles for quick reuse
- **Guest Mode**: Try voice cloning without creating a profile
- **Customizable Scripts**: Edit the reference script used for voice capture
- **Re-record Profiles**: Update existing profiles with new recordings
- **Local Processing**: All processing happens on your device

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

2. Open your browser to `http://127.0.0.1:7860`

### Guest Mode (Quick Start)

1. Read the reference script aloud and record your voice
2. Enter the text you want spoken in your cloned voice
3. Click "Generate Cloned Voice"
4. Play or download the generated audio

### Using Voice Profiles

1. **Create a Profile**: Open "Create New Profile" in the sidebar, enter a name, record your voice, and click "Save Profile"
2. **Select a Profile**: Use the dropdown to switch between saved profiles
3. **Generate Speech**: With a profile selected, just enter text and generate - no recording needed
4. **Re-record**: Open "Re-record Profile" to update a profile's voice with a new recording
5. **Delete**: Open "Delete Profile" to remove a saved profile

### Settings

- **Global Default Script**: Customize the reference script used for Guest mode and new profiles

## Notes

- **First run**: The model (~1.2GB) will be downloaded and cached automatically
- **Model**: Uses `Qwen/Qwen3-TTS-12Hz-0.6B-Base`
- **Sample rate**: 24000 Hz
- **Recording tips**: Speak clearly in a quiet environment for best results
- **Profile storage**: Profiles are saved in the `profiles/` directory

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
