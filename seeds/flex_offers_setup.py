import pandas
from rest_client import RestClient
import json
import datetime
import sys
import re


flex_request_schema = []
flex_request_data_point_schema = []

rest_client = RestClient()

flex_requests = rest_client.get_collection(
    'flex_requests/?where={"name":  {"$regex": "flex_request_1_High"}}')


print(flex_requests)


flex_data = pandas.read_excel("./20211111_20211111_ISPEnergyOffers_01.xlsx",
                              sheet_name='Sheet1',
                              header=0,
                              #  index_col=0,
                              usecols='A:E',
                              engine='openpyxl')


locations = json.loads("""
                       [
                            [
                                38.249318,
                                22.093737,
                                "Aigio"
                            ],
                            [
                                37.980685,
                                23.705723,
                                "Athens"
                            ],
                            [
                                39.157425,
                                20.995194,
                                "Arta"
                            ],
                            [
                                37.941112,
                                23.732509,
                                "Agios Dimitrios"
                            ],
                            [
                                38.250061,
                                22.084725,
                                "Aigio"
                            ],
                            [
                                37.991376,
                                23.749418,
                                "Athens"
                            ],
                            [
                                40.601069,
                                22.952442,
                                "Thessaloniki"
                            ],
                            [
                                39.3734,
                                21.917096,
                                "Karditsa"
                            ],
                            [
                                38.62874,
                                21.405525,
                                "Agrinio"
                            ],
                            [
                                37.989329,
                                23.690366,
                                "Egaleo"
                            ],
                            [
                                38.024273,
                                23.778155,
                                "Filothei"
                            ],
                            [
                                40.970033,
                                22.055022,
                                "Aridaia"
                            ],
                            [
                                38.016637,
                                23.696304,
                                "Peristeri"
                            ],
                            [
                                40.619317,
                                22.961798,
                                "Thessaloniki"
                            ],
                            [
                                38.623446,
                                21.416512,
                                "Agrinio"
                            ],
                            [
                                37.1988532,
                                23.714993,
                                "Athens"
                            ],
                            [
                                37.988677,
                                23.676552,
                                "Egaleo"
                            ],
                            [
                                37.98049,
                                23.730278,
                                "Athens"
                            ],
                            [
                                37.985562,
                                23.725986,
                                "Athens"
                            ],
                            [
                                38.023597,
                                23.78691,
                                "Filothei"
                            ],
                            [
                                37.994219,
                                23.729677,
                                "Athens"
                            ],
                            [
                                38.021162,
                                23.77395,
                                "Filothei"
                            ],
                            [
                                38.000291,
                                23.673114,
                                "Egaleo"
                            ],
                            [
                                40.974697,
                                22.064463,
                                "Aridaia"
                            ],
                            [
                                40.48803,
                                23.601435,
                                "Arnaia"
                            ],
                            [
                                40.600294,
                                22.962571,
                                "Thessaloniki"
                            ],
                            [
                                38.623243,
                                21.411362,
                                "Agrinio"
                            ],
                            [
                                38.253158,
                                22.08833,
                                "Aigio"
                            ],
                            [
                                38.401571,
                                24.044359,
                                "Aliveri"
                            ],
                            [
                                40.608916,
                                22.979978,
                                "Thessaloniki"
                            ],
                            [
                                38.006118,
                                23.737996,
                                "Athens"
                            ],
                            [
                                40.514795,
                                21.688447,
                                "Ptolemaida"
                            ],
                            [
                                40.298002,
                                21.79572,
                                "Kozani"
                            ],
                            [
                                40.610585,
                                22.9527,
                                "Thessaloniki"
                            ],
                            [
                                38.260198,
                                21.747322,
                                "Patras"
                            ],
                            [
                                38.249988,
                                22.085326,
                                "Aigio"
                            ],
                            [
                                40.592139,
                                22.96875,
                                "Thessaloniki"
                            ],
                            [
                                40.610067,
                                22.960511,
                                "Thessaloniki"
                            ],
                            [
                                37.99596,
                                23.68616,
                                "Egaleo"
                            ],
                            [
                                37.985556,
                                23.754561,
                                "Athens"
                            ],
                            [
                                40.300229,
                                21.782159,
                                "Kozani"
                            ],
                            [
                                40.291358,
                                21.788554,
                                "Kozani"
                            ],
                            [
                                37.995152,
                                23.670453,
                                "Egaleo"
                            ],
                            [
                                38.252489,
                                22.076228,
                                "Aigio"
                            ],
                            [
                                39.358868,
                                21.924478,
                                "Karditsa"
                            ]
                        ]   
                       """)


flex_offers = {}

timestamp = ""
flex_offer_id = 0
price = 0

for row in flex_data.itertuples(index=True):
    if timestamp != row.ID_PERIOD:
        timestamp = row.ID_PERIOD
        flex_offer_id = 0

    price = round(row.PRICE / 1000, 5)

    if not flex_offer_id in flex_offers:
        print("id is ", flex_offer_id)
        flex_offers[flex_offer_id] = {
            'id': flex_offer_id,
            'name': f'flex_offer_{flex_offer_id}',
            'country': 'Greece',
            'location': {
                'name': locations[flex_offer_id][2],
                'x':  locations[flex_offer_id][0],
                'y':  locations[flex_offer_id][1],
            },
            'time_granurality_sec': 1800,
            'fo_data_points': {}
        }

    if not timestamp in flex_offers[flex_offer_id]['fo_data_points']:
        flex_offers[flex_offer_id]['fo_data_points'][timestamp] = {}

    if price in flex_offers[flex_offer_id]['fo_data_points'][timestamp]:
        flex_offer_id = len(flex_offers)
        flex_offers[flex_offer_id] = {
            'id': flex_offer_id,
            'name': f'flex_offer_{flex_offer_id}',
            'country': 'Greece',
            'location': {
                'name': locations[flex_offer_id][2],
                'x':  locations[flex_offer_id][0],
                'y':  locations[flex_offer_id][1],
            },
            'time_granurality_sec': 1800,
            'fo_data_points': {
                timestamp: {
                }
            }
        }

    if price == 0 and row.QUANTITY_MW == 0:
        continue

    flex_offers[flex_offer_id]['fo_data_points'][timestamp][price] = {
        'direction': row.DIR,
        'quantity_kw': 1000 * row.QUANTITY_MW,
        'minquantity': 1000 * row.MINQUANTITY
    }

    flex_offer_id = (flex_offer_id + 1) % len(flex_offers)
    print(row.ID_PERIOD, row.PRICE)

print(flex_offers)

# print(json.dumps(flex_offers, indent=4, sort_keys=True))

fo_obj = [{**flex_offer}
          for flex_offer_id, flex_offer in flex_offers.items()]

for o in fo_obj:
    del o['fo_data_points']
    del o['id']

fo_db_obj = [{'flex_offer_id': flex_offer['name'],
              'timestamp': f"{timestamp.isoformat()}Z",
              'flexibility': [
                  {
                      'price_euro_per_kw': price,
                      **values
                  } for price, values in data_points.items()
]} for flex_offer_id, flex_offer in flex_offers.items() for timestamp, data_points in flex_offer['fo_data_points'].items()
]
print(json.dumps(fo_obj, indent=4, sort_keys=True))

# sys.exit()
rest_client.delete_collection("flex_offers")
rest_client.delete_collection("flex_offer_data_points")

ids = rest_client.post_collection("flex_offers", fo_obj)
print(len(fo_obj), len(ids))
cache = {
    flex_offer["name"]: ids[idx]
    for idx, flex_offer in enumerate(fo_obj)
}
print(cache)

for idx, item in enumerate(fo_db_obj):
    # print(item)
    item["flex_offer_id"] = cache[item["flex_offer_id"]]


print(json.dumps(fo_db_obj, indent=4, sort_keys=True))


rest_client.post_collection("flex_offer_data_points",
                            fo_db_obj)
