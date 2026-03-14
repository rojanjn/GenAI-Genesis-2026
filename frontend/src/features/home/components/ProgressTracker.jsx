import styles from './ProgressTracker.module.css'

const GOALS = [
    { label: 'Weekly check-ins', current: 3, total: 5 },
    { label: 'Journal entries', current: 5, total: 7 },
    { label: 'Exercises done', current: 2, total: 4 },
];

const DAYS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
const DONE_DAYS = [0, 1, 2];
const TODAY = 4;

const ProgressTracker = () => {
    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <p className={styles.title}>Your Progress</p>
                <a href="/progress" className={styles.link}>Full report →</a>
            </div>

            {GOALS.map((g) => (
                <div key={g.label} className={styles.goalBlock}>
                    <div className={styles.goalRow}>
                        <span className={styles.goalLabel}>{g.label}</span>
                        <span className={styles.goalVal}>{g.current} / {g.total}</span>
                    </div>
                    <div className={styles.barBg}>
                        <div
                            className={styles.bar}
                            style={{ width: `${(g.current / g.total) * 100}%` }}
                        />
                    </div>
                </div>
            ))}

            <p className={styles.weekLabel}>This week</p>
            <div className={styles.week}>
                {DAYS.map((day, i) => (
                    <div
                        key={i}
                        className={`${styles.day} ${i === TODAY ? styles.today :
                                DONE_DAYS.includes(i) ? styles.done : ''
                            }`}
                    >
                        {day}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ProgressTracker;