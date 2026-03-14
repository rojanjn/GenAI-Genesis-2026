import styles from './ProgressPage.module.css';
import { getProgress, getMoodEntries } from '../utils/storage.js';

const MOOD_HISTORY = [
    { day: 'Mon', value: 6 },
    { day: 'Tue', value: 7 },
    { day: 'Wed', value: 5 },
    { day: 'Thu', value: 8 },
    { day: 'Fri', value: 7 },
    { day: 'Sat', value: 9 },
    { day: 'Sun', value: 7 },
];

const MAX_MOOD = 10;

const ProgressPage = () => {
    const progress = getProgress();

    const STATS = [
        { label: 'Check-in streak', value: String(progress.checkInStreak), sub: 'days in a row' },
        { label: 'Total sessions', value: String(progress.sessionsDone), sub: 'this month' },
        { label: 'Journal entries', value: String(progress.journalCount), sub: 'all time' },
        { label: 'Avg mood score', value: '7.2', sub: 'this week' },
    ];

    const GOALS = [
        { label: 'Weekly check-ins', current: progress.weeklyCheckIns, total: 5 },
        { label: 'Journal entries', current: progress.weeklyJournals, total: 7 },
        { label: 'Exercises done', current: progress.weeklyExercises, total: 4 },
    ];

    return (
        <div className={styles.page}>
            <div className={styles.topbar}>
                <div>
                    <p className={styles.label}>Progress</p>
                    <h1 className={styles.title}>Your growth, <em>visualized.</em></h1>
                </div>
            </div>

            <div className={styles.content}>

                {/* Stats strip */}
                <div className={styles.statsGrid}>
                    {STATS.map((s) => (
                        <div key={s.label} className={styles.statCard}>
                            <p className={styles.statLabel}>{s.label}</p>
                            <p className={styles.statValue}>{s.value}</p>
                            <p className={styles.statSub}>{s.sub}</p>
                        </div>
                    ))}
                </div>

                <div className={styles.grid}>

                    {/* Mood chart */}
                    <div className={styles.card}>
                        <div className={styles.cardHeader}>
                            <p className={styles.cardTitle}>Mood this week</p>
                            <span className={styles.cardSub}>Scale of 1–10</span>
                        </div>
                        <div className={styles.chart}>
                            {MOOD_HISTORY.map((m) => (
                                <div key={m.day} className={styles.bar}>
                                    <div className={styles.barInner}>
                                        <div
                                            className={styles.barFill}
                                            style={{ height: `${(m.value / MAX_MOOD) * 100}%` }}
                                        />
                                    </div>
                                    <span className={styles.barVal}>{m.value}</span>
                                    <span className={styles.barDay}>{m.day}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Weekly goals */}
                    <div className={styles.card}>
                        <div className={styles.cardHeader}>
                            <p className={styles.cardTitle}>Weekly goals</p>
                            <span className={styles.cardSub}>March 10 – 16</span>
                        </div>
                        {GOALS.map((g) => (
                            <div key={g.label} className={styles.goalBlock}>
                                <div className={styles.goalRow}>
                                    <span className={styles.goalLabel}>{g.label}</span>
                                    <span className={styles.goalVal}>{g.current} / {g.total}</span>
                                </div>
                                <div className={styles.barBg}>
                                    <div
                                        className={styles.barProgress}
                                        style={{ width: `${(g.current / g.total) * 100}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>

                </div>

                {/* Streak calendar */}
                <div className={styles.card} style={{ marginTop: '20px' }}>
                    <div className={styles.cardHeader}>
                        <p className={styles.cardTitle}>Check-in streak</p>
                        <span className={styles.cardSub}>March 2026</span>
                    </div>
                    <div className={styles.calendar}>
                        {Array.from({ length: 31 }, (_, i) => {
                            const day = i + 1;
                            const done = progress.checkedInDays.includes(
                                new Date(2026, 2, day).toDateString()
                            );
                            const today = day === new Date().getDate();
                            return (
                                <div
                                    key={day}
                                    className={`${styles.calDay} ${done ? styles.calDone : ''} ${today ? styles.calToday : ''}`}
                                >
                                    {day}
                                </div>
                            );
                        })}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default ProgressPage;