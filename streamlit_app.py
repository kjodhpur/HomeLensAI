"""HomeLens AI: Business Risk Command Center.

Run with:  streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from app.config import APP_NAME, APP_TAGLINE, ASSETS_DIR, NOTEBOOK_FACTS
from app.data_loader import missing_artifacts
from app.model_loader import get_active_model
from app.ui_components import fmt_threshold, inject_css, render_html
from views import (
    executive_overview,
    model_performance,
    provider_monitor,
    responsible_ai,
    review_analyzer,
)

st.set_page_config(
    page_title=f"{APP_NAME} · {APP_TAGLINE}",
    page_icon=str(ASSETS_DIR / "logo_mark.svg"),
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
st.logo(str(ASSETS_DIR / "logo.svg"), icon_image=str(ASSETS_DIR / "logo_mark.svg"), size="large")

missing = missing_artifacts()
if missing:
    st.error(
        "The dashboard artifacts are not available: " + ", ".join(missing)
        + ". Run `python scripts/build_artifacts.py` or copy the notebook's "
        "HomeLensAI_outputs files into `artifacts/`."
    )
    st.stop()

responsible_page = st.Page(responsible_ai.render, title="Responsible AI", icon=":material/verified_user:", url_path="responsible-ai")
pages = {
    "Command center": [
        st.Page(executive_overview.render, title="Executive Overview", icon=":material/space_dashboard:",
                default=True),
        st.Page(review_analyzer.render, title="Review Analyzer", icon=":material/rate_review:", url_path="analyzer"),
        st.Page(provider_monitor.render, title="Provider Monitor", icon=":material/monitoring:", url_path="providers"),
    ],
    "Evidence & governance": [
        st.Page(model_performance.render, title="Model Performance", icon=":material/insights:", url_path="models"),
        responsible_page,
    ],
}
navigation = st.navigation(pages, position="sidebar")

model = get_active_model()
with st.sidebar:
    status_color = "#3DDC84" if model.is_primary else "#FAB219"
    status_label = "DistilBERT online" if model.is_primary else "TF–IDF fallback"
    render_html(
        f"""
        <div class="hl-side-card">
          <div class="hl-side-k">Model status</div>
          <div class="hl-side-status"><i style="background:{status_color};color:{status_color}66"></i>{status_label}</div>
          <div class="hl-side-sub">{model.name} · threshold {fmt_threshold(model.threshold)}</div>
          <div class="hl-side-sub">{model.status_note}</div>
        </div>
        <div class="hl-side-card">
          <div class="hl-side-k">Data scope</div>
          <div class="hl-side-row"><span>Market</span><b>{NOTEBOOK_FACTS['market']}</b></div>
          <div class="hl-side-row"><span>Reviews</span><b>{NOTEBOOK_FACTS['core_reviews']:,}</b></div>
          <div class="hl-side-row"><span>Providers</span><b>{NOTEBOOK_FACTS['providers']:,}</b></div>
          <div class="hl-side-row"><span>Period</span><b>{NOTEBOOK_FACTS['date_start']} – {NOTEBOOK_FACTS['date_end']}</b></div>
        </div>
        """
    )
    st.page_link(responsible_page, label="Responsible-use guidelines", icon=":material/policy:")
    st.caption("Review-based risk signals for human investigation. Not a verdict on any business.")

navigation.run()
