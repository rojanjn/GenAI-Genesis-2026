import styles from './Sidebar.module.css';
import { NavLink } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getUserProfile } from '../../utils/storage';

const NAV_ITEMS = [
    { icon: '🏠', label: 'Home', path: '/' },
    { icon: '📝', label: 'Journal', path: '/journal' },
    { icon: '💬', label: 'Chat', path: '/chat' },
    { icon: '📊', label: 'Progress', path: '/progress' },
    { icon: '⚙', label: 'Settings', path: '/settings' }
];

const JOURNALS = [
    { label: 'All entries', count: 5, color: '#7AAE6A' },
    { label: 'Daily reflections', count: 5, color: '#A8C898' },
    { label: 'Gratitude', count: 8, color: '#C9A07A' },
    { label: 'Anxiety log', count: 4, color: '#C4A0C0' },
];

const Sidebar = () => {
    // const active = '/';
    const [profile, setProfile] = useState(getUserProfile());

    useEffect(() => {
        const onStorage = () => setProfile(getUserProfile());
        window.addEventListener('storage', onStorage);
        return () => window.removeEventListener('storage', onStorage);
    }, []);

    return (
        <aside className={styles.sidebar}>
            <div className={styles.logo}>
                Dear AI-ry<span className={styles.logoAccent}>.</span>
            </div>

            <nav className={styles.nav}>
                {NAV_ITEMS.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        end={item.path === '/'}
                        className={({ isActive }) =>
                            `${styles.navItem} ${isActive ? styles.active : ''}`
                        }
                    >
                        <span className={styles.navIcon}>{item.icon}</span>
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <div className={styles.section}>
                <div className={styles.sectionLabel}>Journal</div>
                {JOURNALS.map((j) => (
                    <div key={j.label} className={styles.journalItem}>
                        <span
                            className={styles.journalDot}
                            style={{ background: j.color }}
                        />
                        <span className={styles.journalLabel}>{j.label}</span>
                        <span className={styles.journalCount}>{j.count}</span>
                    </div>
                ))}
            </div>

            <div className={styles.footer}>
                <div className={styles.avatar}>J</div>
                <div>
                    <div className={styles.userName}>{profile.name || 'Your name'}</div>
                    <div className={styles.userSub}>Member · Feburary 2026</div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;