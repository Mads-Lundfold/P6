import pandas as pd
'''
HOUSE 1
[5] Washing Machine : 20
[6] Dishwasher : 10
[7] TV : 10
[9] htpc (home-theatre PC) : 20
[10] Kettle : 2000
[11] Toaster : 1000
[12] Fridge : 50
[13] microwave : 200
[37] kitchen radio : 2
[38] bedreoom chargers : 1
[42] gas oven : 10
else : 5
'''

house1_power_thresholds = {
    'channel_5' : 20,
    'channel_6' : 10,
    'channel_7' : 10,
    'channel_9' : 20,
    'channel_10' : 2000,
    'channel_11' : 1000,
    'channel_12' : 50,
    'channel_13' : 200,
    'channel_37' : 2,
    'channel_38' : 1,
    'channel_42' : 10
}

'''
HOUSE 2
[8] kettle : 2000
[12] washing machine : 20
[13] dish_washer : 10
[14] fridge : 50
[15] microwave : 200
else : 5
'''

house2_power_thresholds = {
    'channel_8' : 2000,
    'channel_12' : 20,
    'channel_13' : 10,
    'channel_14' : 50,
    'channel_15' : 200
}


'''
HOUSE 3
[2] kettle : 2000
else : 5
'''

house1_power_thresholds = {
    'channel_2' : 2000
}

'''
HOUSE 4
[3] kettle_radio : 2000
[5] freezer : 50
[6] washing machine / microwave / breadmaker : 20
else : 5
'''

house1_power_thresholds = {
    'channel_3' : 2000,
    'channel_5' : 50,
    'channel_6' : 20
}

'''
HOUSE 5
[18] kettle : 2000
[19] fridge / freezer : 50
[22] dishwasher : 10
[23] microwave : 200
[24] washer/dryer : 20
else : 5
'''

house1_power_thresholds = {
    'channel_18' : 2000,
    'channel_19' : 50,
    'channel_22' : 10,
    'channel_23' : 200,
    'channel_24' : 20
}