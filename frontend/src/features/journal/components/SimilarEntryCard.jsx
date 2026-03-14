import styles from './SimilarEntryCard.module.css';

const SimilarEntryCard = ({ entry, score, onClick, isExpanded }) => {
    const moodEmoji = {
        happy: '😊',
        sad: '😢',
        anxious: '😰',
        angry: '😠',
        calm: '😌',
        thoughtful: '🤔',
        reflective: '🪞',
        hopeful: '✨',
        overwhelmed: '😰',
        peaceful: '☮️',
        neutral: '😐',
    };

    const formatDate = (dateString) => {
        try {
            const date = new Date(dateString);
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);

            if (date.toDateString() === today.toDateString()) {
                return 'Today';
            } else if (date.toDateString() === yesterday.toDateString()) {
                return 'Yesterday';
            } else {
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }
        } catch {
            return dateString;
        }
    };

    // Intensity bar color mapping
    const intensityColor = {
        1: '#95E1D3',
        2: '#98D8C8',
        3: '#A8D8EA',
        4: '#FFD93D',
        5: '#FF9999',
    };

    const intensityLevel = entry.intensity || 3;
    const barColor = intensityColor[intensityLevel] || '#95E1D3';

    return (
        <div className={`${styles.card} ${isExpanded ? styles.expanded : ''}`}>
            <button className={styles.cardButton} onClick={onClick}>
                <div className={styles.cardHeader}>
                    <div className={styles.leftSide}>
                        <span className={styles.moodEmoji}>
                            {moodEmoji[entry.mood_label] || '💭'}
                        </span>
                        <div className={styles.cardInfo}>
                            <p className={styles.date}>{formatDate(entry.timestamp)}</p>
                            <p className={styles.moodLabel}>{entry.mood_label}</p>
                        </div>
                    </div>
                    <div className={styles.rightSide}>
                        <div className={styles.similarityScore}>
                            <div className={styles.scoreCircle}>
                                <span className={styles.scoreText}>{score}%</span>
                            </div>
                            <span className={styles.scoreLabel}>similar</span>
                        </div>
                        <span className={styles.expandIcon}>
                            {isExpanded ? '▼' : '▶'}
                        </span>
                    </div>
                </div>

                {isExpanded && (
                    <div className={styles.cardBody}>
                        <div className={styles.preview}>
                            <p>{entry.text}</p>
                        </div>
                        <div className={styles.cardFooter}>
                            <div className={styles.intensity}>
                                <span className={styles.intensityLabel}>Intensity:</span>
                                <div className={styles.intensityBars}>
                                    {[1, 2, 3, 4, 5].map((level) => (
                                        <div
                                            key={level}
                                            className={styles.intensityBar}
                                            style={{
                                                backgroundColor: level <= intensityLevel ? barColor : '#ecf0f1',
                                            }}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </button>
        </div>
    );
};

export default SimilarEntryCard;
