import { useState } from 'react';
import styles from './SimilarEntriesModal.module.css';
import SimilarEntryCard from './SimilarEntryCard';

const SimilarEntriesModal = ({ entries, scores, onClose }) => {
    const [selectedEntry, setSelectedEntry] = useState(null);

    return (
        <>
            <div className={styles.backdrop} onClick={onClose} />
            
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h2 className={styles.title}>
                        📚 Similar moments from your past
                    </h2>
                    <button className={styles.closeBtn} onClick={onClose}>✕</button>
                </div>

                <p className={styles.subtitle}>
                    These entries had similar themes, emotions, or language patterns. 
                    Reflecting on how you felt then might offer perspective.
                </p>

                <div className={styles.entriesList}>
                    {entries && entries.map((entry, idx) => (
                        <SimilarEntryCard
                            key={entry.entry_id}
                            entry={entry}
                            score={scores && scores[idx] ? Math.round(scores[idx] * 100) : 75}
                            onClick={() => setSelectedEntry(selectedEntry === entry.entry_id ? null : entry.entry_id)}
                            isExpanded={selectedEntry === entry.entry_id}
                        />
                    ))}
                </div>

                {(!entries || entries.length === 0) && (
                    <div className={styles.empty}>
                        <p>No similar moments found. Keep journaling to build your history! 📖</p>
                    </div>
                )}

                <div className={styles.footer}>
                    <button className={styles.closeModalBtn} onClick={onClose}>
                        Close
                    </button>
                </div>
            </div>
        </>
    );
};

export default SimilarEntriesModal;
