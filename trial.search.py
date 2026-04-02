#FOr this class I need to take the csvs,
#Create them into a list of req and test cases using the schema
from typing import List
import pandas as pd 
from pydantic import BaseModel
from application.schemas.schema import Requirement, TestCase, TraceabilityRequest
class traceability_service:
    def __init__(self, semantic_engine):
        self.engine = semantic_engine


    def import_csv(self, path:str) -> List[dict]:
        df = pd.read_csv(path)
        df.dropna(how='all', axis=1, inplace=True)
        return df.to_dict(orient="records")
    
    def process_files(self, req_path:str, test_path:str):
        requirements = self.import_csv(req_path)
        test_cases = self.import_csv(test_path)
             
        req_obj = [Requirement(**req) for req in requirements]
        test_obj = [TestCase(**test) for test in test_cases]

        payload= TraceabilityRequest(
            requirements=req_obj, test_cases=test_obj)
        

        results = self.engine.score(payload)
        



# Create a dummy engine for testing
class MockEngine:
    def score(self, data):
        return f"Processed {len(data.requirements)} requirements!"

# Initialize and run
engine = MockEngine()
service = traceability_service(semantic_engine=engine)

# Run the process
results = service.process_files("requirements.csv", "test_cases.csv")
print(results)