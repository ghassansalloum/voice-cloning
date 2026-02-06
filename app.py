"""Voice Cloning Application using Qwen3-TTS with Voice Management."""

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import gradio as gr
import librosa
import mlx.core as mx
import numpy as np
import soundfile as sf

# Global model cache for lazy loading
_model = None
_current_model_id = None
SAMPLE_RATE = 24000  # Qwen3-TTS output sample rate

# Available models (id, display_name, description)
AVAILABLE_MODELS = [
    ("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit", "0.6B 4-bit (Fast)", "Fastest, lower memory, slight quality tradeoff"),
    ("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16", "0.6B bf16 (Balanced)", "Good balance of speed and quality"),
    ("mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit", "1.7B 4-bit (Quality)", "Better quality, moderate speed"),
]
DEFAULT_MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit"

# Voices directory
VOICES_DIR = Path(__file__).parent / "voices"
VOICES_INDEX = VOICES_DIR / "voices.json"

# Default reference script - pangram with diverse phonemes for voice capture
DEFAULT_REFERENCE_SCRIPT = """The quick brown fox jumps over the lazy dog.
She sells seashells by the seashore.
Peter Piper picked a peck of pickled peppers.
How much wood would a woodchuck chuck if a woodchuck could chuck wood?"""

# Guest voice constant
GUEST_VOICE_ID = "quick-test"


def _load_voices_data() -> dict:
    """Load the raw voices.json data."""
    VOICES_DIR.mkdir(exist_ok=True)
    if not VOICES_INDEX.exists():
        return {"voices": []}
    try:
        with open(VOICES_INDEX, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"voices": []}


def _save_voices_data(data: dict) -> None:
    """Save the raw voices.json data."""
    VOICES_DIR.mkdir(exist_ok=True)
    with open(VOICES_INDEX, "w") as f:
        json.dump(data, f, indent=2)


def get_default_script() -> str:
    """Get global default script from voices.json or fallback."""
    data = _load_voices_data()
    return data.get("default_script", DEFAULT_REFERENCE_SCRIPT)


def set_default_script(script: str) -> None:
    """Save global default script to voices.json."""
    data = _load_voices_data()
    data["default_script"] = script
    _save_voices_data(data)


def get_voice_script(voice_id: str) -> str:
    """Get the reference script for a specific voice, or global default."""
    if voice_id == GUEST_VOICE_ID:
        return get_default_script()
    voices = load_voices()
    voice = next((v for v in voices if v["id"] == voice_id), None)
    if voice and "ref_script" in voice:
        return voice["ref_script"]
    return get_default_script()


def get_selected_model_id() -> str:
    """Get the currently selected model ID from settings."""
    data = _load_voices_data()
    return data.get("selected_model", DEFAULT_MODEL_ID)


def set_selected_model_id(model_id: str) -> None:
    """Save the selected model ID to settings."""
    data = _load_voices_data()
    data["selected_model"] = model_id
    _save_voices_data(data)


def get_model():
    """Lazy load the TTS model, reloading if model selection changed."""
    global _model, _current_model_id
    selected_model_id = get_selected_model_id()

    if _model is None or _current_model_id != selected_model_id:
        from mlx_audio.tts.utils import load_model
        _model = load_model(selected_model_id)
        _current_model_id = selected_model_id
    return _model


def get_model_choices() -> list[tuple[str, str]]:
    """Get list of (display_name, model_id) tuples for dropdown."""
    return [(f"{name} - {desc}", model_id) for model_id, name, desc in AVAILABLE_MODELS]


# Available languages for TTS
AVAILABLE_LANGUAGES = [
    ("english", "English"),
    ("french", "French"),
]
DEFAULT_LANGUAGE = "english"


def get_selected_language() -> str:
    """Get the currently selected language from settings."""
    data = _load_voices_data()
    return data.get("selected_language", DEFAULT_LANGUAGE)


def set_selected_language(language: str) -> None:
    """Save the selected language to settings."""
    data = _load_voices_data()
    data["selected_language"] = language
    _save_voices_data(data)


def get_language_choices() -> list[tuple[str, str]]:
    """Get list of (display_name, lang_code) tuples for dropdown."""
    return [(display, code) for code, display in AVAILABLE_LANGUAGES]


# ============================================================================
# Voice Management Functions
# ============================================================================

def load_voices() -> list[dict]:
    """Load all voices from voices.json."""
    data = _load_voices_data()
    return data.get("voices", [])


def save_voices_index(voices: list[dict]) -> None:
    """Persist voice index to voices.json, preserving other fields."""
    data = _load_voices_data()
    data["voices"] = voices
    _save_voices_data(data)


def create_voice(name: str, audio_data: np.ndarray, sample_rate: int, ref_script: str | None = None) -> str:
    """
    Create a new voice with voice recording.

    Args:
        name: Voice display name
        audio_data: Audio data as numpy array (float32, mono)
        sample_rate: Audio sample rate
        ref_script: Custom reference script (uses global default if None)

    Returns:
        Voice ID of created voice
    """
    voice_id = str(uuid.uuid4())
    voice_dir = VOICES_DIR / voice_id
    voice_dir.mkdir(parents=True, exist_ok=True)

    # Use provided script or global default
    script = ref_script if ref_script else get_default_script()

    # Save audio file
    audio_path = voice_dir / "audio.wav"
    sf.write(str(audio_path), audio_data, sample_rate)

    # Update voices index
    voices = load_voices()
    voices.append({
        "id": voice_id,
        "name": name,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "ref_script": script
    })
    save_voices_index(voices)

    return voice_id


def delete_voice(voice_id: str) -> bool:
    """
    Delete a voice and its files.

    Args:
        voice_id: ID of voice to delete

    Returns:
        True if deleted, False if not found
    """
    if voice_id == GUEST_VOICE_ID:
        return False

    voices = load_voices()
    voice = next((v for v in voices if v["id"] == voice_id), None)
    if not voice:
        return False

    # Remove from index
    voices = [v for v in voices if v["id"] != voice_id]
    save_voices_index(voices)

    # Delete voice directory
    voice_dir = VOICES_DIR / voice_id
    if voice_dir.exists():
        import shutil
        shutil.rmtree(voice_dir)

    return True


def get_voice_data(voice_id: str) -> tuple[str, str] | None:
    """
    Get audio path and ref_script for a voice.

    Args:
        voice_id: Voice ID

    Returns:
        Tuple of (audio_path, ref_script), or None if not found
    """
    audio_path_str = get_voice_audio_path(voice_id)
    if audio_path_str is None:
        return None
    ref_script = get_voice_script(voice_id)
    return audio_path_str, ref_script


def get_voice_audio_path(voice_id: str) -> str | None:
    """
    Get the audio file path for a voice.

    Args:
        voice_id: Voice ID

    Returns:
        Path to audio file, or None if not found
    """
    if voice_id == GUEST_VOICE_ID:
        return None

    audio_path = VOICES_DIR / voice_id / "audio.wav"
    if not audio_path.exists():
        return None
    return str(audio_path)


def update_voice_recording(voice_id: str, audio_data: np.ndarray, sample_rate: int, ref_script: str) -> bool:
    """
    Re-record a voice with new audio and script.

    Args:
        voice_id: ID of voice to update
        audio_data: New audio data as numpy array (float32, mono)
        sample_rate: Audio sample rate
        ref_script: Reference script used for recording

    Returns:
        True if updated successfully, False if voice not found
    """
    if voice_id == GUEST_VOICE_ID:
        return False

    voices = load_voices()
    voice_idx = next((i for i, v in enumerate(voices) if v["id"] == voice_id), None)
    if voice_idx is None:
        return False

    voice_dir = VOICES_DIR / voice_id

    # Save new audio file
    audio_path = voice_dir / "audio.wav"
    sf.write(str(audio_path), audio_data, sample_rate)

    # Update voice metadata
    voices[voice_idx]["ref_script"] = ref_script
    save_voices_index(voices)

    return True


def get_voice_choices() -> list[tuple[str, str]]:
    """Get list of (display_name, voice_id) tuples for dropdown."""
    choices = [("Quick Test (record new voice)", GUEST_VOICE_ID)]
    voices = load_voices()
    for v in voices:
        choices.append((v["name"], v["id"]))
    return choices


def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    """Normalize audio data to float32 mono."""
    # Convert to float32 if needed
    if audio_data.dtype == np.int16:
        audio_data = audio_data.astype(np.float32) / 32768.0
    elif audio_data.dtype == np.int32:
        audio_data = audio_data.astype(np.float32) / 2147483648.0

    # Handle stereo audio - convert to mono
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)

    return audio_data


def validate_recording(audio_tuple) -> tuple[bool, str]:
    """
    Validate a recording for quality and duration.

    Args:
        audio_tuple: Gradio audio tuple (sample_rate, audio_data)

    Returns:
        (is_valid, message) tuple
    """
    if audio_tuple is None:
        return False, "No recording found. Please record your voice first."

    sample_rate, audio_data = audio_tuple
    audio_data = normalize_audio(audio_data)

    # Check duration (at least 3 seconds)
    duration = len(audio_data) / sample_rate
    if duration < 3.0:
        return False, f"Recording too short ({duration:.1f}s). Please record at least 3 seconds."

    # Check if recording is too quiet (RMS amplitude)
    rms = np.sqrt(np.mean(audio_data ** 2))
    if rms < 0.01:
        return False, "Recording too quiet. Please speak louder or move closer to the microphone."

    # Check if recording is clipping
    peak = np.max(np.abs(audio_data))
    if peak > 0.95:
        return False, f"Recording is clipping (peak: {peak:.2f}). Please reduce input volume or move away from microphone."

    return True, f"✓ Recording valid ({duration:.1f}s, peak: {peak:.2f})"


def on_audio_recorded(audio_tuple):
    """Provide immediate feedback when audio is recorded."""
    is_valid, message = validate_recording(audio_tuple)
    status_type = "success" if is_valid else "warning"
    return format_status(message, status_type)


# ============================================================================
# Voice Generation Functions
# ============================================================================

def clone_voice_guest(reference_audio, target_text: str, ref_script: str | None = None) -> str:
    """
    Clone voice from reference audio (Guest mode).

    Args:
        reference_audio: Tuple of (sample_rate, audio_data) from Gradio microphone
        target_text: Text to synthesize in the cloned voice
        ref_script: Custom reference script (uses global default if None)

    Returns:
        Path to generated WAV file
    """
    if reference_audio is None:
        raise gr.Error("Please record your voice reading the script first.")

    if not target_text or not target_text.strip():
        raise gr.Error("Please enter some text to generate speech.")

    # Use provided script or global default
    script = ref_script if ref_script else get_default_script()

    sample_rate, audio_data = reference_audio
    audio_data = normalize_audio(audio_data)

    # Resample to model's expected sample rate (24000 Hz) if needed
    if sample_rate != SAMPLE_RATE:
        audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=SAMPLE_RATE)

    # Convert to mlx array for ref_audio parameter
    ref_audio_mx = mx.array(audio_data.astype(np.float32))

    # Load model and generate
    model = get_model()

    print(f"[TTS] Generating with lang_code={get_selected_language()}")

    # Generate speech with cloned voice using mlx-audio
    results = list(model.generate(
        text=target_text.strip(),
        ref_audio=ref_audio_mx,
        ref_text=script,
        lang_code=get_selected_language(),
    ))

    # Convert mlx array to numpy and save
    audio_data = np.array(results[0].audio)

    # Save to temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
        sf.write(out_file.name, audio_data, SAMPLE_RATE)
        return out_file.name


def generate_from_voice(voice_id: str, target_text: str) -> str:
    """
    Generate speech using a saved voice.

    Args:
        voice_id: Voice ID to use
        target_text: Text to synthesize

    Returns:
        Path to generated WAV file
    """
    if not target_text or not target_text.strip():
        raise gr.Error("Please enter some text to generate speech.")

    voice_data = get_voice_data(voice_id)
    if voice_data is None:
        raise gr.Error("Voice data not found. Please recreate the voice.")

    ref_audio_path, ref_script = voice_data

    # Load reference audio and convert to mlx array
    audio_data, file_sample_rate = sf.read(ref_audio_path)

    # Resample to model's expected sample rate (24000 Hz) if needed
    if file_sample_rate != SAMPLE_RATE:
        audio_data = librosa.resample(audio_data, orig_sr=file_sample_rate, target_sr=SAMPLE_RATE)

    ref_audio_mx = mx.array(audio_data.astype(np.float32))

    model = get_model()

    print(f"[TTS] Generating with lang_code={get_selected_language()}")

    # Generate speech with voice's reference audio
    results = list(model.generate(
        text=target_text.strip(),
        ref_audio=ref_audio_mx,
        ref_text=ref_script,
        lang_code=get_selected_language(),
    ))

    # Convert mlx array to numpy and save
    audio_data = np.array(results[0].audio)

    # Save to temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
        sf.write(out_file.name, audio_data, SAMPLE_RATE)
        return out_file.name


# ============================================================================
# Gradio UI
# ============================================================================

def format_status(message: str, status_type: str = "info") -> str:
    """
    Format a status message with appropriate styling.

    Args:
        message: The status message text
        status_type: One of "success", "error", "info", "warning"

    Returns:
        Formatted markdown string with CSS classes
    """
    return f'<div class="status-message status-{status_type}">{message}</div>'


def check_microphone_status():
    """Provide guidance on microphone access."""
    return format_status(
        "Ensure microphone permissions are enabled in your browser and system settings.",
        "info"
    )


def create_ui():
    """Create and configure the Gradio interface."""

    custom_css = """
/* Import Braun-inspired fonts - thin geometric sans-serif */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600&family=DIN+Condensed:wght@400;700&family=Roboto+Mono:wght@300;400&display=swap');

/* Root variables - Braun/Dieter Rams light aesthetic */
:root {
    /* Backgrounds - Cream/White palette */
    --bg-primary: #E8E5DC;
    --bg-secondary: #DDD9CE;
    --bg-tertiary: #F2F0EA;
    --surface-panel: #FFFFFF;

    /* Text - High contrast on light */
    --text-primary: #1A1A1A;
    --text-secondary: #5A5A5A;
    --text-disabled: #9E9E9E;
    --text-label: #3A3A3A;

    /* Accents - Orange primary, Mint success */
    --accent-orange: #FF5722;
    --accent-orange-hover: #E64A19;
    --accent-mint: #7FC8A9;
    --accent-blue: #5B9BD5;
    --accent-red: #D84315;

    /* Borders & Shadows */
    --border-light: #CAC6BA;
    --border-medium: #A8A29E;
    --border-dark: #78716C;
    --shadow-subtle: rgba(0, 0, 0, 0.08);
    --shadow-medium: rgba(0, 0, 0, 0.12);

    /* Hardware Elements */
    --knob-body: #D4D1C6;
    --knob-indicator: #FF5722;
    --led-active: #FF5722;
    --led-inactive: #CAC6BA;

    /* Legacy aliases for compatibility */
    --success: #7FC8A9;
    --warning: #FFA500;
    --error: #D84315;
    --info: #5B9BD5;
    --border: #CAC6BA;
    --border-focus: #FF5722;
}

/* Typography - Thin geometric sans-serif */
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-primary) !important;
    background-image:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.02'/%3E%3C/svg%3E") !important;
    background-attachment: fixed !important;
}

.gradio-container h1 {
    font-family: 'DIN Condensed', 'Inter', sans-serif !important;
    font-weight: 400 !important;
    font-size: 32px !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: var(--text-primary) !important;
    margin-bottom: 8px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid var(--border-medium) !important;
    position: relative !important;
}

/* Subtitle text after h1 */
.gradio-container h1 + div p,
.gradio-container h1 + * p {
    font-size: 11px !important;
    font-weight: 300 !important;
    color: var(--text-secondary) !important;
    margin-top: 4px !important;
    margin-bottom: 16px !important;
    line-height: 1.4 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
}

.gradio-container h2 {
    font-family: 'DIN Condensed', 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 16px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-primary) !important;
    margin-bottom: 16px !important;
}

.gradio-container h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-label) !important;
    margin-bottom: 12px !important;
}

.gradio-container label {
    font-weight: 400 !important;
    font-size: 9px !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}

.gradio-container p,
.gradio-container .markdown {
    font-size: 13px !important;
    font-weight: 300 !important;
    line-height: 1.6 !important;
    color: var(--text-secondary) !important;
}

.gradio-container .markdown ul,
.gradio-container .markdown li {
    color: var(--text-secondary) !important;
}

/* Orange bullet points */
.gradio-container .markdown li::marker {
    color: var(--accent-orange) !important;
}

/* Button hierarchy - Tactile depth */
.gradio-container button {
    font-weight: 400 !important;
    border-radius: 4px !important;
    transition: all 0.15s ease-out !important;
    border: 1px solid var(--border-medium) !important;
    background: linear-gradient(180deg, #FFFFFF 0%, var(--bg-primary) 100%) !important;
    color: var(--text-primary) !important;
    box-shadow: 0 1px 2px var(--shadow-subtle), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
}

.gradio-container button:hover {
    background: linear-gradient(180deg, #FFFFFF 0%, var(--bg-secondary) 100%) !important;
    border-color: var(--accent-orange) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 4px var(--shadow-medium), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
}

.gradio-container button.primary {
    background: linear-gradient(180deg, #FF6B35 0%, var(--accent-orange) 100%) !important;
    color: #FFFFFF !important;
    border-color: var(--accent-orange-hover) !important;
    border-radius: 24px !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
    box-shadow: 0 2px 8px rgba(255, 87, 34, 0.3) !important;
}

.gradio-container button.primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(255, 87, 34, 0.4) !important;
    background: linear-gradient(180deg, #FF7043 0%, var(--accent-orange-hover) 100%) !important;
}

.gradio-container button.stop {
    background: linear-gradient(180deg, #FFFFFF 0%, var(--bg-tertiary) 100%) !important;
    color: var(--accent-red) !important;
    border: 2px solid var(--accent-red) !important;
}

.gradio-container button.stop:hover {
    background: linear-gradient(180deg, #EF5350 0%, var(--accent-red) 100%) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 8px rgba(216, 67, 21, 0.3) !important;
}

.gradio-container button:disabled {
    opacity: 0.3 !important;
    cursor: not-allowed !important;
}

.gradio-container button:active {
    transform: translateY(0) !important;
    box-shadow: inset 0 2px 4px var(--shadow-medium) !important;
}

/* Accordion hierarchy - Hardware panel with LED */
.gradio-container .accordion {
    border: 1px solid var(--border-medium) !important;
    border-radius: 4px !important;
    margin-bottom: 12px !important;
    transition: all 0.15s ease-out !important;
    background: var(--bg-secondary) !important;
    box-shadow: 0 1px 2px var(--shadow-subtle), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
}

.gradio-container .accordion:hover {
    border-color: var(--border-dark) !important;
    box-shadow: 0 2px 4px var(--shadow-medium), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
}

.gradio-container .accordion[open] {
    border-color: var(--border-dark) !important;
    box-shadow: 0 2px 4px var(--shadow-medium), inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
}

.gradio-container .accordion summary {
    font-weight: 400 !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 12px 16px !important;
    cursor: pointer !important;
    user-select: none !important;
    color: var(--text-primary) !important;
}

/* LED indicator - Orange when open, Gray outline when closed */
.gradio-container .accordion[open] summary::before {
    content: "●" !important;
    color: var(--led-active) !important;
    margin-right: 8px !important;
    font-size: 12px !important;
}

.gradio-container .accordion:not([open]) summary::before {
    content: "○" !important;
    color: var(--led-inactive) !important;
    margin-right: 8px !important;
    font-size: 12px !important;
}

/* Danger zone accordion */
.gradio-container .accordion.danger {
    border-color: var(--accent-red) !important;
    background: rgba(216, 67, 21, 0.05) !important;
}

.gradio-container .accordion.danger summary {
    color: var(--accent-red) !important;
}

.gradio-container .accordion.danger:hover {
    border-color: var(--accent-red) !important;
    box-shadow: 0 2px 4px rgba(216, 67, 21, 0.15) !important;
}

/* Form inputs - Inset recessed style */
.gradio-container input[type="text"],
.gradio-container textarea,
.gradio-container select {
    border: 1px solid var(--border-light) !important;
    border-radius: 3px !important;
    padding: 12px 16px !important;
    transition: all 0.15s ease-out !important;
    font-family: 'Inter', sans-serif !important;
    background: var(--surface-panel) !important;
    color: var(--text-primary) !important;
    font-size: 13px !important;
    font-weight: 300 !important;
    box-shadow: inset 0 1px 2px var(--shadow-subtle) !important;
}

.gradio-container input[type="text"]:focus,
.gradio-container textarea:focus,
.gradio-container select:focus {
    outline: none !important;
    border-color: var(--accent-orange) !important;
    box-shadow: inset 0 1px 2px var(--shadow-subtle), 0 0 0 2px rgba(255, 87, 34, 0.15) !important;
}

.gradio-container input[type="text"]::placeholder,
.gradio-container textarea::placeholder {
    color: var(--text-disabled) !important;
}

/* Audio components - Speaker grille pattern */
.gradio-container .audio-container,
.gradio-container .audio-wrapper {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 4px !important;
    padding: 20px !important;
    box-shadow: 0 1px 3px var(--shadow-subtle), inset 0 0 0 1px rgba(255, 255, 255, 0.5) !important;
    position: relative !important;
}

/* Speaker grille dot pattern overlay */
.gradio-container .audio-container::after,
.gradio-container .audio-wrapper::after {
    content: "" !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    background-image: radial-gradient(circle, var(--border-medium) 1px, transparent 1px) !important;
    background-size: 8px 8px !important;
    background-position: 4px 4px !important;
    opacity: 0.3 !important;
    pointer-events: none !important;
    border-radius: 4px !important;
}

.gradio-container .audio-container span,
.gradio-container .audio-wrapper span,
.gradio-container .audio-container div,
.gradio-container .audio-wrapper div {
    color: var(--text-primary) !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* Keyboard focus states - Orange outlines */
.gradio-container button:focus-visible,
.gradio-container .accordion summary:focus-visible,
.gradio-container input:focus-visible,
.gradio-container textarea:focus-visible,
.gradio-container select:focus-visible {
    outline: 2px solid var(--accent-orange) !important;
    outline-offset: 2px !important;
}

/* Spacing - 8px grid system */
.gradio-container hr {
    border: none !important;
    border-top: 1px solid var(--border-light) !important;
    margin: 16px 0 !important;
}

/* Sidebar styling - Clean border */
.gradio-container > .row > .column:first-child {
    position: relative !important;
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-medium) !important;
}

/* Sidebar specific padding */
.gradio-container .block:first-child > .form > .col:first-child {
    padding: 16px !important;
}

/* Main content max-width constraint */
.gradio-container > .row > .column:last-child {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Status messages - Subtle border-left accent */
.gradio-container .markdown.status-message {
    display: block !important;
    padding: 12px 16px !important;
    border-radius: 3px !important;
    font-style: normal !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    margin: 8px 0 !important;
    border: 1px solid var(--border-medium) !important;
    border-left: 3px solid transparent !important;
    box-shadow: 0 1px 2px var(--shadow-subtle) !important;
}

/* Success status - Mint */
.gradio-container .markdown.status-success {
    background: rgba(127, 200, 169, 0.1) !important;
    border-left-color: var(--accent-mint) !important;
    color: #2D5F4D !important;
}

/* Error status - Red */
.gradio-container .markdown.status-error {
    background: rgba(216, 67, 21, 0.1) !important;
    border-left-color: var(--accent-red) !important;
    color: #8B2E0B !important;
}

/* Info status - Blue */
.gradio-container .markdown.status-info {
    background: rgba(91, 155, 213, 0.1) !important;
    border-left-color: var(--accent-blue) !important;
    color: #2E4A6D !important;
}

/* Warning status - Orange */
.gradio-container .markdown.status-warning {
    background: rgba(255, 165, 0, 0.1) !important;
    border-left-color: var(--warning) !important;
    color: #8B5A00 !important;
}

/* Recording feedback - Mechanical blink */
.gradio-container .audio-container {
    position: relative !important;
}

@keyframes mechanicalBlink {
    0%, 50% { opacity: 1; }
    50.01%, 100% { opacity: 0.3; }
}

/* Recording indicator - Orange LED */
.gradio-container .audio-container:has(button[aria-label*="Stop"])::before {
    content: "● REC" !important;
    position: absolute !important;
    top: 12px !important;
    right: 12px !important;
    background: var(--accent-orange) !important;
    color: #FFFFFF !important;
    padding: 4px 8px !important;
    border-radius: 2px !important;
    font-weight: 500 !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    z-index: 10 !important;
    animation: mechanicalBlink 1s step-end infinite !important;
}

/* Primary action buttons - larger and more prominent */
.gradio-container button[scale="2"] {
    font-size: 14px !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
}

/* Recording tips panel - Clean, no rotation */
.recording-tips-panel {
    background: var(--surface-panel) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 3px !important;
    box-shadow: inset 0 1px 2px var(--shadow-subtle) !important;
    padding: 12px !important;
}

/* Final polish */
.gradio-container {
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}

/* Improve overall spacing - 8px grid */
.gradio-container .block {
    gap: 8px !important;
}

/* Clean up markdown spacing */
.gradio-container .markdown {
    margin-bottom: 8px !important;
}

.gradio-container .markdown:empty {
    display: none !important;
}

/* Vertical spacing between major sections */
.gradio-container .accordion {
    margin-top: 8px !important;
    margin-bottom: 8px !important;
}

.gradio-container .accordion:first-of-type {
    margin-top: 16px !important;
}

/* Recording state - Simple orange border */
.gradio-container .audio-container:has(button[aria-label*="Stop"]) {
    border: 2px solid var(--accent-orange) !important;
    box-shadow: 0 2px 8px rgba(255, 87, 34, 0.3) !important;
    position: relative !important;
}

.gradio-container .audio-container:has(button[aria-label*="Stop"]) label {
    color: var(--accent-orange) !important;
    font-weight: 500 !important;
}

/* Hide Gradio footer */
.gradio-container footer {
    display: none !important;
}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Space bar to start/stop recording (when audio component focused)
    document.addEventListener('keydown', function(e) {
        if (e.code === 'Space' && e.target.closest('.audio-container')) {
            e.preventDefault();
            const recordBtn = e.target.closest('.audio-container').querySelector('button');
            if (recordBtn) recordBtn.click();
        }
    });

    // Ctrl/Cmd + Enter to generate
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.code === 'Enter') {
            e.preventDefault();
            const generateBtn = document.querySelector('button[elem_id="generate-button"]');
            if (generateBtn) generateBtn.click();
        }
    });
});
</script>

<style>
/* Hide non-functional share button in audio output */
.audio-container button[aria-label*="share" i],
.audio-container button[title*="share" i],
audio ~ div button:nth-child(2) {
    display: none !important;
}
</style>
"""

    with gr.Blocks(title="Voice Cloning with Qwen3-TTS") as app:

        # State for tracking current voice selection
        current_voice_id = gr.State(value=GUEST_VOICE_ID)

        with gr.Row():
            # ================================================================
            # Sidebar - Voice Management
            # ================================================================
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("## Voice Library")

                # Voice selector dropdown - ALWAYS VISIBLE
                voice_dropdown = gr.Dropdown(
                    choices=get_voice_choices(),
                    value=GUEST_VOICE_ID,
                    label="Select Voice",
                    interactive=True,
                    elem_id="voice-selector"
                )

                # Voice preview player - VISIBLE when voice selected
                voice_preview_audio = gr.Audio(
                    label="Voice Sample",
                    type="filepath",
                    interactive=False,
                    visible=False
                )

                # Language selector - ALWAYS VISIBLE (frequent use)
                language_dropdown = gr.Dropdown(
                    choices=get_language_choices(),
                    value=get_selected_language(),
                    label="Output Language",
                    interactive=True,
                )
                language_status = gr.Markdown("")

                gr.Markdown("---")

                # Quick Actions - ALWAYS VISIBLE
                gr.Markdown("### Quick Actions")

                with gr.Row():
                    new_voice_btn = gr.Button("New Voice", size="sm")
                    manage_voices_btn = gr.Button("Manage", size="sm")

                # New Voice Section - Initially collapsed, opens on button click
                with gr.Column(visible=False) as new_voice_section:
                    gr.Markdown("#### Create New Voice")
                    new_voice_name = gr.Textbox(
                        label="Voice Name",
                        placeholder="Enter a name for this voice..."
                    )

                    gr.Markdown("**Record your voice reading the script:**")

                    with gr.Row():
                        with gr.Column(scale=2):
                            new_voice_script = gr.Textbox(
                                value=get_default_script(),
                                label="Reference Script (editable)",
                                lines=4,
                                interactive=True
                            )

                            new_voice_audio = gr.Audio(
                                sources=["microphone"],
                                type="numpy",
                                label="Record Voice (press Space when focused)"
                            )
                            new_voice_feedback = gr.Markdown("")

                        with gr.Column(scale=1, elem_classes=["recording-tips-panel"]):
                            gr.Markdown("### Recording Tips")
                            gr.Markdown("""
                            - Speak naturally at normal pace
                            - Keep consistent distance from mic
                            - Record at least 10 seconds
                            - Avoid background noise
                            - Don't clip (peak < 0.95)
                            """)

                    with gr.Row():
                        cancel_new_btn = gr.Button("Cancel", size="sm")
                        save_voice_btn = gr.Button("Save Voice", variant="primary", size="sm")
                    voice_status = gr.Markdown("")

                # Management Section - Initially collapsed, opens on button click
                with gr.Column(visible=False) as manage_section:
                    gr.Markdown("#### Manage Voices")

                    # Re-record Voice
                    gr.Markdown("**Re-record Selected Voice**")
                    rerecord_voice_name = gr.Markdown("*Select a saved voice first*")

                    with gr.Row():
                        with gr.Column(scale=2):
                            rerecord_script = gr.Textbox(
                                value=get_default_script(),
                                label="Reference Script (editable)",
                                lines=4,
                                interactive=True
                            )

                            rerecord_audio = gr.Audio(
                                sources=["microphone"],
                                type="numpy",
                                label="Record New Voice (press Space when focused)"
                            )
                            rerecord_feedback = gr.Markdown("")

                            rerecord_btn = gr.Button("Update Voice", variant="primary", interactive=False)
                            rerecord_status = gr.Markdown("")

                        with gr.Column(scale=1, elem_classes=["recording-tips-panel"]):
                            gr.Markdown("### Recording Tips")
                            gr.Markdown("""
                            - Speak naturally at normal pace
                            - Keep consistent distance from mic
                            - Record at least 10 seconds
                            - Avoid background noise
                            - Don't clip (peak < 0.95)
                            """)

                    gr.Markdown("---")

                    # Delete Voice
                    gr.Markdown("**Delete Voice**")
                    gr.Markdown("⚠️ This action cannot be undone.")
                    delete_confirm_text = gr.Textbox(
                        label="Type voice name to confirm",
                        placeholder="Type voice name to enable delete",
                        interactive=True
                    )

                    delete_voice_btn = gr.Button("Delete Selected Voice", variant="stop", interactive=False)
                    delete_status = gr.Markdown("")

                    with gr.Row():
                        close_manage_btn = gr.Button("Close", size="sm")

                # Keyboard Shortcuts Accordion
                with gr.Accordion("Keyboard Shortcuts", open=False):
                    gr.Markdown("""
    - **⌘/Ctrl + Enter**: Generate voice
    - **Space**: Start/stop recording (when audio component focused)
    - **Tab**: Navigate between controls
    - **Enter**: Activate buttons
    """)

                # Settings Accordion - STILL an accordion (rarely changed)
                with gr.Accordion("Advanced Settings", open=False):
                    gr.Markdown("**Model Selection**")
                    model_dropdown = gr.Dropdown(
                        choices=get_model_choices(),
                        value=get_selected_model_id(),
                        label="TTS Model",
                        interactive=True,
                    )
                    model_status = gr.Markdown("")

                    gr.Markdown("**Global Default Script**")
                    gr.Markdown("*Used for Quick Test mode and new voices.*")
                    settings_script = gr.Textbox(
                        value=get_default_script(),
                        label="Default Reference Script",
                        lines=4,
                        interactive=True
                    )
                    save_settings_btn = gr.Button("Save Settings", variant="primary")
                    settings_status = gr.Markdown("")

            # ================================================================
            # Main Area - Voice Generation
            # ================================================================
            with gr.Column(scale=3):
                gr.Markdown("# Voice Cloning Studio")
                gr.Markdown("Professional voice cloning on Apple Silicon with MLX")

                # Recording Studio section (only for Quick Test mode)
                with gr.Column(visible=True) as recording_section:

                    with gr.Row():
                        with gr.Column(scale=2):
                            gr.Markdown("### Reference Script")
                            gr.Markdown("Read this text clearly into your microphone:")
                            guest_script = gr.Textbox(
                                value=get_default_script(),
                                label="Reference Text (editable)",
                                lines=5,
                                interactive=True
                            )

                        with gr.Column(scale=1, elem_classes=["recording-tips-panel"]):
                            gr.Markdown("### Recording Tips")
                            gr.Markdown("""
                            - Speak naturally at normal pace
                            - Keep consistent distance from mic
                            - Record at least 10 seconds
                            - Avoid background noise
                            - Don't clip (peak < 0.95)
                            """)

                    gr.Markdown("### Record Your Voice")

                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="Click microphone icon or press Space to start recording"
                    )
                    audio_input_feedback = gr.Markdown("")

                # Voice info - Hidden (kept for compatibility with event handlers)
                voice_info = gr.Markdown(visible=False)

                # Voice mode message (when using saved voice)
                voice_mode_info = gr.Markdown(
                    visible=False
                )

                # Generation Studio section (always visible)

                text_input = gr.Textbox(
                    label="Text to Speak",
                    placeholder="Enter any text to generate in your cloned voice...",
                    lines=4
                )

                generate_btn = gr.Button("Generate Voice (⌘+Enter)", variant="primary", size="lg", scale=2, elem_id="generate-button")

                # Output Section
                gr.Markdown("### Output")
                audio_output = gr.Audio(
                    label="Generated Speech",
                    type="filepath",
                    interactive=False
                )

                status = gr.Markdown("")

        # ====================================================================
        # Event Handlers
        # ====================================================================

        def toggle_new_voice():
            """Show new voice section, hide manage section."""
            return gr.update(visible=True), gr.update(visible=False)

        def toggle_manage():
            """Show manage section, hide new voice section."""
            return gr.update(visible=False), gr.update(visible=True)

        def close_new_voice():
            """Hide new voice section."""
            return gr.update(visible=False)

        def close_manage():
            """Hide manage section."""
            return gr.update(visible=False)

        new_voice_btn.click(
            fn=toggle_new_voice,
            outputs=[new_voice_section, manage_section]
        )

        manage_voices_btn.click(
            fn=toggle_manage,
            outputs=[new_voice_section, manage_section]
        )

        cancel_new_btn.click(
            fn=close_new_voice,
            outputs=[new_voice_section]
        )

        close_manage_btn.click(
            fn=close_manage,
            outputs=[manage_section]
        )

        # Wire up audio validation feedback
        new_voice_audio.change(
            fn=on_audio_recorded,
            inputs=[new_voice_audio],
            outputs=[new_voice_feedback]
        )

        rerecord_audio.change(
            fn=on_audio_recorded,
            inputs=[rerecord_audio],
            outputs=[rerecord_feedback]
        )

        audio_input.change(
            fn=on_audio_recorded,
            inputs=[audio_input],
            outputs=[audio_input_feedback]
        )

        def on_voice_change(voice_id):
            """Handle voice selection change."""
            is_guest = voice_id == GUEST_VOICE_ID

            if is_guest:
                voice_text = '<p style="font-size: 15px;"><strong>Active Voice:</strong> <span style="color: var(--primary-green);">Quick Test (record new voice)</span></p>'
                script = get_default_script()
                rerecord_name_text = "*Select a saved voice to re-record*"
                preview_audio = None
                preview_visible = False
                recording_studio_visible = True
                voice_mode_visible = False
            else:
                voices = load_voices()
                voice = next((v for v in voices if v["id"] == voice_id), None)
                name = voice["name"] if voice else "Unknown"
                voice_text = f'<p style="font-size: 15px;"><strong>Active Voice:</strong> <span style="color: var(--primary-green);">{name}</span></p>'
                script = get_voice_script(voice_id)
                rerecord_name_text = f"**Re-recording:** {name}"
                preview_audio = get_voice_audio_path(voice_id)
                preview_visible = True
                recording_studio_visible = False
                voice_mode_visible = False

            return (
                voice_id,  # Update state
                voice_text,  # Update voice info
                gr.update(visible=recording_studio_visible),  # recording_section
                gr.update(visible=voice_mode_visible),  # voice_mode_info
                script,  # Update rerecord_script
                rerecord_name_text,  # Update rerecord_voice_name
                gr.update(interactive=not is_guest),  # Enable/disable rerecord_btn
                "",  # Clear rerecord_status
                "",  # Reset delete confirmation text
                gr.update(value=preview_audio, visible=preview_visible),  # voice_preview_audio
            )

        voice_dropdown.change(
            fn=on_voice_change,
            inputs=[voice_dropdown],
            outputs=[current_voice_id, voice_info, recording_section, voice_mode_info, rerecord_script, rerecord_voice_name, rerecord_btn, rerecord_status, delete_confirm_text, voice_preview_audio]
        )

        def on_save_voice(name, audio, script):
            """Handle new voice creation."""
            if not name or not name.strip():
                current_updates = on_voice_change(GUEST_VOICE_ID)
                return (
                    format_status("Please enter a voice name.", "error"),
                    gr.update(),  # dropdown stays same
                    gr.update(visible=True),  # Keep new voice section open
                    *current_updates
                )

            if audio is None:
                current_updates = on_voice_change(GUEST_VOICE_ID)
                return (
                    format_status("Please record your voice first.", "error"),
                    gr.update(),
                    gr.update(visible=True),  # Keep new voice section open
                    *current_updates
                )

            # Validate recording quality
            is_valid, validation_msg = validate_recording(audio)
            if not is_valid:
                current_updates = on_voice_change(GUEST_VOICE_ID)
                return (
                    format_status(validation_msg, "error"),
                    gr.update(),
                    gr.update(visible=True),  # Keep new voice section open
                    *current_updates
                )

            if not script or not script.strip():
                current_updates = on_voice_change(GUEST_VOICE_ID)
                return (
                    format_status("Please enter a reference script.", "error"),
                    gr.update(),
                    gr.update(visible=True),  # Keep new voice section open
                    *current_updates
                )

            try:
                sample_rate, audio_data = audio
                audio_data = normalize_audio(audio_data)
                voice_id = create_voice(name.strip(), audio_data, sample_rate, script.strip())

                # Update dropdown choices
                new_choices = get_voice_choices()

                # Get all voice change updates for the newly created voice
                voice_updates = on_voice_change(voice_id)

                return (
                    format_status(f"✓ Voice '{name}' saved successfully!", "success"),
                    gr.update(choices=new_choices, value=voice_id),
                    gr.update(visible=False),  # Close new voice section on success
                    *voice_updates  # Include all outputs from on_voice_change
                )
            except Exception as e:
                # Keep current state on error
                current_updates = on_voice_change(GUEST_VOICE_ID)
                return (
                    format_status(f"Error creating voice: {str(e)}", "error"),
                    gr.update(),
                    gr.update(visible=True),  # Keep new voice section open on error
                    *current_updates
                )

        save_voice_btn.click(
            fn=on_save_voice,
            inputs=[new_voice_name, new_voice_audio, new_voice_script],
            outputs=[
                voice_status,
                voice_dropdown,
                new_voice_section,  # Control section visibility
                current_voice_id,
                voice_info,
                recording_section,
                voice_mode_info,
                rerecord_script,
                rerecord_voice_name,
                rerecord_btn,
                rerecord_status,
                delete_confirm_text,
                voice_preview_audio  # All outputs from on_voice_change
            ]
        )

        def on_delete_confirm_change(voice_id, confirm_text):
            """Enable delete button only if typed name matches selected voice."""
            if voice_id == GUEST_VOICE_ID:
                return gr.update(interactive=False)

            voices = load_voices()
            voice = next((v for v in voices if v["id"] == voice_id), None)

            if voice and confirm_text.strip() == voice["name"]:
                return gr.update(interactive=True)
            else:
                return gr.update(interactive=False)

        def on_delete_voice(voice_id):
            """Handle voice deletion."""
            if voice_id == GUEST_VOICE_ID:
                return (
                    format_status("Cannot delete Quick Test voice.", "error"),
                    gr.update(),
                    GUEST_VOICE_ID,
                    "",  # Reset text field
                )

            voices = load_voices()
            voice = next((v for v in voices if v["id"] == voice_id), None)
            name = voice["name"] if voice else "Unknown"

            if delete_voice(voice_id):
                new_choices = get_voice_choices()
                return (
                    format_status(f"✓ Voice '{name}' deleted successfully!", "success"),
                    gr.update(choices=new_choices, value=GUEST_VOICE_ID),
                    GUEST_VOICE_ID,
                    "",  # Reset text field
                )
            else:
                return (
                    format_status("Voice not found.", "error"),
                    gr.update(),
                    voice_id,
                    "",  # Reset text field
                )

        delete_confirm_text.change(
            fn=on_delete_confirm_change,
            inputs=[current_voice_id, delete_confirm_text],
            outputs=[delete_voice_btn]
        )

        delete_voice_btn.click(
            fn=on_delete_voice,
            inputs=[current_voice_id],
            outputs=[delete_status, voice_dropdown, current_voice_id, delete_confirm_text]
        )

        def on_model_change(model_id):
            """Handle model selection change."""
            try:
                set_selected_model_id(model_id)
                # Find the model name for display
                model_name = next((name for mid, name, _ in AVAILABLE_MODELS if mid == model_id), "Unknown")
                return format_status(f"Model changed to {model_name}. Will load on next generation.", "info")
            except Exception as e:
                return format_status(f"Error changing model: {str(e)}", "error")

        model_dropdown.change(
            fn=on_model_change,
            inputs=[model_dropdown],
            outputs=[model_status]
        )

        def on_language_change(language):
            """Handle language selection change."""
            try:
                set_selected_language(language)
                display_name = next((d for c, d in AVAILABLE_LANGUAGES if c == language), language)
                return format_status(f"Language set to {display_name}.", "success")
            except Exception as e:
                return format_status(f"Error changing language: {str(e)}", "error")

        language_dropdown.change(
            fn=on_language_change,
            inputs=[language_dropdown],
            outputs=[language_status]
        )

        def on_save_settings(script):
            """Handle saving global default script."""
            if not script or not script.strip():
                return format_status("Please enter a reference script.", "error"), gr.update(), gr.update()

            try:
                set_default_script(script.strip())
                return format_status("✓ Settings saved successfully!", "success"), script.strip(), script.strip()
            except Exception as e:
                return format_status(f"Error saving settings: {str(e)}", "error"), gr.update(), gr.update()

        save_settings_btn.click(
            fn=on_save_settings,
            inputs=[settings_script],
            outputs=[settings_status, new_voice_script, guest_script]
        )

        def on_rerecord(voice_id, audio, script):
            """Handle re-recording a voice."""
            if voice_id == GUEST_VOICE_ID:
                return (
                    format_status("Cannot re-record Quick Test voice. Create a new voice instead.", "error"),
                    gr.update(),  # Keep audio as-is
                    gr.update(),  # Keep preview unchanged
                )

            if audio is None:
                return (
                    format_status("Please record your voice first.", "error"),
                    gr.update(),  # Keep audio as-is
                    gr.update(),  # Keep preview unchanged
                )

            # Validate recording quality
            is_valid, validation_msg = validate_recording(audio)
            if not is_valid:
                return (
                    format_status(validation_msg, "error"),
                    gr.update(),  # Keep audio as-is
                    gr.update(),  # Keep preview unchanged
                )

            if not script or not script.strip():
                return (
                    format_status("Please enter a reference script.", "error"),
                    gr.update(),  # Keep audio as-is
                    gr.update(),  # Keep preview unchanged
                )

            try:
                sample_rate, audio_data = audio
                audio_data = normalize_audio(audio_data)
                success = update_voice_recording(voice_id, audio_data, sample_rate, script.strip())

                if success:
                    voices = load_voices()
                    voice = next((v for v in voices if v["id"] == voice_id), None)
                    name = voice["name"] if voice else "Unknown"

                    # Get updated audio path for preview
                    preview_audio = get_voice_audio_path(voice_id)

                    return (
                        format_status(f"✓ Voice updated for '{name}'! The voice now uses your new recording.", "success"),
                        gr.update(value=None),  # Clear the audio recorder
                        gr.update(value=preview_audio),  # Update preview
                    )
                else:
                    return (
                        format_status("Voice not found.", "error"),
                        gr.update(),  # Keep audio as-is
                        gr.update(),  # Keep preview unchanged
                    )
            except Exception as e:
                return (
                    format_status(f"Error updating voice: {str(e)}", "error"),
                    gr.update(),  # Keep audio as-is
                    gr.update(),  # Keep preview unchanged
                )

        rerecord_btn.click(
            fn=on_rerecord,
            inputs=[current_voice_id, rerecord_audio, rerecord_script],
            outputs=[rerecord_status, rerecord_audio, voice_preview_audio]  # Add voice_preview_audio
        )

        def on_generate(voice_id, audio, text, guest_ref_script, progress=gr.Progress()):
            """Handle voice generation with progress tracking."""
            try:
                progress(0, desc="Initializing...")

                if voice_id == GUEST_VOICE_ID:
                    progress(0.2, desc="Processing reference audio...")
                    result = clone_voice_guest(audio, text, guest_ref_script)
                else:
                    progress(0.2, desc="Loading voice...")
                    result = generate_from_voice(voice_id, text)

                progress(0.8, desc="Generating speech...")
                # Generation happens in the functions above

                progress(1.0, desc="Complete!")
                return result, format_status("✓ Generation complete! Play or download below.", "success")
            except gr.Error as e:
                progress(1.0, desc="Failed")
                raise e
            except Exception as e:
                progress(1.0, desc="Failed")
                return None, format_status(f"Generation failed: {str(e)}", "error")

        generate_btn.click(
            fn=on_generate,
            inputs=[current_voice_id, audio_input, text_input, guest_script],
            outputs=[audio_output, status]
        )

        def on_page_load(voice_id):
            """Refresh dropdown choices and trigger voice change on page load."""
            # Get fresh voice choices
            fresh_choices = get_voice_choices()

            # Ensure the selected voice still exists, otherwise default to guest
            valid_ids = [vid for _, vid in fresh_choices]
            if voice_id not in valid_ids:
                voice_id = GUEST_VOICE_ID

            # Get voice change updates
            voice_updates = on_voice_change(voice_id)

            # Return dropdown update + voice change updates
            return (
                gr.update(choices=fresh_choices, value=voice_id),  # Update dropdown
                *voice_updates  # Unpack voice change outputs
            )

        # Trigger dropdown refresh and voice change on load
        app.load(
            fn=on_page_load,
            inputs=[voice_dropdown],
            outputs=[voice_dropdown, current_voice_id, voice_info, recording_section, voice_mode_info, rerecord_script, rerecord_voice_name, rerecord_btn, rerecord_status, delete_confirm_text, voice_preview_audio]
        )

    return app, custom_css


def migrate_profiles_to_voices():
    """One-time migration from profiles/ to voices/ directory with safety checks."""
    old_dir = Path(__file__).parent / "profiles"
    new_dir = Path(__file__).parent / "voices"
    migration_marker = new_dir / ".migrated"

    # Skip if already migrated
    if migration_marker.exists():
        return

    # Skip if old directory doesn't exist
    if not old_dir.exists():
        # Create new directory if it doesn't exist
        new_dir.mkdir(exist_ok=True)
        return

    # If new_dir exists and has voices, assume migration done
    if new_dir.exists() and any(new_dir.iterdir()):
        print("[Migration] Voices directory already populated, marking as migrated")
        migration_marker.touch()
        return

    try:
        import shutil

        print("[Migration] Starting migration from profiles/ to voices/...")

        # Use copy pattern for safety
        if new_dir.exists():
            shutil.rmtree(new_dir)

        shutil.copytree(str(old_dir), str(new_dir))
        print("[Migration] Copied profiles/ to voices/")

        # Update JSON structure from "profiles" to "voices"
        old_json = old_dir / "profiles.json"
        new_json = new_dir / "voices.json"

        if old_json.exists() or new_json.exists():
            json_path = new_json if new_json.exists() else old_json
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)

                if "profiles" in data and "voices" not in data:
                    data["voices"] = data.pop("profiles")

                    with open(new_dir / "voices.json", "w") as f:
                        json.dump(data, f, indent=2)
                    print("[Migration] Updated JSON structure: profiles -> voices")

            except (json.JSONDecodeError, IOError) as e:
                print(f"[Migration] Warning: Could not update JSON structure: {e}")

        # Mark migration as complete
        migration_marker.touch()
        print("[Migration] Migration successful!")
        print("[Migration] Old data preserved in profiles/ - you can manually delete it after verification")

    except Exception as e:
        print(f"[Migration] Error during migration: {e}")
        print("[Migration] Old data preserved in profiles/ directory")
        # Clean up partial migration
        if new_dir.exists():
            try:
                import shutil
                shutil.rmtree(new_dir)
            except Exception:
                pass


if __name__ == "__main__":
    migrate_profiles_to_voices()
    app_instance, custom_css = create_ui()
    app_instance.launch(server_name="127.0.0.1", server_port=7860, css=custom_css)
