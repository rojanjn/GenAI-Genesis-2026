import styles from './ExerciseList.module.css'

const EXERCISES = [
    {
        icon: '💨',
        name: 'Box Breathing',
        desc: 'Slow your nervous system with a structured 4-4-4-4 breath pattern',
        tag: '5 min · Anxiety relief',
        bg: 'var(--color-green-pale)',
    },
    {
        icon: '🧠',
        name: 'Cognitive Reframing',
        desc: 'Challenge a thought that has been holding you back this week.',
        tag: '10 min · CBT',
        bg: 'var(--color-accent-warm)',
    },
    {
        icon: '🧘',
        name: 'Body Scan Meditation',
        desc: 'A gentle check-in with your physical sensations, head to toe.',
        tag: '8 min · Grounding',
        bg: '#F0EBF5',
    },
];

const ExerciseList = () => {
    return (
        <div className={styles.card}>
            <div className={styles.header}>
                <p className={styles.title}>Recommended for you</p>
                <a href="/exercises" className={styles.link}>See all →</a>
            </div>

            {EXERCISES.map((ex) => (
                <div key={ex.name} className={styles.title}>
                    <div
                        className={styles.icon}
                        style={{ background: ex.bg }}
                    >
                        {ex.icon}
                    </div>
                    <div className={styles.info}>
                        <p className={styles.name}>{ex.name}</p>
                        <p className={styles.desc}>{ex.desc}</p>
                        <span className={styles.tag}>{ex.tag}</span>
                    </div>
                    <span className={styles.arrow}>→</span>
                </div>
            ))}
        </div>
    );
};

export default ExerciseList;