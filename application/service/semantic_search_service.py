#FOr this class I need to take the csvs,
#Create them into a list of req and test cases using the schema
from typing import List,Type
import pandas as pd 
from pydantic import BaseModel
from application.schemas.schema import TraceabilityRequest
from application.service.engine import SemanticEngine


class TraceabilityService:
    def __init__(self):
        self.engine = SemanticEngine()
    
    def import_csv(self, file_obj, model_class:Type[BaseModel]) -> List[BaseModel]:
        #Import CSV
        df = pd.read_csv(file_obj)
        df.dropna(how='all', axis=1, inplace=True)

        #Clean Columns 
        df.columns = df.columns.str.strip().str.lower()

        if "id" in df.columns and "stepaction" in df.columns:
            if "stepnumber" in df.columns:
                df = df.sort_values(["id", "stepnumber"])
            df = (
                df.groupby(["id", "summary"])["stepaction"]
                .apply(list)
                .reset_index(name="steps"))

        csv_columns = set(df.columns)
        expected_columns = set(model_class.model_fields.keys())

        #Check Schema
        missing = expected_columns - csv_columns
        too_many = csv_columns - expected_columns

        if missing:
            print("CSV columns do not match schema")
            raise ValueError(f"CSV columns do not match schema. Missing: {missing}")
        if too_many:
            df.drop(columns=list(too_many), inplace=True) 
        records = df.to_dict(orient="records")
        
        return [model_class(**row) for row in records] 
        
       
    
    def build_payload(self, requirements, test_cases):
        return TraceabilityRequest(
            requirements=requirements,
            test_cases=test_cases
        )
        
    def convert_to_tensor(self, payload):
        return self.engine.convert_to_tensor(payload)
    
    def compare(self, payload, similarity):
        return self.engine.compare(payload, similarity)
    

