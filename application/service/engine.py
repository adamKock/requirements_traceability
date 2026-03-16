from application.schemas.schema import TraceabilityRequest
from sentence_transformers import SentenceTransformer, util
import torch
from collections import defaultdict



class SemanticEngine:
    _model=None
   

    
    def __init__(self):
        if SemanticEngine._model is None:
            SemanticEngine._model = SentenceTransformer("all-mpnet-base-v2")
        self.model = SemanticEngine._model

    def convert_to_tensor(self, payload:TraceabilityRequest):
        requirement_text = [r.description for r in payload.requirements]
        test_case_sentences = [[t.summary] + t.steps for t in payload.test_cases]
        
        n_testcases = len(test_case_sentences)
        n_requirements = len(requirement_text)
        similarity = torch.zeros((n_testcases, n_requirements))

        encoded_req = self.model.encode(requirement_text, convert_to_tensor=True)

        for i, sentances in enumerate(test_case_sentences):
            encoded_steps = self.model.encode(sentances, convert_to_tensor=True)
            sim_matrix = util.cos_sim(encoded_steps,encoded_req)
            similarity[i] = sim_matrix.max(dim=0).values



        return similarity
    

    def compare(self, payload:TraceabilityRequest, similarity):
        testcases = payload.test_cases
        requirements = payload.requirements
        n_testcases, n_requirements = similarity.shape
        print(f"{n_requirements} requirements, {n_testcases} test cases")
        threshold = 0.6
        strong_threshold = 0.75

        mask = similarity >= threshold

        match_counts = mask.sum(dim=1)

        top_scores_values = similarity.max(dim=1).values

        
        status = torch.where(
            match_counts == 0,
            0,
                torch.where(top_scores_values >= strong_threshold, 1, 2))
        status = status.tolist()

        rows, cols = mask.nonzero(as_tuple=True)
        matches_table = torch.stack([rows, cols, similarity[rows, cols]], dim=1)

        grouped = defaultdict(list)

        for row, col, score in matches_table:
            grouped[int(row)].append((int(col), float(score)))

        results_list =[]

        for row_index in range(len(requirements)):
            matches =[]
            if row_index in grouped:
                matches=[
                    {"TestCase": testcases[col].summary + "\n" + "\n".join(
                        f"Step {i+1}: {s}" for i, s in enumerate(testcases[col].steps))
                        ,"Similarity": float(score)}
                    for col, score in grouped[row_index]
                ]

            result ={
                "Requirement": requirements[row_index].description,
                "Match Count": len(matches),
                "Matches": matches
            }
            results_list.append(result)

        return results_list
   
    
      
       
        
        

        






