import streamlit as st

from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
load_dotenv()

import home, trending, account, your, about, buy_me_a_coffee
st.set_page_config(
        page_title="Class",
)


st.markdown(
    """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src=f"https://www.googletagmanager.com/gtag/js?id={os.getenv('analytics_tag')}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', os.getenv('analytics_tag'));
        </script>
    """, unsafe_allow_html=True)
print(os.getenv('analytics_tag'))

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):  # Add 'self' as a parameter here
        with st.sidebar:
            app = option_menu(
                menu_title='Class',
                options=['Account','Home', 'Trending', 'Your Posts', 'about', 'Buy_me_a_coffee'],
                icons=['house-fill', 'person-circle', 'trophy-fill', 'chat-fill', 'info-circle-fill'],
                menu_icon='chat-text-fill',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"}
                }
            )

        # Call the respective app based on the sidebar selection
        if app == "Home":
            home.app()
        elif app == "Account":
            account.app()
        elif app == "Trending":
            trending.app()
        elif app == 'Your Posts':
            your.app()
        elif app == 'about':
            about.app()
        elif app == 'Buy_me_a_coffee':
            buy_me_a_coffee.app()


# Instantiate the class and run the app
multi_app = MultiApp()
multi_app.run()