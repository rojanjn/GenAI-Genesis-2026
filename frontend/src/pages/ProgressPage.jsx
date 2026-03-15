import { useContext, useEffect, useState } from 'react';
import styles from './ProgressPage.module.css';
import { AuthContext } from '../contexts/AuthContext';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const ProgressPage = () => {
    const { token } = useContext(AuthContext);

    const [entryType, setEntryType] = useState('diary');
    const [item, setItem] = useState(null);
    const [currentId, setCurrentId] = useState(null);
    const [meta, setMeta] = useState({
        hasPrevious: false,
        hasNext: false,
        position: 0,
        total: 0,
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fetchHistoryItem = async ({ type = entryType, direction = 'current', id = null } = {}) => {
        if (!token) {
            setError('No auth token found.');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const isDiary = type === 'diary';
            const endpoint = isDiary
                ? `${API_BASE_URL}/api/history/diary/nav`
                : `${API_BASE_URL}/api/history/moods/nav`;

            const params = new URLSearchParams();
            params.append('direction', direction);

            if (isDiary && id) {
                params.append('current_entry_id', id);
            }

            if (!isDiary && id) {
                params.append('current_mood_id', id);
            }

            const response = await fetch(`${endpoint}?${params.toString()}`, {
                method: 'GET',
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to load history.');
            }

            if (isDiary) {
                setItem(data.entry);
                setCurrentId(data.entry?.entry_id || null);
                setMeta({
                    hasPrevious: data.has_previous,
                    hasNext: data.has_next,
                    position: data.position,
                    total: data.total,
                });
            } else {
                setItem(data.mood);
                setCurrentId(data.mood?.mood_id || null);
                setMeta({
                    hasPrevious: data.has_previous,
                    hasNext: data.has_next,
                    position: data.position,
                    total: data.total,
                });
            }
        } catch (err) {
            console.error('History fetch failed:', err);
            setError(err.message || 'Failed to load history.');
            setItem(null);
            setCurrentId(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setItem(null);
        setCurrentId(null);
        setMeta({
            hasPrevious: false,
            hasNext: false,
            position: 0,
            total: 0,
        });

        fetchHistoryItem({
            type: entryType,
            direction: 'current',
            id: null,
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [entryType, token]);

    const goPrevious = () => {
        if (!currentId || !meta.hasPrevious || loading) return;
        fetchHistoryItem({
            type: entryType,
            direction: 'previous',
            id: currentId,
        });
    };

    const goNext = () => {
        if (!currentId || !meta.hasNext || loading) return;
        fetchHistoryItem({
            type: entryType,
            direction: 'next',
            id: currentId,
        });
    };

    const formatTimestamp = (timestamp) => {
        if (!timestamp) return 'No date';
        const parsed = new Date(timestamp);
        if (Number.isNaN(parsed.getTime())) return 'No date';
        return parsed.toLocaleString();
    };

    return (
        <div className={styles.page}>
            <div className={styles.topbar}>
                <h1 className={styles.title}>Your history</h1>

                <div className={styles.tabGroup}>
                    <button
                        type="button"
                        className={`${styles.tabButton} ${entryType === 'diary' ? styles.tabButtonActive : ''}`}
                        onClick={() => setEntryType('diary')}
                    >
                        Journal
                    </button>

                    <button
                        type="button"
                        className={`${styles.tabButton} ${entryType === 'moods' ? styles.tabButtonActive : ''}`}
                        onClick={() => setEntryType('moods')}
                    >
                        Mood
                    </button>
                </div>
            </div>

            <div className={styles.content}>
                {loading && <p className={styles.message}>Loading…</p>}

                {!loading && error && <p className={styles.error}>{error}</p>}

                {!loading && !error && item && (
                    <div className={styles.card}>
                        <p className={styles.date}>
                            {formatTimestamp(item.timestamp)}
                        </p>

                        {entryType === 'diary' ? (
                            <div className={styles.entryBlock}>
                                <p className={styles.text}>
                                    {item.plain_text || item.text || 'No journal text found.'}
                                </p>
                            </div>
                        ) : (
                            <div className={styles.entryBlock}>
                                <p className={styles.moodLine}>
                                    <strong>Mood:</strong> {item.mood || 'Unknown'}
                                </p>
                                <p className={styles.moodLine}>
                                    <strong>Intensity:</strong> {item.intensity ?? 'N/A'}
                                </p>
                                <p className={styles.moodLine}>
                                    <strong>Date:</strong> {item.date || 'No date saved'}
                                </p>
                                <p className={styles.moodLine}>
                                    <strong>Note:</strong> {item.note || 'No note'}
                                </p>
                            </div>
                        )}

                        <div className={styles.position}>
                            Entry {meta.total === 0 ? 0 : meta.position + 1} of {meta.total}
                        </div>
                    </div>
                )}

                {!loading && !error && !item && (
                    <p className={styles.message}>No history found.</p>
                )}

                <div className={styles.navButtons}>
                    <button
                        type="button"
                        onClick={goPrevious}
                        disabled={!meta.hasPrevious || loading}
                        className={styles.navButton}
                    >
                        ← Previous
                    </button>

                    <button
                        type="button"
                        onClick={goNext}
                        disabled={!meta.hasNext || loading}
                        className={styles.navButton}
                    >
                        Next →
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ProgressPage;