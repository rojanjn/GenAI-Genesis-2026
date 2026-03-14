import styles from './HomePage.module.css'
import StatCard from '../features/home/components/StatCard.jsx'

const STATS = [
  { label: 'Check-in streak', value: '2', sub: '↑ days in a row', positive: true },
  { label: 'Sessions done', value: '5', sub: 'this month', positive: false },
  { label: 'Journal entries', value: '5', sub: 'total entries', positive: false },
  { label: 'Mood average', value: '7.2', sub: '↑ up this week', positive: true },
];

const HomePage = () => {
  return (
    <div className={styles.page}>

      {/* === TOPBAR === */}
      <div className={styles.topbar}>
        <div>
          <p className={styles.greeting}>Good morning!</p>
          <h1 className={styles.title}>
            How are you <em>feeling</em> today?
          </h1>
        </div>

        <div className={styles.topbarRight}>
          <span className={styles.dateBadge}>Saturday, March 14</span>
          <button className={styles.btnPrimary}>+ New Entry</button>
        </div>
      </div>

      {/* === STATS === */}
      <div className={styles.statGrid}>
        {STATS.map((s) => (
          <StatCard
            key={s.label}
            label={s.label}
            value={s.value}
            sub={s.sub}
            positive={s.positive}
          />
        ))}
      </div>

    </div>
  );
};

export default HomePage;