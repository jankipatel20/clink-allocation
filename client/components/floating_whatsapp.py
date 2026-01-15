import streamlit as st

def display_floating_whatsapp(phone_number="911234567890"):
    """Compact floating WhatsApp button with previous SVG."""
    st.markdown(
        f"""
        <style>
        /* Compact WhatsApp Floating Button */
        .whatsapp-floating-container {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
        }}

        .whatsapp-floating-btn {{
            width: 56px;  /* Smaller bubble */
            height: 56px;
            background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(37, 211, 102, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            border: 2px solid rgba(255, 255, 255, 0.25);
        }}

        .whatsapp-floating-btn::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }}

        .whatsapp-floating-btn:hover {{
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 10px 30px rgba(37, 211, 102, 0.55);
        }}

        .whatsapp-floating-btn:hover::before {{
            width: 160px;
            height: 160px;
        }}

        .whatsapp-icon {{
            width: 30px;  /* Scaled for smaller button */
            height: 30px;
            fill: #FFFFFF;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));
            z-index: 1;
        }}

        .pulse-ring {{
            position: absolute;
            border: 2px solid rgba(37, 211, 102, 0.4);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{
                width: 56px;
                height: 56px;
                opacity: 1;
            }}
            100% {{
                width: 100px;
                height: 100px;
                opacity: 0;
            }}
        }}

        /* Mobile responsive */
        @media (max-width: 768px) {{
            .whatsapp-floating-container {{
                bottom: 16px;
                right: 16px;
            }}
            .whatsapp-floating-btn {{
                width: 52px;
                height: 52px;
            }}
            .whatsapp-icon {{
                width: 28px;
                height: 28px;
            }}
        }}
        </style>

        <div class="whatsapp-floating-container">
            <div class="pulse-ring"></div>
            <a href="https://wa.me/{phone_number}?text=Hi!%20I%20have%20a%20question%20about%20Clinker%20Optimization" 
               class="whatsapp-floating-btn" target="_blank" rel="noopener">
                <!-- SAME SVG from previous code -->
                <svg class="whatsapp-icon" viewBox="0 0 32 32" aria-hidden="true">
                    <path d="M16 3C9.4 3 4 8.3 4 14.8c0 2.6.9 5 2.5 7L4 29l7.4-2.4c1.9 1 4.1 1.5 6.6 1.5
                             6.6 0 12-5.3 12-11.8C30 8.3 24.6 3 18 3h-2zm0 3c5.1 0 9.2 4 9.2 8.8 0 4.8-4.1 8.8-9.2 8.8-2 0-3.9-.6-5.4-1.6l-.4-.3-4.4 1.4
                             1.4-4.2-.3-.4C6.2 20.3 5.6 18.6 5.6 16.8 5.6 11.9 10 6 16 6zm5.1 10.3c-.3-.2-1.8-.9-2.1-1-.3-.1-.5-.2-.7.2-.2.3-.9 1.1-1.1 1.3-.2.2-.4.2-.7.1-1.9-.8-3.1-2.6-3.2-2.7-.2-.3-.1-.5.1-.7.2-.2.3-.4.4-.5.2-.2.2-.3.3-.5.1-.2.1-.4 0-.5-.1-.2-.7-1.8-1-2.4-.2-.6-.4-.5-.6-.5h-.5c-.2 0-.5.1-.7.3-.3.3-1 1-1 2.4s1.1 2.8 1.2 3c.2.2 2 3.3 5 4.6 3.1 1.3 3.1.9 3.7.8.6-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.1-.1-.3-.2-.6-.3z"/>
                </svg>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Usage: Add at the end of your app
display_floating_whatsapp("919876543210")  # Your number here
