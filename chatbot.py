import streamlit as st
from db import get_conn


QUICK_PROMPTS = [
    "What jobs suit my skills?",
    "How do I improve my resume?",
    "Interview tips for my target role",
    "What skills should I learn next?",
    "Suggest free courses for me",
    "How to prepare for placements?",
    "Write a cold email to a recruiter",
    "What certifications should I do?",
    "How do I negotiate salary?",
    "Review my career roadmap",
]


def get_system_prompt(user, profile):
    skills  = profile.get("skills", [])
    edu     = profile.get("education", [])
    exp     = profile.get("experience", [])
    proj    = profile.get("projects", [])
    certs   = profile.get("certifications", [])

    return f"""You are Aria, a smart and friendly AI assistant for the Student Help Desk portal.
You help students with career advice, resume tips, skill guidance, interview preparation,
placement queries, vocational training suggestions, and general academic support.

Student Profile:
- Name: {user.get('full_name', 'Student')}
- Target Role: {user.get('target_role', 'Not specified')}
- Experience Level: {user.get('experience_level', 'Fresher')}
- Location: {user.get('city', '')}, {user.get('state', '')}
- Skills: {', '.join([s['skill_name'] for s in skills]) or 'not specified'}
- Education: {'; '.join([e['degree']+' from '+e['institution'] for e in edu]) or 'not specified'}
- Experience: {'; '.join([e['role']+' at '+e['company'] for e in exp]) or 'None yet'}
- Projects: {'; '.join([p['title'] for p in proj]) or 'None listed'}
- Certifications: {'; '.join([c['name'] for c in certs]) or 'None listed'}

Guidelines:
- Always personalise answers using the student's profile above.
- Be encouraging, concise, and practical.
- For career advice, suggest roles matching their skills and education.
- For interview prep, tailor to their target role.
- For skill gaps, suggest specific resources (Coursera, NPTEL, YouTube, etc.).
- Keep responses under 300 words unless detail is needed.
- Use bullet points for readability.
- End with a helpful follow-up question or next step.
"""


def call_claude(messages, system_prompt, api_key):
    import anthropic
    client   = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text


def save_chat(user_id, role, message):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO chat_history (user_id,role,message) VALUES (%s,%s,%s)",
                    (user_id, role, message))
        conn.commit(); conn.close()
    except: pass


def load_chat(user_id, limit=50):
    try:
        conn = get_conn(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT role,message FROM chat_history WHERE user_id=%s "
                    "ORDER BY created_at DESC LIMIT %s", (user_id, limit))
        rows = cur.fetchall(); conn.close()
        return list(reversed(rows))
    except: return []


def render_chatbot():
    user    = st.session_state.current_user
    profile = st.session_state.profile

    # ── Banner ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d0d18 0%,#0d1a1f 100%);
                border:1px solid #22d3ee22;border-radius:24px;padding:2rem 2.5rem;
                margin-bottom:1.5rem;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-50px;right:-50px;width:200px;height:200px;
                  background:radial-gradient(circle,#22d3ee18,transparent);border-radius:50%;"></div>
      <div style="font-size:0.62rem;font-family:'JetBrains Mono',monospace;
                  color:#22d3ee;letter-spacing:3px;text-transform:uppercase;">
        Student Help Desk · Module
      </div>
      <div style="font-size:2rem;font-weight:800;margin:0.3rem 0 0.2rem;
                  background:linear-gradient(135deg,#f0f0fa,#67e8f9);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🤖 Aria — AI Assistant
      </div>
      <div style="color:#606080;font-size:0.85rem;">
        Powered by Claude · Knows your profile · Always personalised
      </div>
    </div>""", unsafe_allow_html=True)

    # ── API Key ───────────────────────────────────────────────────────────
    if "anthropic_api_key" not in st.session_state:
        st.session_state.anthropic_api_key = ""

    with st.expander("🔑 Anthropic API Key (required once per session)",
                     expanded=not st.session_state.anthropic_api_key):
        key_inp = st.text_input("Anthropic API Key", value=st.session_state.anthropic_api_key,
                                type="password", placeholder="sk-ant-...", key="api_key_field",
                                help="Get your key at console.anthropic.com")
        if key_inp:
            st.session_state.anthropic_api_key = key_inp
            st.success("✅ API key saved for this session.")

    if not st.session_state.anthropic_api_key:
        st.warning("⚠️ Enter your Anthropic API key above to start chatting.")
        if st.button("← Back to Dashboard", key="back_chat_nokey"):
            st.session_state.active_module = None; st.rerun()
        st.stop()

    # ── Init chat ─────────────────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        saved = load_chat(user["user_id"])
        if saved:
            st.session_state.chat_messages = [
                {"role": m["role"], "content": m["message"]} for m in saved]
        else:
            skills_preview = ", ".join([s["skill_name"] for s in profile.get("skills",[])[:3]])
            welcome = (
                f"Hi **{user['full_name'].split()[0]}**! 👋 I'm **Aria**, your AI assistant.\n\n"
                f"I can see you're targeting **{user.get('target_role','a great career')}** "
                f"{'and have skills in **'+skills_preview+'**' if skills_preview else ''}.\n\n"
                f"How can I help you today?\n"
                f"- 🎯 Career paths & roadmaps\n"
                f"- 📄 Resume & cover letter tips\n"
                f"- 🧠 Interview preparation\n"
                f"- 📚 Skill recommendations\n"
                f"- 🏢 Placement & job search strategies"
            )
            st.session_state.chat_messages = [{"role":"assistant","content":welcome}]

    # ── Layout ────────────────────────────────────────────────────────────
    chat_col, side_col = st.columns([3, 1])

    with side_col:
        st.markdown('<div class="card"><div class="card-header">Quick Prompts</div>',
                    unsafe_allow_html=True)
        for prompt in QUICK_PROMPTS:
            if st.button(prompt, key=f"qp_{prompt[:20]}"):
                st.session_state.chat_messages.append({"role":"user","content":prompt})
                with st.spinner("Aria is thinking..."):
                    try:
                        reply = call_claude(
                            messages=st.session_state.chat_messages,
                            system_prompt=get_system_prompt(user, profile),
                            api_key=st.session_state.anthropic_api_key)
                        st.session_state.chat_messages.append({"role":"assistant","content":reply})
                        save_chat(user["user_id"],"user",prompt)
                        save_chat(user["user_id"],"assistant",reply)
                    except Exception as ex:
                        st.session_state.chat_messages.append({
                            "role":"assistant","content":f"❌ Error: {ex}"})
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Profile snapshot
        skills_prev = [s["skill_name"] for s in profile.get("skills",[])[:5]]
        st.markdown(f"""
        <div class="card">
          <div class="card-header">Your Profile</div>
          <div style="font-size:0.78rem;line-height:2;color:#a0a0c0;">
            🎯 {user.get('target_role','—')}<br>
            📍 {user.get('city','')}, {user.get('state','')}<br>
            💼 {user.get('experience_level','Fresher')}
          </div>
          <div style="margin-top:6px;">
            {''.join([f'<span class="skill-chip" style="font-size:0.65rem;">{s}</span>' for s in skills_prev])}
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.chat_messages = []
            try:
                conn = get_conn(); cur = conn.cursor()
                cur.execute("DELETE FROM chat_history WHERE user_id=%s",(user["user_id"],))
                conn.commit(); conn.close()
            except: pass
            st.rerun()

    with chat_col:
        # Chat display
        st.markdown("""
        <div style="background:var(--surface2);border:1px solid var(--border2);
                    border-radius:16px;padding:1rem;margin-bottom:1rem;
                    max-height:500px;overflow-y:auto;">""", unsafe_allow_html=True)

        for msg in st.session_state.chat_messages:
            is_user = msg["role"] == "user"
            bg      = "#1a1a2e" if not is_user else "#7c6fff18"
            border  = "#7c6fff33" if not is_user else "#7c6fff66"
            align   = "flex-end"  if is_user    else "flex-start"
            avatar  = "👤" if is_user else "🤖"
            nm      = user["full_name"].split()[0] if is_user else "Aria"
            nc      = "#7c6fff" if not is_user else "#ff6b9d"

            content = msg["content"].replace("\n","<br>")
            # bold
            import re as _re
            content = _re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)

            st.markdown(f"""
            <div style="display:flex;justify-content:{align};margin-bottom:1rem;">
              <div style="max-width:82%;background:{bg};border:1px solid {border};
                          border-radius:14px;padding:0.8rem 1rem;">
                <div style="font-size:0.68rem;color:{nc};font-family:'JetBrains Mono',monospace;
                            margin-bottom:0.3rem;">{avatar} {nm}</div>
                <div style="font-size:0.85rem;line-height:1.7;color:#e8e8f0;">{content}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Input
        inp_col, btn_col = st.columns([5, 1])
        with inp_col:
            user_input = st.text_input("", placeholder="Ask Aria anything...",
                                       key="chat_input", label_visibility="collapsed")
        with btn_col:
            send = st.button("Send ➤", key="chat_send")

        if send and user_input.strip():
            st.session_state.chat_messages.append({"role":"user","content":user_input.strip()})
            with st.spinner("Aria is thinking..."):
                try:
                    reply = call_claude(
                        messages=st.session_state.chat_messages,
                        system_prompt=get_system_prompt(user, profile),
                        api_key=st.session_state.anthropic_api_key)
                    st.session_state.chat_messages.append({"role":"assistant","content":reply})
                    save_chat(user["user_id"],"user",user_input.strip())
                    save_chat(user["user_id"],"assistant",reply)
                except Exception as ex:
                    st.session_state.chat_messages.append({
                        "role":"assistant",
                        "content":f"❌ Error: {ex}\n\nCheck your API key."})
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key="back_chatbot"):
        st.session_state.active_module = None; st.rerun()