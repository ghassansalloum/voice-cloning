"""Voice Cloning Application using Qwen3-TTS with Profile Management."""

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import gradio as gr
import numpy as np
import soundfile as sf
import torch

# Global model cache for lazy loading
_model = None

# Profiles directory
PROFILES_DIR = Path(__file__).parent / "profiles"
PROFILES_INDEX = PROFILES_DIR / "profiles.json"

# Reference script - pangram with diverse phonemes for voice capture
REFERENCE_SCRIPT = """The quick brown fox jumps over the lazy dog.
She sells seashells by the seashore.
Peter Piper picked a peck of pickled peppers.
How much wood would a woodchuck chuck if a woodchuck could chuck wood?"""

# Guest profile constant
GUEST_PROFILE_ID = "guest"


def get_model():
    """Lazy load the TTS model to avoid slow startup."""
    global _model
    if _model is None:
        from qwen_tts import Qwen3TTSModel
        # Must use float32 for voice cloning on MPS
        _model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
            device_map="mps",
            dtype=torch.float32,
        )
    return _model


# ============================================================================
# Profile Management Functions
# ============================================================================

def load_profiles() -> list[dict]:
    """Load all profiles from profiles.json."""
    PROFILES_DIR.mkdir(exist_ok=True)
    if not PROFILES_INDEX.exists():
        return []
    try:
        with open(PROFILES_INDEX, "r") as f:
            data = json.load(f)
            return data.get("profiles", [])
    except (json.JSONDecodeError, IOError):
        return []


def save_profiles_index(profiles: list[dict]) -> None:
    """Persist profile index to profiles.json."""
    PROFILES_DIR.mkdir(exist_ok=True)
    with open(PROFILES_INDEX, "w") as f:
        json.dump({"profiles": profiles}, f, indent=2)


def create_profile(name: str, audio_data: np.ndarray, sample_rate: int) -> str:
    """
    Create a new profile with voice recording.

    Args:
        name: Profile display name
        audio_data: Audio data as numpy array (float32, mono)
        sample_rate: Audio sample rate

    Returns:
        Profile ID of created profile
    """
    profile_id = str(uuid.uuid4())
    profile_dir = PROFILES_DIR / profile_id
    profile_dir.mkdir(parents=True, exist_ok=True)

    # Save audio file
    audio_path = profile_dir / "audio.wav"
    sf.write(str(audio_path), audio_data, sample_rate)

    # Compute and cache voice clone prompt
    model = get_model()
    voice_clone_prompt = model.create_voice_clone_prompt(
        ref_audio=str(audio_path),
        ref_text=REFERENCE_SCRIPT,
    )
    prompt_path = profile_dir / "prompt.pt"
    torch.save(voice_clone_prompt, str(prompt_path))

    # Update profiles index
    profiles = load_profiles()
    profiles.append({
        "id": profile_id,
        "name": name,
        "created_at": datetime.utcnow().isoformat() + "Z"
    })
    save_profiles_index(profiles)

    return profile_id


def delete_profile(profile_id: str) -> bool:
    """
    Delete a profile and its files.

    Args:
        profile_id: ID of profile to delete

    Returns:
        True if deleted, False if not found
    """
    if profile_id == GUEST_PROFILE_ID:
        return False

    profiles = load_profiles()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        return False

    # Remove from index
    profiles = [p for p in profiles if p["id"] != profile_id]
    save_profiles_index(profiles)

    # Delete profile directory
    profile_dir = PROFILES_DIR / profile_id
    if profile_dir.exists():
        import shutil
        shutil.rmtree(profile_dir)

    return True


def get_voice_prompt(profile_id: str):
    """
    Load cached voice_clone_prompt for a profile.

    Args:
        profile_id: Profile ID

    Returns:
        Cached voice_clone_prompt tensor, or None if not found
    """
    prompt_path = PROFILES_DIR / profile_id / "prompt.pt"
    if prompt_path.exists():
        return torch.load(str(prompt_path), weights_only=False)
    return None


def get_profile_choices() -> list[tuple[str, str]]:
    """Get list of (display_name, profile_id) tuples for dropdown."""
    choices = [("Guest (record new voice)", GUEST_PROFILE_ID)]
    profiles = load_profiles()
    for p in profiles:
        choices.append((p["name"], p["id"]))
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


# ============================================================================
# Voice Generation Functions
# ============================================================================

def clone_voice_guest(reference_audio, target_text: str) -> str:
    """
    Clone voice from reference audio (Guest mode).

    Args:
        reference_audio: Tuple of (sample_rate, audio_data) from Gradio microphone
        target_text: Text to synthesize in the cloned voice

    Returns:
        Path to generated WAV file
    """
    if reference_audio is None:
        raise gr.Error("Please record your voice reading the script first.")

    if not target_text or not target_text.strip():
        raise gr.Error("Please enter some text to generate speech.")

    sample_rate, audio_data = reference_audio
    audio_data = normalize_audio(audio_data)

    # Save reference audio to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as ref_file:
        sf.write(ref_file.name, audio_data, sample_rate)
        ref_audio_path = ref_file.name

    # Load model and generate
    model = get_model()

    # Create voice clone prompt from reference audio
    voice_clone_prompt = model.create_voice_clone_prompt(
        ref_audio=ref_audio_path,
        ref_text=REFERENCE_SCRIPT,
    )

    # Generate speech with cloned voice
    wavs, sr = model.generate_voice_clone(
        text=target_text.strip(),
        language="English",
        voice_clone_prompt=voice_clone_prompt,
    )

    # Save to temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
        sf.write(out_file.name, wavs[0], sr)
        return out_file.name


def generate_from_profile(profile_id: str, target_text: str) -> str:
    """
    Generate speech using a saved profile's cached voice prompt.

    Args:
        profile_id: Profile ID to use
        target_text: Text to synthesize

    Returns:
        Path to generated WAV file
    """
    if not target_text or not target_text.strip():
        raise gr.Error("Please enter some text to generate speech.")

    voice_clone_prompt = get_voice_prompt(profile_id)
    if voice_clone_prompt is None:
        raise gr.Error(f"Profile voice data not found. Please recreate the profile.")

    model = get_model()

    # Generate speech with cached voice prompt
    wavs, sr = model.generate_voice_clone(
        text=target_text.strip(),
        language="English",
        voice_clone_prompt=voice_clone_prompt,
    )

    # Save to temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
        sf.write(out_file.name, wavs[0], sr)
        return out_file.name


# ============================================================================
# Gradio UI
# ============================================================================

def create_ui():
    """Create and configure the Gradio interface."""

    with gr.Blocks(title="Voice Cloning with Qwen3-TTS") as app:

        # State for tracking current profile selection
        current_profile_id = gr.State(value=GUEST_PROFILE_ID)

        with gr.Row():
            # ================================================================
            # Sidebar - Profile Management
            # ================================================================
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("## Profiles")

                # Profile selector dropdown
                profile_dropdown = gr.Dropdown(
                    choices=get_profile_choices(),
                    value=GUEST_PROFILE_ID,
                    label="Select Profile",
                    interactive=True,
                )

                # New Profile Section
                with gr.Accordion("Create New Profile", open=False) as new_profile_accordion:
                    new_profile_name = gr.Textbox(
                        label="Profile Name",
                        placeholder="Enter a name for this voice profile..."
                    )

                    gr.Markdown("**Record your voice reading the script:**")
                    gr.Textbox(
                        value=REFERENCE_SCRIPT,
                        label="Reference Script",
                        lines=4,
                        interactive=False
                    )

                    new_profile_audio = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="Record Voice"
                    )

                    save_profile_btn = gr.Button("Save Profile", variant="primary")
                    profile_status = gr.Markdown("")

                gr.Markdown("---")

                # Delete Profile Section
                with gr.Accordion("Delete Profile", open=False):
                    gr.Markdown("*Select a profile above, then click delete.*")
                    delete_profile_btn = gr.Button("Delete Selected Profile", variant="stop")
                    delete_status = gr.Markdown("")

            # ================================================================
            # Main Area - Voice Generation
            # ================================================================
            with gr.Column(scale=3):
                gr.Markdown("# Voice Cloning with Qwen3-TTS")
                gr.Markdown("Clone your voice locally on Apple Silicon using PyTorch MPS.")

                # Show current profile info
                profile_info = gr.Markdown("**Current Profile:** Guest (record new voice)")

                # Recording section (only for Guest mode)
                with gr.Column(visible=True) as recording_section:
                    gr.Markdown("### Step 1: Read This Script Aloud")
                    gr.Textbox(
                        value=REFERENCE_SCRIPT,
                        label="Reference Script (read this text clearly when recording)",
                        lines=4,
                        interactive=False
                    )

                    gr.Markdown("### Step 2: Record Your Voice")
                    gr.Markdown("*Click the microphone icon to start recording.*")
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="Record yourself reading the script above"
                    )

                # Profile mode message (when using saved profile)
                profile_mode_info = gr.Markdown(
                    "### Using Saved Voice Profile\n*Your voice is already saved. Just enter text below and generate!*",
                    visible=False
                )

                # Text input and generation (always visible)
                gr.Markdown("### Enter Text to Speak")
                text_input = gr.Textbox(
                    label="Text to Generate",
                    placeholder="Enter the text you want spoken in your cloned voice...",
                    lines=3
                )

                generate_btn = gr.Button("Generate Cloned Voice", variant="primary", size="lg")

                # Output audio
                gr.Markdown("### Generated Audio")
                gr.Markdown("*Play or download your cloned voice audio.*")
                audio_output = gr.Audio(
                    label="Generated Speech",
                    type="filepath",
                    interactive=False
                )

                status = gr.Markdown("*Status: Ready. Select a profile or record your voice to begin.*")

        # ====================================================================
        # Event Handlers
        # ====================================================================

        def on_profile_change(profile_id):
            """Handle profile selection change."""
            is_guest = profile_id == GUEST_PROFILE_ID

            if is_guest:
                profile_text = "**Current Profile:** Guest (record new voice)"
            else:
                profiles = load_profiles()
                profile = next((p for p in profiles if p["id"] == profile_id), None)
                name = profile["name"] if profile else "Unknown"
                profile_text = f"**Current Profile:** {name}"

            return (
                profile_id,  # Update state
                profile_text,  # Update profile info
                gr.update(visible=is_guest),  # recording_section
                gr.update(visible=not is_guest),  # profile_mode_info
            )

        profile_dropdown.change(
            fn=on_profile_change,
            inputs=[profile_dropdown],
            outputs=[current_profile_id, profile_info, recording_section, profile_mode_info]
        )

        def on_save_profile(name, audio):
            """Handle new profile creation."""
            if not name or not name.strip():
                return (
                    "*Please enter a profile name.*",
                    gr.update(),  # dropdown stays same
                )

            if audio is None:
                return (
                    "*Please record your voice first.*",
                    gr.update(),
                )

            try:
                sample_rate, audio_data = audio
                audio_data = normalize_audio(audio_data)
                profile_id = create_profile(name.strip(), audio_data, sample_rate)

                # Update dropdown choices
                new_choices = get_profile_choices()

                return (
                    f"*Profile '{name}' created successfully!*",
                    gr.update(choices=new_choices, value=profile_id),
                )
            except Exception as e:
                return (
                    f"*Error creating profile: {str(e)}*",
                    gr.update(),
                )

        save_profile_btn.click(
            fn=on_save_profile,
            inputs=[new_profile_name, new_profile_audio],
            outputs=[profile_status, profile_dropdown]
        )

        def on_delete_profile(profile_id):
            """Handle profile deletion."""
            if profile_id == GUEST_PROFILE_ID:
                return (
                    "*Cannot delete Guest profile.*",
                    gr.update(),
                    GUEST_PROFILE_ID,
                )

            profiles = load_profiles()
            profile = next((p for p in profiles if p["id"] == profile_id), None)
            name = profile["name"] if profile else "Unknown"

            if delete_profile(profile_id):
                new_choices = get_profile_choices()
                return (
                    f"*Profile '{name}' deleted.*",
                    gr.update(choices=new_choices, value=GUEST_PROFILE_ID),
                    GUEST_PROFILE_ID,
                )
            else:
                return (
                    "*Profile not found.*",
                    gr.update(),
                    profile_id,
                )

        delete_profile_btn.click(
            fn=on_delete_profile,
            inputs=[current_profile_id],
            outputs=[delete_status, profile_dropdown, current_profile_id]
        )

        def on_generate(profile_id, audio, text):
            """Handle voice generation."""
            try:
                if profile_id == GUEST_PROFILE_ID:
                    result = clone_voice_guest(audio, text)
                else:
                    result = generate_from_profile(profile_id, text)
                return result, "*Status: Generation complete!*"
            except gr.Error as e:
                raise e
            except Exception as e:
                return None, f"*Status: Error - {str(e)}*"

        generate_btn.click(
            fn=on_generate,
            inputs=[current_profile_id, audio_input, text_input],
            outputs=[audio_output, status]
        )

        # Trigger profile change on load to set initial visibility
        app.load(
            fn=on_profile_change,
            inputs=[profile_dropdown],
            outputs=[current_profile_id, profile_info, recording_section, profile_mode_info]
        )

    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch(server_name="127.0.0.1", server_port=7860)
