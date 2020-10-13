#!/usr/bin/python
#
# tuya_device_updater
#

import pytuya
import json
import os

# Main configuration from config.json file:
config = None

def read_conf_file():
    file_path = "config.json"
    if os.path.exists(file_path):
        print ("   updating config with file: %s" % (file_path))
        with open(file_path) as json_data:
            try:
                data_string = json.load(json_data)
                for key, value in data_string.items():
                    config.setdefault(key, []).append(value)
            except ValueError as e:
                print( "Error reading the file %s: %s"%(file_name,e))
    else:
        error_msg = "Config file %s does not exists"%(file_path)
        raise OSError(error_msg)

def device_info( deviceid, ip, key, vers ):
    watchdog = 0
    data_out = None
    while True:
        try:
            d = pytuya.OutletDevice(deviceid, ip, key)
            if vers == '3.3':
                d.set_version(3.3)

            data = d.status()
            if(d):
                print('Dictionary %r' % data)
                print('Switch On: %r' % data['dps']['1'])

                if vers == '3.3':
                    if '19' in data['dps'].keys():
                        w = (float(data['dps']['19'])/10.0)
                        data_out["w"] = w
                        mA = float(data['dps']['18'])
                        data_out["mA"] = mA
                        V = (float(data['dps']['20'])/10.0)
                        data_out["V"] = V
                        day = (w/1000.0)*24
                        week = 7.0 * day
                        month = (week * 52.0)/12.0
                        print('Power (W): %f' % w)
                        print('Current (mA): %f' % mA)
                        print('Voltage (V): %f' % V)
                        print('Projected usage (kWh):  Day: %f  Week: %f  Month: %f' % (day, week, month))
                        # return(float(data['dps']['19'])/10.0)
                        return(data_out)
                    else:
                        return(0.0)
                else:
                    if '5' in data['dps'].keys():
                        w = (float(data['dps']['5'])/10.0)
                        data_out["w"] = w
                        mA = float(data['dps']['4'])
                        data_out["mA"] = mA
                        V = (float(data['dps']['6'])/10.0)
                        data_out["V"] = V
                        day = (w/1000.0)*24
                        week = 7.0 * day
                        month = (week * 52.0)/12.0
                        print('Power (W): %f' % w)
                        print('Current (mA): %f' % mA)
                        print('Voltage (V): %f' % V)
                        print('Projected usage (kWh):  Day: %f  Week: %f  Month: %f' % (day, week, month))
                        # return(float(data['dps']['5'])/10.0)
                        return(data_out)
                    else:
                        return(0.0)
            else:
                return(0.0)
            break
        except KeyboardInterrupt:
            pass
        except OSError as o:
            watchdog+=1
            if(watchdog>config['retries']):
                print("OSERROR: No response from plug %s [%s] %s." % (deviceid,ip, o.strerror))
                return(0.0)
            sleep(2)


def update_db(db_data, device_name, data):
    """Instantiate a connection to the InfluxDB."""
    client = InfluxDBClient(db_data["db_host"], db_data["db_port"], db_data["db_user"], db_data["db_password"], db_data["db_dbname"])

    current_time = current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # json_body = [
    #     {
    #         "measurement": "teckin_sp22_1",
    #         "tags": {
    #         },
    #         "time": current_time,
    #         "fields": {
    #             "w": data,
    #             "ma": data,
    #             "v": data,
    #             ...
    #         }
    #     }
    # ]

    # json_body = [
    #     {
    #         "measurement": device_name,
    #         "tags": {},
    #         "time": current_time,
    #         "fields": {
    #             data_name: data
    #         }
    #     }
    # ]

    json_body = [
        {
            "measurement": device_name,
            "tags": {},
            "time": current_time,
            "fields": data
        }
    ]

    print("Write points: {0}".format(json_body))
    # client.write_points(json_body)



def poll_devices():
    for device in config['devices'][0]:
        print("Polling Device %s at %s with protocol version %s" % (device['name'],device['ip'],device['ver']))
        device_data = device_info(device['name'],device['ip'],device['key'],device['ver'])

        if device_data != 0.0:
            update_db(config['db'], device['name'], device_data)


read_conf_file()
# print(config)
# print(config["db"])
poll_devices()
