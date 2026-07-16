import torch
from collections import defaultdict
from application.repo.db import DB_POOL
from application.repo.tensor_codec import encode_tensor, decode_tensor


class TensorRepository:

        def __init__(self):
                pass
                

        async def initialize_schema(self):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                await cursor.execute("""
                                        CREATE TABLE IF NOT EXISTS test_cases (
                                        id SERIAL PRIMARY KEY,
                                        summary TEXT NOT NULL,
                                        job_id TEXT NOT NULL,
                                        embeddings BYTEA)
                                        """)
                                await cursor.execute("""
                                        CREATE TABLE IF NOT EXISTS test_steps (
                                        id SERIAL PRIMARY KEY,
                                        test_case_id INT REFERENCES test_cases(id),
                                        step_text TEXT NOT NULL,
                                        job_id TEXT NOT NULL,
                                        embeddings BYTEA)
                                        """)
                                await cursor.execute("""
                                        CREATE TABLE IF NOT EXISTS test_mappings (
                                        id SERIAL PRIMARY KEY,
                                        cannonical_field TEXT NOT NULL,
                                        varient TEXT NOT NULL)
                                        """)
                                await cursor.execute("""
                                        CREATE TABLE IF NOT EXISTS requirement_mappings (
                                        id SERIAL PRIMARY KEY,
                                        cannonical_field TEXT NOT NULL,
                                        varient TEXT NOT NULL)
                                        """)

        
        async def create_test_case(self,summary,job_id,embedding):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                await cursor.execute("INSERT INTO test_cases (summary,job_id,embeddings) VALUES (%s, %s,%s) RETURNING id",(summary,job_id,encode_tensor(embedding),))
                                row = await cursor.fetchone()
                                test_case_id = row[0]
                                 
                                return test_case_id

        
        async def store_step(self, step_text, embeddings,test_case_id,job_id):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                await cursor.execute("INSERT INTO test_steps (test_case_id,step_text, job_id, embeddings) VALUES (%s,%s,%s,%s) RETURNING id",(test_case_id,step_text,job_id,encode_tensor(embeddings),))
                                row = await cursor.fetchone()
                                step_id  = row[0]

                                 
                                return step_id
        
        async def get_test_cases_by_job_id(self, job_id):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                await cursor.execute("SELECT id, summary FROM test_cases WHERE job_id = %s", (job_id,))
                                rows = await cursor.fetchall()
                                
                                return {row[0]: row[1] for row in rows}                   



        async def get_all_test_case_embeddings(self,job_id):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                await cursor.execute("SELECT id, embeddings FROM test_cases WHERE job_id =%s AND embeddings IS NOT NULL ORDER BY id",(job_id,))
                                rows = await cursor.fetchall()
                                
                                ids = []
                                embeddings = []
                                if not rows:
                                        return [], None
                                for test_case_id, emb_blob in rows:
                                        ids.append(test_case_id)
                                        emb = decode_tensor(emb_blob)
                                        embeddings.append(emb.cpu())
                                return ids, torch.stack(embeddings)
        
        async def store_test_mappings(self,Test_Case_Mapping):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                
                                for key, variants in Test_Case_Mapping.items():
                                        for variant in variants:
                                                await cursor.execute("INSERT INTO test_mappings (cannonical_field, varient) VALUES (%s, %s)",(key,variant))
                                                
                                

        async def get_test_mappings(self):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                await cursor.execute("SELECT cannonical_field, varient FROM test_mappings")
                                rows = await cursor.fetchall()
                                
                                mapping= defaultdict(list)
                                for standard, varient in rows:
                                        mapping[standard].append(varient)
                                return dict(mapping)

        async def store_requirement_mappings(self, requirement_mapping):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                for key, variants in requirement_mapping.items():
                                        for variant in variants:
                                                await cursor.execute("INSERT INTO requirement_mappings (cannonical_field, varient) VALUES (%s, %s)",(key,variant))
                                

        async def get_requirement_mappings(self):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                await cursor.execute("SELECT cannonical_field, varient FROM requirement_mappings")
                                rows = await cursor.fetchall()
                                
                                mapping= defaultdict(list)
                                for standard,varient in rows:    
                                        mapping[standard].append(varient)
                                return dict(mapping)
        
        async def get_all_step_embeddings(self, job_id):
                async with DB_POOL.connection() as conn:
                        async with conn.cursor() as cursor:
                                # Fetch steps and link them to their parent test case
                                await cursor.execute("""
                        SELECT test_case_id, embeddings 
                        FROM test_steps 
                        WHERE job_id = %s AND embeddings IS NOT NULL 
                        ORDER BY test_case_id
                        """, (job_id,))
                                rows = await cursor.fetchall()
                                
                                step_data = defaultdict(list)
                                for tc_id, emb_blob in rows:
                                        step_data[tc_id].append(decode_tensor(emb_blob).cpu())
                                return step_data # Dictionary: {test_case_id: [tensor1, tensor2, ...]}

                






    



