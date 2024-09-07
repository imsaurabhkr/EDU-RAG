import streamlit as st
from firebase_admin import firestore
from gemini_chatbot import gemini_chatbot



def app():
    if 'db' not in st.session_state:
        st.session_state.db = firestore.client()
    
    db = st.session_state.db

    # Check if user is logged in
    if st.session_state.username == '':
        st.warning("Please login to access chat functionality.")
        return

    # User selects Class, Subject, and Chapter
    st.header("Select Class, Subject, and Chapter")

    class_selected = st.selectbox("Select Class", [10, 9, 8])
    subject_selected = st.selectbox("Select Subject", ['Maths', 'English', 'Hindi'])
    chapter_selected = st.selectbox("Select Chapter", [1, 2, 3])

    # Textbox for user input to chat with the bot
    chat_input = st.text_area(label=f"Ask a question about Class {class_selected}, {subject_selected}, Chapter {chapter_selected}", placeholder="Type your question here...")

    if st.button("Submit Query"):
        if chat_input:
            # Call to the chatbot (dummy function for now)
            response = gemini_chatbot(class_selected, subject_selected, chapter_selected, chat_input)
            st.success(f"Chatbot Response: {response}")

            # Store the conversation (question + response) as JSON in Firestore
            info = db.collection('Chats').document(st.session_state.username).get()
            chat_json = {f"{chat_input}": response}
            
            if info.exists:
                info = info.to_dict()
                if 'Content' in info.keys():
                    pos = db.collection('Chats').document(st.session_state.username)
                    # Update Firestore with the new question-answer pair
                    pos.update({u'Content': firestore.ArrayUnion([chat_json])})
                else:
                    data = {"Content": [chat_json], 'Username': st.session_state.username}
                    db.collection('Chats').document(st.session_state.username).set(data)
            else:
                data = {"Content": [chat_json], 'Username': st.session_state.username}
                db.collection('Chats').document(st.session_state.username).set(data)
            
            st.success('Conversation saved!')

    st.header('Previous Chats')

    # Query to get chats for the logged-in user only
    user_chat = db.collection('Chats').document(st.session_state.username).get()
    if user_chat.exists:
        user_chat_data = user_chat.to_dict()
        try:
            # Display each question and answer stored in JSON format for this user
            for chat in user_chat_data['Content'][::-1]:
                for question, answer in chat.items():
                    st.markdown(f"**Question:** {question}")
                    st.markdown(f"**Answer:** {answer}")
                    st.markdown("---")  # To separate each conversation visually
        except:
            st.warning("No chats found for this user.")
    else:
        st.warning("No previous chats available.")
