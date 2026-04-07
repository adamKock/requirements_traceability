from sentence_transformers import SentenceTransformer, util
import torch
from collections import defaultdict
from application.repo.TensorRepository import TensorRepository



class SemanticEngine:
    _model=None
   
    
    def __init__(self,repo:TensorRepository):
        
        if SemanticEngine._model is None:
            SemanticEngine._model = SentenceTransformer("all-mpnet-base-v2")
        self.model = SemanticEngine._model
        self.repo = repo  

    def compare(self, requirements,similarity, ids, job_id):
        print("Similarity:", similarity)
        threshold = 0.45
        mask = similarity >= threshold
        rows, cols = mask.nonzero(as_tuple=True)
        matches_table = torch.stack([rows, cols, similarity[rows, cols]], dim=1)
        grouped = defaultdict(list)

        

        for row, col, score in matches_table.tolist():
            grouped[int(row)].append((int(col), float(score)))
        
        testcase_map = self.repo.get_test_cases_by_job_id(job_id)

        results_list =[]

        for row_index in range(len(requirements)):
            matches = []

            if row_index in grouped:
                matches = []
                for col, score in grouped[row_index]:
                    summary = testcase_map[ids[col]]
                    matches.append({
                        "TestCaseID": ids[col],
                        "TestCase": summary,
                        "Similarity": float(score)
                    })

            result ={
                "Requirement": requirements[row_index].description,
                "Match Count": len(matches),
                "Matches": matches
            }
            results_list.append(result)

        return results_list
   
    
    def store_test_cases(self, test_cases, job_id):
        for t in test_cases:
            emb = self.model.encode(t.summary, convert_to_tensor=True)
            test_case_id = self.repo.create_test_case(t.summary,job_id,emb)
            if t.steps:
                step_embeddings = self.model.encode(t.steps,convert_to_tensor=True)
                for step, step_emb in zip(t.steps, step_embeddings):
                    self.repo.store_step(step, step_emb, test_case_id, job_id)

    def store_test_mappings(self,test_mappings):
        self.repo.store_test_mappings(test_mappings)

    def get_all_test_mappings(self):
        return self.repo.get_test_mappings()


    def compute_similarity(self, requirements,job_id):
        requirement_embeddings = self.model.encode(
            [r.description for r in requirements],
            convert_to_tensor=True)
        
        ids, test_case_embeddings = self.repo.get_all_test_case_embeddings(job_id)
        sim_matrix = util.cos_sim(
            requirement_embeddings.cpu(),
            test_case_embeddings.cpu()
        )

        return {
            "similarity_matrix": sim_matrix,
            "test_case_ids": ids,
            "requirements": requirements
        }
        
        

        






