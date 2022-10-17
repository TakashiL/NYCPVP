## NYC PVP IV Pokemon Map

### Instructions:
1. Clone this repo.

2. Make sure <code>requests, geopy</code> are installed, run the following command if needed:
```commandline
pip install -r requirements.txt
```

3. Run the following command to find spawns:
```commandline
python main.py <spawn_mon_id> <pvp_mon_id> {min_rank} {cp_cap}
```
Default values: <code>min_rank=100, cp_cap=1500</code>

4. Examples:
```commandline
python main.py 747 748
python main.py 747 748 100
python main.py 747 748 100 2500
python main.py 37 Ninetales\(Alolan\) # for special pokemon use this
```

---

### Disclaimer:

This project is completely non-profit and can't be done without querying data from https://nycpokemap.com/
