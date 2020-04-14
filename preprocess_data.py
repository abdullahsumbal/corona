import pandas
import json
from datetime import datetime, timedelta

df = pandas.read_csv('https://health-infobase.canada.ca/src/data/covidLive/covid19.csv')
pre_processed_data = {}

ID = 'id'
PRNAME = 'prname'
NUM_CONFIRMED = 'numconf'
NUM_DEATH = 'numdeaths'
DATE = 'date'
CANADA = 'Canada'

province_mapping = {
    'Quebec': 'CA-QC',
    'Ontario': 'CA-ON',
    'Alberta': 'CA-AB',
    'British Columbia': 'CA-BC',
    'Newfoundland and Labrador': 'CA-NL',
    'Saskatchewan': 'CA-SK',
    'Manitoba': 'CA-MB',
    'New Brunswick': 'CA-NB',
    'Nova Scotia': 'CA-NS',
    'Prince Edward Island': 'CA-PE',
    'Yukon': 'CA-YT',
    'Northwest Territories': 'CA-NT',
    'Nunavut': 'CA-NU'
}

def get_total(name):
    prname = df[PRNAME] == name
    return {
        NUM_CONFIRMED :int((df[prname][NUM_CONFIRMED].iat[-1])),
        NUM_DEATH: int((df[prname][NUM_DEATH].iat[-1])),
        DATE: (df[prname][DATE].iat[-1])
        }

def get_total_days(name, include_date = True):
    timeline_data = []
    prname = df[PRNAME] == name
    for _, row in df[prname].iterrows():
        day_data = {
            NUM_CONFIRMED: row[NUM_CONFIRMED],
            NUM_DEATH: row[NUM_DEATH]
            }
        if include_date:
            day_data[DATE] = row[DATE]
        timeline_data.append(day_data)
    return timeline_data

def get_canada_total():
    return get_total(CANADA)

def get_province_total():
    canada_data = []
    for prname, am_prname in province_mapping.items():
        pr_total_data = get_total(prname)
        pr_total_data[ID] = am_prname
        canada_data.append(pr_total_data)
    return canada_data

def get_canada_total_timeline():
    start_date_str = '01-03-2020'
    end_date_str = '10-04-2020'#df[DATE].max()
    current_date = datetime.strptime(start_date_str, "%d-%m-%Y")
    start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
    end_date = datetime.now()
    canada_total_timeline_data = []
    while(end_date >= current_date):
        current_date_str = current_date.strftime('%d-%m-%Y')
        prname = df[PRNAME] == CANADA
        num_confirmed = df[prname & (df[DATE] == current_date_str)][NUM_CONFIRMED] 
        num_deaths = df[prname & (df[DATE] == current_date_str)][NUM_DEATH]
        # data does not exist
        if num_confirmed.empty:
            # take the previous data
            if current_date > start_date:
                num_confirmed = canada_total_timeline_data[-1]["confirmed"]
            else:
                num_confirmed = 0
        else:
            num_confirmed = int(num_confirmed) 

        # data does not exist
        if num_deaths.empty:
            # take the previous data
            if current_date > start_date:
                num_deaths = canada_total_timeline_data[-1]["deaths"]
            else:
                num_deaths = 0
        else:
            num_deaths = int(num_deaths)

        canada_total_timeline_data.append({"confirmed": num_confirmed, "deaths": num_deaths, "recovered": 0 ,DATE: current_date.strftime('%Y-%m-%d')} )
        # increment by a day
        current_date += timedelta(days=1)

    return canada_total_timeline_data

def get_province_total_timeline():
    start_date_str = '01-03-2020'
    end_date_str = '10-04-2020'#df[DATE].max()
    current_date = datetime.strptime(start_date_str, "%d-%m-%Y")
    start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
    end_date = datetime.now()
    provinces_total_timeline_data = []
    while(end_date >= current_date):
        current_date_str = current_date.strftime('%d-%m-%Y')
        day_data = {DATE: current_date.strftime('%Y-%m-%d')}
        provinces_data = []


        for prname, am_prname in province_mapping.items():
            prname_data = df[PRNAME] == prname
            num_confirmed = df[prname_data & (df[DATE] == current_date_str)][NUM_CONFIRMED] 
            num_deaths = df[prname_data & (df[DATE] == current_date_str)][NUM_DEATH] 
            # data does not exist
            if num_confirmed.empty:
                # take the previous data
                if current_date > start_date:
                    for pr_data in  provinces_total_timeline_data[-1]['list']:
                        # print(provinces_total_timeline_data)
                        if pr_data[ID] == am_prname:
                            num_confirmed = pr_data["confirmed"]
                            break 
                else:
                    num_confirmed = 0
            else:
                num_confirmed = int(num_confirmed)

            # data does not exist
            if num_deaths.empty:
                # take the previous data
                if current_date > start_date:
                    for pr_data in  provinces_total_timeline_data[-1]['list']:
                        if pr_data[ID] == am_prname:
                            num_deaths = pr_data["deaths"]
                            break 
                else:
                    num_deaths = 0
            else:
                num_deaths = int(num_deaths)

            provinces_data.append({"confirmed": num_confirmed, "deaths": num_deaths, "recovered": 0, ID: am_prname})
            
        day_data['list'] = provinces_data
        provinces_total_timeline_data.append(day_data)

        # increment by a day
        current_date += timedelta(days=1)

    return provinces_total_timeline_data


with open('data/js/canada_total.js', 'w') as outfile:
    json_string_data = "var canada_total = " +json.dumps(get_canada_total())
    outfile.write(json_string_data)


with open('data/js/province_total.js', 'w') as outfile:
    json_string_data = "var province_total = " +json.dumps(get_province_total())
    outfile.write(json_string_data)


with open('data/js/canada_total_timeline.js', 'w') as outfile:
    json_string_data = "var canada_total_timeline = " +json.dumps(get_canada_total_timeline())
    outfile.write(json_string_data)


with open('data/js/provinces_total_timeline.js', 'w') as outfile:
    json_string_data = "var provinces_total_timeline = " +json.dumps(get_province_total_timeline())
    outfile.write(json_string_data)
