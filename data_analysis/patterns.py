# Extraction of level 2 patterns.
# The TPM algorithm results in a json file with patterns, we extract the level 2 patterns 
# from that file and transform them into Pattern objects so they are easier to work with

import pandas as pd
import re
import csv
from datetime import datetime


# Class for pattern objects. We make objects so they are easier to work with.
class Patterns:
    def __init__(self, date, appliances, relation, start_times):
        self.date = date                         # month and day pattern occur
        self.appliances = appliances             # appliances within pattern
        self.relation = relation                 # relation between appliances (pattern type)
        self.appliance_start_times = start_times # start time of each appliance in pattern
    
    def print(self):
        print(f'{self.date} | {self.appliances} | {self.relation} | {self.appliance_start_times}')


def optimization_patterns(json_file_path: str):
    extracted_data = pd.read_json(json_file_path)

    patterns = list()

    # Holy shit, 5-double for-loop!!
    for data in extracted_data['patterns']:
        for pattern in data:
            appliances_and_relation = re.split('(>|->|\|)', pattern['pattern'])
            appliances = [appliances_and_relation[0], appliances_and_relation[2]]
            relation = appliances_and_relation[1]
            for key in pattern['time']:
                for occurence in pattern['time'][key]:
                    date = datetime.strptime(occurence[0][0], '%Y-%m-%d %H:%M:%S').strftime('%m-%d')
                    start_times = list()
                    for i in range(len(occurence)):
                        start_times.append(datetime.strptime(occurence[i][0], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S'))
                        
                    patterns.append(Patterns(date, appliances, relation, start_times))
    
    # Sort the patterns based on date
    patterns.sort(key=lambda pattern: pattern.date)

    return patterns


def write_patterns_csv(patterns, file_name: str):
    with open('./data/patterns/' + file_name + '.csv', 'w') as f:
        f.write('Date;Appliances;Relation;Appliance start times\n')
        for p in patterns:
            f.write(f'{p.date};{p.appliances};{p.relation};{p.appliance_start_times}\n')
        

def read_patterns_csv(file_path: str):
    patterns = list()

    with open(file_path, 'r') as file:
        csvreader = csv.reader(file, delimiter=';')
        next(csvreader)
        for row in csvreader:
            patterns.append(Patterns(row[0], row[1], row[2], row[3]))

    return patterns


def main():
    patterns = optimization_patterns('./TPM/TPM/output/Experiment_minsup0.15_minconf_0.6/level2.json')
    #write_patterns_csv(patterns, 'house_1_2014_patterns')
    #read_patterns_csv('./data/patterns/house_1_2014_patterns.csv')

#main()