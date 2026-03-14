import { useState } from 'react';
import styles from './JournalPrompt.module.css'

const PROMPTS = [
    "What's one thing weighing on your mind that you haven't said out loud yet?",
    "Describe a moment this week where you felt most like yourself.",
    "What emotion have you been avoiding, and why?",
    "What would you tell a friend going through what you're going through?",
    "What are you most grateful for right now, even if things are hard?",
];

const JournalPrompt = () => {
    const [promptIndex, setPromptIndex] = useState(0);
    const [entry, setEntry] = useState('');
    const [saved, setSaved] = useState(false);

    const handleNewPrompt = () => {
        setPromptIndex((prev) => (prev + 1) % PROMPTS.length);
        setSaved(false);
    };

    const handleSave = () => {
        if (!entry.trim()) return;
        console.log({ prompt: PROMPTS[promptIndex], entry });
        setSaved(true);
        setEntry('');
    };

    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <p className={styles.title}>Today's reflection</p>
                <button className={styles.newPrompt} onClick={handleNewPrompt}>
                    New prompt ↺
                </button>
            </div>

            <span className={styles.tag}>Daily prompt</span>
            <p className={styles.prompt}>"{PROMPTS[promptIndex]}"</p>

            <textarea
                className={styles.area}
                placeholder="Start weiting; this is just for you..."
                value={entry}
                onChange={(e) => {
                    setEntry(e.target.value);
                    setSaved(false);
                }}
            />

            <div className={styles.footer}>
                <span className={styles.streak}>5-day writing streak</span>
                <button
                    className={`${styles.saveBtn} ${!entry.trim() ? styles.disabled : ''}`}
                    onClick={handleSave}
                    disabled={!entry.trim()}
                >
                    {saved ? 'Saved ✓' : 'Save entry'}
                </button>
            </div>
        </div>
    );
};

export default JournalPrompt;