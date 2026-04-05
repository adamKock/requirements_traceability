import pandas as pd 
def map_test_cases(file_obj):
    df = pd.read_csv(file_obj)
    print(df.columns)
    columns_list = df.columns

    Test_Case_Mapping = {
        "id": ["id", "ID", "iD", "Id", "testcaseid"],
    }
    reverse_map = {
    variant: key
        for key, variants in Test_Case_Mapping.items() 
        for variant in variants}
        
    new_columns_list = [
        reverse_map.get(col, col) 
        for col in columns_list]
        
    #What do we want to do here, we want to iterate through columns (df.cols)
    #Then update those df.cols so they match the new column list 
    for i, col in enumerate(columns_list):
        df.columns[i] = new_columns_list[i]
        
        
    return file_obj


call = map_test_cases("testcasesnew.csv")