import streamlit as st
import mysql.connector
import json
import time

from styles      import GLOBAL_CSS
from db          import get_conn, test_conn, load_full_profile
from auth        import (hash_pw, check_pw, log_login,
                         camera_to_array, save_face_image,
                         extract_embedding, cosine_sim, faces_match)
from onboarding  import render_onboarding
from dashboard   import render_dashboard
from resume      import render_resume
from chatbot     import render_chatbot

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Help Desk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────────────────────
if "db_config" not in st.session_state:
    st.session_state.db_config = {
        "host":"localhost","port":"3306",
        "user":"root","password":"bk123@","database":"faceauth"
    }
if "logged_in"       not in st.session_state: st.session_state.logged_in       = False
if "current_user"    not in st.session_state: st.session_state.current_user    = None
if "profile"         not in st.session_state: st.session_state.profile         = {"loaded":False}
if "active_module"   not in st.session_state: st.session_state.active_module   = None
if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1
if "reg_embedding"   not in st.session_state: st.session_state.reg_embedding   = None

# ══════════════════════════════════════════════════════════════════════════════
# ROUTING — logged in
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.logged_in:
    user = st.session_state.current_user

    if not st.session_state.profile.get("loaded"):
        load_full_profile(user["user_id"])

    if not bool(user.get("profile_completed")):
        render_onboarding()
        st.stop()

    module = st.session_state.active_module
    if   module == "resume":  render_resume()
    elif module == "chatbot": render_chatbot()
    else:                     render_dashboard()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;">
  <div style="font-size:3.5rem;filter:drop-shadow(0 0 25px #7c6fff88);margin-bottom:0.3rem;">🎓</div>
  <h1 style="font-size:2.4rem;font-weight:800;letter-spacing:-1.5px;margin:0;
             background:linear-gradient(135deg,#7c6fff,#ff6b9d);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
    Student Help Desk
  </h1>
  <p style="color:#606080;font-size:0.8rem;font-family:'JetBrains Mono',monospace;margin-top:6px;">
    face-auth · deepface · mysql · claude ai
  </p>
</div>""", unsafe_allow_html=True)

# DB Config
with st.expander("⚙️  Database Configuration", expanded=False):
    c1,c2 = st.columns([2,1])
    with c1:
        st.session_state.db_config["host"]     = st.text_input("Host",     st.session_state.db_config["host"],     key="db_host")
        st.session_state.db_config["user"]     = st.text_input("User",     st.session_state.db_config["user"],     key="db_user")
        st.session_state.db_config["database"] = st.text_input("Database", st.session_state.db_config["database"], key="db_name")
    with c2:
        st.session_state.db_config["port"]     = st.text_input("Port",     st.session_state.db_config["port"],     key="db_port")
        st.session_state.db_config["password"] = st.text_input("Password", st.session_state.db_config["password"], type="password", key="db_pass")
    if st.button("🔌  Test Connection", key="btn_test"):
        ok,msg = test_conn()
        st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

tab_login, tab_reg = st.tabs(["🔑  Login", "📝  Register"])

# ══════════════════════════════════════════════════════════════════════════════
# REGISTER
# ══════════════════════════════════════════════════════════════════════════════
with tab_reg:
    st.markdown('<div class="card"><div class="card-header">Create Account</div>',
                unsafe_allow_html=True)
    r_name  = st.text_input("Full Name",        placeholder="Ada Lovelace",    key="r_name")
    r_email = st.text_input("Email",            placeholder="ada@example.com", key="r_email")
    r_phone = st.text_input("Phone",            placeholder="+91 98765 43210", key="r_phone")
    r_pass  = st.text_input("Password",         type="password",               key="r_pass")
    r_pass2 = st.text_input("Confirm Password", type="password",               key="r_pass2")
    r_auth  = st.selectbox("Login Method",      ["manual","face_id","both"],   key="r_auth")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider">Face Registration — Live Camera</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="cam-hint">
      <span style="font-size:1.8rem;display:block;margin-bottom:0.4rem;">📸</span>
      Position your face clearly in the frame, then click <b>Take Photo</b>
    </div>""", unsafe_allow_html=True)

    reg_cam  = st.camera_input("", key="reg_cam")
    emb_slot = st.empty()

    if reg_cam:
        img_arr = camera_to_array(reg_cam)
        with st.spinner("Detecting face..."):
            emb, bk = extract_embedding(img_arr)
        if emb:
            st.session_state.reg_embedding = emb
            emb_slot.success(f"✅ Face detected via {bk} — {len(emb)} dims")
        else:
            st.session_state.reg_embedding = None
            emb_slot.error(f"❌ No face detected ({bk}) · Better lighting · Face camera · Move closer")

    if st.button("Create Account 🚀", key="btn_register"):
        errors = []
        if not r_name:  errors.append("Full name required")
        if not r_email: errors.append("Email required")
        if not r_pass:  errors.append("Password required")
        if r_pass != r_pass2: errors.append("Passwords do not match")
        if r_auth in ("face_id","both") and not st.session_state.reg_embedding:
            errors.append("Capture a face photo for Face ID")
        if errors:
            for e in errors: st.error(f"❌ {e}")
        else:
            try:
                conn = get_conn(); cur = conn.cursor()
                emb      = st.session_state.reg_embedding
                emb_json = json.dumps(emb) if emb else None
                img_path = save_face_image(reg_cam, r_email) if reg_cam else None
                cur.execute("""INSERT INTO users
                    (full_name,email,phone,password_hash,face_embedding,face_image_path,auth_method)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (r_name, r_email, r_phone, hash_pw(r_pass), emb_json, img_path, r_auth))
                uid = cur.lastrowid
                if emb:
                    cur.execute("INSERT INTO face_samples (user_id,embedding,image_path) VALUES (%s,%s,%s)",
                                (uid, emb_json, img_path))
                conn.commit(); conn.close()
                st.session_state.reg_embedding = None
                st.success("🎉 Account created! Go to Login.")
                st.balloons()
            except mysql.connector.IntegrityError:
                st.error("❌ Email already registered.")
            except Exception as ex:
                st.error(f"❌ {ex}")

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_login:
    mode = st.radio("Method", ["🔑  Password","🤳  Face ID"], horizontal=True, key="login_mode")

    if mode == "🔑  Password":
        st.markdown('<div class="card"><div class="card-header">Password Login</div>',
                    unsafe_allow_html=True)
        l_email = st.text_input("Email",    placeholder="ada@example.com", key="l_email")
        l_pass  = st.text_input("Password", type="password",               key="l_pass")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Login →", key="btn_login"):
            if not l_email or not l_pass:
                st.error("❌ Fill all fields.")
            else:
                try:
                    conn = get_conn(); cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE email=%s", (l_email,))
                    user = cur.fetchone(); conn.close()
                    if not user:
                        st.error("❌ Email not found.")
                    elif not check_pw(l_pass, user["password_hash"]):
                        log_login(user["user_id"],"manual","failed")
                        st.error("❌ Wrong password.")
                    else:
                        log_login(user["user_id"],"manual","success")
                        st.session_state.logged_in    = True
                        st.session_state.current_user = user
                        st.success("✅ Login successful!")
                        time.sleep(0.4); st.rerun()
                except Exception as ex:
                    st.error(f"❌ {ex}")
    else:
        st.markdown('<div class="card"><div class="card-header">Face ID Login</div>',
                    unsafe_allow_html=True)
        fi_email = st.text_input("Registered Email", placeholder="ada@example.com", key="fi_email")
        st.markdown("""
        <div class="cam-hint" style="margin-top:0.8rem;">
          <span style="font-size:1.5rem;display:block;">🤳</span>
          Look straight at the camera and click Take Photo
        </div>""", unsafe_allow_html=True)
        fi_cam = st.camera_input("", key="fi_cam")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Verify Face →", key="btn_face"):
            if not fi_email or not fi_cam:
                st.error("❌ Email and photo required.")
            else:
                try:
                    conn = get_conn(); cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT * FROM users WHERE email=%s", (fi_email,))
                    user = cur.fetchone()
                    if not user:
                        st.error("❌ Email not found."); conn.close()
                    elif not user.get("face_embedding"):
                        st.error("❌ No Face ID registered."); conn.close()
                    else:
                        cur.execute("SELECT embedding FROM face_samples WHERE user_id=%s",
                                    (user["user_id"],))
                        samples = cur.fetchall(); conn.close()
                        with st.spinner("Verifying face..."):
                            live_emb, bk = extract_embedding(camera_to_array(fi_cam))
                        if not live_emb:
                            log_login(user["user_id"],"face_id","failed")
                            st.error(f"❌ No face detected ({bk})")
                        else:
                            stored  = json.loads(user["face_embedding"])
                            matched = faces_match(live_emb, stored)
                            if not matched:
                                for s in samples:
                                    if faces_match(live_emb, json.loads(s["embedding"])):
                                        matched = True; break
                            sim = cosine_sim(live_emb, stored)
                            if matched:
                                log_login(user["user_id"],"face_id","success")
                                st.session_state.logged_in    = True
                                st.session_state.current_user = user
                                st.success(f"✅ Face verified! Similarity: {sim:.2%}")
                                time.sleep(0.4); st.rerun()
                            else:
                                log_login(user["user_id"],"face_id","failed")
                                st.error(f"❌ Face not recognised. Score: {sim:.2%} (need ≥70%)")
                except Exception as ex:
                    st.error(f"❌ {ex}")