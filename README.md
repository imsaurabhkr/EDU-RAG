# EduRAG: An AI-Powered Application for Personalized Learning

Welcome to EduRAG, an AI-powered education platform designed to provide personalized learning experiences for K-12 students using their course textbooks. This platform leverages Retrieval-Augmented Generation (RAG) to enhance the learning process.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Project Overview

EduRAG aims to facilitate personalized learning by integrating AI technologies with traditional educational content. The platform allows students to interact with their course materials more effectively, providing tailored learning experiences based on their needs.

## Features

- **Personalized Learning:** Tailored content recommendations based on student interaction.
- **User-Friendly Interface:** Easy-to-use frontend built with Streamlit.
- **Secure User Onboarding:** Authentication and data storage using Firebase.
- **Real-time Data Retrieval:** Efficient data handling with LangChain and Gemini Developer API.

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Firebase
- **Database:** ChromaDB
- **AI Integration:** LangChain, Gemini Developer API
- **Programming Languages:** Python

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/EduRAG.git
   cd EduRAG
   ```

2. **Set Up Virtual Environment:**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Firebase:**
   - Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/).
   - Enable Email/Password Authentication.
   - Set up Firestore database.
   - Download the `firebaseConfig` object from the Firebase Console and update the `firebase_config.json` file in your project.

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Sign Up / Log In:**
   - Use the authentication interface to sign up or log in.
   
2. **Explore Courses:**
   - Browse through available courses and interact with personalized content.
   
3. **Real-time Learning:**
   - Experience real-time content retrieval and AI-driven recommendations.

## Screenshots

![Homepage](assets/screenshot1.png)
*Caption: Homepage of EduRAG.*

![Course Material](assets/screenshot2.png)
*Caption: Course material page with personalized recommendations.*

## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or inquiries, please contact:

- **Email:** saurabh_k@ma.iitr.ac.in
---

This README file provides a comprehensive overview of your EduRAG project, including setup instructions, usage guidelines, and contribution information. Adjust the content as necessary to fit the specific details and requirements of your project.
