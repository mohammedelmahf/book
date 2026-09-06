# gymbot

Auto-books the 18:00-19:30 gym slot every Mon/Tue/Thu/Fri, 7 days in advance.

## Deploy on Railway

1. Push this repo to GitHub
2. Go to railway.app → New Project → Deploy from GitHub repo
3. Add environment variables in Railway dashboard:
   - `GYM_EMAIL` = your@um6p.ma
   - `GYM_PASSWORD` = yourpassword
4. Railway auto-builds the Dockerfile and runs cron at 06:00 UTC (07:00 Morocco)
