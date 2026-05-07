from sentence_transformers import SentenceTransformer, util
import torch
from collections import defaultdict
from application.repo.TensorRepository import TensorRepository
import math



class SemanticEngine:
    _model=None
   
    
    def __init__(self,repo:TensorRepository):
        
        if SemanticEngine._model is None:
            SemanticEngine._model = SentenceTransformer("all-mpnet-base-v2")
        self.model = SemanticEngine._model
        self.repo = repo  
        self.device = self.model.device

    def compare(self, requirements,job_id,analysis):
        summary_sim = analysis["summary_matrix"].to(self.device)
        step_sim = analysis["step_matrix"].to(self.device)
        ids = analysis["test_case_ids"]

        combined_similarity = torch.maximum(summary_sim, step_sim) 
        threshold = 0.45

        mask = (combined_similarity >= threshold).cpu()
        combined_scores = combined_similarity.cpu()

        rows, cols = mask.nonzero(as_tuple=True)
        grouped = defaultdict(list)
        for row, col in zip(rows.tolist(), cols.tolist()):
            score = float(combined_scores[row, col])
            grouped[row].append((col, score))

     
        
        testcase_map = self.repo.get_test_cases_by_job_id(job_id)
        results_list =[]

        for row_index in range(len(requirements)):
            matches = []

            if row_index in grouped:
                sorted_matches = sorted(grouped[row_index], key=lambda x: x[1], reverse=True)                
                for col, score in sorted_matches:
                    tc_id = ids[col]
                    matches.append({
                        "TestCaseID": tc_id,
                        "TestCase": testcase_map.get(tc_id, "Unknown"),
                        "Similarity":self.get_confidence(score)
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
    
    def store_requirement_mappings(self,requirement_mappings):
        self.repo.store_requirement_mappings(requirement_mappings)

    def get_requirement_mappings(self):
        return self.repo.get_requirement_mappings()

    def compute_similarity(self, requirements,job_id):
        req_embs = self.model.encode(
            [r.description for r in requirements],
            convert_to_tensor=True).to(self.device)
        
        #Test Summary 
        tc_ids, tc_embs = self.repo.get_all_test_case_embeddings(job_id)
        tc_embs = tc_embs.to(self.device)

        summary_sim_matrix = util.cos_sim(req_embs,tc_embs)

        #Step Embeddings 
        step_data = self.repo.get_all_step_embeddings(job_id)
        num_reqs=len(requirements)
        num_tcs=len(tc_ids)

        step_sim_matrix = torch.zeros((num_reqs, num_tcs),device=self.device)

        for col_idx, tc_id in enumerate(tc_ids):
            if tc_id in step_data:
                all_steps_for_tc = torch.stack(step_data[tc_id]).to(self.device)
                res = util.cos_sim(req_embs, all_steps_for_tc)
                best_step_score = torch.max(res, dim=1).values
                step_sim_matrix[:, col_idx] = best_step_score * 0.9
        return {
            "summary_matrix": summary_sim_matrix,
            "step_matrix": step_sim_matrix,
            "test_case_ids": tc_ids,
            "requirements": requirements
        }
    
    @staticmethod
    def get_confidence(raw_score):
        k = 10  
        x0 = 0.45 
        sigmoid = 1 / (1 + math.exp(-k * (raw_score - x0)))
        return round(sigmoid * 100, 1)
        
        

        






