# Similar Entries Feature - Quick Start Guide

## What Was Implemented

✅ **4 New React Components**:
1. **ResponseDisplay** - Shows AI mood analysis and reflective response
2. **SimilarEntriesModal** - Modal overlay for browsing similar past entries
3. **SimilarEntryCard** - Individual expandable entry card
4. **JournalEditor** - Updated to support async flow and new components

✅ **4 CSS Module Files**:
- All components have corresponding `.module.css` files
- Responsive design (mobile, tablet, desktop)
- Smooth animations and transitions
- Color-coded by emotion type

---

## How It Works (User Experience)

### Step 1: Write & Save
User writes a journal entry and clicks "Save entry"

### Step 2: Get Response
System analyzes entry and shows:
- Detected mood (emotion + intensity)
- AI reflection/question/suggestion
- Safety warning (if needed)

### Step 3: Explore Similar Moments (Optional)
User can click "See similar moments" to view past entries with similar themes

### Step 4: Continue
User can start writing another entry, which returns to the editor

---

## Component Architecture

```
JournalEditor
├── (Initial State) Editor + Toolbar
├── handleSave()
│   ├── Find similar entries from localStorage
│   ├── Generate mock AI response
│   └── setState(apiResponse)
│
└── (After Save) ResponseDisplay
    ├── Mood visualization
    ├── AI response (reflection/question/suggestion)
    ├── Safety alert (conditional)
    ├── "See similar moments" button
    │   └── onClick → setState(showSimilarModal=true)
    │
    └── SimilarEntriesModal (if showSimilarModal)
        └── SimilarEntryCard (repeating)
            ├── Header (emoji, date, mood, similarity score)
            └── Body (expandable - preview text + intensity)
```

---

## Current Features (MVP with Local Storage)

✅ Write journal entries with Tiptap editor  
✅ Prompt selection with rotation  
✅ Save to browser localStorage  
✅ Mock AI response generation  
✅ Simple word-overlap similarity search  
✅ Mood visualization with emoji/intensity  
✅ Safety alert display  
✅ Expandable similar entries cards  
✅ Responsive mobile/desktop UI  
✅ Smooth animations  

---

## How to Test

### Manual Testing
1. Open the app and navigate to Journal page
2. Type a journal entry
3. Click "Save entry"
4. See the response displayed
5. Click "See similar moments" if available
6. Expand entries to see full preview
7. Click "Write another entry" to continue
8. Repeat with different topics

### Browser Console
```javascript
// Check saved entries
JSON.parse(localStorage.getItem('journal_entries'))

// Check mood history
JSON.parse(localStorage.getItem('mood_entries'))
```

---

## Integration Points (When Backend Ready)

### JournalEditor.jsx - Line ~82 (handleSave function)
Current: Uses localStorage + mock response  
Future: Replace with API call:

```javascript
const response = await fetch('/api/journal-entry', {
    method: 'POST',
    body: JSON.stringify({
        user_id: 'current-user-id',  // Get from auth context
        prompt: PROMPTS[promptIndex],
        entry: editor.getHTML(),
    }),
});
```

### No Changes Needed For:
- ResponseDisplay.jsx (already structured for API response)
- SimilarEntriesModal.jsx (already expects API data)
- SimilarEntryCard.jsx (format-agnostic)

---

## Styling Overview

All components use CSS Modules with:
- **Color System**: Emotion-based colors (happy: #FFD93D, sad: #6A89CC, etc.)
- **Spacing**: 0.25rem to 2rem in 0.25rem increments
- **Typography**: 3 weights (400, 500, 600, 700) + sizes (0.7rem to 2rem)
- **Animations**: fadeIn, slideUp, expandIn (all ~0.2-0.3s ease)
- **Breakpoints**: Mobile (≤640px), Tablet (641-767px), Desktop (≥768px)

### Key Design Tokens
```css
/* Colors */
--primary-teal: #95E1D3
--secondary-blue: #A8D8EA
--warning-yellow: #FFD93D
--danger-red: #FF6B6B
--text-dark: #2c3e50
--text-light: #7f8c8d
--bg-light: #f8f9fa
--border-light: #ecf0f1

/* Spacing */
--space-xs: 0.25rem
--space-sm: 0.5rem
--space-md: 1rem
--space-lg: 1.5rem
--space-xl: 2rem

/* Animation */
--transition-fast: 0.2s
--transition-normal: 0.3s
--easing-in: ease-in
--easing-out: ease-out
```

---

## File Checklist

✅ `/frontend/src/features/journal/components/JournalEditor.jsx` - Updated  
✅ `/frontend/src/features/journal/components/ResponseDisplay.jsx` - New  
✅ `/frontend/src/features/journal/components/ResponseDisplay.module.css` - New  
✅ `/frontend/src/features/journal/components/SimilarEntriesModal.jsx` - New  
✅ `/frontend/src/features/journal/components/SimilarEntriesModal.module.css` - New  
✅ `/frontend/src/features/journal/components/SimilarEntryCard.jsx` - New  
✅ `/frontend/src/features/journal/components/SimilarEntryCard.module.css` - New  
✅ `/FEATURE_SIMILAR_ENTRIES_IMPLEMENTATION.md` - This doc  

---

## Known Limitations (MVP)

⚠️ **Similarity Search**
- Uses simple word-overlap (not AI embeddings)
- May not find semantically similar entries
- Backend will use OpenAI embeddings when connected

⚠️ **Data Storage**
- Uses localStorage (browser-only, not synced)
- Max ~5-10MB per browser
- Backend will use Firestore when connected

⚠️ **Mood Analysis**
- Mock responses for MVP
- Backend will use OpenAI when connected

⚠️ **User Identification**
- No authentication yet
- All entries stored locally without user_id
- Will use Firebase Auth when connected

---

## Troubleshooting

### Similar Entries Not Showing
- Check if there are past entries in localStorage
- Console: `JSON.parse(localStorage.getItem('journal_entries')).length`
- Entries need word overlap to be detected

### Modal Not Closing
- Try clicking backdrop (semi-transparent area)
- Try clicking the ✕ button in header
- Check browser console for errors

### Styling Issues
- Clear browser cache (Cmd+Shift+R on Mac)
- Check that CSS Module imports are correct
- Verify classNames syntax: `styles.className`

### Components Not Rendering
- Check React DevTools for prop errors
- Verify all imports are present
- Check console for JavaScript errors

---

## Next Phase: Backend Integration

**When `/api/journal-entry` endpoint is ready**:

1. Update JournalEditor.handleSave() to call API
2. Pass actual user_id from auth context
3. Remove mock response generation
4. Remove localStorage fallback (keep for offline support)

**No component changes needed** - all components already accept the API response format!

---

**Last Updated**: March 14, 2026  
**Implementation Status**: ✅ Complete  
**Ready for Integration**: Yes
