# Mission Control UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform voice cloning UI from 6/10 to 10/10 with Spotify-inspired Mission Control design

**Architecture:** Complete CSS and HTML restructure using Gradio components. Replace orange theme with dominant Spotify green (#1DB954). Rebuild sidebar as three-zone command center. Add animated waveform header. Replace emojis with SVG icons. Implement dramatic typography hierarchy.

**Tech Stack:** Gradio 6.4.0, Custom CSS, Inter font, Inline SVG icons, JavaScript animations

---

## Task 1: Update Color System & Foundation CSS

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Replace color variables with Spotify palette**

In the `custom_css` string (around line 502-516), replace the existing `:root` variables with:

```python
/* Root variables - Spotify-inspired green dominance */
:root {
    --primary-green: #1DB954;
    --green-hover: #1ED760;
    --green-dark: #0D7A3A;
    --bg-primary: #121212;
    --bg-secondary: #181818;
    --bg-tertiary: #282828;
    --text-primary: #FFFFFF;
    --text-secondary: #B3B3B3;
    --text-disabled: #535353;
    --success: #1DB954;
    --warning: #FFA500;
    --error: #E22134;
    --info: #1ED760;
}
```

**Step 2: Update container background with texture**

Replace the `.gradio-container` background (around line 520-526) with:

```python
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-primary) !important;
    background-image:
        radial-gradient(circle at top right, rgba(29, 185, 84, 0.05) 0%, transparent 50%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E") !important;
    background-attachment: fixed !important;
}
```

**Step 3: Test color foundation**

Run: `./venv/bin/python app.py`
Expected: App loads with Spotify dark theme, subtle green glow in top-right

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat(ui): update color system to Spotify-inspired palette

Replace orange theme with dominant green (#1DB954).
Update background with subtle green glow and noise texture.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Update Typography System to Dramatic Scale

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Replace font imports**

Update the `@import` line (around line 499) to use Inter instead of Outfit:

```python
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');
```

**Step 2: Update H1 typography**

Replace `.gradio-container h1` rules (around line 528-534) with:

```python
.gradio-container h1 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 900 !important;
    font-size: 48px !important;
    letter-spacing: -0.03em !important;
    color: var(--text-primary) !important;
    margin-bottom: 24px !important;
    padding-bottom: 16px !important;
    border-bottom: 3px solid var(--primary-green) !important;
    position: relative !important;
}

.gradio-container h1::after {
    content: "" !important;
    position: absolute !important;
    bottom: -3px !important;
    left: 0 !important;
    width: 60px !important;
    height: 3px !important;
    background: var(--green-hover) !important;
    box-shadow: 0 0 12px var(--primary-green) !important;
}
```

**Step 3: Update H2 typography (green headers)**

Replace `.gradio-container h2` rules (around line 537-544) with:

```python
.gradio-container h2 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    font-size: 28px !important;
    letter-spacing: -0.02em !important;
    color: var(--primary-green) !important;
    margin-bottom: 16px !important;
}
```

**Step 4: Update H3 and label typography**

Replace `.gradio-container h3` and `label` rules (around line 546-560) with:

```python
.gradio-container h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    color: var(--text-primary) !important;
    margin-bottom: 12px !important;
}

.gradio-container label {
    font-weight: 600 !important;
    font-size: 11px !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
```

**Step 5: Update body text**

Replace paragraph/markdown rules (around line 562-570) with:

```python
.gradio-container p,
.gradio-container .markdown {
    font-size: 15px !important;
    line-height: 1.6 !important;
    color: var(--text-secondary) !important;
}

.gradio-container .markdown ul,
.gradio-container .markdown li {
    color: var(--text-secondary) !important;
}
```

**Step 6: Test typography**

Run: `./venv/bin/python app.py`
Expected: Dramatic scale visible - H1 48px with green underline, H2s in green, clear hierarchy

**Step 7: Commit**

```bash
git add app.py
git commit -m "feat(ui): implement dramatic typography hierarchy

Replace Outfit with Inter font family.
H1: 48px with green underline and glow.
H2: 28px in green color.
H3: 18px bold white.
Clear 2:1 ratio scale for visual hierarchy.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Update Button System to Spotify Style

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Update primary button styles**

Replace `.gradio-container button` and `.gradio-container button.primary` rules (around line 573-598) with:

```python
/* Button hierarchy */
.gradio-container button {
    font-weight: 500 !important;
    border-radius: 8px !important;
    transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    border: 1px solid var(--text-disabled) !important;
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

.gradio-container button:hover {
    background: #3E3E3E !important;
    border-color: var(--primary-green) !important;
    box-shadow: 0 0 16px rgba(29, 185, 84, 0.3) !important;
}

.gradio-container button.primary {
    background: linear-gradient(135deg, var(--primary-green), var(--green-hover)) !important;
    color: #000000 !important;
    border-color: var(--primary-green) !important;
    border-radius: 24px !important;
    padding: 16px 32px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 24px rgba(29, 185, 84, 0.4) !important;
}

.gradio-container button.primary:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 12px 32px rgba(29, 185, 84, 0.6) !important;
    border-color: var(--green-hover) !important;
}
```

**Step 2: Update danger button styles**

Replace `.gradio-container button.stop` rules (around line 600-611) with:

```python
.gradio-container button.stop {
    background: var(--bg-tertiary) !important;
    color: var(--error) !important;
    border: 2px solid var(--error) !important;
}

.gradio-container button.stop:hover {
    background: linear-gradient(135deg, var(--error), #C41E3A) !important;
    color: var(--text-primary) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 20px rgba(226, 33, 52, 0.5) !important;
}
```

**Step 3: Update button active state**

Replace button:active rule (around line 725-728) with:

```python
.gradio-container button:active {
    transform: translateY(1px) scale(0.98) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.1s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
}
```

**Step 4: Test button styles**

Run: `./venv/bin/python app.py`
Expected: Primary buttons green with black text (Spotify style), secondary buttons with green hover glow, danger buttons red

**Step 5: Commit**

```bash
git add app.py
git commit -m "feat(ui): implement Spotify-style button system

Primary: Green gradient with black text, pill shape.
Secondary: Dark with green hover glow.
Danger: Red text/border, fills red on hover.
Add scale/translateY animations.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Update Accordion Styles to Hardware Panel Aesthetic

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Update accordion base styles**

Replace `.gradio-container .accordion` rules (around line 619-642) with:

```python
/* Accordion hierarchy - Hardware panel style */
.gradio-container .accordion {
    border: 1px solid var(--text-disabled) !important;
    border-radius: 8px !important;
    margin-bottom: 12px !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    background: var(--bg-tertiary) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

.gradio-container .accordion:hover {
    border-color: var(--primary-green) !important;
    box-shadow:
        0 4px 16px rgba(0, 0, 0, 0.4),
        0 0 20px rgba(29, 185, 84, 0.2) !important;
    transform: translateY(-1px) !important;
}

.gradio-container .accordion[open] {
    border-color: var(--primary-green) !important;
    box-shadow: 0 4px 24px rgba(29, 185, 84, 0.3) !important;
}

.gradio-container .accordion summary {
    font-weight: 600 !important;
    padding: 12px 16px !important;
    cursor: pointer !important;
    user-select: none !important;
    color: var(--text-primary) !important;
}
```

**Step 2: Add LED indicator effect**

Add new CSS rule for accordion open state indicator:

```python
/* LED indicator for open accordions */
.gradio-container .accordion[open] summary::before {
    content: "●" !important;
    color: var(--primary-green) !important;
    margin-right: 8px !important;
    font-size: 12px !important;
    animation: pulse 2s ease-in-out infinite !important;
}
```

**Step 3: Test accordion styles**

Run: `./venv/bin/python app.py`
Expected: Accordions look like hardware panels, green glow when hovered/open, LED dot appears when open

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat(ui): style accordions as hardware panels

Dark backgrounds with green hover glow.
LED indicator (green dot) appears when open.
Smooth expand/collapse with green shadow.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Update Form Inputs to Match Dark Theme

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Update input field styles**

Replace form input rules (around line 660-678) with:

```python
/* Form inputs - Dark theme */
.gradio-container input[type="text"],
.gradio-container textarea,
.gradio-container select {
    border: 1px solid var(--text-disabled) !important;
    border-radius: 6px !important;
    padding: 12px 16px !important;
    transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    font-family: 'Inter', sans-serif !important;
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    font-size: 15px !important;
}

.gradio-container input[type="text"]:focus,
.gradio-container textarea:focus,
.gradio-container select:focus {
    outline: none !important;
    border-color: var(--primary-green) !important;
    box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.2) !important;
    background: var(--bg-secondary) !important;
}

.gradio-container input[type="text"]::placeholder,
.gradio-container textarea::placeholder {
    color: var(--text-disabled) !important;
}
```

**Step 2: Test input fields**

Run: `./venv/bin/python app.py`
Expected: Input fields dark with green focus glow, readable placeholder text

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): update form inputs to dark theme

Dark backgrounds (#282828) with green focus states.
Readable placeholder text in gray.
Smooth transitions on focus.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Update Audio Component Styles

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Update audio container styles**

Replace audio component rules (around line 682-697) with:

```python
/* Audio components - Custom styled */
.gradio-container .audio-container,
.gradio-container .audio-wrapper {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--text-disabled) !important;
    border-radius: 12px !important;
    padding: 20px !important;
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
```

**Step 2: Update recording state styles**

Replace recording state rules (around line 917-927) with:

```python
/* Recording state - Green glow */
.gradio-container .audio-container:has(button[aria-label*="Stop"]) {
    border: 2px solid var(--primary-green) !important;
    box-shadow:
        0 0 20px rgba(29, 185, 84, 0.6),
        0 0 40px rgba(29, 185, 84, 0.4) !important;
    animation: recordPulseGreen 1.5s ease-in-out infinite !important;
    position: relative !important;
    z-index: 2 !important;
}

@keyframes recordPulseGreen {
    0%, 100% {
        box-shadow: 0 0 20px rgba(29, 185, 84, 0.6), 0 0 40px rgba(29, 185, 84, 0.4);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 30px rgba(29, 185, 84, 0.8), 0 0 60px rgba(29, 185, 84, 0.6);
        transform: scale(1.005);
    }
}
```

**Step 3: Update recording label**

Replace recording label rule (around line 941-944) with:

```python
.gradio-container .audio-container:has(button[aria-label*="Stop"]) label {
    color: var(--primary-green) !important;
    font-weight: 700 !important;
}
```

**Step 4: Update recording badge**

Replace recording badge rule (around line 946-962) with:

```python
.gradio-container .audio-container:has(button[aria-label*="Stop"])::before {
    content: "● RECORDING" !important;
    position: absolute !important;
    top: -12px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: linear-gradient(135deg, var(--primary-green), var(--green-hover)) !important;
    color: #000000 !important;
    padding: 6px 16px !important;
    border-radius: 4px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    z-index: 10 !important;
    box-shadow: 0 4px 12px rgba(29, 185, 84, 0.5) !important;
    animation: pulse 1.5s ease-in-out infinite !important;
}
```

**Step 5: Test audio components**

Run: `./venv/bin/python app.py`
Expected: Audio recorders dark themed, green glow when recording, "RECORDING" badge appears

**Step 6: Commit**

```bash
git add app.py
git commit -m "feat(ui): update audio components to green theme

Dark backgrounds with green borders.
Recording state: green glow and pulsing animation.
Recording badge: green gradient with black text.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Update Status Messages to Green Theme

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Update status message base styles**

Replace status message rules (around line 751-804) with:

```python
/* Status messages - Toast style with green */
.gradio-container .markdown.status-message {
    display: block !important;
    padding: 16px 20px !important;
    border-radius: 8px !important;
    font-style: normal !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    margin: 12px 0 !important;
    border-left: 4px solid transparent !important;
    animation: slideIn 0.3s ease-out !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

/* Success status - Green */
.gradio-container .markdown.status-success {
    background: rgba(29, 185, 84, 0.15) !important;
    border-left-color: var(--success) !important;
    color: var(--success) !important;
    box-shadow: 0 4px 16px rgba(29, 185, 84, 0.2) !important;
}

/* Error status */
.gradio-container .markdown.status-error {
    background: rgba(226, 33, 52, 0.15) !important;
    border-left-color: var(--error) !important;
    color: var(--error) !important;
    box-shadow: 0 4px 16px rgba(226, 33, 52, 0.2) !important;
}

/* Info status - Green */
.gradio-container .markdown.status-info {
    background: rgba(29, 185, 84, 0.15) !important;
    border-left-color: var(--info) !important;
    color: var(--info) !important;
    box-shadow: 0 4px 16px rgba(29, 185, 84, 0.2) !important;
}

/* Warning status */
.gradio-container .markdown.status-warning {
    background: rgba(255, 165, 0, 0.15) !important;
    border-left-color: var(--warning) !important;
    color: var(--warning) !important;
}
```

**Step 2: Test status messages**

Run: `./venv/bin/python app.py`
Test: Save a voice, check microphone → status messages should show green for success/info

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): update status messages to green theme

Success messages: green background and text.
Info messages: green theme.
Error/warning: red and orange respectively.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Update Section Headers with Green Accents

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Update h2 section header styles**

Replace h2 section header rules (around line 835-851) with:

```python
/* Section headers - Green accent */
.gradio-container h2 {
    padding-bottom: 8px !important;
    margin-bottom: 20px !important;
    position: relative !important;
}

/* Remove orange underline, h2 color itself is green */
```

Note: We already made H2s green in Task 2, so no underline needed

**Step 2: Test section headers**

Run: `./venv/bin/python app.py`
Expected: H2 headers appear in green (#1DB954) without underlines

**Step 3: Commit**

```bash
git add app.py
git commit -m "refactor(ui): simplify section headers

Remove underlines since H2s are already green.
Clean, minimal approach following Spotify aesthetic.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Update Global Recording Overlay to Green

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Update recording overlay color**

Replace recording overlay rule (around line 895-915) with:

```python
/* Global recording overlay - Green tint */
.gradio-container:has(.audio-container:has(button[aria-label*="Stop"]))::before {
    content: "" !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    background: radial-gradient(circle, transparent 0%, rgba(29, 185, 84, 0.05) 100%) !important;
    pointer-events: none !important;
    animation: recordingPulseGreen 2s ease-in-out infinite !important;
    z-index: 1 !important;
}

@keyframes recordingPulseGreen {
    0%, 100% {
        opacity: 0.5;
    }
    50% {
        opacity: 1;
    }
}
```

**Step 2: Test recording overlay**

Run: `./venv/bin/python app.py`
Test: Start recording → entire interface should have subtle green tint

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): add green recording overlay

Subtle green radial gradient when recording.
Pulses to reinforce recording state.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Hide Gradio Footer

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Add footer hiding CSS**

Add at the end of custom_css (before closing triple quotes):

```python
/* Hide Gradio footer */
.gradio-container footer {
    display: none !important;
}
```

**Step 2: Test footer removal**

Run: `./venv/bin/python app.py`
Expected: "Built with Gradio" footer no longer visible

**Step 3: Commit**

```bash
git add app.py
git commit -m "refactor(ui): hide Gradio footer branding

Remove default footer to maintain clean professional aesthetic.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Replace Emojis with Text in HTML/Markdown

**Files:**
- Modify: `app.py:1038-1268` (UI structure)

**Step 1: Remove emoji from Voice Library header**

Change line 1038:
```python
gr.Markdown("## Voice Library")
```

No change needed - already no emoji

**Step 2: Remove emojis from quick action buttons**

Change lines 1072-1073:
```python
new_voice_btn = gr.Button("➕ New Voice", size="sm")
manage_voices_btn = gr.Button("⚙️ Manage", size="sm")
```

To:
```python
new_voice_btn = gr.Button("New Voice", size="sm")
manage_voices_btn = gr.Button("Manage", size="sm")
```

**Step 3: Remove emojis from Recording Studio**

Change line 1195:
```python
gr.Markdown("## 🎙️ Recording Studio")
```

To:
```python
gr.Markdown("## Recording Studio")
```

**Step 4: Remove emojis from Generation Studio**

Change line 1238:
```python
gr.Markdown("## 🎬 Generation Studio")
```

To:
```python
gr.Markdown("## Generation Studio")
```

**Step 5: Remove emoji from Generate button**

Change line 1257:
```python
generate_btn = gr.Button("🎵 Generate Voice (⌘+Enter)", variant="primary", size="lg", scale=2, elem_id="generate-button")
```

To:
```python
generate_btn = gr.Button("Generate Voice (⌘+Enter)", variant="primary", size="lg", scale=2, elem_id="generate-button")
```

**Step 6: Remove emojis from microphone check buttons**

Change line 1092:
```python
new_voice_mic_check_btn = gr.Button("🎤 Check Microphone", size="sm")
```

To:
```python
new_voice_mic_check_btn = gr.Button("Check Microphone", size="sm")
```

Change line 1122:
```python
rerecord_mic_check_btn = gr.Button("🎤 Check Microphone", size="sm")
```

To:
```python
rerecord_mic_check_btn = gr.Button("Check Microphone", size="sm")
```

Change line 1222:
```python
guest_mic_check_btn = gr.Button("🎤 Check Microphone", size="sm")
```

To:
```python
guest_mic_check_btn = gr.Button("Check Microphone", size="sm")
```

**Step 7: Remove emoji from Keyboard Shortcuts**

Change line 1153:
```python
with gr.Accordion("⌨️ Keyboard Shortcuts", open=False):
```

To:
```python
with gr.Accordion("Keyboard Shortcuts", open=False):
```

**Step 8: Remove emoji from microphone status**

Change line 488:
```python
"🎤 Ensure microphone permissions are enabled in your browser and system settings.",
```

To:
```python
"Ensure microphone permissions are enabled in your browser and system settings.",
```

**Step 9: Test no emojis visible**

Run: `./venv/bin/python app.py`
Expected: No emojis anywhere in the interface, clean text-only labels

**Step 10: Commit**

```bash
git add app.py
git commit -m "refactor(ui): remove all emojis for professional aesthetic

Replace emoji labels with clean text.
Prepares for SVG icon implementation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Add Sidebar Background Styling

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Add sidebar-specific styles**

Add new CSS rule (around line 748 after spacing section):

```python
/* Sidebar styling - Green gradient overlay */
.gradio-container > .row > .column:first-child {
    position: relative !important;
}

.gradio-container > .row > .column:first-child::before {
    content: "" !important;
    position: absolute !important;
    top: 0 !important;
    right: 0 !important;
    width: 100% !important;
    height: 300px !important;
    background: radial-gradient(circle at top right, rgba(29, 185, 84, 0.08) 0%, transparent 60%) !important;
    pointer-events: none !important;
    z-index: 0 !important;
}

.gradio-container > .row > .column:first-child > * {
    position: relative !important;
    z-index: 1 !important;
}

/* Sidebar specific padding */
.gradio-container .block:first-child > .form > .col:first-child {
    padding: 24px !important;
}
```

**Step 2: Test sidebar styling**

Run: `./venv/bin/python app.py`
Expected: Sidebar has subtle green glow in top-right corner, 24px padding

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): add sidebar green gradient overlay

Subtle green radial gradient in top-right of sidebar.
Reinforces 'power source' aesthetic.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Update Main Content Max-Width

**Files:**
- Modify: `app.py:497-981` (CSS section)

**Step 1: Add main content max-width constraint**

Add new CSS rule before final polish section:

```python
/* Main content max-width constraint */
.gradio-container > .row > .column:last-child {
    max-width: 1200px !important;
    margin: 0 auto !important;
}
```

**Step 2: Test max-width**

Run: `./venv/bin/python app.py`
Expected: Main content area doesn't expand beyond 1200px on wide screens

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): add max-width constraint to main content

Limit main area to 1200px for comfortable reading.
Centers content on wide screens.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Add Waveform Header Placeholder

**Files:**
- Modify: `app.py:1186-1188` (Main area start)

**Step 1: Add waveform header markdown**

Before the H1 "Voice Cloning Studio" heading (line 1187), add:

```python
# Waveform header placeholder (future: animated canvas)
gr.HTML("""
<div style="height: 80px; margin-bottom: 24px; background: linear-gradient(90deg, #0D7A3A 0%, #1DB954 50%, #1ED760 100%); opacity: 0.3; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #B3B3B3; letter-spacing: 2px;">
WAVEFORM VISUALIZATION (PLACEHOLDER)
</div>
""")
```

**Step 2: Test waveform placeholder**

Run: `./venv/bin/python app.py`
Expected: Green gradient bar appears above "Voice Cloning Studio" heading

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): add waveform header placeholder

Static green gradient bar as signature element.
Placeholder for future animated waveform visualization.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Update Page Title and Subtitle

**Files:**
- Modify: `app.py:1187-1188`

**Step 1: Update subtitle to secondary color**

Change line 1188:
```python
gr.Markdown("Professional voice cloning on Apple Silicon with MLX")
```

To add styling:
```python
gr.Markdown('<p style="color: var(--text-secondary); font-size: 16px; margin-top: -16px;">Professional voice cloning on Apple Silicon with MLX</p>')
```

**Step 2: Test subtitle**

Run: `./venv/bin/python app.py`
Expected: Subtitle appears in gray below main heading

**Step 3: Commit**

```bash
git add app.py
git commit -m "style(ui): improve subtitle styling

Gray color for subtitle to reduce visual weight.
Brings it closer to heading.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 16: Add Voice Info Styling

**Files:**
- Modify: `app.py:1191`

**Step 1: Update voice info markdown styling**

The voice_info markdown (line 1191) already uses bold markdown. Enhance by updating the generation function `on_voice_change` to use green for the voice name.

In function `on_voice_change` (around line 1350 and 1361), update:

Line 1350:
```python
voice_text = "**Active Voice:** Quick Test (record new voice)"
```

To:
```python
voice_text = '<p style="font-size: 15px;"><strong>Active Voice:</strong> <span style="color: var(--primary-green);">Quick Test (record new voice)</span></p>'
```

Line 1361:
```python
voice_text = f"**Active Voice:** {name}"
```

To:
```python
voice_text = f'<p style="font-size: 15px;"><strong>Active Voice:</strong> <span style="color: var(--primary-green);">{name}</span></p>'
```

**Step 2: Test voice info styling**

Run: `./venv/bin/python app.py`
Expected: Active voice name appears in green

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): highlight active voice name in green

Voice name appears in Spotify green for emphasis.
Reinforces which voice is currently selected.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 17: Final Visual Testing and Polish

**Files:**
- Test: Run app and verify all changes

**Step 1: Run comprehensive visual test**

Run: `./venv/bin/python app.py`

**Step 2: Verify checklist**

Visual inspection checklist:
- [ ] Background is Spotify dark (#121212) with subtle green glow
- [ ] All text readable (white/gray on dark)
- [ ] H1 is 48px with green underline and glow
- [ ] H2s are 28px and green colored
- [ ] No emojis visible anywhere
- [ ] Primary buttons are green gradient with black text
- [ ] Secondary buttons have green hover glow
- [ ] Accordions have dark backgrounds with green borders on hover
- [ ] Recording state shows green glow and "RECORDING" badge
- [ ] Status messages use green for success/info
- [ ] Sidebar has green gradient overlay in top-right
- [ ] Main content max-width is constrained
- [ ] Waveform placeholder visible above heading
- [ ] Active voice name is green
- [ ] Footer is hidden

**Step 3: Test interactions**

Interactive testing:
- [ ] Hover buttons → green glow appears
- [ ] Click accordion → opens with green glow shadow
- [ ] Focus input → green border appears
- [ ] Start recording → green overlay + pulsing
- [ ] Save voice → green success message
- [ ] Check microphone → green info message

**Step 4: Document completion**

Create file `docs/mission-control-completion.md`:

```markdown
# Mission Control Redesign - Implementation Complete

**Date:** 2026-02-05
**Status:** ✅ Complete

## Changes Implemented

### Color System
- ✅ Spotify green (#1DB954) as dominant color
- ✅ Dark backgrounds (#121212, #181818, #282828)
- ✅ Subtle texture and green gradient overlay

### Typography
- ✅ Inter font family (replaces Outfit)
- ✅ Dramatic scale: 48/28/18px
- ✅ Green H2 headers
- ✅ H1 with green underline and glow

### Buttons
- ✅ Primary: Green gradient with black text
- ✅ Secondary: Green hover glow
- ✅ Danger: Red with hover fill
- ✅ Scale and translate animations

### Components
- ✅ Accordions styled as hardware panels
- ✅ Dark form inputs with green focus
- ✅ Audio components with green recording state
- ✅ Status messages in green theme

### Layout
- ✅ Sidebar green gradient overlay
- ✅ Main content max-width 1200px
- ✅ Waveform header placeholder
- ✅ All emojis removed

### Polish
- ✅ Gradio footer hidden
- ✅ Active voice name in green
- ✅ Recording overlay with green tint
- ✅ Smooth transitions throughout

## Known Limitations

1. **Waveform is placeholder** - Static gradient, not animated
2. **No real-time audio visualization** - Would require Web Audio API + Canvas
3. **Icons still text-based** - SVG icons not implemented (removed emojis only)
4. **Sidebar not restructured** - Three-zone layout not implemented yet
5. **Language selector still dropdown** - Pill buttons not implemented

## Next Phase (Optional Enhancements)

1. Implement animated waveform header with Canvas/Web Audio API
2. Replace text labels with Lucide SVG icons
3. Restructure sidebar into three zones (Voice Control, Quick Actions, Panels)
4. Convert language dropdown to pill buttons
5. Add voice waveform preview in sidebar

## Visual Quality Assessment

**Before:** 6/10 (timid orange accents, flat hierarchy, emojis)
**After:** 8.5/10 (bold green dominance, dramatic typography, professional)

**Remaining for 10/10:**
- Animated waveform signature element
- SVG icon system
- Sidebar three-zone restructure
