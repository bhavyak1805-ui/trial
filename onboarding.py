import streamlit as st
import time
from datetime import date
from db import get_conn, save_onboarding, load_full_profile


def render_onboarding():
    user  = st.session_state.current_user
    step  = st.session_state.get("onboarding_step", 1)
    total = 6

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:1px solid #7c6fff44;
                border-radius:20px;padding:1.5rem 2rem;margin-bottom:1.5rem;">
      <div style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:#7c6fff;
                  letter-spacing:3px;text-transform:uppercase;">One-Time Profile Setup</div>
      <div style="font-size:1.5rem;font-weight:800;margin-top:0.3rem;">
        Let's build your profile,
        <span style="background:linear-gradient(135deg,#7c6fff,#ff6b9d);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          {user['full_name'].split()[0]}
        </span> 👋
      </div>
      <div style="color:#606080;font-size:0.82rem;margin-top:0.2rem;">
        Fill this once — used across all modules forever.
      </div>
    </div>""", unsafe_allow_html=True)

    # Step indicator
    labels = ["Personal","Education","Experience","Projects","Skills","Certifications"]
    cols   = st.columns(total * 2 - 1)
    for i, label in enumerate(labels):
        with cols[i * 2]:
            bg  = "#7c6fff" if i+1==step else "#10b981" if i+1<step else "#1c1c2e"
            fc  = "white"   if i+1<=step else "#606080"
            sym = "✓" if i+1<step else str(i+1)
            cc  = "#7c6fff" if i+1==step else "#606080"
            st.markdown(f"""
            <div style="text-align:center;">
              <div style="width:30px;height:30px;border-radius:50%;background:{bg};color:{fc};
                          display:flex;align-items:center;justify-content:center;
                          font-size:0.75rem;font-weight:700;margin:0 auto 4px;
                          box-shadow:{'0 0 12px #7c6fff66' if i+1==step else 'none'};">
                {sym}
              </div>
              <div style="font-size:0.62rem;color:{cc};font-weight:500;">{label}</div>
            </div>""", unsafe_allow_html=True)
        if i < total - 1:
            with cols[i*2+1]:
                lc = "#10b981" if i+1<step else "#ffffff18"
                st.markdown(f'<div style="height:2px;background:{lc};margin-top:15px;"></div>',
                            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STEP 1 ────────────────────────────────────────────────────────────
    if step == 1:
        st.markdown('<div class="card"><div class="card-header">Personal Information</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            dob         = st.date_input("Date of Birth", value=date(2000,1,1), key="ob_dob")
            city        = st.text_input("City", placeholder="Raipur", key="ob_city")
            linkedin    = st.text_input("LinkedIn URL", placeholder="linkedin.com/in/yourname", key="ob_linkedin")
            target_role = st.selectbox("Target Job Role", [
                "Software Engineer","Data Scientist","Data Analyst",
                "Machine Learning Engineer","Web Developer","Full Stack Developer",
                "DevOps Engineer","Cloud Engineer","UI/UX Designer",
                "Product Manager","Business Analyst","Cybersecurity Analyst"
            ], key="ob_role")
        with c2:
            gender    = st.selectbox("Gender", ["Male","Female","Other","Prefer not to say"], key="ob_gender")
            state     = st.selectbox("State", [
                "Chhattisgarh","Maharashtra","Delhi","Karnataka","Tamil Nadu",
                "Uttar Pradesh","Gujarat","Rajasthan","West Bengal","Telangana",
                "Andhra Pradesh","Kerala","Madhya Pradesh","Punjab","Haryana","Other"
            ], key="ob_state")
            github    = st.text_input("GitHub URL", placeholder="github.com/yourname", key="ob_github")
            exp_level = st.selectbox("Experience Level",
                ["Fresher","0-1 years","1-2 years","2-5 years","5+ years"], key="ob_explevel")
        address   = st.text_area("Address", placeholder="House no, Street, Area", height=70, key="ob_address")
        portfolio = st.text_input("Portfolio / Website", placeholder="yourwebsite.com", key="ob_portfolio")
        about_me  = st.text_area("About Me (used in resume summary)",
            placeholder="I am a passionate CS student with interest in AI/ML...",
            height=100, key="ob_about")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Next → Education", key="ob_next1"):
            st.session_state.ob_personal = {
                "dob":str(dob),"gender":gender,"city":city,"state":state,
                "address":address,"linkedin":linkedin,"github":github,
                "portfolio":portfolio,"target_role":target_role,
                "exp_level":exp_level,"about_me":about_me
            }
            st.session_state.onboarding_step = 2; st.rerun()

    # ── STEP 2 ────────────────────────────────────────────────────────────
    elif step == 2:
        if "ob_edu_list" not in st.session_state:
            st.session_state.ob_edu_list = [{}]
        st.markdown('<div class="card"><div class="card-header">Education Details</div>',
                    unsafe_allow_html=True)
        st.caption("Add all levels — 10th, 12th, Diploma, Degree, PG")
        for i in range(len(st.session_state.ob_edu_list)):
            st.markdown(f"**Entry {i+1}**")
            c1,c2,c3 = st.columns(3)
            with c1:
                degree = st.selectbox("Degree", ["10th","12th","Diploma","B.Tech/B.E","BCA",
                    "B.Sc","BBA","B.Com","M.Tech/M.E","MCA","M.Sc","MBA","PhD","Other"],
                    key=f"edu_deg_{i}")
                inst   = st.text_input("Institution", placeholder="ABC University", key=f"edu_inst_{i}")
            with c2:
                field  = st.text_input("Stream / Field", placeholder="Computer Science", key=f"edu_field_{i}")
                board  = st.text_input("Board / University", placeholder="CGBSE / CSVTU", key=f"edu_board_{i}")
            with c3:
                yf = st.number_input("Year From", 2000, 2030, 2020, key=f"edu_yf_{i}")
                yt = st.number_input("Year To",   2000, 2030, 2024, key=f"edu_yt_{i}")
            c4,c5 = st.columns(2)
            with c4:
                score      = st.text_input("Score", placeholder="8.5 / 85%", key=f"edu_score_{i}")
                score_type = st.selectbox("Type", ["CGPA","Percentage","Grade"], key=f"edu_stype_{i}")
            with c5:
                coursework = st.text_input("Key Subjects", placeholder="DSA, DBMS, ML", key=f"edu_cw_{i}")
            st.session_state.ob_edu_list[i] = {
                "degree":degree,"institution":inst,"field":field,"board":board,
                "year_from":yf,"year_to":yt,"score":score,
                "score_type":score_type,"coursework":coursework
            }
            if i > 0:
                if st.button(f"Remove Entry {i+1}", key=f"rem_edu_{i}"):
                    st.session_state.ob_edu_list.pop(i); st.rerun()
            st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("← Back", key="ob_back2"): st.session_state.onboarding_step=1; st.rerun()
        with c2:
            if st.button("➕ Add Education", key="ob_add_edu"):
                st.session_state.ob_edu_list.append({}); st.rerun()
        with c3:
            if st.button("Next → Experience", key="ob_next2"):
                st.session_state.onboarding_step=3; st.rerun()

    # ── STEP 3 ────────────────────────────────────────────────────────────
    elif step == 3:
        if "ob_exp_list" not in st.session_state: st.session_state.ob_exp_list = []
        st.markdown('<div class="card"><div class="card-header">Work Experience & Internships</div>',
                    unsafe_allow_html=True)
        st.caption("Skip if fresher — click Next directly.")
        for i in range(len(st.session_state.ob_exp_list)):
            st.markdown(f"**Experience {i+1}**")
            c1,c2,c3 = st.columns(3)
            with c1:
                company   = st.text_input("Company", placeholder="Infosys", key=f"exp_co_{i}")
                role      = st.text_input("Role", placeholder="Software Intern", key=f"exp_role_{i}")
            with c2:
                exp_type  = st.selectbox("Type", ["Internship","Full-Time","Part-Time","Freelance"], key=f"exp_type_{i}")
                from_date = st.date_input("From", key=f"exp_from_{i}")
            with c3:
                is_curr   = st.checkbox("Currently Here", key=f"exp_curr_{i}")
                to_date   = st.date_input("To", key=f"exp_to_{i}") if not is_curr else None
            desc = st.text_area("What you did", placeholder="Developed REST APIs using FastAPI...",
                                height=80, key=f"exp_desc_{i}")
            st.session_state.ob_exp_list[i] = {
                "company":company,"role":role,"exp_type":exp_type,
                "from_date":str(from_date),"to_date":str(to_date) if to_date else None,
                "is_current":is_curr,"description":desc
            }
            if st.button("Remove", key=f"rem_exp_{i}"):
                st.session_state.ob_exp_list.pop(i); st.rerun()
            st.markdown("---")
        if not st.session_state.ob_exp_list:
            st.info("No experience added. Click ➕ or Next to skip.")
        st.markdown('</div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("← Back", key="ob_back3"): st.session_state.onboarding_step=2; st.rerun()
        with c2:
            if st.button("➕ Add Experience", key="ob_add_exp"):
                st.session_state.ob_exp_list.append({}); st.rerun()
        with c3:
            if st.button("Next → Projects", key="ob_next3"):
                st.session_state.onboarding_step=4; st.rerun()

    # ── STEP 4 ────────────────────────────────────────────────────────────
    elif step == 4:
        if "ob_proj_list" not in st.session_state: st.session_state.ob_proj_list = [{}]
        st.markdown('<div class="card"><div class="card-header">Projects</div>', unsafe_allow_html=True)
        st.caption("Academic, personal, or open-source projects.")
        for i in range(len(st.session_state.ob_proj_list)):
            st.markdown(f"**Project {i+1}**")
            c1,c2 = st.columns(2)
            with c1:
                title  = st.text_input("Title", placeholder="AI Chatbot", key=f"proj_title_{i}")
                tech   = st.text_input("Tech Stack", placeholder="Python, Flask, MySQL", key=f"proj_tech_{i}")
                github = st.text_input("GitHub URL", placeholder="github.com/you/project", key=f"proj_gh_{i}")
            with c2:
                live   = st.text_input("Live URL", placeholder="yourproject.com", key=f"proj_live_{i}")
                desc   = st.text_area("Description",
                    placeholder="Built an AI chatbot that handles 500+ queries/day...",
                    height=100, key=f"proj_desc_{i}")
            st.session_state.ob_proj_list[i] = {
                "title":title,"tech_stack":tech,"github_url":github,"live_url":live,"description":desc
            }
            if i > 0:
                if st.button("Remove", key=f"rem_proj_{i}"):
                    st.session_state.ob_proj_list.pop(i); st.rerun()
            st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("← Back", key="ob_back4"): st.session_state.onboarding_step=3; st.rerun()
        with c2:
            if st.button("➕ Add Project", key="ob_add_proj"):
                st.session_state.ob_proj_list.append({}); st.rerun()
        with c3:
            if st.button("Next → Skills", key="ob_next4"):
                st.session_state.onboarding_step=5; st.rerun()

    # ── STEP 5 ────────────────────────────────────────────────────────────
    elif step == 5:
        st.markdown('<div class="card"><div class="card-header">Skills</div>', unsafe_allow_html=True)
        role = st.session_state.get("ob_personal",{}).get("target_role","Software Engineer")
        suggestions = {
            "Software Engineer":         ["Python","Java","C++","DSA","Git","MySQL","REST APIs","Linux","Docker","AWS"],
            "Data Scientist":            ["Python","R","Machine Learning","Deep Learning","Pandas","NumPy","TensorFlow","SQL","Tableau","Statistics"],
            "Data Analyst":              ["Python","SQL","Excel","Power BI","Tableau","Statistics","Pandas","Data Visualization"],
            "Web Developer":             ["HTML","CSS","JavaScript","React","Node.js","MongoDB","Git","REST APIs","Bootstrap","TypeScript"],
            "Machine Learning Engineer": ["Python","TensorFlow","PyTorch","Scikit-learn","Deep Learning","NLP","Computer Vision","MLOps","Docker","AWS"],
            "Full Stack Developer":      ["React","Node.js","Python","MongoDB","MySQL","Git","Docker","AWS","REST APIs","TypeScript"],
            "DevOps Engineer":           ["Linux","Docker","Kubernetes","Jenkins","AWS","Terraform","CI/CD","Python","Git","Ansible"],
            "Cloud Engineer":            ["AWS","Azure","GCP","Terraform","Docker","Kubernetes","Linux","Python","Networking","Security"],
            "UI/UX Designer":            ["Figma","Adobe XD","Sketch","HTML","CSS","Prototyping","User Research","Wireframing","Canva","Illustrator"],
        }
        sugg  = suggestions.get(role, ["Python","SQL","Git","Communication","Problem Solving"])
        chips = "".join([f'<span class="skill-chip">{s}</span>' for s in sugg])
        st.markdown(f"**Suggested for {role}:**", unsafe_allow_html=True)
        st.markdown(chips, unsafe_allow_html=True)
        st.caption("Copy skills from above into the fields below")
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            tech  = st.text_input("Technical Skills (comma separated)", placeholder="Python, SQL, ML", key="sk_tech")
            fw    = st.text_input("Frameworks & Libraries", placeholder="React, Django, FastAPI", key="sk_fw")
            tools = st.text_input("Tools & Platforms", placeholder="Git, Docker, Jupyter", key="sk_tools")
        with c2:
            cloud = st.text_input("Cloud & Databases", placeholder="AWS, MySQL, MongoDB", key="sk_cloud")
            soft  = st.text_input("Soft Skills", placeholder="Leadership, Communication", key="sk_soft")
            langs = st.text_input("Languages Known", placeholder="English (Fluent), Hindi (Native)", key="sk_langs")
        skill_list = []
        for name in (tech  or "").split(","):
            if name.strip(): skill_list.append({"name":name.strip(),"category":"Technical","proficiency":"Intermediate"})
        for name in (fw    or "").split(","):
            if name.strip(): skill_list.append({"name":name.strip(),"category":"Framework","proficiency":"Intermediate"})
        for name in (tools or "").split(","):
            if name.strip(): skill_list.append({"name":name.strip(),"category":"Tool","proficiency":"Intermediate"})
        for name in (cloud or "").split(","):
            if name.strip(): skill_list.append({"name":name.strip(),"category":"Cloud/DB","proficiency":"Intermediate"})
        for name in (soft  or "").split(","):
            if name.strip(): skill_list.append({"name":name.strip(),"category":"Soft Skill","proficiency":"Good"})
        for name in (langs or "").split(","):
            if name.strip(): skill_list.append({"name":name.strip(),"category":"Language","proficiency":"Fluent"})
        st.session_state.ob_skills_list = skill_list
        st.markdown('</div>', unsafe_allow_html=True)
        c1,_,c3 = st.columns(3)
        with c1:
            if st.button("← Back", key="ob_back5"): st.session_state.onboarding_step=4; st.rerun()
        with c3:
            if st.button("Next → Certifications", key="ob_next5"):
                st.session_state.onboarding_step=6; st.rerun()

    # ── STEP 6 ────────────────────────────────────────────────────────────
    elif step == 6:
        if "ob_cert_list" not in st.session_state: st.session_state.ob_cert_list = []
        if "ob_ach_list"  not in st.session_state: st.session_state.ob_ach_list  = []

        st.markdown('<div class="card"><div class="card-header">Certifications</div>', unsafe_allow_html=True)
        popular = ["AWS Certified Solutions Architect","Google Data Analytics (Coursera)",
                   "Meta Front-End Developer","TCS iON Career Edge",
                   "NPTEL Python for Data Science","Microsoft Azure Fundamentals",
                   "HackerRank Python (Basic)","Coursera ML — Andrew Ng",
                   "Google Cloud Digital Leader","Cisco CCNA"]
        quick = st.multiselect("Quick Add Popular Certifications", popular, key="ob_quick_certs")
        for cert in quick:
            issuer = ("AWS" if "AWS" in cert else "Google" if "Google" in cert else
                      "Meta" if "Meta" in cert else "TCS" if "TCS" in cert else
                      "NPTEL" if "NPTEL" in cert else "Microsoft" if "Microsoft" in cert else "Coursera")
            if not any(c["name"]==cert for c in st.session_state.ob_cert_list):
                st.session_state.ob_cert_list.append({"name":cert,"issuer":issuer,"year":2024,"credential_id":"","verify_url":""})
        for i, cert in enumerate(st.session_state.ob_cert_list):
            c1,c2,c3,c4 = st.columns([3,2,1,1])
            with c1: cert["name"]   = st.text_input("Name",   cert.get("name",""),   key=f"cert_n_{i}")
            with c2: cert["issuer"] = st.text_input("Issuer", cert.get("issuer",""), key=f"cert_i_{i}")
            with c3: cert["year"]   = st.number_input("Year", 2010, 2026, cert.get("year",2024), key=f"cert_y_{i}")
            with c4:
                if st.button("✕", key=f"rem_cert_{i}"):
                    st.session_state.ob_cert_list.pop(i); st.rerun()
        if st.button("➕ Add Custom Certification", key="ob_add_cert"):
            st.session_state.ob_cert_list.append({"name":"","issuer":"","year":2024,"credential_id":"","verify_url":""}); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-header">Achievements & Extra-Curriculars</div>', unsafe_allow_html=True)
        ach_text = st.text_area("One achievement per line",
            placeholder="1st Prize — State Level Hackathon 2024\nNPTEL Elite Scholar\nNSS Volunteer — 120 hrs",
            height=120, key="ob_ach_text")
        if ach_text:
            st.session_state.ob_ach_list = [
                {"title":line.strip(),"description":"","year":2024}
                for line in ach_text.split("\n") if line.strip()
            ]
        st.markdown('</div>', unsafe_allow_html=True)

        c1,_,c3 = st.columns(3)
        with c1:
            if st.button("← Back", key="ob_back6"): st.session_state.onboarding_step=5; st.rerun()
        with c3:
            if st.button("✅ Save & Go to Dashboard", key="ob_save"):
                with st.spinner("Saving your profile..."):
                    save_onboarding(
                        user_id=st.session_state.current_user["user_id"],
                        personal=st.session_state.get("ob_personal",{}),
                        education_list=st.session_state.get("ob_edu_list",[]),
                        experience_list=st.session_state.get("ob_exp_list",[]),
                        projects_list=st.session_state.get("ob_proj_list",[]),
                        skills_list=st.session_state.get("ob_skills_list",[]),
                        certs_list=st.session_state.ob_cert_list,
                        achievements_list=st.session_state.ob_ach_list,
                    )
                    load_full_profile(st.session_state.current_user["user_id"])
                    conn = get_conn(); cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE user_id=%s",(st.session_state.current_user["user_id"],))
                    st.session_state.current_user = cur.fetchone(); conn.close()
                st.success("✅ Profile saved!")
                time.sleep(0.8); st.rerun()