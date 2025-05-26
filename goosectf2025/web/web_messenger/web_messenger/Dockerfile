# Copy both python apps to /app/ directory
FROM python:3.7-slim

# Install nginx
RUN apt-get update
RUN apt-get install -y nginx supervisor

# COPY nginx configuration file
COPY nginx.conf /etc/nginx/sites-available/default

# COPY supervisord configuration file
COPY supervisord.conf /etc/supervisord.conf

RUN mkdir /app
COPY app /app/app
COPY email /app/email

# Install python dependencies
RUN pip install -r /app/app/requirements.txt
RUN pip install -r /app/email/requirements.txt

# Expose port 80
EXPOSE 80

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
