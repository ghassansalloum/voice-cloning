# UI Testing Checklist

## Typography

- [ ] No emojis visible in labels
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

- [ ] All collapsible sections are accordions
- [ ] Accordions expand/collapse smoothly with animation
- [ ] Hover effects on buttons work (lift effect)
- [ ] Buttons press down on click
- [ ] Focus states visible when tabbing (orange outline)

## Visual Hierarchy

- [ ] Primary buttons are orange with black text
- [ ] Delete button is red
- [ ] Delete accordion has red border and subtle red background
- [ ] Spacing feels balanced between sections
- [ ] No horizontal divider lines visible

## Language Selector

- [ ] Language dropdown is always visible at top
- [ ] Positioned right after profile dropdown
- [ ] No need to open Settings to change language

## Accordion Organization

Order should be:
1. [ ] Create New Profile
2. [ ] Re-record Voice
3. [ ] Settings (Model + Default Script only)
4. [ ] Delete Profile (red, at bottom)

## Delete Safety

- [ ] Cannot delete Guest profile
- [ ] Delete button disabled by default
- [ ] Must type exact profile name to enable delete
- [ ] Text field is clearly labeled
- [ ] Warning message visible ("This action cannot be undone")
- [ ] Text field resets after deletion
- [ ] Text field resets when switching profiles

## Status Feedback

- [ ] Save success shows checkmark "✓ Profile saved successfully!"
- [ ] Delete success shows checkmark "✓ Profile deleted"
- [ ] Error messages are clear
- [ ] Status messages have visual styling (background, border)
- [ ] Messages are readable on dark background

## Audio Components

- [ ] "No microphone found" text displays fully (not cut off)
- [ ] Audio recorder has dark theme styling
- [ ] Audio components are readable

## Responsiveness

- [ ] Works at different window sizes
- [ ] Sidebar doesn't overflow
- [ ] Buttons are clickable (adequate size)
- [ ] Text doesn't overlap

## Accessibility

- [ ] Can navigate with keyboard (Tab key)
- [ ] Focus states are visible
- [ ] Labels are descriptive
- [ ] Colors have sufficient contrast
- [ ] Interactive elements are clearly identifiable

## Animations & Polish

- [ ] Smooth transitions on hover
- [ ] Accordion content fades in when opening
- [ ] No jarring movements
- [ ] Font rendering is smooth (antialiased)

## Known Limitations

1. **Gradio CSS limitations** - Some advanced UI features not possible with pure CSS
2. **Accordion animations** - Basic Gradio accordion animations, can't customize fully
3. **Loading spinners** - Would require custom JavaScript (not implemented)
4. **Status message colors** - Can't dynamically color based on message content without JS
5. **No modal overlays** - Gradio doesn't support true modal dialogs

## Testing Notes

- Test in both Chrome/Safari for best compatibility
- Refresh page between tests to ensure clean state
- Try creating, re-recording, and deleting profiles
- Verify all status messages appear correctly
- Test keyboard navigation thoroughly
