## NYC PVP IV Pokemon Map

Instructions:
1. Clone this repo
2. Make sure <code>requests, geopy</code> are installed, run the following command if needed
```
pip install -r requirements.txt
```
3. Run the following command:
```
python main.py <spawn_mon_id> <pvp_mon_id> {min_rank} {cp_cap}
```
Default value for min_rank is 100, for cp_cap is 1500. 
4. Examples:
```commandline
python main.py 747 748
python main.py 747 748 100
python main.py 747 748 100 2500
```
