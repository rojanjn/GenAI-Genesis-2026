import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { useState } from 'react';
import styles from './JournalEditor.module.css';

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

    const editor = useEditor({
        extensions: [StarterKit],
        content: '',
        onUpdate: () => setSaved(false),
        editorProps: {
            attributes: {
                class: styles.editorArea,
            },
        },
    });

    const isEmpty = !editor || editor.isEmpty;

    const handleNewPrompt = () => {
        setPromptIndex((prev) => (prev + 1) % PROMPTS.length);
        setSaved(false);
    };

    const handleSave = () => {
        if (isEmpty) return;
        console.log({ prompt: PROMPTS[promptIndex], entry: editor.getHTML() });
        setSaved(true);
    };

    return (
        <div className={styles.wrapper}>
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
                        className={`${styles.saveBtn} ${isEmpty ? styles.disabled : ''}`}
                        onClick={handleSave}
                        disabled={isEmpty}
                    >
                        {saved ? 'Saved ✓' : 'Save entry'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default JournalEditor;