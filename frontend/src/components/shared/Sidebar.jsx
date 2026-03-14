import styles from './Sidebar.module.css'

const NAV_ITEMS = [
    { icon: '⌂', label: 'Home', path: '/' },
    { icon: '📓', label: 'Journal', path: '/journal' },
    { icon: '📅', label: 'Sessions', path: '/sessions' },
    { icon: '✦', label: 'Exercises', path: '/exercises' },
    { icon: '◎', label: 'Progress', path: '/progress' },
];

const JOURNALS = [
    { label: 'All entries', count: 24, color: '#7AAE6A' },
    { label: 'Daily reflections', count: 12, color: '#A8C898' },
    { label: 'Gratitude', count: 8, color: '#C9A07A' },
    { label: 'Anxiety log', count: 4, color: '#C4A0C0' },
];

const Sidebar = () => {
    const active = '/';

    return (
        <aside className={styles.sidebar}>
            <div className={styles.logo}>
                {/* TODO: LOGO */}
                LOGO<span className={styles.logoAccent}>.</span>
            </div>

            <nav className={styles.nav}>
                {NAV_ITEMS.map((item) => (
                    <a
                        key={item.path}
                        href={item.path}
                        className={`${styles.navItem} ${active === item.path ? styles.active : ''}`}
                    >
                        <span className={styles.navIcon}>{item.icon}</span>
                        {item.label}
                    </a>
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
                    <div className={styles.userName}>John Doe</div>
                    <div className={styles.userSub}>Member · Feburary 2026</div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;