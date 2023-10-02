# zone.py

from logging import error
from os import listdir
from os.path import join, exists

BIND_CONFIG_DIR = '/etc/bind'
NAMED_CONF_LOCAL_FILE = '/etc/bind/named.conf.local'

def list_zones() -> list:
    zones = []
    for file_name in listdir(BIND_CONFIG_DIR):
        if file_name.endswith('.zone'):
            zones.append(file_name[:-5])

    return zones

def read_zone(name: str) -> str:
    file = join(BIND_CONFIG_DIR, f'{name}.zone')
    try:
        with open(file) as f:
            content = f.read()

        return content
    except Exception as e:
        error(e)
        return f'Zone \'{name}\' does not exist.'

def create_or_update_zone(name: str, serial: int):
    file = join(BIND_CONFIG_DIR, f'{name}.zone')
    content = (
        f"$TTL 604800\n"
        f"@       IN      SOA     ns1.{name}. {name}. (\n"
        f"                        {serial}  ; Serial\n"
        "                        604800   ; Refresh\n"
        "                        86400    ; Retry\n"
        "                        2419200  ; Expire\n"
        "                        604800 ) ; Negative Cache TTL\n"
        "\n"
        f"@       IN      NS      ns1.{name}.\n"
        "ns1     IN      A       127.0.0.1\n"
#        "@       IN      A       193.176.241.76\n"
    )

    with open(file, 'w') as f:
        f.write(content)

def create_zone_if_not_exists(name: str, serial: int):
    path = join(BIND_CONFIG_DIR, f'{name}.zone')
    if not exists(path):
        create_or_update_zone(name, serial)

def update_zone(name: str, content: str, serial: int):
    path = join(BIND_CONFIG_DIR, f'{name}.zone')
    with open(path, 'a') as f:
        f.write(content.replace("{name}", name).replace("{serial}", str(serial)))