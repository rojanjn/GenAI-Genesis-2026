import { useState, useRef, useEffect } from "react";
import styles from './ChatPage.module.css';

const SUGGESTIONS = [
    "I've been feeling overwhelmed lately",
    "Help me reflect on my week",
    "I'm struggling with anxiety",
    "I want to talk about my mood",
];

const INITIAL_MESSAGE = {
    id: 1,
    role: 'assistant',
    text: "Hi, I'm here with you. This is a safe space to share whatever is on your mind. No judgements, just reflection. How are you feeling today?",
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
};

const ChatPage = () => {
    const [messages, setMessages] = useState([INITIAL_MESSAGE]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const bottomRef = useRef(null);
    const textareaRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const handleSend = async (text) => {
        const content = (text || input).trim();
        if (!content) return;

        const userMsg = {
            id: Date.now(),
            role: 'user',
            text: content,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        // TODO: AI RESPONSE REPLACEMENT
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: content, userId: 'current-user' }),
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let replyText = '';

            const replyMsg = { id: Date.now() + 1, role: 'assistant', text: '', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
            setIsTyping(false);
            setMessages(prev => [...prev, replyMsg]);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                replyText += decoder.decode(value, { stream: true });
                setMessages(prev => prev.map(m => m.id === replyMsg.id ? { ...m, text: replyText } : m));
            }
        } catch (err) {
            setIsTyping(false);
            console.error('Chat error:', err);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleInput = (e) => {
        setInput(e.target.value);
        // Auto-resize textarea
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    };

    const showSuggestions = messages.length === 1;

    return (
        <div className={styles.page}>

            {/* Topbar */}
            <div className={styles.topbar}>
                <div className={styles.agentInfo}>
                    <div className={styles.agentAvatar}>
                        <span>🌿</span>
                    </div>
                    <div>
                        <p className={styles.agentName}>sōl companion</p>
                        <p className={styles.agentStatus}>
                            <span className={styles.statusDot} />
                            Here with you
                        </p>
                    </div>
                </div>
                <button className={styles.clearBtn} onClick={() => setMessages([INITIAL_MESSAGE])}>
                    Clear chat
                </button>
            </div>

            {/* Messages */}
            <div className={styles.messages}>

                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`${styles.msgRow} ${msg.role === 'user' ? styles.userRow : styles.assistantRow}`}
                    >
                        {msg.role === 'assistant' && (
                            <div className={styles.assistantAvatar}>🌿</div>
                        )}
                        <div className={styles.msgGroup}>
                            <div className={`${styles.bubble} ${msg.role === 'user' ? styles.userBubble : styles.assistantBubble}`}>
                                {msg.text}
                            </div>
                            <span className={styles.time}>{msg.time}</span>
                        </div>
                    </div>
                ))}

                {/* Typing indicator */}
                {isTyping && (
                    <div className={`${styles.msgRow} ${styles.assistantRow}`}>
                        <div className={styles.assistantAvatar}>🌿</div>
                        <div className={styles.typing}>
                            <span /><span /><span />
                        </div>
                    </div>
                )}

                {/* Suggestions */}
                {showSuggestions && !isTyping && (
                    <div className={styles.suggestions}>
                        {SUGGESTIONS.map((s) => (
                            <button
                                key={s}
                                className={styles.suggestion}
                                onClick={() => handleSend(s)}
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                )}

                <div ref={bottomRef} />
            </div>

            {/* Input area */}
            <div className={styles.inputArea}>
                <div className={styles.inputWrap}>
                    <textarea
                        ref={textareaRef}
                        className={styles.input}
                        placeholder="Share what's on your mind..."
                        value={input}
                        onChange={handleInput}
                        onKeyDown={handleKeyDown}
                        rows={1}
                    />
                    <button
                        className={`${styles.sendBtn} ${!input.trim() ? styles.sendDisabled : ''}`}
                        onClick={() => handleSend()}
                        disabled={!input.trim()}
                    >
                        ↑
                    </button>
                </div>
                <p className={styles.disclaimer}>
                    sōl is not a substitute for professional mental health care.
                </p>
            </div>

        </div>
    );
};

export default ChatPage;