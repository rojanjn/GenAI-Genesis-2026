import { useState, useEffect } from 'react';
import { getUserProfile, saveUserProfile } from '../utils/storage';
import styles from './SettingsPage.module.css';

// const AVATAR_COLORS = ['#3D5A3E', '#7AAE6A', '#C8955A', '#8A7DAE', '#5A8AAE', '#AE5A7D'];
const GOAL_OPTIONS = ['Reduce anxiety', 'Improve mood', 'Build resilience', 'Sleep better', 'Manage stress', 'Process emotions'];
const REMINDER_TIMES = ['Off', '8:00 AM', '9:00 AM', '12:00 PM', '6:00 PM', '9:00 PM'];
// const THEMES = ['Soft Naturals', 'Night Mode'];

const SECTIONS = ['Profile', 'Goals', 'Notifications', 'Data'];

const SettingsPage = () => {
    const [active, setActive] = useState('Profile');
    const [profile, setProfile] = useState({
        name: '',
        email: '',
        // avatarColor: AVATAR_COLORS[0],
        goals: [],
        reminderTime: 'Off',
        theme: 'Soft Naturals',
        journalPrompts: true,
        moodReminders: true,
    });
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const stored = getUserProfile();
        if (stored && Object.keys(stored).length > 0) {
            setProfile(prev => ({ ...prev, ...stored }));
        }
    }, []);

    const update = (key, value) => setProfile(prev => ({ ...prev, [key]: value }));

    const toggleGoal = (goal) => {
        setProfile(prev => ({
            ...prev,
            goals: prev.goals.includes(goal)
                ? prev.goals.filter(g => g !== goal)
                : [...prev.goals, goal],
        }));
    };

    const handleSave = () => {
        saveUserProfile(profile);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const handleExportData = () => {
        const data = {
            profile,
            exportedAt: new Date().toISOString(),
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sol-data.json';
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleClearData = () => {
        if (window.confirm('This will delete all your journal entries, mood logs, and progress. Are you sure?')) {
            ['app_mood_entries', 'app_journal_entries', 'app_progress', 'app_user_profile'].forEach(k => localStorage.removeItem(k));
            setProfile({ name: '', email: '', goals: [], reminderTime: 'Off', theme: 'Soft Naturals', journalPrompts: true, moodReminders: true });
        }
    };

    const initials = profile.name
        ? profile.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
        : '?';

    return (
        <div className={styles.page}>

            <div className={styles.topbar}>
                <h1 className={styles.title}>Settings</h1>
                <button
                    className={`${styles.saveBtn} ${saved ? styles.saveBtnDone : ''}`}
                    onClick={handleSave}
                >
                    {saved ? '✓ Saved' : 'Save changes'}
                </button>
            </div>

            <div className={styles.layout}>

                {/* Sidebar nav */}
                <nav className={styles.nav}>
                    {SECTIONS.map(s => (
                        <button
                            key={s}
                            className={`${styles.navItem} ${active === s ? styles.navActive : ''}`}
                            onClick={() => setActive(s)}
                        >
                            {s}
                        </button>
                    ))}
                </nav>

                {/* Content */}
                <div className={styles.content}>

                    {active === 'Profile' && (
                        <div className={styles.section}>
                            <h2 className={styles.sectionTitle}>Profile</h2>

                            {/* Avatar
                            <div className={styles.avatarRow}>
                                <div
                                    className={styles.avatar}
                                    style={{ background: profile.avatarColor }}
                                >
                                    {initials}
                                </div>
                                <div>
                                    <p className={styles.fieldLabel}>Avatar colour</p>
                                    <div className={styles.colorSwatches}>
                                        {AVATAR_COLORS.map(c => (
                                            <button
                                                key={c}
                                                className={`${styles.swatch} ${profile.avatarColor === c ? styles.swatchActive : ''}`}
                                                style={{ background: c }}
                                                onClick={() => update('avatarColor', c)}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </div> */}

                            <div className={styles.field}>
                                <label className={styles.fieldLabel}>Full name</label>
                                <input
                                    className={styles.input}
                                    type="text"
                                    placeholder="Your name"
                                    value={profile.name}
                                    onChange={e => update('name', e.target.value)}
                                />
                            </div>

                            <div className={styles.field}>
                                <label className={styles.fieldLabel}>Email</label>
                                <input
                                    className={styles.input}
                                    type="email"
                                    placeholder="you@example.com"
                                    value={profile.email}
                                    onChange={e => update('email', e.target.value)}
                                />
                            </div>
                        </div>
                    )}

                    {active === 'Goals' && (
                        <div className={styles.section}>
                            <h2 className={styles.sectionTitle}>Your goals</h2>
                            <p className={styles.sectionDesc}>
                                Select what you'd like to focus on. This helps personalise your experience.
                            </p>
                            <div className={styles.goalGrid}>
                                {GOAL_OPTIONS.map(goal => (
                                    <button
                                        key={goal}
                                        className={`${styles.goalChip} ${profile.goals.includes(goal) ? styles.goalChipActive : ''}`}
                                        onClick={() => toggleGoal(goal)}
                                    >
                                        {goal}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {active === 'Notifications' && (
                        <div className={styles.section}>
                            <h2 className={styles.sectionTitle}>Notifications</h2>

                            <div className={styles.field}>
                                <label className={styles.fieldLabel}>Daily check-in reminder</label>
                                <select
                                    className={styles.select}
                                    value={profile.reminderTime}
                                    onChange={e => update('reminderTime', e.target.value)}
                                >
                                    {REMINDER_TIMES.map(t => (
                                        <option key={t} value={t}>{t}</option>
                                    ))}
                                </select>
                            </div>

                            <div className={styles.toggleRow}>
                                <div>
                                    <p className={styles.fieldLabel}>Journal prompts</p>
                                    <p className={styles.fieldDesc}>Get a daily writing prompt</p>
                                </div>
                                <button
                                    className={`${styles.toggle} ${profile.journalPrompts ? styles.toggleOn : ''}`}
                                    onClick={() => update('journalPrompts', !profile.journalPrompts)}
                                >
                                    <span className={styles.toggleThumb} />
                                </button>
                            </div>

                            <div className={styles.toggleRow}>
                                <div>
                                    <p className={styles.fieldLabel}>Mood reminders</p>
                                    <p className={styles.fieldDesc}>Reminder to log your mood</p>
                                </div>
                                <button
                                    className={`${styles.toggle} ${profile.moodReminders ? styles.toggleOn : ''}`}
                                    onClick={() => update('moodReminders', !profile.moodReminders)}
                                >
                                    <span className={styles.toggleThumb} />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* {active === 'Preferences' && (
                        <div className={styles.section}>
                            <h2 className={styles.sectionTitle}>Preferences</h2>

                            <div className={styles.field}>
                                <label className={styles.fieldLabel}>Theme</label>
                                <div className={styles.themeGrid}>
                                    {THEMES.map(t => (
                                        <button
                                            key={t}
                                            className={`${styles.themeOption} ${profile.theme === t ? styles.themeActive : ''}`}
                                            onClick={() => update('theme', t)}
                                        >
                                            <div className={`${styles.themePreview} ${t === 'Night Mode' ? styles.themePreviewDark : ''}`} />
                                            <span>{t}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )} */}

                    {active === 'Data' && (
                        <div className={styles.section}>
                            <h2 className={styles.sectionTitle}>Your data</h2>
                            <p className={styles.sectionDesc}>
                                All your data is stored locally on your device.
                            </p>

                            <div className={styles.dataCard}>
                                <div>
                                    <p className={styles.fieldLabel}>Export data</p>
                                    <p className={styles.fieldDesc}>Download all your journal entries and mood logs as JSON</p>
                                </div>
                                <button className={styles.outlineBtn} onClick={handleExportData}>
                                    Export
                                </button>
                            </div>

                            <div className={`${styles.dataCard} ${styles.dataCardDanger}`}>
                                <div>
                                    <p className={styles.fieldLabel}>Clear all data</p>
                                    <p className={styles.fieldDesc}>Permanently delete all entries, mood logs, and progress</p>
                                </div>
                                <button className={styles.dangerBtn} onClick={handleClearData}>
                                    Clear
                                </button>
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
