import JournalEditor from '../features/journal/components/JournalEditor.jsx';
import styles from './JournalPage.module.css';

const JournalPage = () => {
    return (
        <div className={styles.page}>
            <div className={styles.topbar}>
                <div>
                    <p className={styles.label}>Your journal</p>
                    <h1 className={styles.title}>Write freely, <em>reflect deeply.</em></h1>
                </div>
            </div>
            <div className={styles.content}>
                <JournalEditor />
            </div>
        </div>
    );
};

export default JournalPage;