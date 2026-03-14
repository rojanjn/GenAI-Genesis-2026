# Deployment Checklist for GenAI-Genesis-2026

## Pre-Deployment (Before Launching to Staging/Production)

### Environment Setup
- [ ] Create `.env` file from `.env.example`
- [ ] Generate strong JWT_SECRET_KEY (32+ random characters)
  ```bash
  openssl rand -hex 32
  ```
- [ ] Configure EMAIL_PROVIDER (sendgrid or smtp)
- [ ] Set up SendGrid API key OR Gmail app password
- [ ] Set FRONTEND_URL to your domain
- [ ] Set DATABASE_URL if using external Postgres (optional)

### Backend Deployment (Railway/Heroku/Render)
- [ ] Create account on [Railway.app](https://railway.app) (recommended)
- [ ] Connect GitHub repository
- [ ] Create new project, select Python
- [ ] Configure environment variables in Railway dashboard:
  ```
  FIREBASE_CREDENTIALS_PATH=/app/.secrets/firebase-creds.json
  OPENAI_API_KEY=sk-proj-...
  JWT_SECRET_KEY=<generated above>
  EMAIL_PROVIDER=sendgrid
  SENDGRID_API_KEY=SG....
  EMAIL_FROM=noreply@genai-genesis.com
  FRONTEND_URL=https://your-frontend.vercel.app
  ENVIRONMENT=production
  ```
- [ ] Add Firebase credentials as secret:
  ```bash
  # Base64 encode your firebase-adminsdk-*.json file
  base64 firebase-adminsdk-abc123.json | pbcopy
  # Add as FIREBASE_CREDENTIALS_BASE64 variable
  ```
- [ ] Create Procfile:
  ```
  web: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] Deploy backend
- [ ] Test: `curl https://your-backend.railway.app/`
- [ ] Check health: `curl https://your-backend.railway.app/docs`

### Frontend Deployment (Vercel)
- [ ] Create account on [Vercel.com](https://vercel.com)
- [ ] Connect GitHub repository
- [ ] Configure environment variables:
  ```
  REACT_APP_API_URL=https://your-backend.railway.app
  REACT_APP_FIREBASE_API_KEY=<from Firebase Console>
  REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
  REACT_APP_FIREBASE_PROJECT_ID=your-project-id
  REACT_APP_FIREBASE_STORAGE_BUCKET=your-bucket
  REACT_APP_FIREBASE_MESSAGING_SENDER_ID=...
  REACT_APP_FIREBASE_APP_ID=...
  ```
- [ ] Set root directory: `frontend`
- [ ] Build command: `npm run build`
- [ ] Deploy frontend
- [ ] Test: Visit your-frontend.vercel.app

### Firebase Configuration
- [ ] Verify Firestore collections created (if not, create manually)
- [ ] Update Firebase security rules:
  ```firestore
  rules_version = '2';
  service cloud.firestore {
    match /databases/{database}/documents {
      match /users/{user_id} {
        allow read, write: if request.auth.uid == user_id;
      }
      match /diary_entries/{entry_id} {
        allow read, write: if request.auth.uid == resource.data.user_id;
        allow create: if request.auth.uid == request.resource.data.user_id;
      }
      match /mood_history/{mood_id} {
        allow read, write: if request.auth.uid == resource.data.user_id;
        allow create: if request.auth.uid == request.resource.data.user_id;
      }
      match /notifications/{notif_id} {
        allow read: if request.auth.uid == resource.data.user_id;
      }
      match /user_profiles/{user_id} {
        allow read, write: if false; // Backend only
      }
    }
  }
  ```
- [ ] Enable Firebase Authentication methods:
  - [ ] Email/Password (already enabled)
- [ ] Configure authorized domains in Firebase Console:
  - [ ] Add your-frontend.vercel.app
  - [ ] Add localhost:3000 (for development)

---

## Testing Checklist (After Deployment)

### Backend Testing
- [ ] API health check: `GET /` returns status
- [ ] API docs accessible: `GET /docs` 
- [ ] Signup endpoint: `POST /api/auth/signup`
  ```bash
  curl -X POST https://your-backend.railway.app/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "TestPass123",
      "display_name": "Test User"
    }'
  ```
- [ ] Login endpoint: `POST /api/auth/login`
- [ ] Protected endpoint with token: `GET /api/auth/profile`
  ```bash
  curl -H "Authorization: Bearer <token>" \
    https://your-backend.railway.app/api/auth/profile
  ```
- [ ] Journal entry endpoint: `POST /api/journal-entry`
- [ ] Mood entry endpoint: `POST /api/mood-entry`
- [ ] Stats endpoint: `GET /api/stats/{user_id}`

### Frontend Testing
- [ ] App loads at home (redirects to login if not authenticated)
- [ ] Signup page accessible
- [ ] Login page accessible
- [ ] Can sign up with valid credentials
- [ ] Can login after signup
- [ ] Dashboard loads with real stats
- [ ] Can write journal entry
- [ ] Can check in mood
- [ ] Can see mood analysis response
- [ ] Can logout

### End-to-End Testing
1. **Full User Flow:**
   - [ ] Sign up new account
   - [ ] Verify user created in Firebase Auth
   - [ ] Verify user profile in Firestore users collection
   - [ ] Write journal entry
   - [ ] Verify entry saved in diary_entries collection
   - [ ] Verify mood saved in mood_history collection
   - [ ] Check dashboard stats are correct
   - [ ] Check mood check-in
   - [ ] Logout and login again

2. **Email Notification Testing:**
   - [ ] Wait 5 minutes for scheduled notification job
   - [ ] Check inbox for mood follow-up email
   - [ ] Verify email contains personalized message
   - [ ] Verify email has correct user

3. **Data Isolation Testing:**
   - [ ] Create account A, get token A
   - [ ] Create account B, get token B
   - [ ] Try to access account B's data with token A
   - [ ] Should get 403 Forbidden error
   - [ ] Try to access account B's data without token
   - [ ] Should get 401 Unauthorized error

### Performance Testing
- [ ] API responses under 500ms (journal entry may take longer due to AI)
- [ ] Frontend loads in under 3s
- [ ] No console errors
- [ ] No network errors

---

## Security Checklist

### Authentication Security
- [ ] JWT_SECRET_KEY is strong (32+ random characters)
- [ ] Tokens expire after 24 hours
- [ ] Tokens require Bearer prefix
- [ ] Password validation enforced (8+ chars, uppercase, lowercase, number)
- [ ] No passwords logged or exposed in errors

### API Security
- [ ] All user endpoints protected with auth
- [ ] Authorization checks verify user ownership
- [ ] CORS properly configured (only allow your frontend domain)
- [ ] No sensitive data in error messages
- [ ] No SQL injection possible (using ORM)
- [ ] No XSS vectors (HTML sanitized by frameworks)

### Data Security
- [ ] Firestore rules restrict unauthorized access
- [ ] User data encrypted at rest (Firebase handles)
- [ ] API uses HTTPS (Vercel and Railway provide)
- [ ] Secrets never in git (use .env, .gitignore verified)
- [ ] Firebase service account JSON never in git

### Backend Security
- [ ] No hardcoded credentials
- [ ] Error messages don't reveal internal details
- [ ] Logging doesn't log sensitive data
- [ ] Dependencies up to date (check requirements.txt)

### Frontend Security
- [ ] No sensitive data in localStorage (using sessionStorage)
- [ ] HTTPS enforced (Vercel default)
- [ ] CSP headers recommended (add to vercel.json)
- [ ] Dependencies up to date (check package.json)

---

## Monitoring & Logging Setup

### Backend Monitoring
- [ ] Enable Railway metrics dashboard
- [ ] Check CPU usage (<20% normal)
- [ ] Check memory usage (<256MB)
- [ ] Check error rate (should be <1%)
- [ ] Check response times (median <100ms)

### Frontend Monitoring
- [ ] Enable Vercel analytics
- [ ] Monitor Core Web Vitals
- [ ] Check page load time (<3s)
- [ ] Check error rate (should be 0%)

### Logging
- [ ] Backend logs visible in Railway dashboard
- [ ] Frontend errors visible in browser console
- [ ] Consider adding Sentry for error tracking:
  ```python
  # backend/api/main.py
  import sentry_sdk
  sentry_sdk.init(dsn="https://key@sentry.io/project")
  ```

---

## Post-Deployment

### After Successful Deployment
- [ ] Update README with deployed URLs
- [ ] Document environment variables needed
- [ ] Create user documentation
- [ ] Share demo link with team
- [ ] Announce launch to stakeholders

### Monitor First 24 Hours
- [ ] Check error rates
- [ ] Monitor API response times
- [ ] Check database performance
- [ ] Monitor email delivery
- [ ] Check for security alerts

### Common Issues to Watch For

**Issue: "CORS error on frontend"**
- Check FRONTEND_URL in backend .env
- Check frontend origin is in cors_origins

**Issue: "401 Unauthorized on all requests"**
- Check JWT_SECRET_KEY is same on frontend and backend
- Check Authorization header format: "Bearer <token>"
- Check token not expired

**Issue: "Email not sending"**
- Check EMAIL_PROVIDER is set
- Check SendGrid API key is valid
- Check email address exists
- Wait 5 minutes for background job to run

**Issue: "Firebase credentials not found"**
- Check FIREBASE_CREDENTIALS_PATH is set correctly
- Check file exists in deployment environment
- Check permissions on file

**Issue: "Database queries slow"**
- Check Firestore indexes are created
- Check queries in insights.py use compound indexes
- Monitor Firestore usage dashboard

---

## Rollback Plan

If critical issue found after deployment:

### Quick Rollback (< 5 min)
1. **Backend:** Redeploy previous commit
   ```bash
   git revert <commit>
   git push  # Railway auto-deploys
   ```

2. **Frontend:** Redeploy previous version
   ```bash
   vercel rollback  # In Vercel dashboard
   ```

### Database Rollback (if data corrupted)
1. Stop all API requests
2. Restore from Firebase backup (automatic daily backups)
3. Verify data integrity
4. Resume service

### Communication
- Notify users if service affected
- Post status update on status page
- Give ETA for fix

---

## Disaster Recovery

### Backup Strategy
- ✅ **Firestore:** Automatic daily backups by Firebase
- ✅ **Code:** GitHub as source of truth
- ⚠️ **Secrets:** Store in secure location, never in git

### Recovery Procedures

**Lost Database:**
1. Restore from Firebase backup (last 24h guaranteed)
2. Or restore from daily export if older
3. Verify with timestamp queries

**Compromised Secrets:**
1. Rotate all API keys (OpenAI, SendGrid, JWT)
2. Update in production environment
3. Monitor for abuse

**User Loses Access:**
1. User can reset password via Firebase Console
2. Or delete account and recreate
3. Data is preserved in Firestore (linked by email)

---

## Scaling Plan (Future)

If app scales beyond MVP:

### Database Scaling
- [ ] Enable Firestore automatic scaling
- [ ] Set up read/write quotas
- [ ] Monitor hot collections
- [ ] Consider data archiving strategy

### Backend Scaling
- [ ] Enable auto-scaling in Railway
- [ ] Add caching layer (Redis)
- [ ] Consider API rate limiting
- [ ] Monitor queue depth

### Frontend Scaling
- [ ] Enable Vercel analytics
- [ ] Monitor Core Web Vitals
- [ ] Consider CDN for assets
- [ ] Optimize images/bundles

---

## Sign-Off

- [ ] All tests passed
- [ ] Security checklist completed
- [ ] Performance acceptable
- [ ] Monitoring set up
- [ ] Team reviewed and approved
- [ ] Ready for production traffic

**Deployed By:** ________________  
**Date:** ________________  
**Notes:** _________________________________________________________________

---

**Final Checklist:** If all items checked, deployment is complete and safe! 🚀
