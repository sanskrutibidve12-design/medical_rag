import streamlit as st
import base64
import os

st.set_page_config(
    page_title="MedRAG – AI Medical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

page = st.query_params.get("page", "home")

# ══════════════════════════════════════════
# GLOBAL STYLES — injected once, works everywhere
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

html, body, [data-testid="stAppViewContainer"] {
    background: #04101f !important;
    font-family: 'Sora', sans-serif !important;
}

/* Streamlit button override */
.stButton > button {
    background: #0d9e6e !important; color: #fff !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 500 !important; padding: 10px 28px !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #0b8a5e !important; }

/* ── Navbar ── */
.navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 48px; background: #04101f;
    border-bottom: 0.5px solid rgba(255,255,255,0.08);
    position: sticky; top: 0; z-index: 999;
}
.brand { display: flex; align-items: center; gap: 10px; }
.brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #0d9e6e, #0fcf99);
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 18px;
}
.brand-text { color: #fff; font-size: 16px; font-weight: 600; font-family: 'Sora', sans-serif; }
.brand-text span { color: #0fcf99; }
.nav-links { display: flex; align-items: center; gap: 4px; }
.nav-pill {
    color: #7a9ab5; padding: 7px 16px; border-radius: 8px;
    font-size: 13px; text-decoration: none; font-family: 'Sora', sans-serif;
    transition: all 0.2s;
}
.nav-pill:hover { color: #fff !important; background: rgba(255,255,255,0.1); }
.nav-pill.active { color: #fff !important; background: rgba(255,255,255,0.1); }
.nav-cta {
    background: #0d9e6e; color: #fff !important; padding: 7px 18px;
    border-radius: 8px; font-size: 13px; font-weight: 500;
    text-decoration: none; font-family: 'Sora', sans-serif; margin-left: 8px;
}
.nav-cta:hover { background: #0b8a5e !important; }

/* ── Page wrap ── */
.page-wrap { max-width: 1060px; margin: 0 auto; padding: 32px 36px 60px; }

/* ── Section chip ── */
.section-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(13,158,110,0.12); border: 0.5px solid rgba(13,158,110,0.35);
    color: #0fcf99; font-size: 11px; font-weight: 500; letter-spacing: 0.8px;
    text-transform: uppercase; padding: 5px 13px; border-radius: 20px; margin-bottom: 20px;
}

/* ── Creator banner ── */
.creator-banner {
    background: linear-gradient(135deg, #071a30, #0a2240);
    border: 0.5px solid rgba(15,207,153,0.2); border-radius: 20px;
    padding: 44px 52px; display: flex; align-items: center; gap: 40px; margin-bottom: 40px;
}
.creator-avatar {
    width: 88px; height: 88px; border-radius: 50%;
    background: linear-gradient(135deg, #0d9e6e, #0fcf99);
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Serif Display', serif; font-size: 28px; color: #04101f;
    font-weight: 700; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(15,207,153,0.2);
}
.creator-greeting { font-size: 13px; color: #0fcf99; font-weight: 500; margin-bottom: 6px; }
.creator-name { font-family: 'DM Serif Display', serif; font-size: 36px; color: #fff; margin-bottom: 10px; }
.creator-desc { font-size: 14px; color: #7a9ab5; line-height: 1.8; }
.creator-desc strong { color: #c8dae8; }
.creator-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.ctag {
    background: rgba(255,255,255,0.05); border: 0.5px solid rgba(255,255,255,0.12);
    color: #a0bdd0; font-size: 12px; padding: 4px 12px; border-radius: 20px;
}

/* ── Two col ── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 36px; }
.info-card {
    background: #071828; border: 0.5px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 28px;
}
.info-card.problem { border-top: 3px solid #e85d5d; }
.info-card.solution { border-top: 3px solid #0fcf99; }
.info-card-title {
    font-size: 17px; font-weight: 600; color: #fff;
    margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
}
.info-card p { font-size: 13.5px; color: #7a9ab5; line-height: 1.8; margin-bottom: 10px; }
.info-card p strong { color: #c8dae8; }
.stat-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.stat-pill {
    background: rgba(15,207,153,0.08); border: 0.5px solid rgba(15,207,153,0.25);
    color: #0fcf99; font-size: 11.5px; padding: 5px 12px; border-radius: 20px; font-weight: 500;
}
.stat-pill.red { background: rgba(232,93,93,0.08); border-color: rgba(232,93,93,0.25); color: #e85d5d; }

/* ── RAG section ── */
.rag-section {
    background: #071828; border: 0.5px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 36px 42px; margin-bottom: 36px;
}
.rag-title { font-family: 'DM Serif Display', serif; font-size: 26px; color: #fff; margin-bottom: 12px; }
.rag-desc { font-size: 14px; color: #7a9ab5; line-height: 1.85; margin-bottom: 26px; }
.rag-desc strong { color: #c8dae8; }
.rag-steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.rag-step {
    background: rgba(255,255,255,0.03); border: 0.5px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 20px 14px; text-align: center;
}
.rag-step-num {
    width: 30px; height: 30px; border-radius: 50%;
    background: rgba(13,158,110,0.2); color: #0fcf99; font-size: 13px; font-weight: 600;
    display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;
}
.rag-step-label { font-size: 13px; font-weight: 600; color: #c8dae8; margin-bottom: 5px; }
.rag-step-desc { font-size: 11.5px; color: #4e6a80; line-height: 1.5; }

/* ── Page header ── */
.page-header { padding: 12px 0 28px; border-bottom: 0.5px solid rgba(255,255,255,0.06); margin-bottom: 32px; }
.page-header-title { font-family: 'DM Serif Display', serif; font-size: 38px; color: #fff; margin-bottom: 10px; }
.page-header-sub { font-size: 14.5px; color: #5a7d96; line-height: 1.7; max-width: 580px; }

/* ── About ── */
.about-section-title { font-family: 'DM Serif Display', serif; font-size: 22px; color: #fff; margin: 28px 0 16px; }
.tool-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.tool-card {
    background: #071828; border: 0.5px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 22px 18px;
}
.tool-icon { font-size: 24px; margin-bottom: 10px; }
.tool-name { font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 6px; }
.tool-desc { font-size: 12.5px; color: #5a7d96; line-height: 1.65; }
.tool-badge {
    display: inline-block; margin-top: 10px;
    background: rgba(13,158,110,0.12); border: 0.5px solid rgba(13,158,110,0.3);
    color: #0fcf99; font-size: 11px; padding: 3px 10px; border-radius: 20px;
}
.feature-list { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 28px; }
.feature-item {
    display: flex; align-items: flex-start; gap: 12px;
    background: #071828; border: 0.5px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 16px;
}
.feature-dot { width: 8px; height: 8px; border-radius: 50%; background: #0fcf99; margin-top: 5px; flex-shrink: 0; }
.feature-text { font-size: 13.5px; color: #8aafca; line-height: 1.6; }
.feature-text strong { color: #c8dae8; display: block; margin-bottom: 3px; }
.limitation-card {
    background: rgba(232,93,93,0.06); border: 0.5px solid rgba(232,93,93,0.2);
    border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
    font-size: 13px; color: #b07070; display: flex; gap: 12px; align-items: flex-start;
}
.limitation-card strong { color: #c87070; }

/* ── Architecture ── */
.arch-flow { display: flex; align-items: center; overflow-x: auto; margin: 24px 0; gap: 0; }
.arch-box {
    flex: 1; min-width: 96px; background: #071828;
    border: 0.5px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 14px 10px; text-align: center;
}
.arch-box.hl { border-color: rgba(15,207,153,0.4); background: rgba(15,207,153,0.06); }
.arch-box-num {
    width: 26px; height: 26px; border-radius: 50%;
    background: rgba(13,158,110,0.2); color: #0fcf99; font-size: 11px; font-weight: 600;
    display: flex; align-items: center; justify-content: center; margin: 0 auto 8px;
}
.arch-box-name { font-size: 11.5px; font-weight: 600; color: #c8dae8; margin-bottom: 4px; }
.arch-box-sub { font-size: 10px; color: #3d5f75; line-height: 1.4; }
.arch-arrow { color: #1d4055; font-size: 20px; padding: 0 3px; flex-shrink: 0; margin-bottom: 20px; }
.tech-stack { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 24px; }
.tech-item {
    background: #071828; border: 0.5px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 18px 14px; text-align: center;
}
.tech-item-icon { font-size: 26px; margin-bottom: 8px; }
.tech-item-name { font-size: 12.5px; font-weight: 600; color: #c8dae8; margin-bottom: 4px; }
.tech-item-role { font-size: 11px; color: #3d5f75; }

/* ── Chatbot ── */
.chat-notice {
    background: rgba(13,158,110,0.08); border: 0.5px solid rgba(13,158,110,0.25);
    border-radius: 10px; padding: 12px 16px; font-size: 13px; color: #4aaa85; margin-bottom: 8px;
}

/* ── CTA link button ── */
.cta-link {
    display: inline-block; text-align: center;
    background: #0d9e6e; color: #fff !important;
    padding: 12px 32px; border-radius: 10px;
    font-size: 14px; font-weight: 500;
    text-decoration: none; font-family: 'Sora', sans-serif;
}
.cta-link:hover { background: #0b8a5e !important; }
.cta-wrap { text-align: center; margin: 20px 0 40px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# NAVBAR — pure st.markdown, always renders fresh
# ══════════════════════════════════════════
def render_navbar(current_page):
    links = ""
    for key, label in {"home": "Home", "about": "About", "architecture": "Architecture"}.items():
        active = "active" if current_page == key else ""
        links += f'<a class="nav-pill {active}" href="?page={key}">{label}</a>'
    links += '<a class="nav-cta" href="?page=chatbot">🩺 Try Chatbot</a>'
    st.markdown(f"""
    <div class="navbar">
        <div class="brand">
            <div class="brand-icon">🩺</div>
            <span class="brand-text">Med<span>RAG</span></span>
        </div>
        <div class="nav-links">{links}</div>
    </div>
    """, unsafe_allow_html=True)


render_navbar(page)


# ══════════════════════════════════════════
# HOME
# ══════════════════════════════════════════
if page == "home":
    st.markdown("""
    <div class="page-wrap">
      <div class="creator-banner">
        <div class="creator-avatar">SB</div>
        <div>
          <div class="creator-greeting">✦ Built with passion by</div>
          <div class="creator-name">Sanskruti Bidve</div>
          <div class="creator-desc">
            I'm a 3rd-year Diploma student in <strong>Information Technology</strong>
            at Government Polytechnic, Nashik. This is my <strong>first RAG-based AI project</strong> —
            a medical chatbot that uses real WHO data to answer health questions intelligently.
            I built this because I believe AI should make healthcare knowledge accessible to everyone,
            not just those with access to doctors.
          </div>
          <div class="creator-tags">
            <span class="ctag">🎓 Diploma – Information Technology</span>
            <span class="ctag">📍 Nashik, Maharashtra</span>
            <span class="ctag">🤖 AI / ML Enthusiast</span>
            <span class="ctag">🐍 Python Developer</span>
          </div>
        </div>
      </div>

      <div class="section-chip">💡 Why This Project?</div>
      <div class="two-col">
        <div class="info-card problem">
          <div class="info-card-title"><span>⚠️</span> The Problem</div>
          <p>Every day, millions of people search online for health answers. The results are
          often unreliable, full of ads, or too technical to understand.</p>
          <p>Doctors cannot realistically answer every question. With a global average of
          <strong>1 doctor per 1,000 people</strong> (WHO data), the gap between medical
          knowledge and public access is enormous.</p>
          <p>People often avoid asking what they feel are "stupid" questions, leading to
          delayed care or unnecessary anxiety.</p>
          <div class="stat-pills">
            <span class="stat-pill red">1:1000 doctor-patient ratio</span>
            <span class="stat-pill red">Misinformation online</span>
            <span class="stat-pill red">No 24/7 access</span>
          </div>
        </div>
        <div class="info-card solution">
          <div class="info-card-title"><span>✅</span> The Solution</div>
          <p><strong>MedRAG</strong> is a conversational AI assistant trained on trusted
          <strong>WHO</strong> documents. It answers medical questions accurately,
          24/7, in plain language — without judgment.</p>
          <p>Instead of hallucinating answers, it uses <strong>Retrieval-Augmented Generation</strong>
          to first find the most relevant paragraphs from verified sources, then generate
          a grounded response.</p>
          <p>Think of it as a knowledgeable medical reference at your fingertips —
          not replacing doctors, but empowering you before or between consultations.</p>
          <div class="stat-pills">
            <span class="stat-pill">WHO-sourced data</span>
            <span class="stat-pill">24/7 availability</span>
            <span class="stat-pill">No hallucinations</span>
          </div>
        </div>
      </div>

      <div class="rag-section">
        <div class="section-chip">🔍 The Technology</div>
        <div class="rag-title">What is Retrieval-Augmented Generation?</div>
        <div class="rag-desc">
          RAG combines a <strong>search engine</strong> and a <strong>language model</strong>.
          Instead of the AI guessing from memory, it first retrieves relevant information from
          a trusted document database, then uses that context to generate a precise, grounded answer.
          This makes it dramatically more reliable for domains like medicine, where accuracy is everything.
        </div>
        <div class="rag-steps">
          <div class="rag-step">
            <div class="rag-step-num">1</div>
            <div class="rag-step-label">You Ask</div>
            <div class="rag-step-desc">Type your medical question in plain language</div>
          </div>
          <div class="rag-step">
            <div class="rag-step-num">2</div>
            <div class="rag-step-label">Embed & Search</div>
            <div class="rag-step-desc">Query converted to vector and matched to WHO docs</div>
          </div>
          <div class="rag-step">
            <div class="rag-step-num">3</div>
            <div class="rag-step-label">Retrieve Context</div>
            <div class="rag-step-desc">Most relevant document chunks are fetched</div>
          </div>
          <div class="rag-step">
            <div class="rag-step-num">4</div>
            <div class="rag-step-label">Gemma Responds</div>
            <div class="rag-step-desc">Local LLM reads context and generates your answer</div>
          </div>
        </div>
      </div>

      <div class="cta-wrap">
        <a class="cta-link" href="?page=chatbot">🩺 Try the Chatbot</a>
      </div>

    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════
elif page == "about":
    st.markdown("""
    <div class="page-wrap">
      <div class="page-header">
        <div class="section-chip">📋 Project Details</div>
        <div class="page-header-title">About MedRAG</div>
        <div class="page-header-sub">
          A deep dive into every component, tool, and design decision that went into
          building this AI-powered medical assistant.
        </div>
      </div>

      <div class="about-section-title">🛠️ Tools & Technologies Used</div>
      <div class="tool-grid">
        <div class="tool-card">
          <div class="tool-icon">🦙</div>
          <div class="tool-name">Gemma (LLM)</div>
          <div class="tool-desc">Google's open-source language model that powers response generation.
          Reads retrieved medical context and produces clear answers —
          runs fully locally with no internet required.</div>
          <span class="tool-badge">Core LLM</span>
        </div>
        <div class="tool-card">
          <div class="tool-icon">🗄️</div>
          <div class="tool-name">Supabase Vector DB</div>
          <div class="tool-desc">Stores document embeddings and conversation history.
          Finds semantically similar chunks from WHO medical documents
          using cosine similarity search via pgvector.</div>
          <span class="tool-badge">Retrieval Layer</span>
        </div>
        <div class="tool-card">
          <div class="tool-icon">🔢</div>
          <div class="tool-name">Sentence Embeddings</div>
          <div class="tool-desc">Converts documents and queries into high-dimensional vectors
          using all-MiniLM-L6-v2. Enables semantic search — finding results
          by meaning, not just keyword matching.</div>
          <span class="tool-badge">Embedding Model</span>
        </div>
        <div class="tool-card">
          <div class="tool-icon">⚡</div>
          <div class="tool-name">Semantic Cache</div>
          <div class="tool-desc">Caches approved answers (thumbs up) in Supabase.
          Similar follow-up questions are served from cache instantly —
          saving LLM inference time and improving speed.</div>
          <span class="tool-badge">Performance Layer</span>
        </div>
        <div class="tool-card">
          <div class="tool-icon">🌐</div>
          <div class="tool-name">Streamlit</div>
          <div class="tool-desc">Python-native web framework used to build the entire interface —
          landing pages, navigation, chat UI, and file upload —
          without writing any separate JavaScript code.</div>
          <span class="tool-badge">Frontend</span>
        </div>
        <div class="tool-card">
          <div class="tool-icon">🏥</div>
          <div class="tool-name">WHO Data Sources</div>
          <div class="tool-desc">All medical knowledge is sourced from official
          World Health Organization documents — ensuring accuracy, credibility,
          and up-to-date global health standards.</div>
          <span class="tool-badge">Knowledge Base</span>
        </div>
      </div>

      <div class="about-section-title">✨ Key Features</div>
      <div class="feature-list">
        <div class="feature-item">
          <div class="feature-dot"></div>
          <div class="feature-text">
            <strong>Context-based response generation</strong>
            Answers always grounded in retrieved WHO document chunks, not AI imagination.
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-dot"></div>
          <div class="feature-text">
            <strong>Thumbs up/down feedback</strong>
            Only approved answers get stored in Supabase — bad answers are never cached.
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-dot"></div>
          <div class="feature-text">
            <strong>Regenerate answers</strong>
            Force the LLM to think again — replaces old cached answers with fresh ones.
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-dot"></div>
          <div class="feature-text">
            <strong>Custom document upload</strong>
            Upload your own PDF or TXT files — chunked, embedded and added to the knowledge base.
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-dot"></div>
          <div class="feature-text">
            <strong>Local LLM — fully offline capable</strong>
            Gemma runs locally, so no sensitive health queries leave your machine.
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-dot"></div>
          <div class="feature-text">
            <strong>Trusted knowledge only</strong>
            Strictly limited to WHO-sourced data — no blogs, no social media, no unverified sources.
          </div>
        </div>
      </div>

      <div class="about-section-title">⚠️ Limitations</div>
      <div class="limitation-card">
        <span>🚫</span>
        <span><strong>Not a replacement for professional medical advice.</strong>
        For informational purposes only. Always consult a licensed doctor for diagnosis and treatment.</span>
      </div>
      <div class="limitation-card">
        <span>📄</span>
        <span><strong>Bounded by the knowledge base.</strong>
        Questions outside the uploaded WHO document scope may not be answered accurately.</span>
      </div>
      <div class="limitation-card">
        <span>🌍</span>
        <span><strong>English only (currently).</strong>
        Processes and responds in English only. Multilingual support is a future enhancement.</span>
      </div>
      <div class="limitation-card">
        <span>⚙️</span>
        <span><strong>Hardware dependent.</strong>
        Running Gemma locally requires a reasonably capable machine.</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# ARCHITECTURE
# ══════════════════════════════════════════
elif page == "architecture":

    # Load image as base64 to embed directly in HTML
    img_path = r"C:\Users\User\OneDrive\Desktop\medical_rag_db\image.jpg"
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        img_tag = f'<img src="data:image/jpeg;base64,{img_data}" style="width:65%;display:block;margin:20px auto;border-radius:12px;" />'
    else:
        img_tag = '<div style="background:#071828;border:1.5px dashed rgba(15,207,153,0.3);border-radius:16px;padding:40px;text-align:center;color:#3d5f75;font-size:14px;">🖼️ Image not found — place image.jpg in project folder</div>'

    st.markdown(f"""
    <div class="page-wrap">
      <div class="page-header">
        <div class="section-chip">🏗️ System Design</div>
        <div class="page-header-title">Architecture</div>
        <div class="page-header-sub">
          How MedRAG works under the hood — from your question to a verified medical answer.
        </div>
      </div>

      <div class="about-section-title">🖼️ System Architecture Diagram</div>
      {img_tag}

      <div class="about-section-title">🔄 RAG Pipeline — Step by Step</div>
      <div class="arch-flow">
        <div class="arch-box"><div class="arch-box-num">1</div><div class="arch-box-name">User Query</div><div class="arch-box-sub">Question entered</div></div>
        <div class="arch-arrow">›</div>
        <div class="arch-box"><div class="arch-box-num">2</div><div class="arch-box-name">Cache Check</div><div class="arch-box-sub">Semantic cache lookup</div></div>
        <div class="arch-arrow">›</div>
        <div class="arch-box hl"><div class="arch-box-num">3</div><div class="arch-box-name">Embed Query</div><div class="arch-box-sub">Convert to vector</div></div>
        <div class="arch-arrow">›</div>
        <div class="arch-box hl"><div class="arch-box-num">4</div><div class="arch-box-name">Vector Search</div><div class="arch-box-sub">Find top-K chunks</div></div>
        <div class="arch-arrow">›</div>
        <div class="arch-box"><div class="arch-box-num">5</div><div class="arch-box-name">Build Prompt</div><div class="arch-box-sub">Inject context</div></div>
        <div class="arch-arrow">›</div>
        <div class="arch-box"><div class="arch-box-num">6</div><div class="arch-box-name">Gemma LLM</div><div class="arch-box-sub">Generate answer</div></div>
        <div class="arch-arrow">›</div>
        <div class="arch-box"><div class="arch-box-num">7</div><div class="arch-box-name">Response</div><div class="arch-box-sub">Display + cache</div></div>
      </div>

      <div class="about-section-title">⚙️ Technology Stack</div>
      <div class="tech-stack">
        <div class="tech-item"><div class="tech-item-icon">🦙</div><div class="tech-item-name">Gemma</div><div class="tech-item-role">Language Model</div></div>
        <div class="tech-item"><div class="tech-item-icon">🔢</div><div class="tech-item-name">Sentence Transformers</div><div class="tech-item-role">Embedding Model</div></div>
        <div class="tech-item"><div class="tech-item-icon">🗄️</div><div class="tech-item-name">Supabase</div><div class="tech-item-role">Vector DB</div></div>
        <div class="tech-item"><div class="tech-item-icon">🐍</div><div class="tech-item-name">Python + Streamlit</div><div class="tech-item-role">Backend & UI</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# CHATBOT — 100% pure Streamlit, zero iframes
# ══════════════════════════════════════════
elif page == "chatbot":

    from rag_chat import chat, store_conversation, replace_conversation, get_existing_conversation, update_feedback
    import PyPDF2
    import io

    st.markdown("""
    <div class="page-wrap">
      <div class="page-header">
        <div class="section-chip">🩺 Live Assistant</div>
        <div class="page-header-title">Medical AI Chatbot</div>
        <div class="page-header-sub">
          Ask any medical question. Answers generated from WHO-verified documents using Gemma + RAG.
        </div>
      </div>
      <div class="chat-notice">
        ⚕️ This assistant is for <strong>informational purposes only</strong>.
        Always consult a licensed healthcare provider.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Document Upload ──
    with st.expander("📁 Upload Your Own Document to the Knowledge Base", expanded=False):
        st.markdown("<p style='font-size:13px;color:#7a9ab5;'>Upload a PDF or TXT file to add to the knowledge base alongside WHO data.</p>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Choose a PDF or TXT file (max 20MB)", type=["pdf", "txt"], label_visibility="collapsed")

        if uploaded_file is not None:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 20:
                st.error("❌ File too large! Please upload a file under 20MB.")
            else:
                st.info(f"📄 **{uploaded_file.name}** — {file_size_mb:.1f} MB")
                if st.button("🚀 Process & Add to Knowledge Base"):
                    with st.spinner("Reading file..."):
                        if uploaded_file.type == "application/pdf":
                            try:
                                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                                text = ""
                                for p in pdf_reader.pages:
                                    text += p.extract_text() or ""
                            except Exception as e:
                                st.error(f"❌ Could not read PDF: {e}")
                                text = ""
                        else:
                            text = uploaded_file.read().decode("utf-8", errors="ignore")

                    if text.strip():
                        from rag_chat import process_custom_document
                        progress_bar = st.progress(0, text="Starting...")
                        words = text.split()
                        total_chunks = max(1, len(words) // 400)
                        progress_bar.progress(20, text=f"Splitting into ~{total_chunks} chunks...")
                        try:
                            stored = process_custom_document(text, source_name=uploaded_file.name.replace(" ", "_"))
                            progress_bar.progress(100, text="Done!")
                            st.success(f"✅ Added **{stored} chunks** from **{uploaded_file.name}** to the knowledge base!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error processing document: {e}")
                    else:
                        st.warning("⚠️ Could not extract any text from this file.")

    st.markdown("---")

    # ── Session state ──
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Hello! I'm MedRAG, your AI medical assistant powered by WHO documents and Gemma. Ask me any health-related question!",
            "stored": True, "embedding": None, "from_cache": False
        })

    # ── Render messages ──
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

            if msg["role"] == "assistant" and not msg.get("stored", False):
                col1, col2, col3, col4 = st.columns([1, 1, 1, 6])

                with col1:
                    if not msg.get("from_cache", False):
                        if st.button("👍", key=f"up_{i}", help="Save this answer"):
                            question = st.session_state.messages[i - 1]["content"]
                            existing = get_existing_conversation(question)
                            if existing:
                                replace_conversation(question, msg["content"])
                            else:
                                store_conversation(question, msg["content"], msg["embedding"])
                            st.session_state.messages[i]["stored"] = True
                            st.success("✅ Saved!")
                            st.rerun()

                with col2:
                    if not msg.get("from_cache", False):
                        if st.button("👎", key=f"down_{i}", help="Discard this answer"):
                            st.session_state.messages[i]["stored"] = True
                            st.warning("❌ Discarded.")
                            st.rerun()

                with col3:
                    if st.button("🔄", key=f"regen_{i}", help="Regenerate"):
                        question = st.session_state.messages[i - 1]["content"]
                        with st.spinner("Regenerating..."):
                            new_answer, new_embedding, _ = chat(question, force_regenerate=True)
                        st.session_state.messages[i] = {
                            "role": "assistant", "content": new_answer,
                            "stored": False, "embedding": new_embedding, "from_cache": False
                        }
                        st.rerun()

            if msg["role"] == "assistant" and msg.get("from_cache", False):
                st.caption("⚡ Retrieved from semantic cache")

    # ── Input ──
    user_input = st.chat_input("Ask your medical question here…")

    if user_input:
        st.session_state.messages.append({
            "role": "user", "content": user_input,
            "stored": True, "embedding": None, "from_cache": False
        })
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving from knowledge base..."):
                response, embedding, from_cache = chat(user_input)
                st.write(response)

        st.session_state.messages.append({
            "role": "assistant", "content": response,
            "stored": False, "embedding": embedding, "from_cache": from_cache
        })
        st.rerun()