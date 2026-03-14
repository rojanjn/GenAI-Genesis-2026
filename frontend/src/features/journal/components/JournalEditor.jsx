import StarterKit from '@tiptap/starter-kit';
import { useEditor, EditorContent } from '@tiptap/react';
import { useState } from 'react';
import styles from './JournalEditor.module.css';
import { saveJournalEntry, getProgress, updateProgress, getJournalEntries } from '../../../utils/storage';
import ResponseDisplay from './ResponseDisplay';
import SimilarEntriesModal from './SimilarEntriesModal';

const PROMPTS = [
    "What's one thing weighing on your mind that you haven't said out loud yet?",
    "Describe a moment this week where you felt most like yourself.",
    "What emotion have you been avoiding, and why?",
    "What would you tell a friend going through what you're going through?",
    "What are you most grateful for right now, even if things are hard?",
];

const Toolbar = ({ editor }) => {
    if (!editor) return null;

    return (
        <div className={styles.toolbar}>
            <button
                className={`${styles.toolBtn} ${editor.isActive('bold') ? styles.toolActive : ''}`}
                onClick={() => editor.chain().focus().toggleBold().run()}
                title="Bold"
            >
                <strong>B</strong>
            </button>
            <button
                className={`${styles.toolBtn} ${editor.isActive('italic') ? styles.toolActive : ''}`}
                onClick={() => editor.chain().focus().toggleItalic().run()}
                title="Italic"
            >
                <em>I</em>
            </button>
            <button
                className={`${styles.toolBtn} ${editor.isActive('strike') ? styles.toolActive : ''}`}
                onClick={() => editor.chain().focus().toggleStrike().run()}
                title="Strikethrough"
            >
                <s>S</s>
            </button>
            <div className={styles.toolDivider} />
            <button
                className={`${styles.toolBtn} ${editor.isActive('bulletList') ? styles.toolActive : ''}`}
                onClick={() => editor.chain().focus().toggleBulletList().run()}
                title="Bullet list"
            >
                ≡
            </button>
            <button
                className={`${styles.toolBtn} ${editor.isActive('orderedList') ? styles.toolActive : ''}`}
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                title="Ordered list"
            >
                1.
            </button>
            <div className={styles.toolDivider} />
            <button
                className={`${styles.toolBtn} ${editor.isActive('blockquote') ? styles.toolActive : ''}`}
                onClick={() => editor.chain().focus().toggleBlockquote().run()}
                title="Blockquote"
            >
                "
            </button>
            <button
                className={styles.toolBtn}
                onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}
                title="Clear formatting"
            >
                ✕
            </button>
        </div>
    );
};

const JournalEditor = () => {
    const [promptIndex, setPromptIndex] = useState(0);
    const [saved, setSaved] = useState(false);
    const [content, setContent] = useState('');
    const [apiResponse, setApiResponse] = useState(null);
    const [showSimilarModal, setShowSimilarModal] = useState(false);
    const [loading, setLoading] = useState(false);

    const editor = useEditor({
        extensions: [StarterKit],
        content: '',
        onUpdate: ({ editor }) => {
            setSaved(false);
            setContent(editor.getText().trim());
        },
        editorProps: {
            attributes: {
                class: styles.editorArea,
            },
        },
    });

    const isEmpty = content.length === 0;

    const handleNewPrompt = () => {
        setPromptIndex((prev) => (prev + 1) % PROMPTS.length);
        setSaved(false);
    };

    const findSimilarEntries = (currentText) => {
        /**
         * Simple similarity search using common words
         * In production, this would use OpenAI embeddings
         */
        const allEntries = getJournalEntries();
        const pastEntries = allEntries.slice(1); // Exclude current entry
        
        const currentWords = currentText.toLowerCase().split(/\s+/).filter(w => w.length > 3);
        
        const similarity = (entry) => {
            const entryWords = entry.content.toLowerCase().split(/\s+/).filter(w => w.length > 3);
            const matches = currentWords.filter(w => entryWords.some(ew => ew.includes(w) || w.includes(ew)));
            return matches.length / Math.max(currentWords.length, 1);
        };
        
        const scored = pastEntries.map(entry => ({
            ...entry,
            similarityScore: similarity(entry)
        }));
        
        return scored
            .filter(entry => entry.similarityScore > 0.1)
            .sort((a, b) => b.similarityScore - a.similarityScore)
            .slice(0, 3)
            .map(entry => ({
                entry_id: entry.id.toString(),
                text: entry.content.replace(/<[^>]*>/g, '').substring(0, 200), // Strip HTML
                timestamp: entry.date,
                mood_label: 'reflective',
                intensity: 5
            }));
    };

    const handleSave = async () => {
        if (isEmpty) return;
        
        setLoading(true);
        
        // Save to local storage
        saveJournalEntry(PROMPTS[promptIndex], editor.getHTML());

        const progress = getProgress();
        updateProgress({
            journalCount: progress.journalCount + 1,
            weeklyJournals: progress.weeklyJournals + 1,
        });

        // Simulate API response
        const similarEntries = findSimilarEntries(content);
        const similarityScores = similarEntries.map(() => (0.7 + Math.random() * 0.25).toFixed(2).map(Number));
        
        const mockResponse = {
            success: true,
            entry_id: `entry_${Date.now()}`,
            mood_id: `mood_${Date.now()}`,
            message: 'Journal entry saved',
            prompt: PROMPTS[promptIndex],
            mood: {
                emotion: 'thoughtful',
                intensity: 0.6,
                themes: ['reflection', 'growth'],
                risk_level: 'low',
                needs_followup: false,
                reasoning_summary: 'You seem to be in a reflective mood.'
            },
            response: {
                reflection: 'It sounds like you\'re processing some important thoughts. That\'s a sign of growth.',
                open_question: 'What would it feel like to take one small step forward today?',
                coping_suggestion: 'Take a moment to acknowledge your reflection and write down one thing you\'re proud of.'
            },
            support_level: 'low',
            updated_profile: {
                common_stressors: [],
                recurring_emotions: ['reflective', 'thoughtful'],
                helpful_strategies: ['journaling'],
                support_preferences: [],
                recent_patterns: [],
                summary: 'You are developing a journaling practice.'
            },
            safety_flag: false,
            similar_entries: similarEntries,
            similarity_scores: similarityScores,
            similar_entries_used: similarEntries.length
        };

        setApiResponse(mockResponse);
        setSaved(true);
        setLoading(false);
    };

    return (
        <div className={styles.wrapper}>
            {!apiResponse ? (
                <>
                    {/* Prompt bar */}
                    <div className={styles.promptBar}>
                        <div className={styles.promptLeft}>
                            <span className={styles.promptTag}>Today's prompt</span>
                            <p className={styles.promptText}>"{PROMPTS[promptIndex]}"</p>
                        </div>
                        <button className={styles.newPrompt} onClick={handleNewPrompt}>
                            New prompt ↺
                        </button>
                    </div>

                    {/* Toolbar */}
                    <Toolbar editor={editor} />

                    {/* Editor body */}
                    <div className={styles.editorWrap}>
                        <EditorContent editor={editor} />
                    </div>

                    {/* Footer */}
                    <div className={styles.footer}>
                        <span className={styles.streak}>🌿 5-day writing streak</span>
                        <div className={styles.footerRight}>
                            <button
                                className={`${styles.saveBtn} ${isEmpty || loading ? styles.disabled : ''}`}
                                onClick={handleSave}
                                disabled={isEmpty || loading}
                            >
                                {loading ? 'Saving...' : saved ? 'Saved ✓' : 'Save entry'}
                            </button>
                        </div>
                    </div>
                </>
            ) : (
                <>
                    <ResponseDisplay 
                        data={apiResponse}
                        onViewSimilar={() => setShowSimilarModal(true)}
                        onNewEntry={() => {
                            setApiResponse(null);
                            setContent('');
                            editor?.commands.setContent('');
                        }}
                    />

                    {showSimilarModal && apiResponse?.similar_entries?.length > 0 && (
                        <SimilarEntriesModal
                            entries={apiResponse.similar_entries}
                            scores={apiResponse.similarity_scores}
                            onClose={() => setShowSimilarModal(false)}
                        />
                    )}
                </>
            )}
        </div>
    );
};

export default JournalEditor;