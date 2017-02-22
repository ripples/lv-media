import itertools

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from server.libs.database import connect


def run(envs: dict):
    if envs['environment'] != "production":
        return

    connection = connect()
    with connection.cursor() as cursor:

        cursor.execute("SELECT email FROM users WHERE invited=b'0'")
        emails = list(itertools.chain(*cursor.fetchall()))

        url = 'http://{}:{}/internal/users/invite'.format(envs['lv-server-host'], envs['lv-server-port'])
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.1)))
        response = s.post(url, json={'emails': emails})
        response.raise_for_status()

        cursor.executemany("UPDATE users SET invited=b'1' WHERE email = %s", emails)
