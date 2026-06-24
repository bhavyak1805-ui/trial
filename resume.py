import streamlit as st
import re
from io import BytesIO
from db import get_conn


TEMPLATES = {
    "Modern":    "#7c6fff",
    "Classic":   "#1e3a5f",
    "Executive": "#1a1a1a",
    "Creative":  "#e91e63",
    "Tech":      "#00897b",
}


def build_summary(user, skills):
    sk = ", ".join([s["skill_name"] for s in skills[:5]]) if skills else "various technologies"
    return (
        f"Motivated {user.get('experience_level','fresher')} professional targeting "
        f"{user.get('target_role','Software Engineer')} roles. "
        f"Proficient in {sk}. "
        f"Based in {user.get('city','')}, {user.get('state','')}. "
        f"Passionate about building impactful, scalable solutions."
    )

def resume_strength(user, edu, skills, exp, proj, certs, ach):
    checks = [
        (bool(user.get("full_name")), 10, "Name"),
        (bool(user.get("about_me")),  15, "Summary"),
        (bool(edu),   20, "Education"),
        (bool(skills),20, "Skills"),
        (bool(exp),   15, "Experience"),
        (bool(proj),  10, "Projects"),
        (bool(certs),  7, "Certifications"),
        (bool(ach),    3, "Achievements"),
    ]
    score   = sum(pts for ok, pts, _ in checks if ok)
    done    = [lbl for ok, pts, lbl in checks if ok]
    missing = [lbl for ok, pts, lbl in checks if not ok]
    return score, done, missing

def ats_check(resume_text, jd):
    stop = {"and","the","or","for","with","that","this","are","from","have","will","you",
            "our","your","they","been","has","not","can","all","also","more","than","but",
            "was","were","must","should","able","work","using","use","used"}
    def kw(t):
        words = re.findall(r'\b[a-zA-Z][a-zA-Z+#.]{1,}\b', t.lower())
        return set(w for w in words if w not in stop and len(w)>2)
    rw = kw(resume_text); jw = kw(jd)
    matched = rw & jw; missing = jw - rw
    score   = round(len(matched)/max(len(jw),1)*100, 1)
    return score, sorted(matched)[:30], sorted(missing)[:30]


def generate_pdf(user, edu, exp, proj, skills, certs, ach, summary, role, template):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    HRFlowable, Table, TableStyle)
    from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=1.8*cm, leftMargin=1.8*cm,
                            topMargin=1.5*cm,  bottomMargin=1.5*cm)

    themes = {
        "Modern":    {"accent":"#7c6fff","dark":"#1a1a2e","mid":"#4a4a6a"},
        "Classic":   {"accent":"#1e3a5f","dark":"#0f1f35","mid":"#4a6080"},
        "Executive": {"accent":"#1a1a1a","dark":"#000000","mid":"#555555"},
        "Creative":  {"accent":"#e91e63","dark":"#1a0a14","mid":"#7b3050"},
        "Tech":      {"accent":"#00897b","dark":"#00251a","mid":"#2e7d68"},
    }
    th     = themes.get(template, themes["Modern"])
    ACCENT = colors.HexColor(th["accent"])
    DARK   = colors.HexColor(th["dark"])
    MID    = colors.HexColor(th["mid"])
    MGRAY  = colors.HexColor("#888899")

    def sty(name, **kw): return ParagraphStyle(name, **kw)

    name_s   = sty("N",  fontSize=24,fontName="Helvetica-Bold",textColor=DARK,  spaceAfter=2,leading=26)
    role_s   = sty("R",  fontSize=11,fontName="Helvetica",     textColor=ACCENT,spaceAfter=2,leading=14)
    cont_s   = sty("C",  fontSize=8, fontName="Helvetica",     textColor=MGRAY, spaceAfter=8,leading=12)
    sec_s    = sty("S",  fontSize=9, fontName="Helvetica-Bold",textColor=ACCENT,spaceBefore=12,spaceAfter=3,leading=12)
    sub_s    = sty("SB", fontSize=9, fontName="Helvetica-Bold",textColor=DARK,  spaceAfter=1,leading=13)
    date_s   = sty("D",  fontSize=8, fontName="Helvetica",     textColor=MGRAY, spaceAfter=1,leading=12,alignment=TA_RIGHT)
    sm_s     = sty("SM", fontSize=8, fontName="Helvetica",     textColor=MGRAY, spaceAfter=2,leading=12)
    body_s   = sty("B",  fontSize=8.5,fontName="Helvetica",    textColor=MID,   spaceAfter=2,leading=13,alignment=TA_JUSTIFY)
    bullet_s = sty("BL", fontSize=8.5,fontName="Helvetica",    textColor=MID,   spaceAfter=1,leading=13,leftIndent=10)

    def section(title):
        return [Paragraph(title.upper(), sec_s),
                HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=5)]

    def row_table(left_para, right_para):
        return Table([[left_para, right_para]], colWidths=["75%","25%"],
            style=TableStyle([
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
                ("BOTTOMPADDING",(0,0),(-1,-1),0),("TOPPADDING",(0,0),(-1,-1),0)]))

    story = []
    story.append(Paragraph(user.get("full_name","").upper(), name_s))
    story.append(Paragraph(role, role_s))
    contacts = list(filter(None,[
        user.get("email",""),user.get("phone",""),
        f"{user.get('city','')}, {user.get('state','')}".strip(", "),
        user.get("linkedin_url",""),user.get("github_url",""),user.get("portfolio_url",""),
    ]))
    story.append(Paragraph("  ·  ".join(contacts), cont_s))
    story.append(HRFlowable(width="100%", thickness=2.5, color=ACCENT, spaceAfter=6, spaceBefore=2))

    story += section("Professional Summary")
    story.append(Paragraph(summary, body_s))
    story.append(Spacer(1,4))

    if edu:
        story += section("Education")
        for e in edu:
            story.append(row_table(
                Paragraph(f"<b>{e['degree']}</b> — {e.get('field_of_study','')}", sub_s),
                Paragraph(f"{e['year_from']} – {e['year_to']}", date_s)))
            story.append(Paragraph(
                f"{e['institution']}  ·  {e.get('board_university','')}  ·  "
                f"{e['score']} {e.get('score_type','')}", sm_s))
            if e.get("coursework"):
                story.append(Paragraph(f"Coursework: {e['coursework']}", sm_s))

    if skills:
        story += section("Technical Skills")
        cats = {}
        for s in skills: cats.setdefault(s["category"],[]).append(s["skill_name"])
        for cat, lst in cats.items():
            story.append(Paragraph(f"<b>{cat}:</b>  {', '.join(lst)}", body_s))

    if exp:
        story += section("Work Experience")
        for e in exp:
            to_dt = "Present" if e["is_current"] else str(e.get("to_date",""))[:7]
            story.append(row_table(
                Paragraph(f"<b>{e['role']}</b>  ·  {e['company']}", sub_s),
                Paragraph(f"{str(e.get('from_date',''))[:7]} – {to_dt}", date_s)))
            story.append(Paragraph(e["exp_type"], sm_s))
            if e.get("description"):
                for b in [b.strip() for b in e["description"].split(".") if b.strip()]:
                    story.append(Paragraph(f"▸  {b}.", bullet_s))
            story.append(Spacer(1,3))

    if proj:
        story += section("Projects")
        for p in proj:
            story.append(Paragraph(f"<b>{p['title']}</b>", sub_s))
            story.append(Paragraph(f"Tech Stack: {p.get('tech_stack','')}", sm_s))
            if p.get("description"):
                story.append(Paragraph(p["description"], body_s))
            links = list(filter(None,[
                f"GitHub: {p['github_url']}" if p.get("github_url") else "",
                f"Live: {p['live_url']}"     if p.get("live_url")   else ""]))
            if links: story.append(Paragraph("  ·  ".join(links), sm_s))
            story.append(Spacer(1,2))

    if certs:
        story += section("Certifications")
        for c in certs:
            story.append(Paragraph(f"▸  {c['name']}  ·  {c['issuer']}  ·  {c['issue_year']}", bullet_s))

    if ach:
        story += section("Achievements & Extra-Curriculars")
        for a in ach:
            story.append(Paragraph(f"▸  {a['title']}", bullet_s))

    doc.build(story)
    buf.seek(0)
    return buf


def resume_html_preview(user, edu, exp, proj, skills, certs, ach, summary, role, theme_color):
    cats = {}
    for s in skills: cats.setdefault(s["category"],[]).append(s["skill_name"])

    edu_html  = "".join([f"""
    <div class='rv-item'>
      <div style='display:flex;justify-content:space-between;'>
        <span class='rv-title'>{e['degree']} — {e.get('field_of_study','')}</span>
        <span class='rv-date'>{e['year_from']} – {e['year_to']}</span>
      </div>
      <div class='rv-sub'>{e['institution']} · {e['score']} {e.get('score_type','')}</div>
    </div>""" for e in edu])

    exp_html  = "".join([f"""
    <div class='rv-item'>
      <div style='display:flex;justify-content:space-between;'>
        <span class='rv-title'>{e['role']} · {e['company']}</span>
        <span class='rv-date'>{str(e.get('from_date',''))[:7]} – {'Present' if e['is_current'] else str(e.get('to_date',''))[:7]}</span>
      </div>
      <div class='rv-sub' style='color:{theme_color};'>{e['exp_type']}</div>
      {''.join([f"<div class='rv-bullet'>▸ {b.strip()}.</div>" for b in (e.get('description') or '').split('.') if b.strip()])}
    </div>""" for e in exp])

    proj_html = "".join([f"""
    <div class='rv-item'>
      <span class='rv-title'>{p['title']}</span>
      <div class='rv-sub'>Tech: {p.get('tech_stack','')}</div>
      <div class='rv-body'>{p.get('description','')}</div>
    </div>""" for p in proj])

    skill_html = "".join([
        f"<div style='margin-bottom:5px;'><b style='font-size:0.68rem;color:#444;'>{cat}:</b><br>"
        + "".join([f"<span class='rv-chip'>{s}</span>" for s in lst]) + "</div>"
        for cat, lst in cats.items()])

    cert_html = "".join([f"<div class='rv-bullet'>▸ {c['name']} · {c['issuer']} ({c['issue_year']})</div>" for c in certs])
    ach_html  = "".join([f"<div class='rv-bullet'>▸ {a['title']}</div>" for a in ach])
    contacts  = " · ".join(filter(None,[
        user.get("email",""), user.get("phone",""),
        f"{user.get('city','')}, {user.get('state','')}".strip(", "),
        user.get("linkedin_url",""), user.get("github_url","")]))

    return f"""
    <div style="background:white;border-radius:14px;padding:2.5rem 2.8rem;color:#1a1a2e;
                font-family:'Inter',sans-serif;line-height:1.6;
                box-shadow:0 20px 60px rgba(0,0,0,0.5);max-width:820px;margin:0 auto;">
      <style>
        .rv-name  {{font-size:1.7rem;font-weight:800;color:#1a1a2e;letter-spacing:-0.5px;}}
        .rv-role  {{font-size:0.95rem;color:{theme_color};font-weight:600;margin:3px 0 6px;}}
        .rv-cont  {{font-size:0.72rem;color:#888;}}
        .rv-sec   {{font-size:0.6rem;letter-spacing:2.5px;text-transform:uppercase;
                   color:{theme_color};font-weight:700;border-bottom:2px solid {theme_color};
                   padding-bottom:3px;margin:1.2rem 0 0.6rem;}}
        .rv-item  {{margin-bottom:0.8rem;}}
        .rv-title {{font-size:0.85rem;font-weight:700;color:#1a1a2e;}}
        .rv-sub   {{font-size:0.75rem;color:#666;margin:1px 0 3px;}}
        .rv-date  {{font-size:0.72rem;color:#aaa;white-space:nowrap;}}
        .rv-body  {{font-size:0.78rem;color:#444;}}
        .rv-bullet{{font-size:0.78rem;color:#444;margin:2px 0 2px 6px;}}
        .rv-chip  {{display:inline-block;background:{theme_color}15;color:{theme_color};
                   border:1px solid {theme_color}33;border-radius:5px;
                   padding:2px 8px;font-size:0.65rem;margin:2px;}}
        hr.rv     {{border:none;border-top:2.5px solid {theme_color};margin:6px 0 10px;}}
      </style>
      <div class="rv-name">{user.get('full_name','').upper()}</div>
      <div class="rv-role">{role}</div>
      <div class="rv-cont">{contacts}</div>
      <hr class="rv">
      <div class="rv-sec">Professional Summary</div>
      <div class="rv-body">{summary}</div>
      {'<div class="rv-sec">Education</div>'       + edu_html   if edu    else ''}
      {'<div class="rv-sec">Technical Skills</div>'+ skill_html if skills else ''}
      {'<div class="rv-sec">Work Experience</div>' + exp_html   if exp    else ''}
      {'<div class="rv-sec">Projects</div>'        + proj_html  if proj   else ''}
      {'<div class="rv-sec">Certifications</div>'  + cert_html  if certs  else ''}
      {'<div class="rv-sec">Achievements</div>'    + ach_html   if ach    else ''}
    </div>"""


def render_resume():
    profile = st.session_state.profile
    user    = profile["user"]
    edu     = profile["education"]
    exp     = profile["experience"]
    proj    = profile["projects"]
    skills  = profile["skills"]
    certs   = profile["certifications"]
    ach     = profile["achievements"]

    if "res_summary"  not in st.session_state:
        st.session_state.res_summary  = user.get("about_me") or build_summary(user, skills)
    if "res_role"     not in st.session_state:
        st.session_state.res_role     = user.get("target_role","Software Engineer")
    if "res_template" not in st.session_state:
        st.session_state.res_template = "Modern"

    # ── Banner ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d0d18 0%,#13131f 50%,#1a1030 100%);
                border:1px solid #ff6b9d22;border-radius:24px;padding:2rem 2.5rem;
                margin-bottom:1.5rem;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-60px;right:-60px;width:250px;height:250px;
                  background:radial-gradient(circle,#ff6b9d18,transparent);border-radius:50%;"></div>
      <div style="font-size:0.62rem;font-family:'JetBrains Mono',monospace;
                  color:#ff6b9d;letter-spacing:3px;text-transform:uppercase;">
        Student Help Desk · Module
      </div>
      <div style="font-size:2rem;font-weight:800;margin:0.3rem 0 0.2rem;
                  background:linear-gradient(135deg,#f0f0fa,#c4b5fd);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        AI Resume Maker
      </div>
      <div style="color:#606080;font-size:0.85rem;">
        Professional · ATS-Optimised · Live Preview · One-Click PDF Export
      </div>
    </div>""", unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs([
        "🎨  Builder", "👁️  Live Preview", "📊  ATS Analyser",
        "📥  Export PDF", "🗂️  My Versions"
    ])

    # ══════════════════════════════════════════════════════════════════════
    # TAB 1 — BUILDER
    # ══════════════════════════════════════════════════════════════════════
    with t1:
        left_col, right_col = st.columns([3, 2])

        with left_col:
            # Settings
            st.markdown('<div class="card"><div class="card-header">Resume Settings</div>',
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                version_name = st.text_input("Version Name", "My Resume v1", key="res_version")
                st.session_state.res_role = st.text_input(
                    "Target Role", st.session_state.res_role, key="res_role_inp")
            with c2:
                template = st.selectbox("Template", list(TEMPLATES.keys()), key="res_tpl_sel",
                    index=list(TEMPLATES.keys()).index(st.session_state.res_template))
                st.session_state.res_template = template
                swatches = "".join([
                    f'<div title="{t}" style="width:22px;height:22px;border-radius:50%;'
                    f'background:{c};display:inline-block;margin:2px;cursor:pointer;'
                    f'{"border:2px solid white;box-shadow:0 0 8px "+c if t==template else "border:2px solid transparent"};"></div>'
                    for t,c in TEMPLATES.items()])
                st.markdown(f'<div style="margin-top:6px;">{swatches}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Summary
            st.markdown('<div class="card"><div class="card-header">Professional Summary</div>',
                        unsafe_allow_html=True)
            st.session_state.res_summary = st.text_area(
                "Edit your summary", value=st.session_state.res_summary,
                height=120, key="res_sum_area")
            wc = len(st.session_state.res_summary.split())
            wc_col = "#10b981" if 40<=wc<=80 else "#f59e0b"
            st.markdown(f'<div style="font-size:0.72rem;color:{wc_col};text-align:right;">'
                        f'{wc} words {"✓ Ideal" if 40<=wc<=80 else "(aim 40–80)"}</div>',
                        unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Education
            st.markdown('<div class="card"><div class="card-header">Education</div>',
                        unsafe_allow_html=True)
            if edu:
                for e in edu:
                    st.markdown(f"""
                    <div class="timeline-item">
                      <div style="font-weight:600;font-size:0.88rem;color:#f0f0fa;">{e['degree']}</div>
                      <div style="font-size:0.8rem;color:#a0a0c0;">{e['institution']} · {e.get('field_of_study','')}</div>
                      <div style="font-size:0.75rem;color:#606080;">{e['year_from']} – {e['year_to']}
                        &nbsp;·&nbsp;<span style="color:#7c6fff;">{e['score']} {e.get('score_type','')}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("No education found. Update your profile.")
            st.markdown('</div>', unsafe_allow_html=True)

            # Experience
            if exp:
                st.markdown('<div class="card"><div class="card-header">Experience</div>',
                            unsafe_allow_html=True)
                for e in exp:
                    to = "Present" if e["is_current"] else str(e.get("to_date",""))[:7]
                    st.markdown(f"""
                    <div class="timeline-item">
                      <div style="display:flex;justify-content:space-between;">
                        <div>
                          <div style="font-weight:600;font-size:0.88rem;color:#f0f0fa;">{e['role']}</div>
                          <div style="font-size:0.8rem;color:#a0a0c0;">{e['company']}</div>
                        </div>
                        <div style="font-size:0.72rem;color:#606080;white-space:nowrap;margin-left:1rem;">
                          {str(e.get('from_date',''))[:7]} – {to}
                        </div>
                      </div>
                      <span class="badge cyan" style="margin-top:4px;">{e['exp_type']}</span>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Projects
            if proj:
                st.markdown('<div class="card"><div class="card-header">Projects</div>',
                            unsafe_allow_html=True)
                for p in proj:
                    chips = "".join([f'<span class="skill-chip" style="font-size:0.65rem;">{t.strip()}</span>'
                                     for t in (p.get("tech_stack","") or "").split(",") if t.strip()])
                    st.markdown(f"""
                    <div class="card-sm">
                      <div style="font-weight:600;font-size:0.88rem;margin-bottom:4px;color:#f0f0fa;">
                        🚀 {p['title']}
                      </div>
                      <div style="margin-bottom:5px;">{chips}</div>
                      <div style="font-size:0.78rem;color:#a0a0c0;">
                        {(p.get('description','') or '')[:100]}{'...' if len(p.get('description','') or '')>100 else ''}
                      </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with right_col:
            # Skills
            st.markdown('<div class="card"><div class="card-header">Skills</div>',
                        unsafe_allow_html=True)
            if skills:
                cats = {}
                for s in skills: cats.setdefault(s["category"],[]).append(s["skill_name"])
                for cat, lst in cats.items():
                    st.markdown(f'<div style="font-size:0.68rem;color:#606080;margin:8px 0 4px;">{cat.upper()}</div>',
                                unsafe_allow_html=True)
                    st.markdown("".join([f'<span class="skill-chip">{s}</span>' for s in lst]),
                                unsafe_allow_html=True)
            else:
                st.warning("No skills. Update your profile.")
            st.markdown('</div>', unsafe_allow_html=True)

            # Certifications
            if certs:
                st.markdown('<div class="card"><div class="card-header">Certifications</div>',
                            unsafe_allow_html=True)
                for c in certs:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:10px;
                                padding:0.5rem 0;border-bottom:1px solid #ffffff0f;">
                      <div style="width:32px;height:32px;border-radius:8px;background:#7c6fff22;
                                  display:flex;align-items:center;justify-content:center;
                                  font-size:1rem;flex-shrink:0;">📜</div>
                      <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#f0f0fa;">{c['name']}</div>
                        <div style="font-size:0.72rem;color:#606080;">{c['issuer']} · {c['issue_year']}</div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Achievements
            if ach:
                st.markdown('<div class="card"><div class="card-header">Achievements</div>',
                            unsafe_allow_html=True)
                for a in ach:
                    st.markdown(f'<div style="font-size:0.82rem;padding:4px 0;color:#a0a0c0;">'
                                f'<span style="color:#fbbf24;">🏆</span> {a["title"]}</div>',
                                unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Strength meter
            score, done_list, miss_list = resume_strength(user, edu, skills, exp, proj, certs, ach)
            label = "Weak" if score<40 else "Good" if score<65 else "Strong" if score<85 else "Excellent"
            bar_c = "#f43f5e" if score<40 else "#f59e0b" if score<65 else "#7c6fff" if score<85 else "#10b981"
            st.markdown(f"""
            <div class="card">
              <div class="card-header">Resume Strength</div>
              <div style="display:flex;align-items:center;gap:1rem;margin-bottom:10px;">
                <div style="font-size:2.5rem;font-weight:800;color:{bar_c};line-height:1;">{score}</div>
                <div>
                  <div style="font-size:1rem;font-weight:700;color:{bar_c};">{label}</div>
                  <div style="font-size:0.72rem;color:#606080;">out of 100</div>
                </div>
              </div>
              <div class="progress-wrap">
                <div class="progress-fill" style="width:{score}%;background:{bar_c};"></div>
              </div>
              <div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:5px;">
                {''.join([f'<span class="badge green">✓ {d}</span>' for d in done_list])}
                {''.join([f'<span class="badge red">+ {m}</span>' for m in miss_list])}
              </div>
            </div>""", unsafe_allow_html=True)

            if st.button("💾  Save Resume Version", key="save_resume", use_container_width=True):
                try:
                    conn = get_conn(); cur = conn.cursor()
                    cur.execute("""INSERT INTO resumes
                        (user_id,version_name,target_role,summary,template,ats_score)
                        VALUES (%s,%s,%s,%s,%s,%s)""",
                        (user["user_id"], version_name, st.session_state.res_role,
                         st.session_state.res_summary, template, score))
                    conn.commit(); conn.close()
                    st.success(f"✅ '{version_name}' saved!")
                except Exception as ex:
                    st.error(f"❌ {ex}")

    # ══════════════════════════════════════════════════════════════════════
    # TAB 2 — LIVE PREVIEW
    # ══════════════════════════════════════════════════════════════════════
    with t2:
        st.markdown("""
        <div style="background:var(--surface2);border:1px solid var(--border2);
                    border-radius:12px;padding:0.8rem 1.2rem;margin-bottom:1rem;">
          <div style="font-size:0.78rem;color:#606080;">
            👁️ Live preview of your resume. Change template in Builder tab to update.
          </div>
        </div>""", unsafe_allow_html=True)
        theme_color = TEMPLATES.get(st.session_state.res_template, "#7c6fff")
        st.markdown(resume_html_preview(user,edu,exp,proj,skills,certs,ach,
            st.session_state.res_summary, st.session_state.res_role, theme_color),
            unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # TAB 3 — ATS ANALYSER
    # ══════════════════════════════════════════════════════════════════════
    with t3:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d0d18,#130d1f);
                    border:1px solid #7c6fff22;border-radius:16px;
                    padding:1.2rem 1.6rem;margin-bottom:1.2rem;">
          <div style="font-size:1rem;font-weight:700;">📊 ATS Score Analyser</div>
          <div style="font-size:0.8rem;color:#606080;margin-top:2px;">
            Paste any job description to instantly check your keyword match score
          </div>
        </div>""", unsafe_allow_html=True)

        jd = st.text_area("Paste Job Description", height=220, key="ats_jd_input",
            placeholder="We are looking for a Software Engineer proficient in Python, "
                        "REST APIs, Docker, AWS, CI/CD, MySQL, React...")

        if st.button("🔍  Run ATS Analysis", key="btn_ats"):
            if not jd.strip():
                st.error("Please paste a job description first.")
            else:
                resume_text = " ".join(filter(None,[
                    user.get("about_me",""), st.session_state.res_summary,
                    " ".join(s["skill_name"] for s in skills),
                    " ".join(e["degree"]+" "+e.get("field_of_study","") for e in edu),
                    " ".join(e["role"]+" "+e.get("description","") for e in exp),
                    " ".join(p["title"]+" "+p.get("tech_stack","") for p in proj),
                ]))
                ats_score, matched, missing = ats_check(resume_text, jd)
                color = "#f43f5e" if ats_score<40 else "#f59e0b" if ats_score<65 else "#10b981"
                grade = ("Needs Work 🔴" if ats_score<40 else "Average 🟡" if ats_score<65
                         else "Good Match 🟢" if ats_score<80 else "Excellent 🌟")

                c1,c2,c3 = st.columns(3)
                for col,val,lbl,clr in [
                    (c1,f"{ats_score}%","ATS Match Score",color),
                    (c2,str(len(matched)),"Keywords Matched","#10b981"),
                    (c3,str(len(missing)),"Keywords Missing","#f43f5e")]:
                    with col:
                        st.markdown(f"""
                        <div class="stat-card" style="border-color:{clr}44;">
                          <div style="font-size:2.8rem;font-weight:800;color:{clr};line-height:1.1;">{val}</div>
                          <div class="stat-label">{lbl}</div>
                          {'<div style="font-size:0.78rem;color:'+clr+';margin-top:4px;">'+grade+'</div>' if lbl=='ATS Match Score' else ''}
                        </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                mc, xc = st.columns(2)
                with mc:
                    st.markdown('<div class="card"><div class="card-header">✅ Matched Keywords</div>', unsafe_allow_html=True)
                    chips = "".join([f'<span class="skill-chip green">{w}</span>' for w in matched])
                    st.markdown(chips or '<div style="color:#606080;font-size:0.82rem;">None matched</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with xc:
                    st.markdown('<div class="card"><div class="card-header">❌ Missing Keywords</div>', unsafe_allow_html=True)
                    chips = "".join([f'<span class="skill-chip red">{w}</span>' for w in missing])
                    st.markdown(chips or '<div style="color:#606080;font-size:0.82rem;">🎉 Nothing missing!</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                if ats_score < 70:
                    st.markdown("""
                    <div style="background:#f59e0b12;border:1px solid #f59e0b33;border-radius:12px;padding:1rem 1.2rem;margin-top:0.5rem;">
                      <div style="font-weight:600;color:#fbbf24;margin-bottom:6px;">💡 Tips to Improve</div>
                      <div style="font-size:0.82rem;color:#a0a0c0;line-height:1.8;">
                        • Add missing keywords naturally into your Skills or Experience sections<br>
                        • Match exact terminology from the JD<br>
                        • Include the job title exactly as written in the JD<br>
                        • Quantify your achievements with numbers and metrics
                      </div>
                    </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # TAB 4 — EXPORT PDF
    # ══════════════════════════════════════════════════════════════════════
    with t4:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1f0d,#0d1a0d);border:1px solid #10b98133;
                    border-radius:16px;padding:1.2rem 1.6rem;margin-bottom:1.2rem;">
          <div style="font-size:1rem;font-weight:700;">📥 Export Resume as PDF</div>
          <div style="font-size:0.8rem;color:#606080;margin-top:2px;">
            Professional, ATS-safe, font-embedded PDF
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-header">Export Settings</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            dl_role     = st.text_input("Target Role on PDF", value=st.session_state.res_role, key="dl_role")
            dl_template = st.selectbox("PDF Template", list(TEMPLATES.keys()),
                index=list(TEMPLATES.keys()).index(st.session_state.res_template), key="dl_tpl")
        with c2:
            tc = TEMPLATES[dl_template]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-top:28px;">
              <div style="width:44px;height:44px;border-radius:12px;background:{tc};
                          box-shadow:0 4px 15px {tc}66;"></div>
              <div>
                <div style="font-weight:600;font-size:0.9rem;">{dl_template}</div>
                <div style="font-size:0.72rem;color:#606080;">{tc}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        dl_summary = st.text_area("Summary for PDF", value=st.session_state.res_summary,
                                   height=90, key="dl_summary")
        st.markdown('</div>', unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            items = [("✅" if user.get("full_name") else "❌","Personal Info"),
                     ("✅" if edu    else "➕","Education"),
                     ("✅" if skills else "➕","Skills"),
                     ("✅" if exp    else "➕","Experience"),
                     ("✅" if proj   else "➕","Projects"),
                     ("✅" if certs  else "➕","Certifications"),
                     ("✅" if ach    else "➕","Achievements")]
            rows = "".join([f'<div style="display:flex;gap:8px;font-size:0.8rem;padding:3px 0;">'
                            f'<span>{s}</span><span style="color:#a0a0c0;">{l}</span></div>'
                            for s,l in items])
            st.markdown(f'<div class="card"><div class="card-header">Included Sections</div>{rows}</div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="card">
              <div class="card-header">PDF Features</div>
              <div style="font-size:0.82rem;color:#a0a0c0;line-height:2.2;">
                ✦ ATS-safe Helvetica fonts<br>
                ✦ Professional two-column dates<br>
                ✦ Colour-coded section markers<br>
                ✦ Compact single-page design<br>
                ✦ Immediate download
              </div>
            </div>""", unsafe_allow_html=True)

        if st.button("⬇️  Generate & Download PDF", key="btn_dl_pdf", use_container_width=True):
            with st.spinner("Building your professional PDF..."):
                try:
                    buf = generate_pdf(user,edu,exp,proj,skills,certs,ach,
                                       dl_summary, dl_role, dl_template)
                    fname = f"{user.get('full_name','Resume').replace(' ','_')}_Resume.pdf"
                    st.download_button("📥  Download PDF Now", data=buf,
                                       file_name=fname, mime="application/pdf",
                                       use_container_width=True)
                    st.success("✅ PDF ready!")
                except Exception as ex:
                    st.error(f"❌ PDF Error: {ex}")

    # ══════════════════════════════════════════════════════════════════════
    # TAB 5 — SAVED VERSIONS
    # ══════════════════════════════════════════════════════════════════════
    with t5:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d0d18,#0d131f);border:1px solid #22d3ee22;
                    border-radius:16px;padding:1.2rem 1.6rem;margin-bottom:1.2rem;">
          <div style="font-size:1rem;font-weight:700;">🗂️ Saved Resume Versions</div>
        </div>""", unsafe_allow_html=True)
        try:
            conn = get_conn(); cur = conn.cursor(dictionary=True)
            cur.execute("""SELECT resume_id,version_name,target_role,ats_score,
                                  template,created_at,updated_at
                           FROM resumes WHERE user_id=%s ORDER BY updated_at DESC""",
                        (user["user_id"],))
            versions = cur.fetchall(); conn.close()
            if versions:
                for v in versions:
                    sc  = v["ats_score"] or 0
                    sc_col  = "#f43f5e" if sc<40 else "#f59e0b" if sc<65 else "#10b981"
                    tpl_col = TEMPLATES.get(v["template"] or "Modern","#7c6fff")
                    st.markdown(f"""
                    <div style="background:var(--surface2);border:1px solid var(--border2);
                                border-radius:14px;padding:1rem 1.4rem;margin-bottom:0.6rem;
                                display:flex;justify-content:space-between;align-items:center;">
                      <div style="display:flex;align-items:center;gap:14px;">
                        <div style="width:38px;height:38px;border-radius:10px;background:{tpl_col}22;
                                    display:flex;align-items:center;justify-content:center;font-size:1.2rem;">📄</div>
                        <div>
                          <div style="font-weight:700;font-size:0.9rem;color:#f0f0fa;">{v['version_name']}</div>
                          <div style="font-size:0.75rem;color:#606080;margin-top:1px;">
                            🎯 {v['target_role']} &nbsp;·&nbsp; 🎨 {v['template'] or 'Modern'}
                          </div>
                        </div>
                      </div>
                      <div style="text-align:right;">
                        <div style="font-size:1.2rem;font-weight:800;color:{sc_col};">{sc}%</div>
                        <div style="font-size:0.68rem;color:#606080;">{str(v['updated_at'])[:10]}</div>
                      </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center;padding:3rem;background:var(--surface2);
                            border:1px dashed var(--border2);border-radius:16px;">
                  <div style="font-size:2.5rem;margin-bottom:0.5rem;">📄</div>
                  <div style="font-size:0.95rem;color:#a0a0c0;font-weight:600;">No saved versions yet</div>
                  <div style="font-size:0.8rem;color:#606080;margin-top:4px;">
                    Build your resume in the Builder tab and click Save
                  </div>
                </div>""", unsafe_allow_html=True)
        except Exception as ex:
            st.error(f"❌ {ex}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key="back_resume"):
        st.session_state.active_module = None
        st.rerun()
        