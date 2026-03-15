import styles from './ResponseDisplay.module.css';

const ResponseDisplay = ({ data, onViewSimilar, onNewEntry }) => {
    const { mood, response, safety_flag, similar_entries } = data;

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
    };

    const emotionColor = {
        happy: '#FFD93D',
        sad: '#6A89CC',
        anxious: '#F0A500',
        angry: '#FF6B6B',
        calm: '#95E1D3',
        thoughtful: '#C8B8FF',
        reflective: '#A8D8EA',
        hopeful: '#FFB6C1',
        overwhelmed: '#FFB6C1',
        peaceful: '#98D8C8',
    };

    return (
        <div className={styles.responseContainer}>
            <div className={styles.header}>
                <h2>Your reflection has been saved</h2>
                <p className={styles.subtitle}>Here's what we noticed:</p>
            </div>

            {/* Mood Analysis */}
            <div className={styles.moodSection}>
                <div className={styles.moodCard} style={{ borderLeftColor: emotionColor[mood?.emotion] || '#95E1D3' }}>
                    <div className={styles.moodHeader}>
                        <span className={styles.moodEmoji}>
                            {moodEmoji[mood?.emotion] || '💭'}
                        </span>
                        <div className={styles.moodText}>
                            <h3 className={styles.emotion}>
                                {mood?.emotion?.charAt(0).toUpperCase() + mood?.emotion?.slice(1)}
                            </h3>
                            <p className={styles.reasoning}>{mood?.reasoning_summary}</p>
                        </div>
                    </div>
                    <div className={styles.moodDetails}>
                        <div className={styles.intensityBar}>
                            <div 
                                className={styles.intensityFill}
                                style={{
                                    width: `${(mood?.intensity || 0) * 100}%`,
                                    backgroundColor: emotionColor[mood?.emotion] || '#95E1D3'
                                }}
                            />
                        </div>
                        <span className={styles.intensityLabel}>
                            Intensity: {Math.round((mood?.intensity || 0) * 100)}%
                        </span>
                    </div>
                </div>
            </div>

            {/* Safety Flag */}
            {safety_flag && (
                <div className={styles.safetyAlert}>
                    <span className={styles.safetyIcon}>⚠️</span>
                    <div className={styles.safetyText}>
                        <p className={styles.safetyTitle}>We want to check in</p>
                        <p className={styles.safetyMessage}>
                            What you've shared suggests you might benefit from additional support. 
                            Please reach out to a trusted person or professional if needed.
                        </p>
                    </div>
                </div>
            )}

            {/* AI Response */}
            <div className={styles.responseSection}>
                <h4 className={styles.responseTitle}>Our reflection:</h4>
                
                {response?.reflection && (
                    <div className={styles.responseBox}>
                        <p className={styles.responseText}>{response.reflection}</p>
                    </div>
                )}

                {response?.open_question && (
                    <div className={styles.questionBox}>
                        <p className={styles.questionLabel}>Something to think about:</p>
                        <p className={styles.questionText}>"{response.open_question}"</p>
                    </div>
                )}

                {response?.coping_suggestion && (
                    <div className={styles.suggestionBox}>
                        <p className={styles.suggestionLabel}>💡 A little challenge for today:</p>
                        <p className={styles.suggestionText}>{response.coping_suggestion}</p>
                    </div>
                )}
            </div>

            {/* Similar Entries Button */}
            {similar_entries && similar_entries.length > 0 && (
                <button className={styles.similarBtn} onClick={onViewSimilar}>
                    📚 See {similar_entries.length} similar moment{similar_entries.length > 1 ? 's' : ''} from your past
                </button>
            )}

            {/* Action Buttons */}
            <div className={styles.actions}>
                <button className={styles.newEntryBtn} onClick={onNewEntry}>
                    ← Write another entry
                </button>
            </div>
        </div>
    );
};

export default ResponseDisplay;
