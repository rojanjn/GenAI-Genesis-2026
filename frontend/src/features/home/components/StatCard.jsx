import styles from './StatCard.module.css'

const StatCard = ({ label, value, sub, positive }) => {
    return (
        <div className={styles.card}>
            <p className={styles.label}>{label}</p>
            <p className={styles.value}>{value}</p>
            <p className={`${styles.sub} ${positive ? styles.positive : ''}`}>
                {sub}
            </p>
        </div>
    );
}

export default StatCard;