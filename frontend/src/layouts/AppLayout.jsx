import Sidebar from '../components/shared/Sidebar.jsx'
import styles from './AppLayout.module.css'

const AppLayout = ({ children }) => {
    return (
        <div className={styles.layout}>
            <Sidebar />
            <main className={styles.main}>
                {children}
            </main>
        </div>
    );
};

export default AppLayout;