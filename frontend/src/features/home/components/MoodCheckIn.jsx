import styles from './MoodCheckIn.module.css';
import { useState } from 'react';
import { saveMoodEntry, getProgress, updateProgress } from '../../../utils/storage';

const MOODS = [
    { emoji: '😌', label: 'Calm' },
    { emoji: '😔', label: 'Low' },
    { emoji: '😤', label: 'Tense' },
    { emoji: '🌤', label: 'Hopeful' },
    { emoji: '😰', label: 'Anxious' },
];

const MoodCheckIn = () => {
    const [selected, setSelected] = useState(null);
    const [note, setNote] = useState('');

    const handleSave = () => {
        if (!selected) return;
        saveMoodEntry(selected, note);

        // update progress
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
    };

    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <p className={styles.title}>Mood Check-in</p>
                <a href="/progress" className={styles.link}>History →</a>
            </div>

            <p className={styles.prompt}>
                "Whats's closest to how you feel right now?"
            </p>

            <div className={styles.moodRow}>
                {MOODS.map((m) => (
                    <button
                        key={m.label}
                        className={`${styles.moodBtn} ${selected === m.label ? styles.selected : ''}`}
                        onClick={() => setSelected(m.label)}
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
            />

            <button
                className={`${styles.saveBtn} ${!selected ? styles.disabled : ''}`}
                onClick={handleSave}
                disabled={!selected}
            >
                Save check-in
            </button>
        </div>
    );
};

export default MoodCheckIn;