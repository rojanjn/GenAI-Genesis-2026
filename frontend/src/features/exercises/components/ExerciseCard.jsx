import styles from './ExerciseCard.module.css';

const ExerciseCard = ({ icon, name, desc, tag, duration, bg, onClick }) => {
    return (
        <div className={styles.card} onClick={onClick}>
            <div className={styles.iconWrap} style={{ background: bg }}>
                {icon}
            </div>
            <div className={styles.info}>
                <p className={styles.name}>{name}</p>
                <p className={styles.desc}>{desc}</p>
            </div>
            <div className={styles.footer}>
                <span className={styles.tag}>{tag}</span>
                <span className={styles.duration}>{duration}</span>
            </div>
        </div>
    );
};

export default ExerciseCard;