// Keys
const KEYS = {
    MOOD: 'app_mood_entries',
    JOURNAL: 'app_journal_entries',
    PROGRESS: 'app_progress',
};

// --- Mood ---
export const saveMoodEntry = (mood, note) => {
    const entries = getMoodEntries();
    const newEntry = {
        id: Date.now(),
        mood,
        note,
        date: new Date().toISOString(),
    };
    entries.unshift(newEntry);
    localStorage.setItem(KEYS.MOOD, JSON.stringify(entries));
    return newEntry;
};

export const getMoodEntries = () => {
    const data = localStorage.getItem(KEYS.MOOD);
    return data ? JSON.parse(data) : [];
};

// --- Journal ---
export const saveJournalEntry = (prompt, content) => {
    const entries = getJournalEntries();
    const newEntry = {
        id: Date.now(),
        prompt,
        content,
        date: new Date().toISOString(),
    };
    entries.unshift(newEntry);
    localStorage.setItem(KEYS.JOURNAL, JSON.stringify(entries));
    return newEntry;
};

export const getJournalEntries = () => {
    const data = localStorage.getItem(KEYS.JOURNAL);
    return data ? JSON.parse(data) : [];
};

// --- Progress ---
export const getProgress = () => {
    const data = localStorage.getItem(KEYS.PROGRESS);
    return data ? JSON.parse(data) : {
        checkInStreak: 0,
        sessionsDone: 0,
        journalCount: 0,
        moodAverage: 0,
        weeklyCheckIns: 0,
        weeklyJournals: 0,
        weeklyExercises: 0,
        checkedInDays: [],
    };
};

export const updateProgress = (updates) => {
    const current = getProgress();
    const updated = { ...current, ...updates };
    localStorage.setItem(KEYS.PROGRESS, JSON.stringify(updated));
    return updated;
};

// --- Debug helper ---
export const exportAllData = () => {
    return {
        mood: getMoodEntries(),
        journal: getJournalEntries(),
        progress: getProgress(),
    };
};

export const getUserProfile = () => JSON.parse(localStorage.getItem('app_user_profile') || '{}');
export const saveUserProfile = (data) => {
    localStorage.setItem('app_user_profile', JSON.stringify(data));
    window.dispatchEvent(new Event('storage'));
};
