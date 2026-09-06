FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY book_gym.py .

# Cron: 07:00 Mon/Tue/Thu/Fri (Morocco = UTC+1, so 06:00 UTC) — books 14 days ahead
RUN echo "0 6 * * 1,2,4,5 cd /app && python book_gym.py >> /app/gym_cron.log 2>&1" > /etc/cron.d/gymbot \
    && chmod 0644 /etc/cron.d/gymbot \
    && crontab /etc/cron.d/gymbot

CMD ["cron", "-f"]
