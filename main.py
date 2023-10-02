# main.py

from flask import Flask, render_template, request, redirect, url_for
import logging
from zone import list_zones, create_zone_if_not_exists, read_zone, update_zone
import subprocess

app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

# Define the NAMED_CONF_LOCAL_FILE variable here
NAMED_CONF_LOCAL_FILE = '/etc/bind/named.conf.local'

@app.route('/', methods=['GET', 'POST'])
def index():
    zones = list_zones()
    data = request.form
    zone_name = request.args.get('zone_name')
    serial = 20231001  # Replace with your desired serial number

    if zone_name is not None and request.method == 'GET':
        create_zone_if_not_exists(zone_name, serial)

        content = read_zone(zone_name)
        return render_template('manage_dns.html', zones=zones, zone_name=zone_name, zone_content=content)

    if request.method == 'POST':
        record_type = data.get('record_type')
        record_name = data.get('record_name')
        record_value = data.get('record_value')
        zone_name = data.get('zone_name')

        if record_name is not None and record_type is not None and record_value is not None and zone_name is not None:
            create_zone_if_not_exists(zone_name, serial)

            new_record = f"{record_name} IN {record_type} {record_value}"
            update_zone(zone_name, f"\n{new_record}", serial)

            named_conf_content = ""
            with open(NAMED_CONF_LOCAL_FILE, 'r') as named_conf:
                named_conf_content = named_conf.read()

            if f'zone "{zone_name}" IN' not in named_conf_content:
                with open(NAMED_CONF_LOCAL_FILE, 'a') as named_conf:
                    named_conf.write(f'zone "{zone_name}" IN {{\n')
                    named_conf.write('\ttype master;\n')
                    named_conf.write(f'\tfile "/etc/bind/{zone_name}.zone";\n')
                    named_conf.write('};\n')

            # Reload the BIND9 service after making changes
            subprocess.run(['systemctl', 'reload', 'bind9'])

            return redirect(url_for('index'))

    return render_template('manage_dns.html', zones=zones, zone_name=zone_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)