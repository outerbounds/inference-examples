# coding: utf-8
import requests
import os
import json
import argparse
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import numpy as np


def get_auth_headers():
    from metaflow.metaflow_config import SERVICE_AUTH_KEY
    return {"x-api-key": SERVICE_AUTH_KEY}
    if os.environ.get('METAFLOW_SERVICE_AUTH_KEY'):
        return {"x-api-key": os.environ.get('METAFLOW_SERVICE_AUTH_KEY')}
    try:
        from outerbounds_app_client import OuterboundsAppClient
        return OuterboundsAppClient().get_auth_headers()
    except ImportError:
        return {}

DEFAULT_MODEL = "Alibaba-NLP/gte-reranker-modernbert-base"

@dataclass
class ScoringResult:
    """Result of scoring a text pair using cross-encoder"""
    text_1: str
    text_2: str
    score: float
    
@dataclass
class BatchScoringResult:
    """Result of batch scoring multiple text pairs"""
    scores: List[float]
    pairs: List[List[str]]
    average_score: float

class vLLMScoringClient:
    """Client for scoring text pairs using vLLM cross-encoder models"""
    
    def __init__(self, 
                 model: str = DEFAULT_MODEL,
                 server_url: Optional[str] = None,
                 use_offline: bool = True,
                 **llm_kwargs):
        """
        Initialize the scoring client
        
        Args:
            model: Cross-encoder model name (e.g., BAAI/bge-reranker-v2-m3)
            server_url: URL of vLLM server if using online API
            use_offline: Whether to use offline inference or online API
            **llm_kwargs: Additional arguments for LLM initialization
        """
        self.model_name = model
        self.server_url = server_url
        self.use_offline = use_offline
        
        if use_offline:
            # Initialize offline LLM for scoring
            default_kwargs = {
                "task": "score",
                "enforce_eager": True,
            }
            default_kwargs.update(llm_kwargs)
            from vllm import LLM
            self.llm = LLM(model=model, **default_kwargs)
        else:
            if not server_url:
                raise ValueError("server_url is required when use_offline=False")
            self.api_url = f"{server_url.rstrip('/')}/score"
    
    def score_pair(self, text_1: str, text_2: str) -> ScoringResult:
        """
        Score a single text pair
        
        Args:
            text_1: First text (typically the query)
            text_2: Second text (typically the document to score against query)
            
        Returns:
            ScoringResult with the score
        """
        if self.use_offline:
            return self._score_offline_single(text_1, text_2)
        else:
            return self._score_online_single(text_1, text_2)
    
    def score_batch(self, 
                   text_1: Union[str, List[str]], 
                   texts_2: List[str]) -> BatchScoringResult:
        """
        Score multiple text pairs in batch
        
        Args:
            text_1: Single query text or list of query texts
            texts_2: List of texts to score against the query/queries
            
        Returns:
            BatchScoringResult with all scores
        """
        if self.use_offline:
            return self._score_offline_batch(text_1, texts_2)
        else:
            return self._score_online_batch(text_1, texts_2)
    
    def _score_offline_single(self, text_1: str, text_2: str) -> ScoringResult:
        """Score using offline vLLM inference"""
        outputs = self.llm.score(text_1, [text_2])
        score = outputs[0].outputs.score
        return ScoringResult(text_1=text_1, text_2=text_2, score=score)
    
    def _score_offline_batch(self, 
                           text_1: Union[str, List[str]], 
                           texts_2: List[str]) -> BatchScoringResult:
        """Batch score using offline vLLM inference"""
        outputs = self.llm.score(text_1, texts_2)
        scores = [output.outputs.score for output in outputs]
        
        # Create pairs list
        if isinstance(text_1, str):
            pairs = [[text_1, text_2] for text_2 in texts_2]
        else:
            pairs = [[t1, t2] for t1, t2 in zip(text_1, texts_2)]
        
        return BatchScoringResult(
            scores=scores,
            pairs=pairs,
            average_score=np.mean(scores)
        )
    
    def _score_online_single(self, text_1: str, text_2: str) -> ScoringResult:
        """Score using online vLLM API"""
        payload = {
            "model": self.model_name,
            "text_1": text_1,
            "text_2": text_2,
            "encoding_format": "float"
        }
        
        headers = {"User-Agent": "vLLM Scoring Client"}
        headers.update(get_auth_headers())
        
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        data = result.get("data",[])
        score = data[0].get("score", 0.0)
        
        return ScoringResult(text_1=text_1, text_2=text_2, score=score)
    
    def _score_online_batch(self, 
                          text_1: Union[str, List[str]], 
                          texts_2: List[str]) -> BatchScoringResult:
        """Batch score using online vLLM API"""
        payload = {
            "model": self.model_name,
            "text_1": text_1,
            "text_2": texts_2,
            "encoding_format": "float"
        }
        
        headers = {"User-Agent": "vLLM Scoring Client"}
        headers.update(get_auth_headers())
        
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        data = result.get("data",[])
        scores = [d.get("score", 0.0) for d in data]
        
        # Create pairs list
        if isinstance(text_1, str):
            pairs = [[text_1, text_2] for text_2 in texts_2]
        else:
            pairs = [[t1, t2] for t1, t2 in zip(text_1, texts_2)]
        
        return BatchScoringResult(
            scores=scores,
            pairs=pairs,
            average_score=np.mean(scores) if scores else 0.0
        )
    
    def rank_documents(self, 
                      query: str, 
                      documents: List[str], 
                      top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Rank documents by relevance to a query
        
        Args:
            query: The search query
            documents: List of documents to rank
            top_k: Number of top documents to return (None for all)
            
        Returns:
            List of dictionaries with document, score, and rank
        """
        result = self.score_batch(query, documents)
        
        # Create ranked results
        ranked_results = []
        for i, (score, pair) in enumerate(zip(result.scores, result.pairs)):
            ranked_results.append({
                "document": pair[1],
                "score": score,
                "original_index": i
            })
        
        # Sort by score (descending)
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank
        for i, item in enumerate(ranked_results):
            item["rank"] = i + 1
        
        # Return top_k results
        if top_k:
            return ranked_results[:top_k]
        return ranked_results
    
    def find_best_match(self, 
                       query: str, 
                       candidates: List[str]) -> Dict[str, Any]:
        """
        Find the best matching candidate for a query
        
        Args:
            query: The search query
            candidates: List of candidate texts
            
        Returns:
            Dictionary with best match information
        """
        result = self.score_batch(query, candidates)
        
        best_idx = np.argmax(result.scores)
        best_score = result.scores[best_idx]
        best_match = candidates[best_idx]
        
        return {
            "query": query,
            "best_match": best_match,
            "best_score": best_score,
            "best_index": best_idx,
            "all_scores": result.scores
        }


def print_scoring_results(results: Union[ScoringResult, BatchScoringResult, List[Dict]]):
    """Print formatted scoring results"""
    print("=" * 60)
    print("vLLM SCORING RESULTS")
    print("=" * 60)
    
    if isinstance(results, ScoringResult):
        print(f"Text 1: {results.text_1}")
        print(f"Text 2: {results.text_2}")
        print(f"Score: {results.score:.4f}")
        
    elif isinstance(results, BatchScoringResult):
        print(f"Batch Results ({len(results.scores)} pairs)")
        print(f"Average Score: {results.average_score:.4f}")
        print("-" * 40)
        
        for i, (score, pair) in enumerate(zip(results.scores, results.pairs)):
            print(f"Pair {i+1}:")
            print(f"  Text 1: {pair[0][:50]}...")
            print(f"  Text 2: {pair[1][:50]}...")
            print(f"  Score: {score:.4f}")
            print()
            
    elif isinstance(results, list) and results:
        # Ranked results
        print("RANKED DOCUMENTS")
        print("-" * 40)
        for item in results:
            print(f"Rank {item['rank']}: Score {item['score']:.4f}")
            print(f"  Document: {item['document'][:100]}...")
            print()
    
    print("=" * 60)


def parse_args():
    parser = argparse.ArgumentParser(description="vLLM Cross-Encoder Scoring Client")
    parser.add_argument(
        "--model", type=str, default=DEFAULT_MODEL,
        help="Cross-encoder model name"
    )
    parser.add_argument(
        "--server-url", type=str, default=None,
        help="vLLM server URL (for online mode)"
    )
    parser.add_argument(
        "--offline", action="store_true", default=True,
        help="Use offline inference (default)"
    )
    parser.add_argument(
        "--online", action="store_true",
        help="Use online API (requires --server-url)"
    )
    parser.add_argument(
        "--text1", type=str, required=True,
        help="First text (query)"
    )
    parser.add_argument(
        "--text2", type=str, nargs="+", required=True,
        help="Second text(s) to score against first text"
    )
    parser.add_argument(
        "--rank", action="store_true",
        help="Rank documents by relevance"
    )
    parser.add_argument(
        "--top-k", type=int, default=None,
        help="Number of top results to show when ranking"
    )
    parser.add_argument(
        "--input-file", type=str, default=None,
        help="JSON file with scoring pairs"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Determine mode
    use_offline = args.offline and not args.online
    if args.online and not args.server_url:
        raise ValueError("--server-url is required when using --online")
    
    # Initialize client
    client = vLLMScoringClient(
        model=args.model,
        server_url=args.server_url,
        use_offline=use_offline
    )
    
    if args.input_file:
        # Load from file
        with open(args.input_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # List of scoring pairs
            results = []
            for item in data:
                text1 = item.get("text_1", "")
                text2 = item.get("text_2", "")
                result = client.score_pair(text1, text2)
                results.append(result)
            
            # Print all results
            for result in results:
                print_scoring_results(result)
        else:
            # Single batch
            text1 = data.get("text_1", "")
            texts2 = data.get("text_2", [])
            result = client.score_batch(text1, texts2)
            print_scoring_results(result)
    
    elif len(args.text2) == 1:
        # Single pair scoring
        result = client.score_pair(args.text1, args.text2[0])
        print_scoring_results(result)
    
    else:
        # Batch scoring
        if args.rank:
            # Rank documents
            ranked = client.rank_documents(args.text1, args.text2, args.top_k)
            print_scoring_results(ranked)
        else:
            # Regular batch scoring
            result = client.score_batch(args.text1, args.text2)
            print_scoring_results(result)


if __name__ == "__main__":
    main() 