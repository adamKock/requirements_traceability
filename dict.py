import pandas as pd 
columns_list = ["testcaseid", "step", "action"]


Test_Case_Mapping = {
        "id": ["id", "ID", "iD", "Id", "testcaseid"]
        }


rev_map = {
    "id":"id",
    "ID":"id",
    "iD":"id",
    "Id":"id",
    "testcaseid":"id"
}

reverse_map = {
    variant: key
    for key, variants in Test_Case_Mapping.items() 
    for variant in variants}

# replace in original list
new_columns_list = [
    reverse_map.get(col, col) 
    for col in columns_list
]


#Then we need to assign the new columns back to the old column file 

for i,col in enumerate(columns_list):
    columns_list[i] = new_columns_list[i]

def map_test_cases(file_obj):
    df = pd.read_csv(file_obj)
    df.dropna(how='all', axis=1, inplace=True)
    columns_list = df.columns.tolist()
    Test_Case_Mapping = {
        "id": ["id", "ID", "iD", "Id", "testcaseid"],
        "Work Item Type":[ "workitemtype"],
        "Test Step":["teststep", "teststeps","step"],
         "Step Action":["stepaction", "stepactions","steps"],
    }
    reverse_map = {
    variant: key
        for key, variants in Test_Case_Mapping.items() 
        for variant in variants}
        
    new_columns_list = [
        reverse_map.get(col, col) 
        for col in columns_list]
        
    df.columns = new_columns_list 
        
        
    return df


call = map_test_cases("testcasesnew.csv")


print(call.head())
