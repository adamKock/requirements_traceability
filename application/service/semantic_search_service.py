from typing import List,Type
import pandas as pd 
from pydantic import BaseModel
from application.schemas.schema import Requirement
from io import StringIO



#ID,Work Item Type,Title,Test Step,Step Action,Step Expected,Area Path,Assigned To,State


class TraceabilityService:
    def __init__(self,engine):
        self.engine = engine

    def map_requirements(self, file_obj):
        df= pd.read_csv(file_obj)
        df.dropna(how='all', axis=1, inplace=True)
        req_columns_list = df.columns.tolist()
        requirement_mapping={
            "id": ["id", "ID", "iD", "Id", "requirementid"],
            "name": ["name", "Name", "requirementname", "title", "Title", "summary", "Summary"],
            "description": ["description", "Description", "requirementdescription", "description", "Description"]
        }

        rev_map = {
            variant: key
            for key, variants in requirement_mapping.items()
            for variant in variants
        }
        new_req_columns = [
            rev_map.get(col, col)
            for col in req_columns_list

        ]
        df.columns = new_req_columns
        output = StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output


    
    def map_test_cases(self,file_obj):
        df = pd.read_csv(file_obj)
        df.dropna(how='all', axis=1, inplace=True)
        columns_list = df.columns.tolist()
        Test_Case_Mapping = {
            "id": ["id", "ID", "iD", "Id", "testcaseid"],
            "summary":["Summary", "Title", "title"],
            "stepnumber":["teststep", "teststeps","step", "Test Steps"],
            "stepaction":["stepactions","StepAction"]
        }
        reverse_map = {
        variant: key
            for key, variants in Test_Case_Mapping.items() 
            for variant in variants}
        
        new_columns_list = [
            reverse_map.get(col, col) 
            for col in columns_list]
        
        df.columns = new_columns_list 

        output = StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return output

        
    
    def import_csv(self, csv, model_class:Type[BaseModel]) -> List[BaseModel]:
        df = pd.read_csv(csv)
        df.dropna(how='all', axis=1, inplace=True)

        #Clean Columns 
        df.columns = df.columns.str.strip().str.lower()
        print(df.columns)

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
        
       
    def store_test_cases(self, test_cases, job_id):
        return self.engine.store_test_cases(test_cases, job_id)
    
    def compute_similarity(self, requirements):
        return self.engine.compute_similarity(requirements)
    
    def run_traceability(self, requirements: List[Requirement],job_id):
        # 1. Compute similarity against the DB (via Engine)
        analysis = self.engine.compute_similarity(requirements,job_id)
        print(analysis)
        # 2. Compare
        results = self.engine.compare(
            requirements=requirements,
            similarity=analysis["similarity_matrix"],
            ids=analysis["test_case_ids"],
            job_id=job_id
        )
        return results
    
 
    

