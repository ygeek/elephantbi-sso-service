FROM python:3.6.3

RUN apt-get update && \
    apt-get install -y \
    nginx \
	supervisor && \
	rm -rf /var/lib/apt/lists/*

# setup nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY config/deploy/nginx.conf /etc/nginx/sites-available/default

# setup supervisor to run nginx and uwsgi
COPY config/deploy/supervisord.d/* /etc/supervisord.d/
COPY config/deploy/supervisord.conf /etc/supervisord.conf

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.
COPY sso_service /home/docker/code/
RUN pip install --upgrade pip
RUN pip install -Ur /home/docker/code/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

EXPOSE 80

COPY . /home/docker/code/

WORKDIR /home/docker/code/

ENV PATH="/home/docker/bin:${PATH}"

COPY config/deploy/start.py /home/docker/bin/entrypoint
RUN chmod a+x /home/docker/bin/entrypoint && mkdir -p /var/logs/
ENTRYPOINT ["entrypoint"]
