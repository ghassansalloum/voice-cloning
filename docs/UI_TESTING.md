# UI Testing Checklist - Professional Recording Interface

## Typography

- [ ] No emojis visible in labels (except Quick Actions buttons and section headers)
- [ ] Headings use Syne font (bold, distinctive)
- [ ] Body text uses DM Sans
- [ ] Labels are uppercase and smaller
- [ ] Text is light colored and readable on dark background

## Dark Theme

- [ ] Background is dark (black/near-black)
- [ ] Text has good contrast (light gray on dark)
- [ ] Orange accents used for primary actions
- [ ] No dark text on dark backgrounds

## Interactions

- [ ] Toggle sections (New Voice, Manage) expand/collapse smoothly
- [ ] Only one toggle section visible at a time
- [ ] Hover effects on buttons work (lift effect)
- [ ] Buttons press down on click
- [ ] Focus states visible when tabbing (orange outline)
- [ ] Keyboard shortcuts work (Space for recording, ⌘+Enter for generate)

## Visual Hierarchy

- [ ] Primary buttons are orange with black text
- [ ] Delete button is red
- [ ] Spacing feels balanced between sections
- [ ] Section headers have orange underline
- [ ] Status messages are prominent (toast-style with colored backgrounds)

## Voice Library (Sidebar)

### Always Visible
- [ ] Voice selector dropdown at top
- [ ] Voice preview player (when saved voice selected)
- [ ] Language dropdown (frequently used)
- [ ] Quick Actions buttons (➕ New Voice, ⚙️ Manage)

### Toggle Sections
- [ ] New Voice section hidden by default
- [ ] Manage section hidden by default
- [ ] Clicking Quick Action button shows appropriate section
- [ ] Sections have Cancel/Close buttons
- [ ] Only one section visible at a time

### Advanced Settings Accordion
- [ ] Keyboard Shortcuts accordion (collapsed by default)
- [ ] Advanced Settings accordion (collapsed by default)
- [ ] Model selection in Advanced Settings
- [ ] Global default script in Advanced Settings

## Recording Studio (Main Area - Quick Test Mode)

- [ ] Section visible only in Quick Test mode
- [ ] "🎙️ Recording Studio" header with orange underline
- [ ] Two-column layout: Script (left) + Tips (right)
- [ ] Reference script is editable
- [ ] Recording tips displayed in bullet points
- [ ] Microphone check button visible
- [ ] Audio recorder prominent with clear label
- [ ] Space key starts/stops recording when audio focused
- [ ] Recording validation feedback appears immediately
- [ ] Visual feedback during recording (red border, pulsing, "● RECORDING" badge)

## Generation Studio (Main Area - Always Visible)

- [ ] "🎬 Generation Studio" header with orange underline
- [ ] Two-column layout: Text input (left) + Tips (right)
- [ ] Text input is large (4 lines)
- [ ] Generation tips displayed in bullet points
- [ ] Generate button is prominent with keyboard hint "(⌘+Enter)"
- [ ] Estimated generation time note visible
- [ ] Progress bar appears during generation
- [ ] Output section clearly labeled
- [ ] Generated audio player functional

## Voice Management

### Voice Preview
- [ ] Preview player appears when saved voice selected
- [ ] Preview hidden for Quick Test mode
- [ ] Preview updates after re-recording
- [ ] Preview appears immediately after creating new voice

### New Voice Creation
- [ ] Voice name field required
- [ ] Reference script editable
- [ ] Microphone check button functional
- [ ] Recording validation provides feedback
- [ ] Save button creates voice and closes section
- [ ] Cancel button closes section without saving
- [ ] Dropdown updates with new voice

### Re-record Voice
- [ ] Only enabled for saved voices
- [ ] Shows current voice name
- [ ] Reference script editable
- [ ] Microphone check button functional
- [ ] Recording validation provides feedback
- [ ] Update button saves and updates preview

### Delete Safety
- [ ] Cannot delete Quick Test voice
- [ ] Delete button disabled by default
- [ ] Must type exact voice name to enable delete
- [ ] Text field is clearly labeled
- [ ] Warning message visible ("This action cannot be undone")
- [ ] Text field resets after deletion
- [ ] Text field resets when switching voices
- [ ] Deletion redirects to Quick Test mode

## Recording Validation

- [ ] Validates duration (minimum 3 seconds)
- [ ] Checks volume level (not too quiet)
- [ ] Detects clipping (peak > 0.95)
- [ ] Provides immediate feedback with colored status
- [ ] Success shows green with duration and peak info
- [ ] Warnings show yellow/red with specific issue
- [ ] Validation runs automatically after recording
- [ ] Validation prevents saving invalid recordings

## Recording Feedback

- [ ] Microphone check button shows info message
- [ ] Recording border turns red and pulses during recording
- [ ] "● RECORDING" badge appears at top of audio component
- [ ] Label turns red during recording
- [ ] Effects disappear when recording stops
- [ ] Works for all three recording locations (new voice, re-record, guest)

## Status Messages (Toast Style)

- [ ] Success messages are green background
- [ ] Error messages are red background
- [ ] Info messages are orange background
- [ ] Warning messages are yellow background
- [ ] Messages have colored left border
- [ ] Messages slide in with animation
- [ ] Messages are prominent and readable
- [ ] Messages show relevant icons (✓ for success)

## Progress Tracking

- [ ] Progress bar appears during generation
- [ ] Shows status: "Initializing...", "Processing...", "Generating...", "Complete!"
- [ ] Button shows loading state during generation
- [ ] Progress completes at 100% on success
- [ ] Progress shows "Failed" on error

## Keyboard Shortcuts

- [ ] Space bar starts/stops recording (when audio component focused)
- [ ] ⌘/Ctrl + Enter triggers generate button
- [ ] Tab navigates between controls
- [ ] Enter activates buttons
- [ ] Keyboard Shortcuts accordion documents all shortcuts
- [ ] Generate button label shows "(⌘+Enter)" hint

## Accessibility

- [ ] Can navigate with keyboard (Tab key)
- [ ] Focus states are visible
- [ ] Labels are descriptive
- [ ] Colors have sufficient contrast
- [ ] Interactive elements clearly identifiable
- [ ] elem_id attributes on key components (voice-selector, generate-button)
- [ ] ARIA-friendly structure

## Audio Components

- [ ] Audio components have dark theme styling
- [ ] Text in audio components not cut off
- [ ] Audio players functional
- [ ] Waveform displays during recording (where supported)
- [ ] No microphone permission issues

## Responsiveness

- [ ] Works at different window sizes
- [ ] Sidebar doesn't overflow
- [ ] Buttons are clickable (adequate size)
- [ ] Text doesn't overlap
- [ ] Two-column layouts stack appropriately on narrow screens

## Animations & Polish

- [ ] Smooth transitions on hover
- [ ] Section toggles are smooth
- [ ] Status messages slide in
- [ ] Recording pulse animation is smooth
- [ ] Progress bar animation is smooth
- [ ] No jarring movements
- [ ] Font rendering is smooth (antialiased)
- [ ] Button lift effect on hover
- [ ] Button press effect on click

## Data Migration

- [ ] Existing profiles/ directory auto-migrates to voices/
- [ ] Migration is safe (copies, doesn't delete original)
- [ ] Migration marker file prevents re-running
- [ ] voices.json structure updated from "profiles" to "voices"
- [ ] All existing voice data preserved

## Cross-Browser Compatibility

- [ ] Works in Chrome
- [ ] Works in Safari
- [ ] Works in Firefox
- [ ] Microphone access works in all browsers
- [ ] Keyboard shortcuts work in all browsers
- [ ] CSS animations work in all browsers

## Edge Cases

- [ ] Switching voices while recording (should clear recording)
- [ ] Deleting currently selected voice (should redirect to Quick Test)
- [ ] Creating voice with duplicate name (should allow)
- [ ] Re-recording with invalid audio (should reject)
- [ ] Generating with empty text (should show error)
- [ ] Page refresh preserves selected voice
- [ ] Voice preview updates correctly in all scenarios

## Performance

- [ ] UI remains responsive during generation
- [ ] Progress updates smoothly
- [ ] No lag when switching voices
- [ ] Recording feedback is immediate
- [ ] Status messages appear without delay
- [ ] Model loads efficiently on first generation

## Known Limitations

1. **Gradio CSS limitations** - Some advanced UI features not possible with pure CSS
2. **Real VU meter** - Cannot show real-time audio levels during recording (Gradio limitation)
3. **Recording waveform** - Limited by Gradio's audio component capabilities
4. **Modal dialogs** - Gradio doesn't support true modal overlays
5. **Custom cursors** - Not implemented (CSS complexity)

## Testing Notes

- Test in Chrome/Safari/Firefox for compatibility
- Refresh page between tests to ensure clean state
- Try full workflow: create voice → record → validate → generate → re-record → delete
- Verify all status messages appear correctly
- Test keyboard navigation thoroughly
- Test with different microphones
- Test with different recording lengths
- Test with very quiet/loud audio
- Verify migration works with existing data

## Professional Recording Interface Checklist

- [ ] UI feels like professional recording software (not a demo)
- [ ] Recording workflow is clear and intuitive
- [ ] Status feedback is immediate and prominent
- [ ] Terminology is professional ("voices" not "profiles")
- [ ] Primary actions are always visible (not hidden in accordions)
- [ ] Keyboard shortcuts make workflow efficient
- [ ] Visual feedback gives confidence (recording state, progress)
- [ ] Error messages are helpful and actionable
