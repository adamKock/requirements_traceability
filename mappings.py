
import pandas as pd





def map_columns(file_obj):
    Requirement_Mapping = {}
    Test_Case_Mapping = {
        "id": ["id", "ID", "iD", "Id", "testcaseid"],
        "ID":["id", "ID", "iD", "Id", "testcaseid"],
        "Work Item Type":[ "workitemtype"],
        "Test Step":["teststep", "teststeps","step"],
        "Step Action":["stepaction", "stepactions","steps"],

        }
    

        #what I need to do is go through all the columns and if I one of those values
        #In the list shows then map that column to the key in the dictionary

    df = pd.read_csv(file_obj)
    df.columns = df.columns.str.strip().str.lower()
    cols = df.columns
    for col in cols: 
        for key in Test_Case_Mapping:
            if key[Test_Case_Mapping] == cols:
                cols = key[Test_Case_Mapping]



        

call = map_columns("testcasesnew.csv") 