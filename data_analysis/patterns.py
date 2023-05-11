# Extraction of level 2 patterns.
# The TPM algorithm results in a json file with patterns, we extract the level 2 patterns 
# from that file and transform them into Pattern objects so they are easier to work with

import pandas as pd
import re
from datetime import datetime

# Class for pattern objects. We make objects so they are easier to work with.
class Level2Pattern:
    def __init__(self, first_appliance, second_appliance, relation, support, confidence):
        self.first_appliance = first_appliance
        self.second_appliance = second_appliance
        self.relation = relation
        self.support = support
        self.confidence = confidence
    
    def print(self):
        print(f'{self.first_appliance} {self.relation} {self.second_appliance}, support: {self.support}, confidence: {self.confidence}')


def pattern_extraction(json_file_path: str):
    # Read JSON file and convert to pandas dataframe
    extracted_data = pd.read_json(json_file_path)
    
    patterns = list()

    # Iterate through each pattern in the dataframe
    for data in extracted_data['patterns']:
        for pattern in data:
            # Split the information about each pattern 
            appliances_and_relation = re.split('(>|->|\|)', pattern['pattern'])
            first_appliance = appliances_and_relation[0]
            second_appliance = appliances_and_relation[2]
            relation = appliances_and_relation[1]
            support = pattern['supp']
            confidence = pattern['conf']
            
            # Create pattern object
            level_2_pattern = Level2Pattern(first_appliance, second_appliance, relation, support, confidence)
            
            # Append pattern to list of patterns
            patterns.append(level_2_pattern)

    return patterns


class Patterns:
    def __init__(self, date, appliances, relation, start_times):
        self.date = date
        self.appliances = appliances
        self.relation = relation
        self.start_times = start_times
    
    def print(self):
        print(f'{self.date} | {self.appliances} | {self.relation} | {self.start_times}')


def optimization_patterns(json_file_path: str):
    extracted_data = pd.read_json(json_file_path)
    print(extracted_data)

    patterns = list()

    for data in extracted_data['patterns']:
        for pattern in data:
            appliances_and_relation = re.split('(>|->|\|)', pattern['pattern'])
            appliances = (appliances_and_relation[0], appliances_and_relation[2])
            relation = appliances_and_relation[1]
            for key in pattern['time']:
                for occurence in pattern['time'][key]:
                    date = datetime.strptime(occurence[0][0], '%Y-%m-%d %H:%M:%S').strftime('%m-%d')
                    start_times = (datetime.strptime(occurence[0][0], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S'), 
                                   datetime.strptime(occurence[1][0], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S'))
                    
                    patterns.append(Patterns(date, appliances, relation, start_times))
    
    patterns.sort(key=lambda pattern: pattern.date)

    return patterns

def main():
    patterns = optimization_patterns('./TPM/TPM/output/Experiment_minsup0.15_minconf_0.6/level2.json')
    for p in patterns:
        p.print()

    '''
    for pattern in patterns:
        pattern.print()
    '''

main()