from setuptools import setup, find_packages

setup(
    name="legal-ai-toolkit",
    version="1.0.0",
    author="Jamil Khan (Viverun)",
    description="Zero-ML pipeline and dataset for Indian legal documents",
    url="https://github.com/viverun/legal-ai-toolkit",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "legal_ai_toolkit": [
            "data/judgments/*.json",
            "data/raw/judgments/unclassified/*.txt",
            "data/indices/*.json",
            "data/splits/*.txt"
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "requests>=2.26.0",
        "beautifulsoup4>=4.10.0",
        "streamlit>=1.20.0",
        "plotly>=5.13.0",
        "networkx>=3.0",
        "tqdm>=4.60.0"
    ],
    entry_points={
        "console_scripts": [
            "legal-ai-dashboard=legal_ai_toolkit.cli_dashboard:main",
            "legal-ai=legal_ai_toolkit.cli:main",
        ],
    },
)
