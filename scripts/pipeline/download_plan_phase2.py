import sys
import os

# Add the current directory to path to import from download_indian_kanoon
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from download_indian_kanoon import ScaledDownloader

downloader = ScaledDownloader()

# PHASE 2: 574 cases to reach 1,000
# Focus: Service Law (best clustering) + Criminal Bail (high similarity)

query_plan_phase2 = {
    'SERVICE_PROMOTION': [
        "seniority promotion challenged DPC 2023",
        "seniority promotion challenged DPC 2024",  
        "promotion denied service rules 2023",
        "promotion denied service rules 2024",
        "Article 16 promotion seniority service",
        "selection list promotion challenged",
        "merit cum seniority promotion",
        "promotion roster reservation"
    ],
    
    'SERVICE_PENSION': [
        "family pension denial service",
        "pension arrears calculation service",
        "gratuity calculation dispute",
        "commutation pension service"
    ],
    
    'CRIMINAL_BAIL_IPC498A': [
        "IPC 498A bail application 2023",
        "IPC 498A bail application 2024",
        "IPC 498A cruelty bail",
        "dowry harassment bail 498A",
        "matrimonial cruelty bail IPC 498A"
    ],
    
    'CRIMINAL_BAIL_IPC304B': [
        "IPC 304B dowry death bail 2023",
        "IPC 304B dowry death bail 2024",
        "dowry death bail application",
        "IPC 304B anticipatory bail"
    ],
    
    'SERVICE_REGULARIZATION': [
        "regularization daily wage employee",
        "temporary employee regularization service",
        "adhoc employee regularization",
        "Umadevi regularization challenge"
    ],
    
    'CRIMINAL_QUASHING': [
        "Section 482 CrPC quashing FIR",
        "inherent powers quashing complaint",
        "482 CrPC matrimonial dispute",
        "quashing private complaint 482"
    ],
    
    'CIVIL_ARBITRATION_SEC34': [
        "Section 34 arbitration award challenge 2023",
        "Section 34 arbitration award challenge 2024",
        "set aside arbitral award Section 34",
        "Section 34 Arbitration Act challenge"
    ]
}

print("🚀 PHASE 2: Scaling to 1,000 Cases")
print("Target: 574 additional cases")
print("="*60)

total_downloaded = 0
for category, queries in query_plan_phase2.items():
    print(f"\n📂 {category}")
    for query in queries:
        count = downloader.search_and_download(query, category, max_results=25)
        total_downloaded += count

print(f"\n🏁 Phase 2 Complete: {total_downloaded} new cases downloaded")
