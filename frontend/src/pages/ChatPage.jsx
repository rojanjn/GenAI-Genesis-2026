import { useState, useRef, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";
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
    const { user, token } = useContext(AuthContext);
    const navigate = useNavigate();
    const [messages, setMessages] = useState([INITIAL_MESSAGE]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const bottomRef = useRef(null);
    const textareaRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const buildChatHistory = (allMessages) => {
        return allMessages
            .filter((msg) => msg.role === 'user' || msg.role === 'assistant')
            .map((msg) => ({
                role: msg.role,
                content: msg.text,
            }));
    };

    const handleSend = async (text) => {
        const content = (text || input).trim();
        if (!content) return;

        // Check authentication
        if (!user || !token) {
            const errorMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                text: "Please log in to use chat. Redirecting you to login...",
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };
            setMessages((prev) => [...prev, errorMsg]);
            setTimeout(() => navigate('/login'), 2000);
            return;
        }

        const userMsg = {
            id: Date.now(),
            role: 'user',
            text: content,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        const updatedMessages = [...messages, userMsg];

        setMessages(updatedMessages);
        setInput('');
        setIsTyping(true);

        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }

        try {
            const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

            console.log('Sending chat request to:', `${API_BASE}/api/chat/`);

            const response = await fetch(`${API_BASE}/api/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    message: content,
                    chat_history: buildChatHistory(messages),
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Backend error:', response.status, errorText);
                throw new Error(`HTTP error ${response.status}: ${errorText}`);
            }

            const data = await response.json();

            const replyText = `${data.response.reply} ${data.response.open_question}`.trim();

            const replyMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                text: replyText,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };

            setMessages((prev) => [...prev, replyMsg]);
        } catch (err) {
            console.error('Chat error:', err);

            const errorMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                text: `Chat error: ${err.message}`,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };

            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
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
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    };

    const showSuggestions = messages.length === 1;

    return (
        <div className={styles.page}>

            <div className={styles.topbar}>
                <div className={styles.agentInfo}>
                    <div className={styles.agentAvatar}>
                        <span>🌿</span>
                    </div>
                    <div>
                        <p className={styles.agentName}>Dear Ai-ry Chat</p>
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

                {isTyping && (
                    <div className={`${styles.msgRow} ${styles.assistantRow}`}>
                        <div className={styles.assistantAvatar}>🌿</div>
                        <div className={styles.typing}>
                            <span /><span /><span />
                        </div>
                    </div>
                )}

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
                    Dear AI-ry is not a substitute for professional mental health care. Its responses draw on motivational interviewing principles, inspired by research by Prof. Jonathan Rose at the University of Toronto on chatbot-based smoking cessation.                </p>
            </div>
        </div>
    );
};

export default ChatPage;