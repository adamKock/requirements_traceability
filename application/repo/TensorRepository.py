import pickle
import torch
class TensorRepository:

        def __init__(self, connection):
                self.conn = connection
                self.curr = connection.cursor()
                self.curr.execute("CREATE TABLE IF NOT EXISTS requirements (id SERIAL PRIMARY KEY, requirement_text TEXT NOT NULL, embeddings BYTEA)")
                self.curr.execute("CREATE TABLE IF NOT EXISTS test_cases (id SERIAL PRIMARY KEY, summary TEXT NOT NULL, job_id TEXT NOT NULL, embeddings BYTEA)")
                self.curr.execute("CREATE TABLE IF NOT EXISTS test_steps (id SERIAL PRIMARY KEY, test_case_id INT REFERENCES test_cases(id), step_text TEXT NOT NULL,job_id TEXT NOT NULL, embeddings BYTEA)")
                self.conn.commit()
                self.curr.close()



        def store_requirements(self, requirement_text, embeddings):
                curr = self.conn.cursor()
                curr.execute("INSERT INTO requirements (requirement_text, embeddings) VALUES (%s, %s) RETURNING id",(requirement_text,pickle.dumps(embeddings),))
                requirement_id = curr.fetchone()[0]
                self.conn.commit()
                curr.close()  
                return requirement_id 
        
        def create_test_case(self,summary,job_id,embedding):
                curr = self.conn.cursor()
                curr.execute("INSERT INTO test_cases (summary,job_id,embeddings) VALUES (%s, %s,%s) RETURNING id",(summary,job_id,pickle.dumps(embedding),))
                test_case_id = curr.fetchone()[0]
                self.conn.commit()
                curr.close()  
                return test_case_id

        
        def store_step(self, step_text, embeddings,test_case_id,job_id):
                curr = self.conn.cursor()
                curr.execute("INSERT INTO test_steps (test_case_id,step_text, job_id, embeddings) VALUES (%s,%s,%s,%s) RETURNING id",(test_case_id,step_text,job_id,pickle.dumps(embeddings),))
                step_id = curr.fetchone()[0]
                self.conn.commit()
                curr.close()  
                return step_id
        
        def get_test_cases_by_job_id(self, job_id):
                cursor = self.conn.cursor()
                cursor.execute("SELECT id, summary FROM test_cases WHERE job_id = %s", (job_id,))
                rows = cursor.fetchall()
                cursor.close()
                return {row[0]: row[1] for row in rows}                   



        def get_all_test_case_embeddings(self,job_id):
                curr = self.conn.cursor()
                curr.execute("SELECT id, embeddings FROM test_cases WHERE job_id =%s AND embeddings IS NOT NULL ORDER BY id",(job_id,))
                rows = curr.fetchall()
                curr.close()
                ids = []
                embeddings = []
                if not rows:
                        return [], None
                for test_case_id, emb_blob in rows:
                        ids.append(test_case_id)
                        emb = pickle.loads(emb_blob)
                        embeddings.append(emb.cpu())

                return ids, torch.stack(embeddings)
                






    



