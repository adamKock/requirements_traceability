from sentence_transformers import SentenceTransformer, util, CrossEncoder
import torch
from collections import defaultdict
from application.repo.TensorRepository import TensorRepository
import math
from fastapi.concurrency import run_in_threadpool
from rank_bm25 import BM25Okapi
import re


class SemanticEngine:
    _model=None
    _reranker = None
   
    
    def __init__(self,repo:TensorRepository):
        if SemanticEngine._model is None:
            SemanticEngine._model = SentenceTransformer("all-mpnet-base-v2")
        if SemanticEngine._reranker is None:
            SemanticEngine._reranker = CrossEncoder("cross-encoder/stsb-roberta-base")
        self.model = SemanticEngine._model
        self._reranker = SemanticEngine._reranker

        self.repo = repo  
        self.device = self.model.device

    @staticmethod
    def _tokenize(text: str):
        # simple whitespace + lowercase tokenizer, good enough for BM25
        return re.findall(r"\w+", text.lower())

    async def compare(self, requirements,job_id,analysis):
        summary_sim = analysis["summary_matrix"].to(self.device)
        step_sim = analysis["step_matrix"].to(self.device)
        ids = analysis["test_case_ids"]

        bm25_sim = analysis["bm25_matrix"].to(self.device)
        semantic_similarity = torch.maximum(summary_sim, step_sim)

        # BM25 can only ADD confidence for exact-term overlap, never subtract —
        # protects paraphrased-but-correct matches (e.g. "face scanning" vs "facial recognition")
        combined_similarity = semantic_similarity + (0.15 * bm25_sim)
        combined_similarity = torch.clamp(combined_similarity, max=1.0)

        NOISE_FLOOR = 0.30       # raised from 0.20 — cuts the 0-15% noise you're seeing
        CONFIDENT_THRESHOLD = 0.45

        mask = (combined_similarity >= NOISE_FLOOR).cpu()
        combined_scores = combined_similarity.cpu()

        # =========== NEW: needed for MatchedVia lookup ===========
        summary_scores_cpu = summary_sim.cpu()
        step_scores_cpu = step_sim.cpu()
        # =========== END NEW ===========
       

        rows, cols = mask.nonzero(as_tuple=True)
        grouped = defaultdict(list)
        for row, col in zip(rows.tolist(), cols.tolist()):
            score = float(combined_scores[row, col])
            grouped[row].append((col, score))

     
        
        testcase_map = await self.repo.get_test_cases_by_job_id(job_id)
        results_list =[]
        
        RERANK_TOP_N =5

        for row_index in range(len(requirements)):
            matches = []

            if row_index in grouped:
                sorted_matches = sorted(grouped[row_index], key=lambda x: x[1], reverse=True)      
                top_candidates = sorted_matches[:RERANK_TOP_N]
                remaining = sorted_matches[RERANK_TOP_N:]   
                req_text = requirements[row_index].description   

                if top_candidates:
                    pairs = [
                        (req_text, testcase_map.get(ids[col], ""))
                        for col, _ in top_candidates
                    ]
                    rerank_scores = await run_in_threadpool(self._reranker.predict, pairs)

                    reranked = []
                    for (col, bi_score), ce_score in zip(top_candidates, rerank_scores):
                        tc_id = ids[col]
                         # =========== NEW ===========
                        matched_via = "step" if step_scores_cpu[row_index, col] > summary_scores_cpu[row_index, col] else "summary"
                        # =========== END NEW ===========
                       
                        reranked.append({
                            "TestCaseID": tc_id,
                            "TestCase": testcase_map.get(tc_id, "Unknown"),
                            "Similarity": self.get_confidence(bi_score, ce_score),
                            "NeedsReview": bi_score < CONFIDENT_THRESHOLD,   # NEW
                            "MatchedVia": matched_via                        # NEW
                                })
                    reranked.sort(key=lambda m: m["Similarity"], reverse=True)
                    matches.extend(reranked)

                    for col, bi_score in remaining:
                        tc_id = ids[col]
                        # =========== NEW ===========
                        matched_via = "step" if step_scores_cpu[row_index, col] > summary_scores_cpu[row_index, col] else "summary"
                        # =========== END NEW ===========
                        matches.append({
                        "TestCaseID": tc_id,
                        "TestCase": testcase_map.get(tc_id, "Unknown"),
                        "Similarity": self.get_confidence(bi_score),
                        "NeedsReview": bi_score < CONFIDENT_THRESHOLD,   # NEW
                        "MatchedVia": matched_via 
                            })

            result={
                "Requirement": requirements[row_index].description,
                "Match Count": len(matches),
                "NeedsReviewCount": sum(1 for m in matches if m["NeedsReview"]),
                "Matches": matches

            }
            results_list.append(result)

        return results_list


               
   
    
    async def store_test_cases(self, test_cases, job_id):
        for t in test_cases:
            emb = await run_in_threadpool(self.model.encode(t.summary, convert_to_tensor=True))
            test_case_id = await self.repo.create_test_case(t.summary,job_id,emb)
            if t.steps:
                step_embeddings = await run_in_threadpool(self.model.encode, t.steps, convert_to_tensor=True)
                for step, step_emb in zip(t.steps, step_embeddings):
                    await self.repo.store_step(step, step_emb, test_case_id, job_id)


    async def compute_similarity(self, requirements,job_id):
        req_embs = await run_in_threadpool(
            self.model.encode,
            [r.description for r in requirements],
            convert_to_tensor=True
        )
        req_embs = req_embs.to(self.device)
        
        #Test Summary 
        tc_ids, tc_embs = await self.repo.get_all_test_case_embeddings(job_id)
        if not tc_ids:
            return "No test cases found for job_id: " + str(job_id)
        
        tc_embs = tc_embs.to(self.device)

        summary_sim_matrix = util.cos_sim(req_embs,tc_embs)

        #Step Embeddings 
        step_data = await self.repo.get_all_step_embeddings(job_id)
        num_reqs=len(requirements)
        num_tcs=len(tc_ids)

        step_sim_matrix = torch.zeros((num_reqs, num_tcs),device=self.device)

        for col_idx, tc_id in enumerate(tc_ids):
            if tc_id in step_data:
                all_steps_for_tc = torch.stack(step_data[tc_id]).to(self.device)
                res = util.cos_sim(req_embs, all_steps_for_tc)
                best_step_score = torch.max(res, dim=1).values
                step_sim_matrix[:, col_idx] = best_step_score * 0.9

        # =========== NEW: BM25 lexical scoring — ADD THIS BLOCK ===========
        testcase_map = await self.repo.get_test_cases_by_job_id(job_id)
        tc_texts = [testcase_map.get(tc_id, "") for tc_id in tc_ids]
        tokenized_corpus = [self._tokenize(t) for t in tc_texts]
        bm25 = BM25Okapi(tokenized_corpus)

        bm25_matrix = torch.zeros((num_reqs, num_tcs), device=self.device)
        for row_idx, req in enumerate(requirements):
            tokenized_query = self._tokenize(req.description)
            raw_scores = bm25.get_scores(tokenized_query)
            bm25_matrix[row_idx, :] = torch.tensor(raw_scores, device=self.device)

        row_max = bm25_matrix.max(dim=1, keepdim=True).values
        row_max = torch.clamp(row_max, min=1e-6)
        bm25_normalized = bm25_matrix / row_max
        # =========== END NEW BLOCK ===========
        return {
            "summary_matrix": summary_sim_matrix,
            "step_matrix": step_sim_matrix,
            "bm25_matrix": bm25_normalized,
            "test_case_ids": tc_ids,
            "requirements": requirements
        }

    @staticmethod
    def get_confidence(raw_score, rerank_score=None):
        if rerank_score is not None:
            low, high = 0.15, 0.85  # calibrated from labeled pairs — see notes below
            stretched = (float(rerank_score) - low) / (high - low)
            stretched = max(0.0, min(1.0, stretched))
            return round(stretched * 100, 1)

        k = 10
        x0 = 0.45
        sigmoid = 1 / (1 + math.exp(-k * (raw_score - x0)))
        return round(sigmoid * 100, 1)
        
        

        






