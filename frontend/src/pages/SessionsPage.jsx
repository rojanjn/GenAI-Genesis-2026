import styles from './SessionsPage.module.css';

const SESSIONS = [
    {
        therapist: 'Dr. Nadia Voss',
        initials: 'NV',
        type: 'Individual therapy',
        date: 'Monday, March 17',
        time: '11:00 AM',
        status: 'upcoming',
    },
    {
        therapist: 'Dr. Nadia Voss',
        initials: 'NV',
        type: 'Individual therapy',
        date: 'Monday, March 10',
        time: '11:00 AM',
        status: 'completed',
        note: 'Discussed coping strategies for work stress.',
    },
    {
        therapist: 'Dr. Nadia Voss',
        initials: 'NV',
        type: 'Individual therapy',
        date: 'Monday, March 3',
        time: '11:00 AM',
        status: 'completed',
        note: 'Explored patterns in anxiety triggers.',
    },
    {
        therapist: 'Dr. Nadia Voss',
        initials: 'NV',
        type: 'Individual therapy',
        date: 'Monday, February 24',
        time: '11:00 AM',
        status: 'completed',
        note: 'Introduced CBT journaling exercises.',
    },
];

const SessionsPage = () => {
    return (
        <div className={styles.page}>
            <div className={styles.topbar}>
                <div>
                    <p className={styles.label}>Sessions</p>
                    <h1 className={styles.title}>Your therapy <em>journey.</em></h1>
                </div>
                <button className={styles.bookBtn}>+ Book session</button>
            </div>

            <div className={styles.content}>

                {/* Therapist card */}
                <div className={styles.therapistCard}>
                    <div className={styles.therapistAvatar}>NV</div>
                    <div className={styles.therapistInfo}>
                        <p className={styles.therapistName}>Dr. Nadia Voss</p>
                        <p className={styles.therapistSub}>Licensed Psychotherapist · CBT Specialist</p>
                    </div>
                    <div className={styles.therapistActions}>
                        <button className={styles.msgBtn}>Message</button>
                        <button className={styles.bookBtn2}>Book session</button>
                    </div>
                </div>

                {/* Upcoming */}
                <div className={styles.section}>
                    <p className={styles.sectionLabel}>Upcoming</p>
                    {SESSIONS.filter(s => s.status === 'upcoming').map((s, i) => (
                        <div key={i} className={`${styles.sessionCard} ${styles.upcoming}`}>
                            <div className={styles.sessionLeft}>
                                <div className={styles.sessionAvatar}>{s.initials}</div>
                                <div>
                                    <p className={styles.sessionName}>{s.therapist}</p>
                                    <p className={styles.sessionType}>{s.type}</p>
                                </div>
                            </div>
                            <div className={styles.sessionMid}>
                                <p className={styles.sessionDate}>{s.date}</p>
                                <p className={styles.sessionTime}>{s.time}</p>
                            </div>
                            <button className={styles.joinBtn}>Join session</button>
                        </div>
                    ))}
                </div>

                {/* Past */}
                <div className={styles.section}>
                    <p className={styles.sectionLabel}>Past sessions</p>
                    {SESSIONS.filter(s => s.status === 'completed').map((s, i) => (
                        <div key={i} className={styles.sessionCard}>
                            <div className={styles.sessionLeft}>
                                <div className={styles.sessionAvatar}>{s.initials}</div>
                                <div>
                                    <p className={styles.sessionName}>{s.therapist}</p>
                                    <p className={styles.sessionType}>{s.type}</p>
                                </div>
                            </div>
                            <div className={styles.sessionMid}>
                                <p className={styles.sessionDate}>{s.date}</p>
                                <p className={styles.sessionTime}>{s.time}</p>
                            </div>
                            <span className={styles.completedBadge}>Completed</span>
                        </div>
                    ))}
                </div>

            </div>
        </div>
    );
};

export default SessionsPage;