
from typing import List, Optional, Dict
from pydantic import BaseModel



class YouTubeAutomationState(BaseModel):
    selected_niche: Optional[str]
    niche_context: dict
    video_idea: Optional[str]
    keywords: List[str]
    script: Optional[str]
    video_asset_path: Optional[str]
    metadata: dict
    published: bool
    performance_metrics: dict



class NicheCandidate(BaseModel):
    name: str
    search_demand: float
    trend_velocity: float
    competition_score: float
    estimated_rpm: float
    monetization_score: float
    final_score: float
    metadata: Dict


class NicheDiscoveryState(BaseModel):
    candidates: List[NicheCandidate]
    ranked: List[NicheCandidate]
    top_niches: List[NicheCandidate]

    