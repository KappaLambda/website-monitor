# Website Monitor Application

Website status monitor RESTful API made with Django REST Framework 3.11.0 and Vue JS 2.6.7.

## Table of Contents

- [Demo](#demo)
- [Requirements](#requirements)
- [Setup](#setup)
  - [Docker](#docker)
    - [Development](#development)
    - [Production](#production)
      - [Cron job to periodically renew the SSL certificates](#cron-job-to-periodically-renew-the-ssl-certificates)
  - [Repo Checkout](#repo-checkout)
    - [Apply migrations](#apply-migrations)
  - [Run rqworker and rqscheduler](#run-rqworker-and-rqscheduler)
    - [Run in Development mode](#run-in-development-mode)
    - [Run in Production mode](#run-in-production-mode)
- [Enpoints](#enpoints)
- [Authentication / Authorization](#authentication--authorization)
- [SSL Certificate](#ssl-certificate)
- [Tests Notes](#tests-notes)
- [License](#license)

## Demo

Live demo [here](https://website-monitor.liopetas.com/).

## Requirements

- Ubuntu 18.04
- Python 3.7.4
- [pyenv](https://github.com/pyenv/pyenv) - [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- PostgreSQL 10
- NodeJS
- Redis
- Docker (optional)

## Setup

You can either choose to use [Docker](#docker) or [checkout repository](#repo-checkout).

### Docker

You have to install [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/).

Change `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` in `./docker/django_api/.env` file if you want.

#### Development

```bash
# To build and/or run containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# To stop containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

After running docker containers, you can access the frontend at <http://localhost:8080> and the backend at <http://localhost:8000>.

#### Production

First you need to create an `.env` file under `docker/ssl/` directory with `CF_EMAIL` and `CF_KEY` variables assigned with your Cloudflare email and api key values.

Example:

```txt
CF_EMAIL=your_cloudflare_email
CF_KEY=your_cloudflare_key
```

Then to build and bring up the containers.

```bash
# To build and/or run containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# To stop containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

##### Cron job to periodically renew the SSL certificates

Make sure that cron service is up and runnnig and add the following in crontab. (`crontab -e`)

```bash
# Run every day at 02:00 am
0 2 * * *   docker start wm_sslcerts
```

### Repo Checkout

Refer to [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv), [PostgreSQL](https://www.postgresql.org/), [NodeJS](https://nodejs.org/en/) and [Redis](https://redis.io) documentation for installation, requirements and dependencies

By default, database name is `website_monitor_db` and database user is `kappalambda`. If you want to change them, create/export enviroment variables `POSTGRES_DB` and `POSTGRES_USER` with the values you desire.

```bash
# Install Python 3.7.4 with pyenv and create a virtual env based on this version
pyenv install 3.7.4
pyenv virtualenv 3.7.4 website_monitor

# Clone repo, set virtual env and install requirements.
git clone https://github.com/KappaLambda/website-monitor.git /srv/www/website-monitor/
cd /srv/www/website-monitor/
pyenv local website_monitor
pip install -r requirements.txt

# Export environment variables
export POSTGRES_PASSWORD='your-database-password'
export POSTGRES_DB='your-database-name' # optional
export POSTGRES_USER='your-database-user' # optional
```

#### Apply migrations

```bash
# Apply migrations (development mode)
cd /srv/www/website-monitor/website_monitor/
python manage.py migrate --setting=website_monitor.settings.dev

# Apply migrations (production mode)
cd /srv/www/website-monitor/website_monitor/
python manage.py migrate

```

#### Run rqworker and rqscheduler

Open two additional shell windows/tabs

```bash
For rqworker

cd /srv/www/website-monitor/website_monitor/
python manage.py rqworker default
```

```bash
For rqscheduler

cd /srv/www/website-monitor/
rqscheduler --interval=10
```

#### Run in Development mode

```bash
# Run Backend
cd /srv/www/website-monitor/website_monitor/
python manage.py runserver --setting=website_monitor.settings.dev


# Run Frontend
cd /srv/www/website-monitor/frontend/
npm install
npm run dev
```

Access developement frontend at <http://localhost:8080> and the backend at <http://localhost:8000>.

#### Run in Production mode

To issue SSL Certificates check the [SSL Certificate](#ssl-certificate) section. Edit in `./nginx-blocks/website-monitor.liopetas.com.conf` the `ssl_certificate` and `ssl_certificate_key` to the location of your generated certificate keys.

```bash
# Install frontend packages and build sources
cd /srv/www/website-monitor/frontend/
npm install && npm run build

# Create simlink for Nginx block (if repo cloned to another path than /srv/www/ change the path below)
sudo ln -s /srv/www/website-monitor/nginx-blocks/website-monitor.liopetas.com.conf /etc/nginx/sites-enabled/website-monitor.liopetas.com.conf
sudo nginx -t && sudo service nginx restart

# Collect django static files
cd /srv/www/website-monitor/website_monitor/
python manage.py collectstatic --no-input

# Run gunicorn (cd to ROOT of repository)
./gunicorn.sh
```

## Enpoints

Base URL: <https://website-monitor.liopetas.com/>

- api home - [/api/](https://website-monitor.liopetas.com/api/)
- check tasks list - [/api/check-tasks/](https://website-monitor.liopetas.com/check-tasks)
- single check task - [/api/check-tasks/[CheckTask id]/]()
- results for check task - [/api/check-tasks/[CheckTask id]/results]()

## Authentication / Authorization

For authentication / authorization the API implements the Oauth2.0 authorization protocol and the Implicit Grant flow through [Auth0](https://auth0.com/) services. The following endpoints are provided:

- Login - [Auth0 login endpoint](https://website-monitor.auth0.com/authorize?client_id=gyT7SQ7O5XUyq4trptvZndrbi0gnxTrc&redirect_uri=http://website-monitor.liopetas.com/&audience=https://website-monitor/api&response_type=token&scope=openid%20profile%20read:check-tasks%20write:check-tasks) (This URL is prefixed with openid, profile auth0 scopes and read:check-tasks, write:check-tasks api scopes)

  - Base URL: <https://website-monitor.auth0.com/authorize/>
  - Query Parameters
    - cliend_id=gyT7SQ7O5XUyq4trptvZndrbi0gnxTrc
    - redirect_uri=<https://website-monitor.liopetas.com/>
    - audience=audience=<https://website-monitor/api>
    - response_type=token
    - scope=openid profile read:check-tasks write:check-tasks

- Logout - [Auth0 logout endpoint](https://website-monitor.auth0.com/logout)

**Note:** At this stage there are no scope limitations for any user. Both `read:check-tasks` and `write:check-tasks` scopes will be granted for all users as long as the request includes them.

## SSL Certificate

For SSL Certificate I used [dehydrated](https://github.com/lukas2511/dehydrated) and this [custom hook for CloudFlare](https://github.com/kappataumu/letsencrypt-cloudflare-hook) that enables the use of DNS records instead of a web server to complete the whole process and request a certificate from [Let's Encrypt](https://letsencrypt.org/). For more info, read [this blog post](https://kappataumu.com/articles/letsencrypt-cloudflare-dns-01-hook.html).

For better security the entire certificate renewal proccess is running using the root account and certificates will be owned by root.

Below are the steps:

```bash
cd
sudo -s
mkdir ssl-cert
cd /ssl-cert/
git clone https://github.com/lukas2511/dehydrated.git
cd dehydrated/
mkdir hooks
git clone https://github.com/kappataumu/letsencrypt-cloudflare-hook hooks/cloudflare
pyenv virtualenv 3.7.0 letsencrypt
pyenv local letsencrypt
pip install -r hooks/cloudflare/requirements.txt
export CF_EMAIL='user@example.com'  # Change this to your Cloudflare account email
export CF_KEY='K9uX2HyUjeWg5AhAb'  # Change this to your Cloudflare API key
./dehydrated --register --accept-terms
./dehydrated -c -d website-monitor.liopetas.com -t dns-01 -k 'hooks/cloudflare/hook.py'
```

To automate the process, I created the following files in `~/ssl-cert/dehydrated/` as the root user.

**domains.txt**

```txt
website-monitor.liopetas.com
```

**config**

```txt
export CF_EMAIL=user@example.com
export CF_KEY=K9uX2HyUjeWg5AhAb

CHALLENGETYPE="dns-01"
```

**hook.sh**

```bash
$(pyenv which python) /home/kappalambda/ssl-cert/dehydrated/hooks/cloudflare/hook.py "$@"

```

**cron.sh**

```bash
#!/usr/bin/env bash

/home/kappalambda/ssl-cert/dehydrated/dehydrated \
    --cron \
    --hook '/home/kappalambda/ssl-cert/dehydrated/hook.sh'

systemctl restart nginx.service
```

I also added a crontab job as the root user for `cron.sh`.

```bash
PATH=/home/user/.pyenv/plugins/pyenv-virtualenv/shims:/home/user/.pyenv/shims:/home/user/.pyenv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin

0 1 * * * /home/user/ssl-cert/dehydrated/cron.sh >> /home/user/ssl-cert/dehydrated/cron.log 2>&1
```

**`PATH` variable:** Cron's default path is set to `$PATH=/usr/bin:/bin` and this means `$(pyenv which python)` in `hook.py` will not work unless pyenv's path is included in `$PATH`. Define `PATH` variable in cron's jobs list with the desired value.

## Tests Notes

For testing purposes tokens have been created to mock the Auth0 ones. A key pair was used to sign the expected payload. The expected payload is:

```python
{
    'http://website-monitor.liopetas.com/email': auth0 user email,  # auth0 user email, included in payload with custom rule in Auth0
    'iss': 'https://website-monitor.auth0.com/',  # issuer
    'sub': auth0|auth0 username,  # auth0 username
    'aud': ['https://website-monitor/api',
            'https://website-monitor.auth0.com/userinfo'],  #audience
    'iat': unix formatted timestamp,  # Issued at time
    'exp': unix formatted timestamp,  # Expire at time
    'azp': 'gyT7SQ7O5XUyq4trptvZndrbi0gnxTrc',  # auth0 app client_id
    'scope': token scopes,  # token scopes
}
```

To test permissions,two tokens, with all scopes and different user each one, have been created. Also, for one user, three additional tokens have been created. One with only `read-check-tasks` scope, one with only `write:check-tasks` scope and one with no scopes at all. Test Tokens expire after 100 years.

## License

[The MIT License](LICENSE.md)
