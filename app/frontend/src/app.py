import streamlit as st
from layout.layout import setup_page_config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from utils import init_session_state
from store.model_store import ModelStore


from pages.home import render_home
from pages.login import render_login
from pages.register import render_register
from pages.profile import render_profile
from pages.chat_history import render_chat_history
from pages.single_prediction import render_single_prediction
from pages.batch_prediction import render_batch_prediction
from pages.developer import render_developers

# Initialize session state
init_session_state()

def main():
    """Main application entry point"""
    setup_page_config()
    
   
    from config.text_styles import apply_custom_styles
    apply_custom_styles()
    
    
    render_sidebar()
    
    # Main content area
    with st.container():
        render_header()
        
        
        current_page = st.session_state.get('current_page', 'home')
        
        #
        protected_pages = ['profile', 'chat_history']
        
        if current_page in protected_pages and not ModelStore.is_authenticated():
            st.warning("Please login to access this page")
            render_login()
        else:
            
            if current_page == 'home':
                render_home()
            elif current_page == 'single_prediction':
                render_single_prediction()
            elif current_page == 'batch_prediction':
                render_batch_prediction()
            elif current_page == 'login':
                render_login()
            elif current_page == 'register':
                render_register()
            elif current_page == 'profile':
                render_profile()
            elif current_page == 'chat_history':
                render_chat_history()

            elif current_page == 'developer':
                render_developers()
            else:
                render_home()
        
        render_footer()

if __name__ == "__main__":
    main()