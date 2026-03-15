import styles from './MoodCheckIn.module.css';
import { useState, useContext } from 'react';
import AuthContext from '../../../contexts/AuthContext';
import { saveMoodEntry, getProgress, updateProgress } from '../../../utils/storage';

const MOODS = [
    { emoji: '😌', label: 'Calm' },
    { emoji: '😔', label: 'Low' },
    { emoji: '😤', label: 'Tense' },
    { emoji: '🌤', label: 'Hopeful' },
    { emoji: '😰', label: 'Anxious' },
];

const MoodCheckIn = () => {
    const { user, token } = useContext(AuthContext);
    const [selected, setSelected] = useState(null);
    const [note, setNote] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const handleSave = async () => {
        if (!selected || !user || !token) return;
        
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            // Call backend API with authentication
            const response = await fetch(`${API_BASE_URL}/api/mood-entry`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    user_id: user.uid,
                    mood: selected,
                    intensity: 5, // Default intensity, could be made interactive
                    note: note,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save mood');
            }

            const data = await response.json();
            
            // Also save to localStorage as fallback
            saveMoodEntry(selected, note);

            // Update progress
            const progress = getProgress();
            const today = new Date().toDateString();
            const alreadyCheckedIn = progress.checkedInDays.includes(today);

            updateProgress({
                weeklyCheckIns: alreadyCheckedIn ? progress.weeklyCheckIns : progress.weeklyCheckIns + 1,
                checkInStreak: alreadyCheckedIn ? progress.checkInStreak : progress.checkInStreak + 1,
                checkedInDays: alreadyCheckedIn ? progress.checkedInDays : [...progress.checkedInDays, today],
            });

            setNote('');
            setSelected(null);
            setSuccess(true);
            
            // Clear success message after 2 seconds
            setTimeout(() => setSuccess(false), 2000);
        } catch (err) {
            console.error('Error saving mood:', err);
            setError(err.message || 'Failed to save mood');
            // Still save locally if backend fails
            saveMoodEntry(selected, note);
            setNote('');
            setSelected(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <p className={styles.title}>Mood Check-in</p>
                <a href="/progress" className={styles.link}>History →</a>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}
            {success && <div className={styles.successMessage}>✓ Mood saved!</div>}

            <p className={styles.prompt}>
                "Whats's closest to how you feel right now?"
            </p>

            <div className={styles.moodRow}>
                {MOODS.map((m) => (
                    <button
                        key={m.label}
                        className={`${styles.moodBtn} ${selected === m.label ? styles.selected : ''}`}
                        onClick={() => setSelected(m.label)}
                        disabled={loading || !user}
                    >
                        <span className={styles.emoji}>{m.emoji}</span>
                        <span className={styles.moodLabel}>{m.label}</span>
                    </button>
                ))}
            </div>

            <textarea
                className={styles.note}
                placeholder="Add a note... (optional)"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                disabled={loading}
            />

            <button
                className={`${styles.saveBtn} ${!selected || loading ? styles.disabled : ''}`}
                onClick={handleSave}
                disabled={!selected || loading || !user}
            >
                {loading ? 'Saving...' : 'Save check-in'}
            </button>
        </div>
    );
};

export default MoodCheckIn;