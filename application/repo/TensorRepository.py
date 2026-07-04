import pickle
import torch
from collections import defaultdict
from db import get_db_connection
class TensorRepository:

        def __init__(self):
                pass
                


        def initialize_schema(self):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                cursor.execute("CREATE TABLE IF NOT EXISTS test_cases (id SERIAL PRIMARY KEY, summary TEXT NOT NULL, job_id TEXT NOT NULL, embeddings BYTEA)")
                                cursor.execute("CREATE TABLE IF NOT EXISTS test_steps (id SERIAL PRIMARY KEY, test_case_id INT REFERENCES test_cases(id), step_text TEXT NOT NULL,job_id TEXT NOT NULL, embeddings BYTEA)")
                                cursor.execute("CREATE TABLE IF NOT EXISTS test_mappings (id SERIAL PRIMARY KEY, cannonical_field TEXT NOT NULL, varient TEXT NOT NULL)")
                                cursor.execute("CREATE TABLE IF NOT EXISTS requirement_mappings (id SERIAL PRIMARY KEY, cannonical_field TEXT NOT NULL, varient TEXT NOT NULL)")
                                

        
        def create_test_case(self,summary,job_id,embedding):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                cursor.execute("INSERT INTO test_cases (summary,job_id,embeddings) VALUES (%s, %s,%s) RETURNING id",(summary,job_id,pickle.dumps(embedding),))
                                test_case_id = cursor.fetchone()[0]
                                 
                                return test_case_id

        
        def store_step(self, step_text, embeddings,test_case_id,job_id):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                cursor.execute("INSERT INTO test_steps (test_case_id,step_text, job_id, embeddings) VALUES (%s,%s,%s,%s) RETURNING id",(test_case_id,step_text,job_id,pickle.dumps(embeddings),))
                                step_id = cursor.fetchone()[0]
                                 
                                return step_id
        
        def get_test_cases_by_job_id(self, job_id):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                cursor.execute("SELECT id, summary FROM test_cases WHERE job_id = %s", (job_id,))
                                rows = cursor.fetchall()
                                
                                return {row[0]: row[1] for row in rows}                   



        def get_all_test_case_embeddings(self,job_id):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                cursor.execute("SELECT id, embeddings FROM test_cases WHERE job_id =%s AND embeddings IS NOT NULL ORDER BY id",(job_id,))
                                rows = cursor.fetchall()
                                
                                ids = []
                                embeddings = []
                                if not rows:
                                        return [], None
                                for test_case_id, emb_blob in rows:
                                        ids.append(test_case_id)
                                        emb = pickle.loads(emb_blob)
                                        embeddings.append(emb.cpu())
                                return ids, torch.stack(embeddings)
        
        def store_test_mappings(self,Test_Case_Mapping):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                for key, variants in Test_Case_Mapping.items():
                                        for variant in variants:
                                                cursor.execute("INSERT INTO test_mappings (cannonical_field, varient) VALUES (%s, %s)",(key,variant))
                                                
                                

        def get_test_mappings(self):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                cursor.execute("SELECT cannonical_field, varient FROM test_mappings")
                                rows = cursor.fetchall()
                                
                                mapping= defaultdict(list)
                                for standard, varient in rows:
                                        mapping[standard].append(varient)
                                return dict(mapping)

        def store_requirement_mappings(self, requirement_mapping):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                for key, variants in requirement_mapping.items():
                                        for variant in variants:
                                                cursor.execute("INSERT INTO requirement_mappings (cannonical_field, varient) VALUES (%s, %s)",(key,variant))
                                

        def get_requirement_mappings(self):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                cursor.execute("SELECT cannonical_field, varient FROM requirement_mappings")
                                rows = cursor.fetchall()
                                
                                mapping= defaultdict(list)
                                for standard,varient in rows:    
                                        mapping[standard].append(varient)
                                return dict(mapping)
        
        def get_all_step_embeddings(self, job_id):
                with get_db_connection() as conn:
                        with conn.cursor() as cursor:
                                # Fetch steps and link them to their parent test case
                                cursor.execute("""
                        SELECT test_case_id, embeddings 
                        FROM test_steps 
                        WHERE job_id = %s AND embeddings IS NOT NULL 
                        ORDER BY test_case_id
                        """, (job_id,))
                                rows = cursor.fetchall()
                                
                                step_data = defaultdict(list)
                                for tc_id, emb_blob in rows:
                                        step_data[tc_id].append(pickle.loads(emb_blob).cpu())
                                return step_data # Dictionary: {test_case_id: [tensor1, tensor2, ...]}

                






    



