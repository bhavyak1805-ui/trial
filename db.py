import mysql.connector
import streamlit as st


def get_conn():
    cfg = st.session_state.get("db_config", {})
    return mysql.connector.connect(
        host=cfg.get("host", "localhost"),
        port=int(cfg.get("port", 3306)),
        user=cfg.get("user", "root"),
        password=cfg.get("password", "bk123@"),
        database=cfg.get("database", "faceauth"),
    )


def test_conn():
    try:
        c = get_conn()
        c.close()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


def load_full_profile(user_id):
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cur.fetchone()

    cur.execute("SELECT * FROM education      WHERE user_id=%s ORDER BY year_to DESC",  (user_id,))
    edu  = cur.fetchall()

    cur.execute("SELECT * FROM experience     WHERE user_id=%s ORDER BY from_date DESC", (user_id,))
    exp  = cur.fetchall()

    cur.execute("SELECT * FROM projects       WHERE user_id=%s", (user_id,))
    proj = cur.fetchall()

    cur.execute("SELECT * FROM skills         WHERE user_id=%s", (user_id,))
    skills = cur.fetchall()

    cur.execute("SELECT * FROM certifications WHERE user_id=%s", (user_id,))
    certs = cur.fetchall()

    cur.execute("SELECT * FROM achievements   WHERE user_id=%s", (user_id,))
    ach   = cur.fetchall()

    conn.close()

    st.session_state.profile = {
        "user": user, "education": edu, "experience": exp,
        "projects": proj, "skills": skills,
        "certifications": certs, "achievements": ach,
        "loaded": True,
    }


def save_onboarding(user_id, personal, education_list, experience_list,
                    projects_list, skills_list, certs_list, achievements_list):
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("""
        UPDATE users SET
            dob=%s, gender=%s, address=%s, city=%s, state=%s,
            linkedin_url=%s, github_url=%s, portfolio_url=%s,
            target_role=%s, experience_level=%s, about_me=%s,
            profile_completed=TRUE
        WHERE user_id=%s
    """, (personal.get("dob"), personal.get("gender"),
          personal.get("address"), personal.get("city"), personal.get("state"),
          personal.get("linkedin"), personal.get("github"), personal.get("portfolio"),
          personal.get("target_role"), personal.get("exp_level"),
          personal.get("about_me"), user_id))

    for tbl in ["education","experience","projects","skills","certifications","achievements"]:
        cur.execute(f"DELETE FROM {tbl} WHERE user_id=%s", (user_id,))

    for e in education_list:
        cur.execute("""INSERT INTO education
            (user_id,degree,institution,board_university,field_of_study,
             year_from,year_to,score,score_type,coursework)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, e.get("degree"), e.get("institution"), e.get("board"),
             e.get("field"), e.get("year_from"), e.get("year_to"),
             e.get("score"), e.get("score_type"), e.get("coursework")))

    for e in experience_list:
        cur.execute("""INSERT INTO experience
            (user_id,company,role,from_date,to_date,is_current,exp_type,description)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, e.get("company"), e.get("role"), e.get("from_date"),
             e.get("to_date"), e.get("is_current", False),
             e.get("exp_type"), e.get("description")))

    for p in projects_list:
        cur.execute("""INSERT INTO projects
            (user_id,title,tech_stack,description,github_url,live_url)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (user_id, p.get("title"), p.get("tech_stack"), p.get("description"),
             p.get("github_url"), p.get("live_url")))

    for s in skills_list:
        cur.execute("INSERT INTO skills (user_id,skill_name,category,proficiency) VALUES (%s,%s,%s,%s)",
                    (user_id, s.get("name"), s.get("category"), s.get("proficiency")))

    for c in certs_list:
        cur.execute("""INSERT INTO certifications
            (user_id,name,issuer,issue_year,credential_id,verify_url)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (user_id, c.get("name"), c.get("issuer"), c.get("year"),
             c.get("credential_id"), c.get("verify_url")))

    for a in achievements_list:
        cur.execute("INSERT INTO achievements (user_id,title,description,year) VALUES (%s,%s,%s,%s)",
                    (user_id, a.get("title"), a.get("description"), a.get("year")))

    conn.commit()
    conn.close()