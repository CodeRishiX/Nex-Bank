from datetime import datetime
import streamlit as st
import requests
from time import sleep
import requests.exceptions
import re
import pandas as pd
import json

# Display an animated success or error message with CSS animation
def animated_message(message, message_type="success"):
    placeholder = st.empty()
    with placeholder.container():
        if message_type == "success":
            st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
    sleep(2)
    placeholder.empty()

# Validate password strength
def validate_password_strength(password):
    errors = []
    if len(password) < 8:
        errors.append("At least 8 characters")
    if not any(char.isdigit() for char in password):
        errors.append("At least one number")
    if not any(char.islower() for char in password):
        errors.append("At least one lowercase letter")
    if not any(char.isupper() for char in password):
        errors.append("At least one uppercase letter")
    if not any(char in '@#$%^&+=!' for char in password):
        errors.append("At least one special character (@#$%^&+=!)")
    return len(errors) == 0, errors

# Generate password strength meter HTML
def password_requirements(password):
    requirements = [
        (len(password) >= 8, "At least 8 characters"),
        (any(char.isdigit() for char in password), "At least one number"),
        (any(char.islower() for char in password), "At least one lowercase letter"),
        (any(char.isupper() for char in password), "At least one uppercase letter"),
        (any(char in '@#$%^&+=!' for char in password), "At least one special character (@#$%^&+=!)")
    ]
    met_count = sum(1 for met, _ in requirements if met)
    total_requirements = len(requirements)
    unmet_requirements = [text for met, text in requirements if not met]
    progress_html = f"""
    <div class="password-strength-container">
        <div class="password-strength-header">
            <span>Password Strength</span>
            <span>{met_count}/{total_requirements}</span>
        </div>
        <div class="password-strength-meter">
            <div class="password-strength-progress" style="width: {met_count / total_requirements * 100}%"></div>
        </div>
    </div>
    """
    return progress_html, unmet_requirements

# Input validation functions
def validate_email(email):
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_pattern, email))

def validate_phone(phone):
    phone_pattern = r'^\d{10}$'
    return bool(re.match(phone_pattern, phone))

BACKEND_URL = "https://state-bank-of-india.onrender.com"

# Enhanced Custom CSS with modern animations
st.markdown("""
<style>
:root {
    --primary: #0d1b2a;
    --secondary: #00aaff;
    --neon-glow: #66d9ff;
    --accent: #b3d9ff;
    --background: #0a0f1c;
    --card-bg: rgba(20, 30, 50, 0.9);
    --text-color: #e0e7ff;
    --glass: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.15);
    --dark-blue: #1E3A8A;
    --neon-blue: #3B82F6;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, var(--background), #1b263b);
    font-family: 'Poppins', sans-serif;
    color: var(--text-color);
    overflow-x: hidden;
}

/* Floating particles animation */
.particles {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    pointer-events: none;
}

.particle {
    position: absolute;
    background: rgba(100, 200, 255, 0.5);
    border-radius: 50%;
    animation: float linear infinite;
}

@keyframes float {
    0% {
        transform: translateY(0) translateX(0);
        opacity: 1;
    }
    100% {
        transform: translateY(-100vh) translateX(20vw);
        opacity: 0;
    }
}

/* Main header with enhanced animation */
h1 {
    font-family: 'Orbitron', sans-serif;
    color: var(--secondary);
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.5), 0 0 20px rgba(0, 212, 255, 0.3);
    text-align: center;
    margin: 0;
    font-size: 3rem;
    letter-spacing: 2px;
    padding: 0.5rem 0;
    animation: glow 2s ease-in-out infinite alternate, floatTitle 6s ease-in-out infinite;
    position: relative;
}

@keyframes floatTitle {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-10px);
    }
}

@keyframes glow {
    from { 
        text-shadow: 0 0 5px var(--secondary), 0 0 10px var(--secondary); 
    }
    to { 
        text-shadow: 0 0 15px var(--secondary), 0 0 30px var(--secondary), 0 0 45px var(--secondary); 
    }
}

/* Hero section with animated gradient */
.hero-container {
    position: relative;
    padding: 2rem;
    border-radius: 20px;
    margin: 2rem 0;
    background: linear-gradient(135deg, rgba(13, 27, 42, 0.8), rgba(0, 170, 255, 0.3));
    border: 1px solid rgba(0, 170, 255, 0.2);
    box-shadow: 0 0 30px rgba(0, 170, 255, 0.1);
    overflow: hidden;
    animation: gradientPulse 8s ease infinite;
}

@keyframes gradientPulse {
    0% {
        background: linear-gradient(135deg, rgba(13, 27, 42, 0.8), rgba(0, 170, 255, 0.3));
    }
    50% {
        background: linear-gradient(135deg, rgba(13, 27, 42, 0.8), rgba(0, 170, 255, 0.5));
    }
    100% {
        background: linear-gradient(135deg, rgba(13, 27, 42, 0.8), rgba(0, 170, 255, 0.3));
    }
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        to bottom right,
        transparent 0%,
        rgba(0, 170, 255, 0.1) 50%,
        transparent 100%
    );
    animation: shine 6s infinite;
    transform: rotate(30deg);
}

@keyframes shine {
    0% {
        transform: translateX(-100%) rotate(30deg);
    }
    100% {
        transform: translateX(100%) rotate(30deg);
    }
}

.hero-text {
    font-size: 1.4rem;
    line-height: 1.6;
    margin-bottom: 2rem;
    color: rgba(255, 255, 255, 0.85);
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
    position: relative;
    z-index: 1;
}

/* Feature cards with 3D tilt effect */
.feature-container {
    display: flex;
    justify-content: space-between;
    margin: 3rem 0;
    gap: 2rem;
    perspective: 1000px;
}

.feature-card {
    flex: 1;
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    transition: all 0.4s ease;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border: 1px solid var(--glass-border);
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
    transform-style: preserve-3d;
    position: relative;
}

.feature-card:hover {
    transform: translateY(-8px) scale(1.02) rotateX(5deg) rotateY(5deg);
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
    border-color: var(--accent);
}

.feature-icon {
    font-size: 3.5rem;
    margin-bottom: 1.5rem;
    color: var(--secondary);
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    animation: pulse 1.5s infinite, floatIcon 4s ease-in-out infinite;
}

@keyframes floatIcon {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-10px);
    }
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

.feature-card h3 {
    margin-bottom: 1rem;
    color: var(--text-color);
    font-weight: 600;
    text-shadow: 0 0 5px rgba(0, 212, 255, 0.3);
}

.feature-card p {
    color: rgba(255, 255, 255, 0.7);
}

/* Main action buttons with wave effect */
.main-action-btn {
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
    z-index: 1;
}

.main-action-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, var(--primary), var(--secondary));
    z-index: -1;
    transition: all 0.4s ease;
}

.main-action-btn:hover::before {
    background: linear-gradient(45deg, var(--secondary), var(--accent));
}

.main-action-btn::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 5px;
    height: 5px;
    background: rgba(255, 255, 255, 0.5);
    opacity: 0;
    border-radius: 100%;
    transform: scale(1, 1) translate(-50%);
    transform-origin: 50% 50%;
}

.main-action-btn:focus:not(:active)::after {
    animation: ripple 1s ease-out;
}

@keyframes ripple {
    0% {
        transform: scale(0, 0);
        opacity: 0.5;
    }
    100% {
        transform: scale(20, 20);
        opacity: 0;
    }
}

/* Password strength meter */
.password-strength-container {
    margin-top: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 1rem;
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.password-strength-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: var(--text-color);
}

.password-strength-meter {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    margin-bottom: 1rem;
    overflow: hidden;
}

.password-strength-progress {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #8BC34A);
    transition: width 0.3s ease;
}

/* Streamlit buttons customization */
.stButton > button {
    background: linear-gradient(45deg, var(--primary), var(--secondary));
    color: white;
    border: 2px solid var(--secondary);
    padding: 1rem 2rem;
    font-size: 1.2rem;
    font-weight: 700;
    font-family: 'Poppins', sans-serif;
    border-radius: 30px;
    transition: all 0.4s ease;
    box-shadow: 0 0 5px rgba(0, 212, 255, 0.2), inset 0 0 3px rgba(0, 212, 255, 0.1);
    position: relative;
    overflow: hidden;
    width: 100%;
    margin: 0.5rem 0;
}

.stButton > button:hover {
    transform: scale(1.05) translateY(-3px);
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.3), 0 0 20px rgba(0, 212, 255, 0.2);
    background: linear-gradient(45deg, var(--secondary), var(--accent));
    border-color: white;
    filter: brightness(0.9);
}

/* Hide Streamlit menu and live indicator */
.st-emotion-cache-1avcm0n, .st-emotion-cache-1dp5vir {
    display: none !important;
}

/* Remove blinking cursor from input fields */
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    caret-color: transparent;
    outline: none;
    box-shadow: none;
}

/* Loading animation */
.progress-container {
    width: 100%;
    max-width: 400px;
    margin: 1rem auto;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.progress-bar {
    width: 100%;
    max-width: 400px;
    height: 40px;
    background: linear-gradient(90deg, #1E3A8A, #3B82F6);
    border-radius: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-family: 'Poppins', sans-serif;
    font-size: 1.2rem;
    font-weight: 500;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}

.progress-bar::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 0;
    background: rgba(255, 255, 255, 0.3);
    animation: fill-from-middle 2s infinite ease-in-out;
}

@keyframes fill-from-middle {
    0% {
        width: 0;
        left: 50%;
        transform: translateX(-50%);
    }
    50% {
        width: 100%;
        left: 0;
        transform: none;
    }
    100% {
        width: 0;
        left: 50%;
        transform: translateX(-50%);
    }
}

/* Animation for Success/Failure Messages */
@keyframes fadeInOut {
    0% { opacity: 0; transform: translateY(20px); }
    20% { opacity: 1; transform: translateY(0); }
    80% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-20px); }
}

.success-message, .error-message {
    animation: fadeInOut 2s ease-in-out forwards;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    font-weight: 500;
    font-size: 1.1rem;
}

.success-message {
    background: rgba(76, 175, 80, 0.2);
    border: 1px solid #4CAF50;
    color: #4CAF50;
}

.error-message {
    background: rgba(244, 67, 54, 0.2);
    border: 1px solid #F44336;
    color: #F44336;
}

.glass-panel {
    background: var(--glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.1);
}

/* Styled Transaction History Table */
.stDataFrame {
    width: 100%;
    overflow-x: auto;
}

.stDataFrame table {
    width: 100%;
    border-collapse: collapse;
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: 10px;
    overflow: hidden;
}

.stDataFrame th, .stDataFrame td {
    padding: 0.75rem;
    text-align: left;
    color: var(--text-color);
    border-bottom: 1px solid var(--glass-border);
}

.stDataFrame th {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    color: white;
    font-weight: 600;
}

.stDataFrame tr:hover {
    background: rgba(255, 255, 255, 0.05);
}

@media (max-width: 768px) {
    .feature-container {
        flex-direction: column;
        gap: 1.5rem;
    }
    h1 {
        font-size: 2.2rem;
    }
    .hero-text {
        font-size: 1.2rem;
    }
    .stButton > button {
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
    }
    .progress-container {
        max-width: 300px;
    }
    .progress-bar {
        max-width: 300px;
        height: 35px;
        font-size: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Add floating particles to the background
def add_particles():
    if "particles_added" not in st.session_state:
        st.session_state.particles_added = False

    if not st.session_state.particles_added:
        particles_html = """
        <div class="particles" id="particles-js"></div>
        <script>
            // Check if particles are already added
            if (!document.getElementById('particles-js') || document.getElementById('particles-js').childElementCount > 0) {
                return;
            }

            const particles = document.getElementById('particles-js');
            const particleCount = 30;

            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');

                const size = Math.random() * 4 + 2;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;

                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100 + 100}%`;

                const duration = Math.random() * 10 + 10;
                particle.style.animationDuration = `${duration}s`;

                particle.style.animationDelay = `${Math.random() * 5}s`;

                particles.appendChild(particle);
            }
        </script>
        """
        st.markdown(particles_html, unsafe_allow_html=True)
        st.session_state.particles_added = True

# Display the app header with enhanced animation
def app_header():
    st.markdown("""
    <h1>
        <span style="display: inline-block; animation: floatTitle 6s ease-in-out infinite;">🏦</span>
        <span style="display: inline-block; animation: floatTitle 6s ease-in-out infinite 0.2s;">Nex</span>
        <span style="display: inline-block; animation: floatTitle 6s ease-in-out infinite 0.4s;">Bank</span>
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("---")

# Initialize session state variables
if "token" not in st.session_state:
    st.session_state.update({
        "token": None,
        "accnumber": None,
        "email": None,
        "balance": None,
        "show_otp_input": False,
        "transfer_otp_requested": False,
        "current_page": "main",
        "reg_stage": 1,
        "forgot_pwd_stage": 1,
        "reg_data": {},
        "forgot_data": {},
        "login_data": {},
        "transaction_history": None,
        "dashboard_section": "welcome",
        "loading": False,
        "reg_pwd1": "",
        "forgot_pwd1": "",
        "otp_attempts": {},
        "security_answer_attempts": {},
        "particles_added": False
    })

# Rate limiting for OTP requests and security answer attempts
MAX_ATTEMPTS = 5
ATTEMPT_WINDOW = 3600  # 1 hour in seconds

def check_rate_limit(user_id, attempt_type):
    current_time = datetime.now().timestamp()
    attempts = st.session_state[attempt_type].get(user_id, [])
    attempts = [t for t in attempts if current_time - t < ATTEMPT_WINDOW]
    st.session_state[attempt_type][user_id] = attempts
    if len(attempts) >= MAX_ATTEMPTS:
        return False
    attempts.append(current_time)
    st.session_state[attempt_type][user_id] = attempts
    return True

# Main app structure
app_header()
add_particles()

# Main Menu (shown when not logged in)
if not st.session_state.token and st.session_state.current_page == "main":
    with st.container():
        st.markdown("""
        <div class="hero-container">
            <h2 style="color: var(--secondary); margin-bottom: 1.5rem; text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);">
                Next-Gen Banking Awaits
            </h2>
            <p class="hero-text">
                Experience banking reimagined with our cutting-edge platform that combines 
                <span style="color: var(--neon-glow); font-weight: 600;">quantum-grade security</span>, 
                <span style="color: var(--neon-glow); font-weight: 600;">lightning-fast transactions</span>, and 
                <span style="color: var(--neon-glow); font-weight: 600;">seamless accessibility</span>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-container">
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>Quantum Security</h3>
            <p>Hashed OTPs with env-secured credentials and rate-limiting</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Lightning Transfers</h3>
            <p>Instant global transactions with near-zero latency</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🌌</div>
            <h3>Cosmic Access</h3>
            <p>Bank from anywhere with our space-grade infrastructure</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📝 Registration", key="reg_btn"):
            st.session_state.current_page = "register"
            st.session_state.reg_stage = 1
            st.rerun()
    with col2:
        if st.button("🔐 Login", key="login_btn"):
            st.session_state.current_page = "login"
            st.rerun()
    with col3:
        if st.button("🔑 Forgot Password", key="forgot_btn"):
            st.session_state.current_page = "forgot_pwd"
            st.session_state.forgot_pwd_stage = 1
            st.rerun()

# Registration Flow
elif st.session_state.current_page == "register":
    st.header("New Account Registration")
    if st.session_state.reg_stage == 1:
        with st.form("reg_init"):
            st.subheader("Step 1: Account Details")
            reg_acc = st.text_input("Account Number", key="reg_acc")
            reg_email_input = st.text_input("Email Address", key="reg_email")
            if st.form_submit_button("Send Verification OTP"):
                if not reg_acc:
                    st.error("Account number cannot be empty.")
                elif not reg_email_input:
                    st.error("Email address cannot be empty.")
                elif not validate_email(reg_email_input):
                    st.error("Please enter a valid email address.")
                else:
                    user_id = reg_acc
                    if not check_rate_limit(user_id, "otp_attempts"):
                        st.error("Too many OTP requests. Please try again later.")
                    else:
                        st.session_state.loading = True
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-bar">Requesting OTP</div>
                        </div>
                        """, unsafe_allow_html=True)
                        sleep(1)
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/register/init",
                                params={"accountNumber": reg_acc, "email": reg_email_input}
                            )
                            response.raise_for_status()
                            response_data = response.json()
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if response_data.get("status") == "success":
                                st.session_state.reg_data = {"reg_acc": reg_acc, "reg_email": reg_email_input}
                                animated_message("OTP sent to registered email!")
                                st.session_state.reg_stage = 2
                                st.rerun()
                            else:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(f"Registration failed: {response_data.get('message', 'Unknown error')}")
                        except requests.exceptions.HTTPError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if e.response.status_code == 400:
                                try:
                                    response_data = e.response.json()
                                    st.error(
                                        f"Registration failed: {response_data.get('message', 'Invalid account number or email')}")
                                except ValueError:
                                    st.error("Registration failed: Invalid response from server.")
                            else:
                                st.error(f"Registration failed: {str(e)}")
                        except requests.exceptions.RequestException as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Registration failed: {str(e)}")
                        except ValueError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Registration failed: Invalid JSON response: {str(e)}")

    elif st.session_state.reg_stage == 2:
        with st.form("reg_complete"):
            st.subheader("Step 2: Complete Registration")
            reg_acc = st.session_state.reg_data.get("reg_acc", "")
            reg_email = st.session_state.reg_data.get("reg_email", "")
            reg_otp = st.text_input("Verification OTP", key="reg_otp")
            sec_question = st.selectbox(
                "Security Question",
                ["What is your pet's name?", "What is your mother's maiden name?",
                 "What is the name of your first school?"],
                index=0,
                key="sec_question"
            )
            question_choices = {
                "What is your pet's name?": 1,
                "What is your mother's maiden name?": 2,
                "What is the name of your first school?": 3
            }
            security_question_choice = question_choices[sec_question]
            sec_answer = st.text_input("Security Answer", key="sec_answer")
            pwd1 = st.text_input("Password", type="password", key="reg_pwd1")
            pwd2 = st.text_input("Confirm Password", type="password", key="reg_pwd2")

            if pwd1:
                progress_html, unmet_requirements = password_requirements(pwd1)
                st.markdown(progress_html, unsafe_allow_html=True)
                if unmet_requirements:
                    st.error("Password does not meet the following requirements:\n- " + "\n- ".join(unmet_requirements))

            if st.form_submit_button("Complete Registration"):
                if not reg_otp:
                    st.error("OTP cannot be empty.")
                elif not sec_answer:
                    st.error("Security answer cannot be empty.")
                elif not pwd1 or not pwd2:
                    st.error("Password fields cannot be empty.")
                else:
                    st.session_state.loading = True
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <div class="progress-container">
                        <div class="progress-bar">Completing Registration</div>
                    </div>
                    """, unsafe_allow_html=True)
                    sleep(1)
                    if pwd1 != pwd2:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error("Passwords do not match!")
                    else:
                        is_strong, strength_errors = validate_password_strength(pwd1)
                        if not is_strong:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(
                                "Password does not meet the following requirements:\n- " + "\n- ".join(strength_errors))
                        else:
                            try:
                                response = requests.post(
                                    f"{BACKEND_URL}/register/complete",
                                    params={
                                        "accountNumber": reg_acc,
                                        "otp": reg_otp,
                                        "securityQuestionChoice": security_question_choice,
                                        "securityAnswer": sec_answer,
                                        "password1": pwd1,
                                        "password2": pwd2,
                                        "email": reg_email
                                    }
                                )
                                response.raise_for_status()
                                response_data = response.json()
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                if response_data.get("status") == "success":
                                    animated_message("Registration successful! Redirecting to main menu...")
                                    sleep(2)
                                    st.session_state.reg_data = {}
                                    st.session_state.current_page = "main"
                                    st.session_state.reg_stage = 1
                                    st.rerun()
                                else:
                                    st.session_state.loading = False
                                    loading_placeholder.empty()
                                    st.error(f"Registration failed: {response_data.get('message', 'Unknown error')}")
                            except requests.exceptions.HTTPError as e:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                if e.response.status_code == 400:
                                    try:
                                        response_data = e.response.json()
                                        st.error(
                                            f"Registration failed: {response_data.get('message', 'Invalid OTP or security answer')}")
                                    except ValueError:
                                        st.error("Registration failed: Invalid response from server.")
                                else:
                                    st.error(f"Registration failed: {str(e)}")
                            except requests.exceptions.RequestException as e:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(f"Registration failed: {str(e)}")
                            except ValueError as e:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(f"Registration failed: Invalid JSON response: {str(e)}")

        if st.button("← Back to Main Menu"):
            st.session_state.reg_data = {}
            st.session_state.current_page = "main"
            st.session_state.reg_stage = 1
            st.rerun()

# Login Flow
elif st.session_state.current_page == "login":
    st.header("Login to Your Account")
    if not st.session_state.show_otp_input:
        with st.form("login_init"):
            accnumber = st.text_input("Account Number", key="login_acc")
            password = st.text_input("Password", type="password", key="login_pwd")
            if st.form_submit_button("Request OTP"):
                if not accnumber:
                    st.error("Account number cannot be empty.")
                elif not password:
                    st.error("Password cannot be empty.")
                else:
                    user_id = accnumber
                    if not check_rate_limit(user_id, "otp_attempts"):
                        st.error("Too many OTP requests. Please try again later.")
                    else:
                        st.session_state.loading = True
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-bar">Requesting OTP</div>
                        </div>
                        """, unsafe_allow_html=True)
                        sleep(1)
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/login/request-otp",
                                params={"accnumber": accnumber, "password": password}
                            )
                            response.raise_for_status()
                            response_data = response.json()
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if response_data.get("status") == "success":
                                st.session_state.login_data = {"accnumber": accnumber, "password": password}
                                animated_message("OTP sent to registered email!")
                                st.session_state.show_otp_input = True
                                st.rerun()
                            else:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(f"Login failed: {response_data.get('message', 'Unknown error')}")
                        except requests.exceptions.HTTPError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if e.response.status_code == 400:
                                try:
                                    response_data = e.response.json()
                                    st.error(
                                        f"Login failed: {response_data.get('message', 'Invalid account number or password')}")
                                except ValueError:
                                    st.error("Login failed: Invalid response from server.")
                            else:
                                st.error(f"Login failed: {str(e)}")
                        except requests.exceptions.RequestException as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Login failed: {str(e)}")
                        except ValueError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Login failed: Invalid JSON response: {str(e)}")
    else:
        with st.form("login_verify"):
            otp = st.text_input("Enter OTP", key="login_otp")
            login_accnumber = st.session_state.login_data.get("accnumber", "")
            login_password = st.session_state.login_data.get("password", "")
            if st.form_submit_button("Verify OTP"):
                if not otp:
                    st.error("OTP cannot be empty.")
                else:
                    st.session_state.loading = True
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <div class="progress-container">
                        <div class="progress-bar">Verifying OTP</div>
                    </div>
                    """, unsafe_allow_html=True)
                    sleep(1)
                    try:
                        verify_response = requests.post(
                            f"{BACKEND_URL}/login/verify",
                            params={"accnumber": login_accnumber, "password": login_password, "otp": otp}
                        )
                        verify_response.raise_for_status()
                        response_data = verify_response.json()
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        if response_data.get("status") == "success":
                            st.session_state.token = response_data["token"]
                            st.session_state.accnumber = response_data["accnumber"]
                            st.session_state.email = response_data["email"]
                            st.session_state.balance = response_data["balance"]
                            st.session_state.login_data = {}
                            animated_message("Login successful! Redirecting to dashboard...")
                            sleep(2)
                            st.session_state.current_page = "main"
                            st.rerun()
                        else:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Verification failed: {response_data.get('message', 'Unknown error')}")
                    except requests.exceptions.HTTPError as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        if e.response.status_code == 400:
                            try:
                                response_data = e.response.json()
                                st.error(f"Verification failed: {response_data.get('message', 'Invalid OTP')}")
                            except ValueError:
                                st.error("Verification failed: Invalid response from server.")
                        else:
                            st.error(f"Verification failed: {str(e)}")
                    except requests.exceptions.RequestException as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error(f"Verification failed: {str(e)}")
                    except ValueError as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error(f"Verification failed: Invalid JSON response: {str(e)}")

    if st.button("← Back to Main Menu"):
        st.session_state.login_data = {}
        st.session_state.current_page = "main"
        st.session_state.show_otp_input = False
        st.rerun()

# Forgot Password Flow
elif st.session_state.current_page == "forgot_pwd":
    st.header("Forgot Password")
    if st.session_state.forgot_pwd_stage == 1:
        with st.form("forgot_init"):
            st.subheader("Step 1: Verify Account")
            forgot_acc = st.text_input("Account Number", key="forgot_acc")
            forgot_phone = st.text_input("Phone Number", key="forgot_phone")
            if st.form_submit_button("Get Security Question"):
                if not forgot_acc:
                    st.error("Account number cannot be empty.")
                elif not forgot_phone:
                    st.error("Phone number cannot be empty.")
                elif not validate_phone(forgot_phone):
                    st.error("Please enter a valid 10-digit phone number.")
                else:
                    st.session_state.loading = True
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <div class="progress-container">
                        <div class="progress-bar">Fetching Security Question</div>
                    </div>
                    """, unsafe_allow_html=True)
                    sleep(1)
                    try:
                        response = requests.get(
                            f"{BACKEND_URL}/get-security-question",
                            params={"accountNumber": forgot_acc, "phoneNumber": forgot_phone}
                        )
                        response.raise_for_status()
                        response_data = response.json()
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        if response_data.get("question"):
                            st.session_state.forgot_data = {
                                "forgot_acc": forgot_acc,
                                "forgot_phone": forgot_phone,
                                "security_question": response_data["question"],
                                "answer_hash": response_data["answerHash"]
                            }
                            animated_message(f"Security Question: {response_data['question']}")
                            st.session_state.forgot_pwd_stage = 2
                            st.rerun()
                        else:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(
                                f"Failed to retrieve security question: {response_data.get('message', 'Unknown error')}")
                    except requests.exceptions.HTTPError as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        if e.response.status_code == 404:
                            st.error("Account not found. Please check your account number or phone number.")
                        else:
                            st.error(f"Failed to retrieve security question: {str(e)}")
                    except requests.exceptions.RequestException as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error(f"Failed to retrieve security question: {str(e)}")
                    except ValueError as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error(f"Failed to retrieve security question: Invalid JSON response: {str(e)}")

    elif st.session_state.forgot_pwd_stage == 2:
        with st.form("forgot_verify"):
            st.subheader("Step 2: Verify Security Answer")
            forgot_acc = st.session_state.forgot_data.get("forgot_acc", "")
            forgot_phone = st.session_state.forgot_data.get("forgot_phone", "")
            security_question = st.session_state.forgot_data.get("security_question", "")
            st.write(f"Security Question: {security_question}")
            answer = st.text_input("Your Answer", key="forgot_answer")
            if st.form_submit_button("Verify Answer"):
                if not answer:
                    st.error("Security answer cannot be empty.")
                else:
                    user_id = forgot_acc
                    if not check_rate_limit(user_id, "security_answer_attempts"):
                        st.error("Too many attempts. Please try again later.")
                    else:
                        st.session_state.loading = True
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-bar">Verifying Answer</div>
                        </div>
                        """, unsafe_allow_html=True)
                        sleep(1)
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/verify-security-answer",
                                json={"accountNumber": forgot_acc, "answer": answer}
                            )
                            response.raise_for_status()
                            response_data = response.json()
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if response_data.get("status") == "success":
                                animated_message("OTP sent to registered email!")
                                st.session_state.forgot_pwd_stage = 3
                                st.rerun()
                            else:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(
                                    f"Failed to verify security answer: {response_data.get('message', 'Unknown error')}")
                        except requests.exceptions.HTTPError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if e.response.status_code == 400:
                                try:
                                    response_data = e.response.json()
                                    message = response_data.get("message", "Unknown error")
                                    if "incorrect security answer" in message.lower():
                                        st.error("Incorrect security answer. Please try again.")
                                    else:
                                        st.error(f"Failed to verify security answer: {message}")
                                except ValueError:
                                    st.error("Failed to verify security answer: Invalid response from server.")
                            else:
                                st.error(f"Failed to verify security answer: {str(e)}")
                        except requests.exceptions.RequestException as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Failed to verify security answer: {str(e)}")
                        except ValueError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Failed to verify security answer: Invalid JSON response: {str(e)}")

    elif st.session_state.forgot_pwd_stage == 3:
        with st.form("forgot_reset"):
            st.subheader("Step 3: Reset Password")
            forgot_acc = st.session_state.forgot_data.get("forgot_acc", "")
            otp = st.text_input("Enter OTP", key="forgot_otp")
            new_pwd1 = st.text_input("New Password", type="password", key="forgot_pwd1")
            new_pwd2 = st.text_input("Confirm New Password", type="password", key="forgot_pwd2")

            if new_pwd1:
                progress_html, unmet_requirements = password_requirements(new_pwd1)
                st.markdown(progress_html, unsafe_allow_html=True)
                if unmet_requirements:
                    st.error("Password does not meet the following requirements:\n- " + "\n- ".join(unmet_requirements))

            if st.form_submit_button("Reset Password"):
                if not otp:
                    st.error("OTP cannot be empty.")
                elif not new_pwd1 or not new_pwd2:
                    st.error("Password fields cannot be empty.")
                else:
                    st.session_state.loading = True
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <div class="progress-container">
                        <div class="progress-bar">Resetting Password</div>
                    </div>
                    """, unsafe_allow_html=True)
                    sleep(1)
                    if new_pwd1 != new_pwd2:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error("Passwords do not match!")
                    else:
                        is_strong, strength_errors = validate_password_strength(new_pwd1)
                        if not is_strong:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(
                                "Password does not meet the following requirements:\n- " + "\n- ".join(strength_errors))
                        else:
                            try:
                                response = requests.post(
                                    f"{BACKEND_URL}/reset-password",
                                    json={
                                        "accountNumber": forgot_acc,
                                        "otp": otp,
                                        "newPassword": new_pwd1,
                                    }
                                )
                                response.raise_for_status()
                                response_data = response.json()
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                if response_data.get("status") == "success":
                                    animated_message("Password reset successful! Redirecting to login...")
                                    sleep(2)
                                    st.session_state.forgot_data = {}
                                    st.session_state.current_page = "login"
                                    st.session_state.forgot_pwd_stage = 1
                                    st.rerun()
                                else:
                                    st.session_state.loading = False
                                    loading_placeholder.empty()
                                    st.error(f"Password reset failed: {response_data.get('message', 'Unknown error')}")
                            except requests.exceptions.HTTPError as e:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                if e.response.status_code == 400:
                                    try:
                                        response_data = e.response.json()
                                        message = response_data.get("message", "Invalid OTP")
                                        if "otp" in message.lower():
                                            st.error("Invalid OTP. Please try again.")
                                        else:
                                            st.error(f"Password reset failed: {message}")
                                    except ValueError:
                                        st.error("Invalid OTP. Please try again.")
                                else:
                                    st.error(f"Password reset failed: {str(e)}")
                            except requests.exceptions.RequestException as e:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(f"Password reset failed: {str(e)}")
                            except ValueError as e:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(f"Password reset failed: Invalid JSON response: {str(e)}")

        if st.button("← Back to Main Menu"):
            st.session_state.forgot_data = {}
            st.session_state.current_page = "main"
            st.session_state.forgot_pwd_stage = 1
            st.rerun()

# Logged-in Dashboard
elif st.session_state.token:
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
        <div class="glass-panel" style="text-align: center;">
            <h3>💰 Account Balance</h3>
            <h2>₹{st.session_state.balance:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
        <div class="glass-panel" style="text-align: center;">
            <h3>👤 Account Holder</h3>
            <p style="font-size: 1.2rem;">{st.session_state.email}</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""
        <div class="glass-panel" style="text-align: center;">
            <h3>🔢 Account Number</h3>
            <p style="font-size: 1.2rem;">{st.session_state.accnumber}</p>
        </div>
        """, unsafe_allow_html=True)

    quick_cols = st.columns(3)
    with quick_cols[0]:
        if st.button("💸 New Transfer", key="quick_transfer"):
            st.session_state.dashboard_section = "transfer"
            st.rerun()
    with quick_cols[1]:
        if st.button("📜 View History", key="quick_history"):
            st.session_state.dashboard_section = "history"
            st.rerun()
    with quick_cols[2]:
        if st.button("📧 Send Statement", key="quick_statement"):
            st.session_state.dashboard_section = "statement"
            st.rerun()

    if st.session_state.dashboard_section == "welcome":
        st.markdown("""
        <div class="glass-panel" style="text-align: center; margin-bottom: 0;">
            <h3>Welcome to Your Dashboard</h3>
            <p style="font-size: 1.2rem;">Select an action above to manage your account.</p>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.dashboard_section == "transfer":
        with st.container():
            st.markdown("""
            <div style="text-align: center; margin-bottom: 0.5rem;">
                <p style="font-size: 1.2rem; color: var(--text-color);">
                    Securely transfer funds to any account.
                </p>
            </div>
            """, unsafe_allow_html=True)
          ##  st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.header("💸 Transfer Funds")
            to_account = st.text_input("To Account Number", key="transfer_to")
            amount = st.number_input("Amount", min_value=0.01, key="transfer_amount")

            if st.button("Request Transfer OTP", key="transfer_req_otp"):
                if not to_account:
                    st.error("To account number cannot be empty.")
                elif amount <= 0:
                    st.error("Amount must be greater than 0.")
                else:
                    user_id = st.session_state.accnumber
                    if not check_rate_limit(user_id, "otp_attempts"):
                        st.error("Too many OTP requests. Please try again later.")
                    else:
                        st.session_state.loading = True
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-bar">Requesting OTP</div>
                        </div>
                        """, unsafe_allow_html=True)
                        sleep(1)
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/transfer/request-otp",
                                params={
                                    "fromAccount": st.session_state.accnumber,
                                    "toAccount": to_account,
                                    "amount": amount
                                }
                            )
                            response.raise_for_status()
                            response_data = response.json()
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if response_data.get("status") == "success":
                                animated_message("OTP sent to your email!")
                                st.session_state.transfer_otp_requested = True
                            else:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(
                                    f"Failed to request transfer OTP: {response_data.get('message', 'Unknown error')}")
                        except requests.exceptions.HTTPError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if e.response.status_code == 400:
                                try:
                                    response_data = e.response.json()
                                    st.error(
                                        f"Failed to request transfer OTP: {response_data.get('message', 'Invalid account or amount')}")
                                except ValueError:
                                    st.error("Failed to request transfer OTP: Invalid response from server.")
                            else:
                                st.error(f"Failed to request transfer OTP: {str(e)}")
                        except requests.exceptions.RequestException as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Failed to request transfer OTP: {str(e)}")
                        except ValueError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Failed to request transfer OTP: Invalid JSON response: {str(e)}")

            if st.session_state.transfer_otp_requested:
                transfer_otp = st.text_input("Enter Transfer OTP", key="transfer_otp")
                if st.button("Confirm Transfer", key="transfer_confirm"):
                    if not transfer_otp:
                        st.error("Transfer OTP cannot be empty.")
                    else:
                        st.session_state.loading = True
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                        <div class="progress-container">
                            <div class="progress-bar">Confirming Transfer</div>
                        </div>
                        """, unsafe_allow_html=True)
                        sleep(1)
                        headers = {
                            "Authorization": f"Bearer {st.session_state.token}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "fromAccount": st.session_state.accnumber,
                            "toAccount": to_account,
                            "amount": amount,
                            "otp": transfer_otp
                        }
                        try:
                            transfer_response = requests.post(
                                f"{BACKEND_URL}/transfer",
                                json=payload,
                                headers=headers
                            )
                            transfer_response.raise_for_status()
                            response_data = transfer_response.json()
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if response_data.get("status") == "success":
                                st.session_state.balance -= amount
                                st.session_state.transfer_otp_requested = False
                                animated_message("✅ Transfer successful! Balance updated.")
                                st.balloons()
                                st.session_state.dashboard_section = "welcome"
                                st.rerun()
                            else:
                                st.session_state.loading = False
                                loading_placeholder.empty()
                                st.error(f"Transfer failed: {response_data.get('message', 'Unknown error')}")
                        except requests.exceptions.HTTPError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            if e.response.status_code == 400:
                                try:
                                    response_data = e.response.json()
                                    message = response_data.get("message", "Unknown error")
                                    if "fraudulent" in message.lower():
                                        st.error("Transaction failed: Fraud detected by ML model.")
                                    else:
                                        st.error(f"Transfer failed: {message}")
                                except ValueError:
                                    st.error("Transfer failed: Invalid response from server.")
                            else:
                                st.error(f"Transfer failed: {str(e)}")
                        except requests.exceptions.RequestException as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Transfer failed: {str(e)}")
                        except ValueError as e:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Transfer failed: Invalid JSON response: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.dashboard_section == "history":
        with st.container():
            st.markdown("""
            <div style="text-align: center; margin-bottom: 0.5rem;">
                <p style="font-size: 1.2rem; color: var(--text-color);">
                    View your recent transactions here.
                </p>
            </div>
            """, unsafe_allow_html=True)
           ## st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.header("📜 Transaction History")
            if st.button("View Transaction History Live", key="view_history"):
                st.session_state.loading = True
                loading_placeholder = st.empty()
                loading_placeholder.markdown("""
                <div class="progress-container">
                    <div class="progress-bar">Fetching Transaction History</div>
                </div>
                """, unsafe_allow_html=True)
                sleep(1)
                headers = {
                    "Authorization": f"Bearer {st.session_state.token}"
                }
                try:
                    response = requests.get(
                        f"{BACKEND_URL}/get-transaction-history",
                        headers=headers,
                        params={"accountNumber": st.session_state.accnumber}
                    )
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.loading = False
                    loading_placeholder.empty()
                    if response.status_code == 200:
                        history_data = data.get("history")
                        if isinstance(history_data, str):
                            # Parse the string into a list of dictionaries
                            lines = history_data.strip().split('\n')
                            if len(lines) < 2:  # At least header and one row
                                st.session_state.transaction_history = []
                            else:
                                # Extract headers and rows
                                headers = [h.strip() for h in lines[0].split('|')]
                                rows = []
                                for line in lines[2:]:  # Skip header and separator line
                                    if line.strip():
                                        values = [v.strip() for v in line.split('|')]
                                        if len(values) == len(headers):
                                            row_dict = dict(zip(headers, values))
                                            # Map to expected column names
                                            mapped_row = {
                                                "date": row_dict.get("Date and Time", ""),
                                                "fromAccount": row_dict.get("Sender", ""),
                                                "toAccount": row_dict.get("Receiver", ""),
                                                "amount": float(row_dict.get("Amount", 0.0)),
                                                "status": row_dict.get("Status", "")
                                            }
                                            rows.append(mapped_row)
                                st.session_state.transaction_history = rows
                        elif isinstance(history_data, list):
                            st.session_state.transaction_history = history_data
                        else:
                            st.session_state.transaction_history = None
                            st.error(f"Failed to fetch history: Invalid data format. Expected a list or string, got {type(history_data)}.")
                    else:
                        st.session_state.transaction_history = None
                        st.error(f"Failed to fetch history: Invalid response status. Response: {data}")
                except requests.exceptions.HTTPError as e:
                    st.session_state.loading = False
                    loading_placeholder.empty()
                    if e.response.status_code == 400:
                        try:
                            response_data = e.response.json()
                            st.error(f"Failed to fetch history: {response_data.get('message', 'Invalid request')}")
                        except ValueError:
                            st.error("Failed to fetch history: Invalid response from server.")
                    else:
                        st.error(f"Failed to fetch history: {str(e)}")
                except requests.exceptions.RequestException as e:
                    st.session_state.loading = False
                    loading_placeholder.empty()
                    st.error(f"Failed to fetch history: {str(e)}")
                except ValueError as e:
                    st.session_state.loading = False
                    loading_placeholder.empty()
                    st.error(f"Failed to fetch history: Invalid JSON response: {str(e)}")

            if st.session_state.transaction_history is not None:
                try:
                    history_data = st.session_state.transaction_history
                    if not history_data:
                        st.info("No transaction history available.")
                    else:
                        df = pd.DataFrame(history_data)
                        expected_columns = ["date", "fromAccount", "toAccount", "amount", "status"]
                        if all(col in df.columns for col in expected_columns):
                            df = df[expected_columns]
                            df.columns = ["Date", "From Account", "To Account", "Amount", "Status"]
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.error("Transaction history data is missing expected columns.")
                except (json.JSONDecodeError, ValueError) as e:
                    st.error(f"Failed to parse transaction history: {str(e)}")
           ## st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.dashboard_section == "statement":
        with st.container():
            st.markdown("""
            <div style="text-align: center; margin-bottom: 0.5rem;">
                <p style="font-size: 1.2rem; color: var(--text-color);">
                    Request your account statement via email.
                </p>
            </div>
            """, unsafe_allow_html=True)
          ##  st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.header("📧 Send Statement via Email")
            with st.form("send_statement_form"):
                month = st.number_input("Month (1-12)", min_value=1, max_value=12, step=1, key="statement_month")
                year = st.number_input("Year", min_value=2025, max_value=2026, step=1, key="statement_year")
                if st.form_submit_button("Send Statement"):
                    st.session_state.loading = True
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <div class="progress-container">
                        <div class="progress-bar">Sending Statement</div>
                    </div>
                    """, unsafe_allow_html=True)
                    sleep(1)
                    headers = {
                        "Authorization": f"Bearer {st.session_state.token}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/send-statement",
                            headers=headers,
                            data={
                                "accountNumber": st.session_state.accnumber,
                                "month": month,
                                "year": year
                            }
                        )
                        response.raise_for_status()
                        response_data = response.json()
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        if response.status_code == 200:
                            animated_message(f"Statement sent to {st.session_state.email}!")
                        else:
                            st.session_state.loading = False
                            loading_placeholder.empty()
                            st.error(f"Failed to send statement: {response_data.get('message', 'Unknown error')}")
                    except requests.exceptions.HTTPError as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        if e.response.status_code == 400:
                            try:
                                response_data = e.response.json()
                                st.error(f"Failed to send statement: {response_data.get('message', 'Invalid request')}")
                            except ValueError:
                                st.error("Failed to send statement: Invalid response from server.")
                        else:
                            st.error(f"Failed to send statement: {str(e)}")
                    except requests.exceptions.RequestException as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error(f"Failed to send statement: {str(e)}")
                    except ValueError as e:
                        st.session_state.loading = False
                        loading_placeholder.empty()
                        st.error(f"Failed to send statement: Invalid JSON response: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.dashboard_section != "welcome":
        with st.container():
            st.markdown('<div style="margin-top: 0;">', unsafe_allow_html=True)
            if st.button("← Back to Dashboard"):
                st.session_state.dashboard_section = "welcome"
                st.session_state.transfer_otp_requested = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
       ## st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            animated_message("Logged out successfully!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)