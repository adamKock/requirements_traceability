from typing import List,Type
import pandas as pd 
from pydantic import BaseModel
from application.schemas.schema import Requirement, TraceabilityRequest
from application.service.engine import SemanticEngine


class TraceabilityService:
    def __init__(self,engine):
        self.engine = engine
    
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
    
 
    

