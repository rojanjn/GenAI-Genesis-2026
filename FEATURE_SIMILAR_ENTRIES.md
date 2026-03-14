# Feature Design: Optional Similar Entries Display

**Status**: Pending Frontend Updates (Blocked)
**Priority**: Medium-High (Post-MVP Enhancement)
**Branch**: To be implemented after frontend refactor
**Date Created**: March 14, 2026

---

## Feature Overview

After a user submits a journal entry, provide an **optional** button allowing them to view past entries with similar emotions/themes. This helps users discover patterns and reflect on their emotional journey.

**User Value**: Pattern recognition + Reflective journaling
**Technical Complexity**: Low-Medium
**Time Estimate**: 2-4 hours (once frontend structure is finalized)

---

## Feature Flow

### User Journey

```
1. User writes journal entry
   ↓
2. Clicks "Save entry"
   ↓
3. AI analyzes mood + generates response
   ↓
4. Frontend displays:
   - Today's mood analysis
   - AI reflective response
   - [Optional] "🔍 See similar feelings you've had?" button
   ↓
5a. User skips → Entry is saved, done
   ↓
5b. User clicks button → Modal opens showing similar past entries
   ↓
6. User reviews similar entries, dates, moods
   ↓
7. User closes modal or reflects on patterns
```

---

## Backend Requirements

### API Response Structure

**Endpoint**: `POST /api/journal-entry`

**Current Response** (already implemented):
```json
{
  "entry_id": "abc123",
  "mood_id": "mood456",
  "success": true,
  "mood": {
    "emotion": "anxious",
    "intensity": 0.8,
    "themes": ["work", "deadlines"],
    "risk_level": "low",
    "needs_followup": false
  },
  "response": {
    "reflection": "It sounds like you're feeling...",
    "open_question": "What would help you...",
    "coping_suggestion": "Try taking a short break..."
  },
  "similarity_scores": [0.95, 0.87, 0.82],
  "similar_entries_used": 3
}
```

**What Needs To Be Added** (Medium Priority Fix #5):
```json
{
  // ... all of above ...
  "similar_entries": [
    {
      "entry_id": "entry_001",
      "text": "I felt stressed about work deadlines today...",
      "timestamp": "2026-03-10T14:30:00Z",
      "mood_label": "anxious",
      "intensity": 8
    },
    {
      "entry_id": "entry_002",
      "text": "Another stressful day with presentations...",
      "timestamp": "2026-03-05T09:15:00Z",
      "mood_label": "stressed",
      "intensity": 7
    },
    {
      "entry_id": "entry_003",
      "text": "Couldn't focus on anything today...",
      "timestamp": "2026-02-28T16:45:00Z",
      "mood_label": "tense",
      "intensity": 7
    }
  ],
  "similarity_scores": [0.95, 0.87, 0.82]
}
```

**Note**: `similar_entries` array will be empty `[]` if user has fewer than 2 past entries.

---

## Frontend Implementation Plan

### Files to Modify/Create

#### 1. **JournalEditor.jsx** (MODIFY)
**Current state**: 
- Handles form input
- Calls backend on save
- Shows success/saved state

**Changes needed**:
```javascript
// Add to state
const [apiResponse, setApiResponse] = useState(null)
const [showSimilarModal, setShowSimilarModal] = useState(false)
const [loading, setLoading] = useState(false)

// Modify handleSave to be async
const handleSave = async () => {
  if (isEmpty) return
  
  setLoading(true)
  try {
    const response = await fetch('/api/journal-entry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: getCurrentUserId(), // From auth/context
        prompt: PROMPTS[promptIndex],
        entry: editor.getHTML()
      })
    })
    
    const data = await response.json()
    setApiResponse(data)  // Store full response
    setSaved(true)
  } catch (error) {
    console.error('Error saving entry:', error)
  } finally {
    setLoading(false)
  }
}

// Conditional render of ResponseDisplay
{apiResponse && (
  <ResponseDisplay 
    data={apiResponse}
    onViewSimilar={() => setShowSimilarModal(true)}
  />
)}

// Modal for similar entries
{showSimilarModal && apiResponse?.similar_entries?.length > 0 && (
  <SimilarEntriesModal
    entries={apiResponse.similar_entries}
    scores={apiResponse.similarity_scores}
    onClose={() => setShowSimilarModal(false)}
  />
)}
```

#### 2. **ResponseDisplay.jsx** (CREATE)
**Purpose**: Display AI response + button to view similar entries

**Props**:
```javascript
{
  data: {
    mood: object,
    response: object,
    updated_profile: object,
    safety_flag: boolean,
    similar_entries: array,
    similarity_scores: array,
  },
  onViewSimilar: function
}
```

**Components**:
- Mood indicator (emotion, intensity, themes)
- AI response (reflection, question, suggestion)
- Safety warning (if `safety_flag === true`)
- Button: "🔍 See similar feelings" (only if similar_entries.length > 0)

**Styling**:
- Card-based layout
- Color-coded mood indicators
- Smooth transitions

#### 3. **SimilarEntriesModal.jsx** (CREATE)
**Purpose**: Display similar past entries in a modal/expanded view

**Props**:
```javascript
{
  entries: [
    {
      entry_id: string,
      text: string,
      timestamp: string,
      mood_label: string,
      intensity: number
    }
  ],
  scores: [0.95, 0.87, 0.82],
  onClose: function
}
```

**Components**:
- Modal overlay/backdrop
- Title: "Similar Moments in Your Journey"
- Entry list:
  ```jsx
  entries.map((entry, index) => (
    <SimilarEntryCard
      date={formatDate(entry.timestamp)}
      mood={entry.mood_label}
      intensity={entry.intensity}
      text={entry.text}
      similarity={formatPercentage(scores[index])}
      onExpand={...}
    />
  ))
  ```
- Close button

#### 4. **SimilarEntryCard.jsx** (CREATE - Optional Sub-Component)
**Purpose**: Individual entry card in the modal

**Props**:
```javascript
{
  date: string,
  mood: string,
  intensity: number,
  text: string,
  similarity: string,
  onExpand: function
}
```

**Renders**:
```jsx
<div className="card">
  <div className="header">
    <span className="date">March 10, 2:30 PM</span>
    <span className="similarity">95% similar</span>
  </div>
  <div className="mood-row">
    <MoodBadge mood="anxious" />
    <span className="intensity">8/10</span>
  </div>
  <p className="preview">
    "I felt stressed about work deadlines today..."
  </p>
  <button onClick={onExpand}>Read full entry →</button>
</div>
```

#### 5. **CSS Files** (CREATE/MODIFY)
- `ResponseDisplay.module.css` (new)
- `SimilarEntriesModal.module.css` (new)
- `SimilarEntryCard.module.css` (new)
- Possibly update `JournalEditor.module.css` for layout

---

## Detailed Specifications

### Similar Entries Modal UI

**Desktop View** (Modal Dialog):
```
┌─────────────────────────────────────────────┐
│  Similar Moments in Your Journey        ✕  │
├─────────────────────────────────────────────┤
│                                             │
│  ✓ March 10, 2:30 PM                       │
│    😰 Anxious (8/10)                       │
│    95% similar                              │
│    "I felt stressed about work deadlines..."│
│    [Read full entry →]                     │
│                                             │
│  ✓ March 5, 9:15 AM                        │
│    😟 Stressed (7/10)                      │
│    87% similar                              │
│    "Another difficult presentation today..."│
│    [Read full entry →]                     │
│                                             │
│  ✓ Feb 28, 4:45 PM                         │
│    😐 Tense (7/10)                         │
│    82% similar                              │
│    "Couldn't focus on anything today..."   │
│    [Read full entry →]                     │
│                                             │
└─────────────────────────────────────────────┘
```

**Mobile View** (Bottom Sheet/Expandable):
```
Similar entries appear as expandable cards
that slide up from bottom of screen
```

---

### Response Display UI

**After Entry Submission**:
```
┌─────────────────────────────────────────────┐
│                                             │
│  Today's Mood: Anxious                     │
│  Intensity: 8/10                           │
│  Themes: work, deadlines, stress           │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                             │
│  💭 Reflection                              │
│  "It sounds like you're feeling overwhelmed│
│  with work responsibilities. That's a      │
│  common response to pressure..."           │
│                                             │
│  ❓ Something to Consider                  │
│  "What would help you feel more in control│
│  right now?"                               │
│                                             │
│  💡 Try This                                │
│  "Take a 5-minute break and list 3 things │
│  you've already accomplished today."       │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                             │
│  [🔍 See 3 similar feelings you've had]   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Edge Cases

### 1. User has no past entries
```javascript
if (!entries || entries.length === 0) {
  // Don't show button
  // Or show: "Start building your reflection history..."
}
```

### 2. Entry is first submission
```javascript
// Show message: "Come back tomorrow to see how your mood patterns develop!"
```

### 3. Similar entries exist but with low similarity (<0.5)
```javascript
// Show all entries but note: "These have some patterns in common"
// Or filter out very low similarity scores
```

### 4. User clicks while entry is still loading
```javascript
// Disable button during loading
<button disabled={loading}>
  {loading ? 'Processing...' : '🔍 See similar feelings'}
</button>
```

### 5. Safety flag is true (high risk)
```javascript
// Display crisis resource prominently
<div className="safety-warning">
  ⚠️ We're concerned about your wellbeing.
  [Crisis Hotline: 988]
</div>
```

---

## Data Display Standards

### Date/Time Formatting
```javascript
// Option 1: Relative time
"2 days ago"
"Last week"
"March 10"

// Option 2: Absolute time (for clarity)
"March 10, 2:30 PM"
"March 5 at 9:15 AM"

// Recommendation: Use both
"March 10, 2:30 PM (2 days ago)"
```

### Mood Labels
```javascript
// Use consistent emoji mapping
const moodEmojis = {
  "happy": "😊",
  "anxious": "😰",
  "stressed": "😟",
  "sad": "😢",
  "calm": "😌",
  "excited": "🤩",
  "overwhelmed": "😵",
  "lonely": "😔",
  "grateful": "🙏",
  "tense": "😐"
}
```

### Similarity Scores
```javascript
// Display as percentage
`${(similarity * 100).toFixed(0)}% similar`

// Or as visual indicator
█████████░ 95%
```

---

## Performance Considerations

### When to Load
```javascript
// Load similar entries ONLY when user clicks button
// (Not on initial page load)

const handleViewSimilar = async () => {
  if (!apiResponse?.similar_entries) {
    // They're already in response, just show
    setShowSimilarModal(true)
  }
}
```

### Text Truncation
```javascript
// Truncate entry preview to 150 characters
const truncate = (text, length = 150) => {
  return text.length > length 
    ? text.substring(0, length) + '...' 
    : text
}
```

### Lazy Loading (Optional)
```javascript
// If many similar entries:
// - Show first 5
// - Add "View all" button
// - Load rest on demand
```

---

## Accessibility Requirements

- [ ] Modal has proper focus management (trap focus, return focus)
- [ ] Close button with keyboard shortcut (Escape)
- [ ] ARIA labels for mood indicators
- [ ] Color contrast meets WCAG AA standard
- [ ] Touch targets at least 44x44px (mobile)
- [ ] Screen reader announces: "Similar entries modal, 3 entries"
- [ ] Keyboard navigation: Tab through entries and buttons

---

## Testing Checklist

### Unit Tests
- [ ] Similar entries render correctly with sample data
- [ ] Modal opens/closes with state updates
- [ ] Date formatting works for various timestamps
- [ ] Similarity scores display correctly

### Integration Tests
- [ ] Entry submission triggers API call
- [ ] API response includes similar_entries array
- [ ] Modal displays when button clicked
- [ ] Entries display in correct order (highest similarity first)
- [ ] Close button removes modal from DOM

### User Tests
- [ ] Users understand "similar feelings" concept
- [ ] Button is discoverable (not hidden)
- [ ] Modal is readable on mobile
- [ ] Entry preview length is sufficient
- [ ] Users find the feature helpful

---

## Future Enhancements (Out of Scope)

1. **Click to expand**: Show full entry text in modal
2. **Filter by date range**: "Similar entries from last month"
3. **Filter by mood**: "Show only anxious moments"
4. **Compare side-by-side**: Entry vs similar entry
5. **Mark as helpful**: "This reflection helped me" button
6. **Share insights**: "You often feel stressed on Mondays"
7. **Export timeline**: Download your reflection journey

---

## Implementation Checklist

- [ ] Backend: Add `similar_entries` to API response (Medium Priority Fix #5)
- [ ] Frontend: Create `ResponseDisplay.jsx` component
- [ ] Frontend: Create `SimilarEntriesModal.jsx` component
- [ ] Frontend: Create `SimilarEntryCard.jsx` sub-component
- [ ] Frontend: Create CSS modules for new components
- [ ] Frontend: Modify `JournalEditor.jsx` to handle async response
- [ ] Frontend: Add state management for modal display
- [ ] Frontend: Add error handling for API failures
- [ ] Testing: Unit tests for components
- [ ] Testing: Integration tests for modal flow
- [ ] Testing: Accessibility audit
- [ ] Testing: Mobile responsiveness
- [ ] Documentation: Update component README
- [ ] Code review with frontend developer

---

## Files Involved Summary

**Backend** (1 file):
- `backend/api/diary.py` — Add `similar_entries` to response

**Frontend** (6 files):
- `JournalEditor.jsx` — Modify for async + state management
- `ResponseDisplay.jsx` — Create new component
- `SimilarEntriesModal.jsx` — Create new component
- `SimilarEntryCard.jsx` — Create new sub-component
- `ResponseDisplay.module.css` — Create styles
- `SimilarEntriesModal.module.css` — Create styles

**Total Effort**: ~300-400 lines of new code + testing

---

## Status: BLOCKED

⏸️ **Waiting for**: Frontend refactor/cleanup to be completed
📅 **Target Start Date**: After frontend updates merged
🔗 **Related PR/Branch**: TBD
👤 **Assigned To**: Frontend Developer + Faris (Architecture Review)

---

## Notes for Implementation

When you're ready to implement this:

1. **Pull the latest frontend changes first**
2. **Review current component structure** with your frontend dev
3. **Ensure API response is updated** (Medium Priority Fix #5)
4. **Test modal behavior** on both desktop and mobile
5. **Consider animation** for modal entrance/exit
6. **Add loading state** while fetching/processing

This is a solid "post-MVP" feature that adds real value to the user experience without blocking the core product.
