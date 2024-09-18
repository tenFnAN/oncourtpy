# OnCourt

[OnCourt](https://www.oncourt.info/) Tennis Database Helper Functions

Before using these functions, ensure that you have installed the OnCourt database and obtained the necessary database password for connection.

## Installation  
- pip install git+https://github.com/tenFnAN/oncourtpy

## Usage
```
import oncourtpy.oncourt as onc
tns_wta = onc.OncourtDb( 'wta', 'single')
today_schedule = tns_wta.query_oncourt_schedule_today()
player_df = tns_wta.query_oncourt_playerdata(players_id= today_schedule[['id_P1', 'id_P2']].melt()['value'].unique() )

tns_atp = onc.OncourtDb( 'atp', 'double') 
today_single_pre_atp = tns_atp.query_oncourt_schedule_today()
```

I would like to invite to my [Twitter](https://x.com/tennisMiner) , where I share daily doses of tennis statistics.
