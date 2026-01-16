import json
import os
from pathlib import Path

class PrecedentDatabase:
    """
    Authoritative landmark judgment database
    Integrates with your citation extraction
    """
    
    LANDMARKS = {
        # Constitutional Law
        "KESAVANANDA_BHARATI": {
            "full_citation": "Kesavananda Bharati v. State of Kerala, (1973) 4 SCC 225",
            "short_name": "Kesavananda Bharati",
            "year": 1973,
            "court": "Supreme Court",
            "bench_strength": 13,
            "legal_principle": "Basic structure doctrine",
            "issues": ["constitutional_amendment", "basic_structure", "judicial_review"],
            "provisions": ["Article 368", "Article 13"],
            "keywords": ["basic structure", "amendment", "constituent power"],
            "binding_authority": "SC",
            "overrules": [],
            "status": "good_law"
        },
        "MANEKA_GANDHI": {
            "full_citation": "Maneka Gandhi v. Union of India, (1978) 1 SCC 248",
            "short_name": "Maneka Gandhi",
            "year": 1978,
            "court": "Supreme Court",
            "bench_strength": 7,
            "legal_principle": "Article 21 expanded meaning - procedure must be fair, just and reasonable",
            "issues": ["personal_liberty", "article_21", "natural_justice"],
            "provisions": ["Article 21", "Article 14", "Article 19"],
            "keywords": ["personal liberty", "procedure established by law", "natural justice"],
            "binding_authority": "SC",
            "overrules": ["AK Gopalan"],
            "status": "good_law"
        },
        
        # Criminal Law
        "BACHAN_SINGH": {
            "full_citation": "Bachan Singh v. State of Punjab, (1980) 2 SCC 684",
            "short_name": "Bachan Singh",
            "year": 1980,
            "court": "Supreme Court",
            "bench_strength": 5,
            "legal_principle": "Death penalty - rarest of rare doctrine",
            "issues": ["sentencing", "death_penalty", "article_21"],
            "provisions": ["IPC 302", "Article 21"],
            "keywords": ["rarest of rare", "death sentence", "mitigating circumstances"],
            "binding_authority": "SC",
            "status": "good_law"
        },
        "ARNESH_KUMAR": {
            "full_citation": "Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273",
            "short_name": "Arnesh Kumar",
            "year": 2014,
            "court": "Supreme Court",
            "legal_principle": "Mandatory arrest not required for offences punishable less than 7 years",
            "issues": ["bail", "arrest", "personal_liberty"],
            "provisions": ["CrPC 41", "CrPC 437"],
            "keywords": ["arrest", "bail", "unnecessary arrest", "CrPC 41"],
            "binding_authority": "SC",
            "status": "good_law"
        },
        
        # Service Law
        "UMADEVI": {
            "full_citation": "Secretary, State of Karnataka v. Umadevi, (2006) 4 SCC 1",
            "short_name": "Umadevi",
            "year": 2006,
            "court": "Supreme Court",
            "legal_principle": "No automatic regularization of temporary/daily wage employees",
            "issues": ["regularization", "seniority_promotion", "article_14"],
            "provisions": ["Article 14", "Article 16"],
            "keywords": ["regularization", "temporary employee", "daily wage", "back door entry"],
            "binding_authority": "SC",
            "status": "good_law"
        },
        "DAVINDER_PAL_SINGH": {
            "full_citation": "State of Punjab v. Davinder Pal Singh, (2020) 8 SCC 1",
            "short_name": "Davinder Pal Singh",
            "year": 2020,
            "court": "Supreme Court",
            "legal_principle": "Promotion cannot be denied without opportunity of hearing",
            "issues": ["seniority_promotion", "natural_justice"],
            "provisions": ["Article 14", "Article 16"],
            "keywords": ["promotion", "natural justice", "opportunity to be heard"],
            "binding_authority": "SC",
            "status": "good_law"
        },
        
        # Evidence Law
        "ANVAR_PV": {
            "full_citation": "Anvar P.V. v. P.K. Basheer, (2014) 10 SCC 473",
            "short_name": "Anvar P.V.",
            "year": 2014,
            "court": "Supreme Court",
            "legal_principle": "Electronic evidence - certificate under Section 65B mandatory",
            "issues": ["electronic_evidence", "admissibility"],
            "provisions": ["Evidence Act 65B"],
            "keywords": ["electronic evidence", "Section 65B", "certificate", "admissibility"],
            "binding_authority": "SC",
            "status": "good_law"
        }
    }
    
    @classmethod
    def match_citation(cls, citation_text: str):
        """Match extracted citation to known landmark"""
        citation_upper = citation_text.upper()
        
        for prec_id, data in cls.LANDMARKS.items():
            # Match by short name or key terms
            if data["short_name"].upper() in citation_upper:
                return {
                    "precedent_id": prec_id,
                    **data,
                    "matched_by": "short_name"
                }
            
            # Match by year and SCC reporter
            if str(data["year"]) in citation_text and "SCC" in citation_upper:
                return {
                    "precedent_id": prec_id,
                    **data,
                    "matched_by": "year_reporter"
                }
        
        return None
    
    @classmethod
    def find_relevant_precedents(cls, issues: list, sections: list):
        """Find precedents relevant to given issues/sections"""
        relevant = []
        
        for prec_id, data in cls.LANDMARKS.items():
            # Check issue overlap
            issue_match = any(issue in data["issues"] for issue in issues)
            
            # Check provision overlap
            section_match = any(
                any(sec in prov for sec in sections)
                for prov in data["provisions"]
            )
            
            if issue_match or section_match:
                relevance_score = 0
                if issue_match:
                    relevance_score += 2
                if section_match:
                    relevance_score += 1
                
                relevant.append({
                    "precedent_id": prec_id,
                    **data,
                    "relevance_score": relevance_score
                })
        
        # Sort by relevance
        relevant.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant
    
    @classmethod
    def get_all_precedents(cls):
        """Get all precedents as list"""
        return [
            {"precedent_id": pid, **data}
            for pid, data in cls.LANDMARKS.items()
        ]
