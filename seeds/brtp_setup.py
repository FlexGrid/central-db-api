import pandas
from rest_client import RestClient
import json
import datetime
import sys
import re

dt = datetime.datetime(2021, 11, 11, 0, 0)

nshift_per_user_data = pandas.read_excel("./BRTP Input.xlsx",
                                         sheet_name='Shiftable Devices',
                                         header=0,
                                         index_col=0,
                                         engine='openpyxl')

nshift_cons_data = pandas.read_excel(
    "./BRTP Input.xlsx",
    sheet_name='Shiftable Consumption',
    header=0,
    index_col=[0, 1],
    # skiprows=1,
    #  nrows=np.sum(nshift_per_user),
    usecols='A:Z',
    engine='openpyxl')

sheetname_sufix = {
    'Low': 'LF',
    'Medium': 'MF',
    'High': 'HF',
}

nevs_per_user_data = pandas.read_excel("./BRTP Input.xlsx",
                                       sheet_name='EVs',
                                       header=0,
                                       index_col=0,
                                       usecols='A:C',
                                       engine='openpyxl')

nevs_cons_data = pandas.read_excel("./BRTP Input.xlsx",
                                   sheet_name='EV Consumption',
                                   header=0,
                                   index_col=[0, 1],
                                   engine='openpyxl')

desired_x_data = pandas.read_excel("./BRTP Input.xlsx",
                                   sheet_name='Desired Consumption',
                                   header=0,
                                   index_col=0,
                                   engine='openpyxl')

baseload_data = pandas.read_excel("./BRTP Input.xlsx",
                                  sheet_name='BaseLoad',
                                  header=0,
                                  index_col=0,
                                  engine='openpyxl')

dr_prosumer_schema = []
curtailable_load_schema = []
load_entry_schema = []
flex_request_schema = []
flex_request_data_point_schema = []
flex_id = 1
for flexibility_level in ['Low', 'Medium', 'High']:
    deadlines_shifts_data = pandas.read_excel(
        "./BRTP Input.xlsx",
        sheet_name=f'Shiftable Deadlines {sheetname_sufix[flexibility_level]}',
        header=0,
        index_col=0,
        # skiprows=1,
        #  nrows=np.sum(nshift_per_user),
        # usecols='A:Z',
        engine='openpyxl')

    delta_shifts_data = pandas.read_excel(
        "./BRTP Input.xlsx",
        sheet_name=f'Shiftable Price {sheetname_sufix[flexibility_level]}',
        header=0,
        index_col=0,
        engine='openpyxl')

    deadlines_evs_data = pandas.read_excel(
        "./BRTP Input.xlsx",
        sheet_name=f'EVs Deadlines {sheetname_sufix[flexibility_level]}',
        header=0,
        index_col=0,
        engine='openpyxl')
    delta_evs_data = pandas.read_excel(
        "./BRTP Input.xlsx",
        sheet_name=f'EVs Price {sheetname_sufix[flexibility_level]}',
        header=0,
        index_col=0,
        engine='openpyxl')

    curtailable_bids_data = pandas.read_excel(
        "./BRTP Input.xlsx",
        sheet_name=f'Curtailable Offers {sheetname_sufix[flexibility_level]}',
        header=[0, 1],
        index_col=[0, 1],
        engine='openpyxl')

    flex_request_data = pandas.read_excel(
        "./BRTP Input.xlsx",
        sheet_name=f'Flex Request {flexibility_level}',
        header=[0, 1],
        index_col=0,
        engine='openpyxl')

    for user_id, rowvalue in nshift_per_user_data.iterrows():
        prosumer = {
            "name": f"user_{user_id}_{flexibility_level}",
            "flexibility_level": flexibility_level,
            'shiftable_devices': [],
            'EVs': []
        }

        for t in range(
                1,
                int(desired_x_data.count(axis='columns')[f"user={user_id}"]) +
                1):
            load_enrty = {
                'timestamp':
                (dt + datetime.timedelta(hours=t -
                                         1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'desired_consumption_kw':
                float(desired_x_data[f"t={t}"][f"user={user_id}"]),
                'base_load_kw':
                float(baseload_data[f"t={t}"][f"user={user_id}"]),
                'flexibility': [],
                'prosumer_id':
                prosumer['name'],
            }

            user = None
            for (u, step), rv in curtailable_bids_data.iterrows():
                if (int(u) > 0):
                    user = u
                if user == user_id:
                    price_euro_per_kw = float(rv[(f"t={t}", "Price")])
                    quantity_kw = float(rv[(f"t={t}", "Quantity")])
                    # if (price_euro_per_kw > 0 or quantity_kw > 0):
                    load_enrty['flexibility'] += [{
                        'price_euro_per_kw': price_euro_per_kw,
                        'quantity_kw': quantity_kw,
                    }]
            # prosumer['curtailable_load'] += [load_enrty]
            curtailable_load_schema += [load_enrty]

        for device_id in range(1, int(rowvalue['Number Of Devices']) + 1):
            device = {'name': f'device_{device_id}'}
            for t in range(
                    1,
                    int(
                        nshift_cons_data.count(
                            axis='columns')[(f"user={user_id}", device_id)]) +
                    1):
                kw = float(nshift_cons_data[f"t={t}"][(f"user={user_id}",
                                                       device_id)])
                if kw > 0:
                    load_entry = {
                        'timestamp': (dt + datetime.timedelta(hours=t - 1)
                                      ).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'kw':
                        kw,
                        'price_euro_per_kw':
                        delta_shifts_data[f"User {user_id}"]
                        [f"Device {device_id}"],
                        'deadline':
                        (dt +
                         datetime.timedelta(hours=float(deadlines_shifts_data[
                             f"User {user_id}"][f"Device {device_id}"]) -
                                            1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "prosumer_id":
                        prosumer["name"],
                        "obj_name":
                        device['name'],
                        "type":
                        "shiftable_devices",
                        "offset":
                        device_id - 1,
                    }
                    load_entry_schema += [load_entry]
            prosumer['shiftable_devices'] += [device]

        for ev_id in range(1, int(nevs_per_user_data['EVs'][user_id]) + 1):
            ev = {
                'name': f'ev_{ev_id}',
                'charge_limit':
                float(nevs_per_user_data['Charge Limit'][user_id]),
            }

            for t in range(
                    1,
                    int(
                        nevs_cons_data.count(
                            axis='columns')[(f"user={user_id}", ev_id)]) + 1):
                kw = float(nevs_cons_data[f"t={t}"][(f"user={user_id}",
                                                     ev_id)])
                if kw > 0:
                    load_entry = {
                        'timestamp': (dt + datetime.timedelta(hours=t - 1)
                                      ).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'kw':
                        kw,
                        'deadline': (dt + datetime.timedelta(
                            hours=float(deadlines_evs_data[f"User {user_id}"]
                                        [f"Device {ev_id}"]) -
                            1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'price_euro_per_kw':
                        delta_evs_data[f"User {user_id}"][f"Device {ev_id}"],
                        "prosumer_id":
                        prosumer["name"],
                        "obj_name":
                        ev['name'],
                        "type":
                        "EVs",
                        "offset":
                        ev_id - 1,
                    }
                    load_entry_schema += [load_entry]

            prosumer['EVs'] += [ev]
        dr_prosumer_schema += [prosumer]

    flex_request_name = f"flex_request_{flex_id}_{flexibility_level}"
    flex_request_schema += [{
        'name': flex_request_name,
        "flexibility_level": flexibility_level,
    }]

    for t in range(1, int(rv.count() / 2 + 1)):

        entries = []
        for step, rv in flex_request_data.iterrows():

            # print(step, float(rv[f"t={t}"]["Price"]))
            entries += [{
                'price_euro_per_kw': float(rv[f"t={t}"]["Price"]),
                'quantity_kw': float(rv[f"t={t}"]["Quantity"]),
            }]

        flex_request_data_point_schema += [{
            'flex_request_id':
            flex_request_name,
            'timestamp':
            (dt +
             datetime.timedelta(hours=t - 1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'flexibility':
            entries,
        }]

    # print(json.dumps(flex_request_data_point_schema, indent=4, sort_keys=True))
    # sys.exit()

print(dr_prosumer_schema)
print(json.dumps(dr_prosumer_schema, indent=4, sort_keys=True))

# sys.exit(1)

rest_client = RestClient()
result = rest_client.get_collection("dr_prosumers")
print(json.dumps(result, indent=4, sort_keys=True))
print(f"Total: {len(result)}")

rest_client.delete_collection("curtailable_loads")
rest_client.delete_collection("load_entries")

rest_client.delete_collection("dr_prosumers")

rest_client.delete_collection("flex_requests")
rest_client.delete_collection("flex_request_data_points")

ids = rest_client.post_collection("dr_prosumers", dr_prosumer_schema)

print(f"The ids are {ids}")

cache = {
    prosumer["name"]: ids[idx]
    for idx, prosumer in enumerate(dr_prosumer_schema)
}

print(f"The cache is {cache}")

for idx, item in enumerate(curtailable_load_schema):
    # print(item)
    item["prosumer_id"] = cache[item["prosumer_id"]]

for idx, item in enumerate(load_entry_schema):
    # print(item)
    item["prosumer_id"] = cache[item["prosumer_id"]]

rest_client.post_collection("curtailable_loads", curtailable_load_schema)

rest_client.post_collection("load_entries", load_entry_schema)

ids = rest_client.post_collection("flex_requests", flex_request_schema)

cache = {
    flex_request["name"]: ids[idx]
    for idx, flex_request in enumerate(flex_request_schema)
}

for idx, item in enumerate(flex_request_data_point_schema):
    # print(item)
    item["flex_request_id"] = cache[item["flex_request_id"]]

rest_client.post_collection("flex_request_data_points",
                            flex_request_data_point_schema)
