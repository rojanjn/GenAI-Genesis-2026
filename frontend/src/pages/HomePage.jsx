import styles from './HomePage.module.css';
import { useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../contexts/AuthContext';
import StatCard from '../features/home/components/StatCard.jsx';
import MoodCheckIn from '../features/home/components/MoodCheckIn.jsx';
import JournalPrompt from '../features/home/components/JournalPrompt.jsx';
import ExerciseList from '../features/home/components/ExerciseList.jsx';
import ProgressTracker from '../features/home/components/ProgressTracker.jsx';
import { useNavigate } from 'react-router-dom';
import { getUserProfile } from '../utils/storage';


const STATS = [
  { label: 'Check-in streak', value: '2', sub: '↑ days in a row', positive: true },
  { label: 'Sessions done', value: '5', sub: 'this month', positive: false },
  { label: 'Journal entries', value: '5', sub: 'total entries', positive: false },
  { label: 'Mood average', value: '7.2', sub: '↑ up this week', positive: true },
];

const HomePage = () => {
  const navigate = useNavigate();
  const { user, token } = useContext(AuthContext);
  const { name } = getUserProfile();
  const firstName = name?.split(' ')[0] || 'there';
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Default stats
  const DEFAULT_STATS = [
    { label: 'Check-in streak', value: '0', sub: 'days in a row', positive: false },
    { label: 'Sessions done', value: '0', sub: 'this month', positive: false },
    { label: 'Journal entries', value: '0', sub: 'total entries', positive: false },
    { label: 'Mood average', value: '0.0', sub: 'out of 10', positive: false },
  ];

  // Fetch user stats from backend
  useEffect(() => {
    if (!user || !token) {
      setLoading(false);
      return;
    }

    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stats/${user.uid}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch stats');
        }

        const data = await response.json();
        
        // Transform backend response to stats format
        const transformedStats = [
          { 
            label: 'Check-in streak', 
            value: data.streak?.toString() || '0', 
            sub: 'days in a row', 
            positive: (data.streak || 0) > 0 
          },
          { 
            label: 'Journal entries', 
            value: data.total_entries?.toString() || '0', 
            sub: 'total entries', 
            positive: false 
          },
          { 
            label: 'Mood check-ins', 
            value: data.total_moods?.toString() || '0', 
            sub: 'entries', 
            positive: false 
          },
          { 
            label: 'Mood average', 
            value: (data.mood_average?.toFixed(1) || '0.0').toString(), 
            sub: 'out of 10', 
            positive: (data.mood_average || 0) >= 5 
          },
        ];
        
        setStats(transformedStats);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError(err.message);
        setStats(DEFAULT_STATS);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user, token, API_BASE_URL]);

  const displayStats = stats || DEFAULT_STATS;

  return (
    <div className={styles.page}>

      {/* === TOPBAR === */}
      <div className={styles.topbar}>
        <div>
          <p className={styles.greeting}>Good morning!</p>
          <h1 className={styles.title}>
            How are you <em>feeling</em> today, {firstName}?
          </h1>
        </div>

        <div className={styles.topbarRight}>
          <span className={styles.dateBadge}>Saturday, March 14</span>
          <button className={styles.btnPrimary} onClick={() => navigate('/journal')}>
            + New entry
          </button>
        </div>
      </div>

      {/* === STATS === */}
      <div className={styles.statGrid}>
        {displayStats.map((s) => (
          <StatCard
            key={s.label}
            label={s.label}
            value={s.value}
            sub={s.sub}
            positive={s.positive}
          />
        ))}
      </div>

      {/* Content grid */}
      <div className={styles.contentGrid}>
        <MoodCheckIn />
        <JournalPrompt />
        <ExerciseList />
        <ProgressTracker />
      </div>

    </div>
  );
};

export default HomePage;