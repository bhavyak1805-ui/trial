import streamlit as st
from db import get_conn        


def render_dashboard():
    user    = st.session_state.current_user
    profile = st.session_state.profile
    name    = user["full_name"]

    # ── Welcome banner ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px solid #6c63ff44;
                border-radius:20px;padding:2rem;margin-bottom:1.5rem;
                position:relative;overflow:hidden;">
      <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
                  background:radial-gradient(circle,#6c63ff22,transparent);
                  border-radius:50%;"></div>
      <div style="font-size:0.7rem;font-family:'JetBrains Mono',monospace;color:#6c63ff;
                  letter-spacing:3px;text-transform:uppercase;margin-bottom:0.4rem;">
        Student Help Desk
      </div>
      <div style="font-size:2rem;font-weight:700;line-height:1.2;">
        Welcome back,
        <span style="background:linear-gradient(135deg,#6c63ff,#ff6584);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          {name}
        </span> 👋
      </div>
      <div style="color:#666680;font-size:0.85rem;margin-top:0.5rem;">
        {user.get('email','')} &nbsp;·&nbsp;
        {user.get('target_role','') or 'Set your target role'} &nbsp;·&nbsp;
        {user.get('city','') or ''}{', ' + user.get('state','') if user.get('state') else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick stats ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("🎓", "Education",  len(profile.get("education",  [])), "entries"),
        ("🛠️", "Skills",     len(profile.get("skills",     [])), "added"),
        ("💼", "Experience", len(profile.get("experience", [])), "entries"),
        ("🚀", "Projects",   len(profile.get("projects",   [])), "added"),
    ]
    for col, (icon, label, val, unit) in zip([c1, c2, c3, c4], stats):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:1rem;">
              <div style="font-size:1.8rem;">{icon}</div>
              <div style="font-size:1.6rem;font-weight:700;color:#6c63ff;">{val}</div>
              <div style="font-size:0.72rem;color:#666680;">{label} {unit}</div>
            </div>""", unsafe_allow_html=True)

    # ── Module grid ───────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.7rem;font-family:'JetBrains Mono',monospace;color:#6c63ff;
                letter-spacing:3px;text-transform:uppercase;margin:1.2rem 0 0.8rem;">
      Modules
    </div>""", unsafe_allow_html=True)

    modules = [
        {"icon": "🎯", "title": "Career Guidance",
         "desc": "Explore career paths, aptitude tests & counselling tailored to your profile.",
         "color": "#6c63ff", "key": "career"},
        {"icon": "📄", "title": "AI Resume Maker",
         "desc": "Build a professional ATS-friendly resume from your profile data.",
         "color": "#ff6584", "key": "resume"},
        {"icon": "🤖", "title": "AI Chatbot — Aria",
         "desc": "Ask anything — career guidance, resume tips, interview prep, skill advice.",
         "color": "#06b6d4", "key": "chatbot"},
        {"icon": "📁", "title": "Documents",
         "desc": "Upload, manage & verify academic certificates and identity documents.",
         "color": "#22c55e", "key": "docs"},
        {"icon": "🛠️", "title": "Vocational Training",
         "desc": "Browse skill-based training programs, workshops & certification courses.",
         "color": "#f59e0b", "key": "training"},
        {"icon": "🏢", "title": "Placement",
         "desc": "View job listings, company visits, interview prep & placement stats.",
         "color": "#a855f7", "key": "placement"},
    ]

    col_a, col_b = st.columns(2)
    for idx, mod in enumerate(modules):
        col = col_a if idx % 2 == 0 else col_b
        with col:
            st.markdown(f"""
            <div class="module-card">
              <div style="position:absolute;top:0;left:0;width:4px;height:100%;
                          background:{mod['color']};border-radius:4px 0 0 4px;"></div>
              <div style="font-size:1.8rem;margin-bottom:0.4rem;">{mod['icon']}</div>
              <div style="font-weight:600;font-size:0.95rem;margin-bottom:0.3rem;">
                {mod['title']}
              </div>
              <div style="color:#666680;font-size:0.78rem;line-height:1.5;">
                {mod['desc']}
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Open {mod['title']}", key=f"open_{mod['key']}"):
                if mod["key"] in ("resume", "chatbot"):
                    st.session_state.active_module = mod["key"]
                    st.rerun()
                else:
                    st.info(f"🚧 **{mod['title']}** — Coming soon!")

    # ── Profile card + recent logins ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    pc, lc = st.columns([1, 2])

    with pc:
        st.markdown(f"""
        <div class="card">
          <div class="card-header">My Profile</div>
          <div style="font-size:0.82rem;line-height:2.2;">
            👤 <b>{user.get('full_name','')}</b><br>
            📧 {user.get('email','')}<br>
            📱 {user.get('phone') or '—'}<br>
            🎯 {user.get('target_role') or '—'}<br>
            📍 {user.get('city','')}{', '+user.get('state','') if user.get('state') else ''}<br>
            📅 Since {str(user.get('created_at',''))[:10]}
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("✏️ Edit Profile", key="edit_profile_btn"):
            try:
                conn = get_conn(); cur = conn.cursor()
                cur.execute("UPDATE users SET profile_completed=FALSE WHERE user_id=%s",
                            (user["user_id"],))
                conn.commit(); conn.close()
            except:
                pass
            st.session_state.current_user["profile_completed"] = False
            st.session_state.onboarding_step = 1
            st.rerun()

    with lc:
        try:
            conn = get_conn(); cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT login_method, login_time, login_status "
                "FROM login_history WHERE user_id=%s "
                "ORDER BY login_time DESC LIMIT 6",
                (user["user_id"],))
            rows = cur.fetchall(); conn.close()
            st.markdown('<div class="card"><div class="card-header">Recent Logins</div>',
                        unsafe_allow_html=True)
            if rows:
                for r in rows:
                    bc = "#22c55e" if r["login_status"] == "success" else "#ef4444"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:0.45rem 0;border-bottom:1px solid #2a2a38;font-size:0.78rem;">
                      <span style="color:#888;">{str(r['login_time'])[:16]}</span>
                      <span class="badge">{r['login_method']}</span>
                      <span style="background:{bc}22;color:{bc};border:1px solid {bc}44;
                                   border-radius:20px;padding:1px 8px;font-size:0.68rem;">
                        {r['login_status']}
                      </span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#666680;font-size:0.82rem;">No history yet.</div>',
                            unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        except:
            pass

    # ── Logout ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.logged_in     = False
        st.session_state.current_user  = None
        st.session_state.profile       = {"loaded": False}
        st.session_state.active_module = None
        st.rerun()