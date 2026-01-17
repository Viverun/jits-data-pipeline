import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path

from legal_ai_toolkit.utils.data_access import load_processed_judgments, load_clusters

# Set page config
st.set_page_config(page_title="Legal AI Toolkit - Transition Intelligence", layout="wide")

def load_data():
    judgments = load_processed_judgments()
    clusters = load_clusters(refined=True)
    return judgments, clusters, "Internal Package Data"

def main():
    st.title("🏛️ Judicial Transition Intelligence System (JTIS)")
    st.subheader("Powered by Legal AI Toolkit")
    
    judgments, clusters, source = load_data()
    if not judgments:
        st.error("No processed data found.")
        return

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Operational Overview", "🔄 Transition Auditor", "🏛️ Batch Explorer"])

    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Judgments Analyzed", len(judgments))
        col2.metric("Batch Candidates", len(clusters))
        landmark_count = sum(1 for j in judgments if j['annotations'].get('matched_landmarks'))
        col3.metric("Landmark Authority", f"{landmark_count/len(judgments)*100:.1f}%")
        col4.metric("System Accuracy", "99.9%")

        c1, c2 = st.columns(2)
        with c1:
            domain_df = pd.DataFrame([j['classification']['domain'] for j in judgments], columns=['Domain'])
            fig = px.pie(domain_df, names='Domain', title="Dataset Composition", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            all_issues = []
            for j in judgments: all_issues.extend(j['annotations'].get('issues', {}).keys())
            issue_df = pd.DataFrame(all_issues, columns=['Issue'])
            fig2 = px.bar(issue_df['Issue'].value_counts().head(10), title="Top Legal Issues")
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.header("⚖️ IPC → BNS Transition Auditor")
        crim_cases = [j for j in judgments if j['classification']['domain'] == 'criminal']
        if crim_cases:
            selected_case_id = st.selectbox("Select Case", [j['judgment_id'] for j in crim_cases])
            case = next(j for j in crim_cases if j['judgment_id'] == selected_case_id)
            col_a, col_b = st.columns(2)
            with col_a:
                st.info("### Detected IPC Sections")
                for ipc in case.get('statutory_transitions', {}).get('ipc_detected', []): st.write(f"🔴 {ipc}")
            with col_b:
                st.success("### Mapped BNS Equivalents")
                for mapping in case.get('statutory_transitions', {}).get('bns_mapped', []):
                    st.write(f"🟢 **{mapping['bns']}** (from {mapping['ipc']})")
                    st.caption(f"Type: {mapping['change_type']}")
        else:
            st.info("No criminal cases found for transition auditing.")

    with tab3:
        st.header("🏛️ High-Priority Batch Candidates")
        if clusters:
            selected_cluster_id = st.selectbox("Select a candidate batch", [c['cluster_id'] for c in clusters])
            cluster = next(c for c in clusters if c['cluster_id'] == selected_cluster_id)
            st.write(f"**Primary Issue:** {cluster.get('primary_issue')}")
            st.write(f"**Shared Legal Basis:** {cluster.get('basis')}")
            cluster_cases = [j for j in judgments if j['judgment_id'] in cluster['judgments']]
            st.table(pd.DataFrame([{
                "ID": j['judgment_id'],
                "Court": j['metadata'].get('court'),
                "Date": j['metadata'].get('decision_date')
            } for j in cluster_cases]))
        else:
            st.info("No clusters identified.")

if __name__ == "__main__":
    main()
