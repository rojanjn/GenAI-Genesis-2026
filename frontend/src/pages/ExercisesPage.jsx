import ExerciseCard from '../features/exercises/components/ExerciseCard.jsx';
import styles from './ExercisesPage.module.css';

const EXERCISES = [
    {
        icon: '💨',
        name: 'Box Breathing',
        desc: 'Slow your nervous system with a structured 4-4-4-4 breath pattern. Great for acute anxiety or stress.',
        tag: 'Anxiety relief',
        duration: '5 min',
        bg: 'var(--color-green-pale)',
    },
    {
        icon: '🧠',
        name: 'Cognitive Reframing',
        desc: 'Identify and challenge unhelpful thought patterns using CBT techniques.',
        tag: 'CBT',
        duration: '10 min',
        bg: 'var(--color-accent-warm)',
    },
    {
        icon: '🧘',
        name: 'Body Scan Meditation',
        desc: 'A gentle awareness practice moving attention through each part of your body.',
        tag: 'Grounding',
        duration: '8 min',
        bg: '#F0EBF5',
    },
    {
        icon: '📓',
        name: 'Gratitude Journaling',
        desc: 'Write down three things you are grateful for to shift focus toward the positive.',
        tag: 'Mood boost',
        duration: '5 min',
        bg: '#FFF3E0',
    },
    {
        icon: '🌊',
        name: 'Progressive Muscle Relaxation',
        desc: 'Tense and release each muscle group to release physical tension held in the body.',
        tag: 'Stress relief',
        duration: '12 min',
        bg: '#E3F2FD',
    },
    {
        icon: '🌅',
        name: 'Morning Intention Setting',
        desc: 'Start your day with a clear focus by setting one meaningful intention for the day ahead.',
        tag: 'Mindfulness',
        duration: '3 min',
        bg: 'var(--color-green-pale)',
    },
];

const CATEGORIES = ['All', 'Anxiety relief', 'CBT', 'Grounding', 'Mood boost', 'Stress relief', 'Mindfulness'];

const ExercisesPage = () => {
    return (
        <div className={styles.page}>
            <div className={styles.topbar}>
                <div>
                    <p className={styles.label}>Exercises</p>
                    <h1 className={styles.title}>Tools for your <em>wellbeing.</em></h1>
                </div>
            </div>

            <div className={styles.content}>
                <div className={styles.categories}>
                    {CATEGORIES.map((c) => (
                        <button key={c} className={`${styles.catBtn} ${c === 'All' ? styles.catActive : ''}`}>
                            {c}
                        </button>
                    ))}
                </div>

                <div className={styles.grid}>
                    {EXERCISES.map((ex) => (
                        <ExerciseCard key={ex.name} {...ex} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ExercisesPage;