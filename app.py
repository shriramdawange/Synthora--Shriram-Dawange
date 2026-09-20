"""Streamlit Web UI for arXiv Paper Digest Agent."""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from graph import build_graph
from state import AgentState
from nodes.qa_loop import qa_node

st.set_page_config(
    page_title="arXiv Paper Digest Agent",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { max-width: 100%; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("arXiv Paper Digest Agent")
st.caption("Offline AI-powered paper analysis | Built by Shriram Dawange")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "result" not in st.session_state:
    st.session_state.result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

tab_analyze, tab_compare, tab_synthesize = st.tabs(["Analyze Paper", "Compare Papers", "Synthesize Topic"])

with tab_analyze:
    col1, col2 = st.columns([2, 1])
    with col1:
        paper_input = st.text_input(
            "Enter arXiv ID or research topic:",
            placeholder="e.g., 1706.03762 or attention mechanisms",
            key="paper_input",
        )
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("Analyze", type="primary", key="analyze_btn")

    if analyze_btn and paper_input:
        with st.spinner("Fetching and analyzing paper..."):
            state = AgentState(
                user_input=paper_input, query_type="", arxiv_id=None,
                compare_ids=[], search_results=[], selected_paper=None,
                raw_pdf_text="", sections={}, chunks=[], vector_store_path=None,
                briefing=None, conversation_history=[], author_info=[],
                recommendations=[], comparison_papers=[], comparison_result=None,
                synthesis=None, error=None,
            )
            result = st.session_state.graph.invoke(state)
            st.session_state.result = result

    if st.session_state.result:
        r = st.session_state.result
        briefing = r.get("briefing")

        if briefing:
            st.markdown("---")
            st.markdown(f"## {briefing.title}")
            st.markdown(f"**Authors:** {', '.join(briefing.authors[:5])}")
            st.markdown(f"**arXiv:** {briefing.arxiv_id} | **Published:** {briefing.published}")

            st.markdown("### Summary")
            st.info(briefing.summary)

            col_a, col_b = st.columns(2)
            with col_a:
                if briefing.problem_statement:
                    st.markdown("### Problem")
                    for p in briefing.problem_statement:
                        st.markdown(f"- {p}")
                if briefing.method:
                    st.markdown("### Method")
                    for m in briefing.method:
                        st.markdown(f"- {m}")
            with col_b:
                if briefing.key_results:
                    st.markdown("### Results")
                    for r in briefing.key_results:
                        st.markdown(f"- {r}")
                if briefing.limitations:
                    st.markdown("### Limitations")
                    for l in briefing.limitations:
                        st.markdown(f"- {l}")

            if briefing.suggested_questions:
                st.markdown("### Suggested Questions")
                for q in briefing.suggested_questions:
                    st.markdown(f"- {q}")

        if r.get("author_info"):
            st.markdown("---")
            st.markdown("## Authors")
            for author in r["author_info"][:3]:
                with st.expander(f"{author['name']}"):
                    st.write(f"**Fields:** {', '.join(author.get('fields', [])[:3])}")
                    st.write(f"**Papers on arXiv:** {author.get('paper_count', 0)}")
                    if author.get("recent_papers"):
                        st.markdown("**Recent Papers:**")
                        for p in author["recent_papers"][:3]:
                            st.markdown(f"- {p['title'][:80]} ({p['published']})")

        if r.get("recommendations"):
            st.markdown("---")
            st.markdown("## Similar Papers")
            for i, rec in enumerate(r["recommendations"][:5], 1):
                st.markdown(f"**{i}. {rec['title'][:70]}**")
                st.caption(f"{rec.get('arxiv_id', '')} | {rec.get('published', '')}")

        st.markdown("---")
        st.markdown("### Ask Questions")
        question = st.text_input("What do you want to know?", key="qa_input")
        if question and st.session_state.result:
            with st.spinner("Thinking..."):
                qa_state = dict(st.session_state.result)
                qa_state["user_input"] = question
                qa_result = qa_node(qa_state)
                if qa_result.get("conversation_history"):
                    st.session_state.result["conversation_history"] = qa_result["conversation_history"]
                    latest = qa_result["conversation_history"][-1]
                    st.markdown("**Answer:**")
                    st.write(latest.grounded_answer)

with tab_compare:
    st.markdown("## Compare Two Papers")
    col1, col2 = st.columns(2)
    with col1:
        id1 = st.text_input("Paper 1 arXiv ID:", placeholder="1706.03762", key="compare_id1")
    with col2:
        id2 = st.text_input("Paper 2 arXiv ID:", placeholder="2010.11930", key="compare_id2")

    if st.button("Compare", type="primary", key="compare_btn"):
        if id1 and id2:
            with st.spinner("Comparing papers..."):
                state = AgentState(
                    user_input=f"compare {id1} {id2}", query_type="compare",
                    arxiv_id=None, compare_ids=[id1, id2], search_results=[],
                    selected_paper=None, raw_pdf_text="", sections={},
                    chunks=[], vector_store_path=None, briefing=None,
                    conversation_history=[], author_info=[], recommendations=[],
                    comparison_papers=[], comparison_result=None, synthesis=None,
                    error=None,
                )
                result = st.session_state.graph.invoke(state)
                papers = result.get("comparison_papers", [])
                comp = result.get("comparison_result", {})
                if papers and len(papers) >= 2:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"### {papers[0]['title'][:50]}")
                        st.caption(f"arXiv: {papers[0]['arxiv_id']}")
                    with col_b:
                        st.markdown(f"### {papers[1]['title'][:50]}")
                        st.caption(f"arXiv: {papers[1]['arxiv_id']}")
                    if comp:
                        if comp.get("similarities"):
                            st.markdown("**Similarities:**")
                            for s in comp["similarities"]:
                                st.markdown(f"- {s}")
                        if comp.get("differences"):
                            st.markdown("**Differences:**")
                            for d in comp["differences"]:
                                st.markdown(f"- {d}")
                        if comp.get("recommendation"):
                            st.info(f"**Recommendation:** {comp['recommendation']}")
        else:
            st.warning("Please enter both paper IDs.")

with tab_synthesize:
    st.markdown("## Synthesize Research Topic")
    topic = st.text_input(
        "Enter research topic:",
        placeholder="e.g., transformer attention mechanisms",
        key="synth_topic",
    )
    if st.button("Synthesize", type="primary", key="synth_btn"):
        if topic:
            with st.spinner("Searching and synthesizing papers..."):
                state = AgentState(
                    user_input=topic, query_type="synthesize", arxiv_id=None,
                    compare_ids=[], search_results=[], selected_paper=None,
                    raw_pdf_text="", sections={}, chunks=[], vector_store_path=None,
                    briefing=None, conversation_history=[], author_info=[],
                    recommendations=[], comparison_papers=[], comparison_result=None,
                    synthesis=None, error=None,
                )
                result = st.session_state.graph.invoke(state)
                synth = result.get("synthesis")
                if synth:
                    if synth.get("common_themes"):
                        st.markdown("**Common Themes:**")
                        for t in synth["common_themes"]:
                            st.markdown(f"- {t}")
                    if synth.get("evolution"):
                        st.markdown(f"**Field Evolution:** {synth['evolution']}")
                    if synth.get("key_findings"):
                        st.markdown("**Key Findings:**")
                        for f in synth["key_findings"]:
                            st.markdown(f"- {f}")
                    if synth.get("open_questions"):
                        st.markdown("**Open Questions:**")
                        for q in synth["open_questions"]:
                            st.markdown(f"- {q}")
                    if synth.get("future_directions"):
                        st.markdown("**Future Directions:**")
                        for d in synth["future_directions"]:
                            st.markdown(f"- {d}")
        else:
            st.warning("Please enter a topic.")

st.markdown("---")
st.caption("Built by Shriram Dawange | Offline AI (Ollama + LangGraph)")
