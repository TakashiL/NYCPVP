import sys
import datetime
import requests
import json
import math
from geopy.geocoders import Nominatim

cp_multiplier = [0.09399999678, 0.1351374321, 0.1663978696, 0.1926509132, 0.2157324702, 0.2365726514, 0.2557200491,
                 0.2735303721, 0.2902498841, 0.3060573814, 0.3210875988, 0.335445032, 0.3492126763, 0.3624577366,
                 0.3752355874, 0.3875924077, 0.3995672762, 0.4111935532, 0.4225000143, 0.4329264205, 0.4431075454,
                 0.4530599482, 0.4627983868, 0.4723360853, 0.481684953, 0.4908558072, 0.499858439, 0.508701749,
                 0.5173939466, 0.5259425161, 0.5343543291, 0.5426357538, 0.5507926941, 0.5588305845, 0.5667545199,
                 0.5745691281, 0.5822789073, 0.5898879079, 0.5974000096, 0.6048236487, 0.6121572852, 0.619404108,
                 0.6265671253, 0.6336491787, 0.6406529546, 0.6475809714, 0.6544356346, 0.6612192658, 0.6679340005,
                 0.6745818856, 0.6811649203, 0.6876849013, 0.6941436529, 0.700542901, 0.7068842053, 0.7131690749,
                 0.7193990946, 0.7255755869, 0.7317000031, 0.7347410386, 0.7377694845, 0.7407855797, 0.7437894344,
                 0.7467811972, 0.749761045, 0.7527290997, 0.7556855083, 0.7586303702, 0.7615638375, 0.7644860496,
                 0.7673971653, 0.7702972937, 0.7731865048, 0.7760649471, 0.7789327502, 0.7817900508, 0.7846369743,
                 0.7874736085, 0.7903000116, 0.792803968, 0.7953000069, 0.7978038984, 0.8003000021, 0.8028038719,
                 0.8052999973, 0.8078038508, 0.8102999926, 0.8128038352, 0.8152999878, 0.8178038066, 0.820299983,
                 0.8228037786, 0.8252999783, 0.8278037509, 0.8302999735, 0.8328037534, 0.8353000283, 0.8378037559,
                 0.8403000236, 0.842803729, 0.8453000188, 0.8478037024, 0.850300014, 0.852803676, 0.8553000093,
                 0.8578036499, 0.8603000045, 0.862803624, 0.8652999997]

cp_multiplier_power_2 = [x ** 2 for x in cp_multiplier]
cp_multiplier_power_4 = [x ** 4 for x in cp_multiplier]


def get_pokemon_base_dict():
    f = open("pokemon_base_data.json")
    pokemon_base_data = json.load(f)
    f.close()

    pokemon_base_dict = {}
    for item in pokemon_base_data:
        pokemon_base_dict[item["id"]] = item
    return pokemon_base_dict


def get_current_spawns(mon_id, min_iv, time, since=0):
    api = f"https://nycpokemap.com/query2.php?mons={mon_id}&minIV={min_iv}&time={time}&since={since}"
    response = requests.get(api, headers={"referer": "https://nycpokemap.com/"})
    if response.status_code == 200:
        print("Successfully fetched the current spawn data")
        return response.json()['pokemons']
    else:
        print(f"There's a {response.status_code} error with your request")


def get_cp(at, df, st, multiple2):
    return math.floor((at * math.sqrt(df * st) * multiple2) / 10)


def get_level_cap(at, df, st, target_cp, cpm4, max_lvl):
    max_cpm4 = (target_cp + 1) * (target_cp + 1) * 100 / (at * at * df * st)
    cap = sum(map(lambda x: x <= max_cpm4, cpm4))
    return min(cap, max_lvl) - 1


def get_pvp_iv_whole_rankings(cp_cap, poke, max_lvl):
    iv_combos = []
    for at in range(16):
        for df in range(16):
            for st in range(16):
                iv_combos.append({"at": at, "df": df, "st": st})

    products = []
    for iv_combo in iv_combos:
        at = math.floor(poke['at'] + iv_combo['at'])
        df = math.floor(poke['df'] + iv_combo['df'])
        st = math.floor(poke['st'] + iv_combo['st'])
        level = get_level_cap(at, df, st, cp_cap, cp_multiplier_power_4, max_lvl)
        stat_product = cp_multiplier_power_2[level] * at * df * math.floor(cp_multiplier[level] * st)
        products.append([stat_product, level, iv_combo['at'], iv_combo['df'], iv_combo['st']])
    products = sorted(products, key=lambda x: -x[0])
    ranking_dict = {}
    for i in range(len(products)):
        ranking = i+1
        product = products[i]
        product.insert(0, ranking)
        key = (product[3], product[4], product[5])
        ranking_dict[key] = product
    return ranking_dict


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit("Please provide at least two args: spawn_mon_id and pvp_mon_id")

    spawn_mon_id = int(args[0])
    pvp_mon_id = int(args[1])
    target_rank = int(args[2]) if len(args) > 2 else 100
    cp_cap = int(args[3]) if len(args) > 3 else 1500

    locator = Nominatim(user_agent="NYCPVP")

    pokemon_base_dict = get_pokemon_base_dict()
    pvp_mon = pokemon_base_dict[pvp_mon_id]
    pvp_mon_rankings = get_pvp_iv_whole_rankings(cp_cap, pvp_mon, max_lvl=99)

    now_epoch = datetime.datetime.now().strftime('%s')
    current_spawns = get_current_spawns(spawn_mon_id, 1, now_epoch)

    # base example: {667: { "id": 667, "name": "Litleo", "at": 139, "df": 112, "st": 158}}
    # spawn example: {'pokemon_id': 747, 'lat': 40.71228988, 'lng': -73.95641737, 'despawn': 1664773371, 'disguise': 0, 'attack': 11, 'defence': 6, 'stamina': 10, 'move1': 236, 'move2': 92, 'costume': -1, 'gender': 1, 'shiny': 0, 'form': -1, 'cp': 93, 'level': 4, 'weather': 0}

    print(f"Target rank: {target_rank} | CP Cap: {cp_cap}")

    good_spawns = []
    for spawn in current_spawns:
        stats = pvp_mon_rankings[(spawn['attack'], spawn['defence'], spawn['stamina'])]
        if stats[0] <= target_rank:
            spawn['rankings'] = stats[0]
            spawn['level'] = stats[2]
            good_spawns.append(spawn)

    good_spawns = sorted(good_spawns, key=lambda x: x['rankings'])
    for gs in good_spawns:
        despawn_time = datetime.datetime.fromtimestamp(gs['despawn'])
        left_time = (despawn_time - datetime.datetime.now()).seconds / 60
        coords = f"{gs['lat']},{gs['lng']}"
        address = locator.reverse(coords).address

        print_dict = {'pokemon_id': gs['pokemon_id'],
                      'ranking': gs['rankings'],
                      'coords': coords,
                      'iv': f"{gs['attack']}/{gs['defence']}/{gs['stamina']}",
                      'until': f"{str(despawn_time)} ({round(left_time, 2)} minutes left)",
                      'pvp_level': gs['level']/2 + 1,
                      'address': address,
                      'map': f"https://maps.google.com/maps?q={coords}",
                      }
        print(print_dict)

    if len(good_spawns) == 0:
        print("No qualified spawn found, please try next time!")
