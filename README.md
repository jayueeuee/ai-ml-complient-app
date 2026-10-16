# AI Governance Complaint Management System 🏙️

Welcome to the **AI Governance Complaint Management System**, an intelligent, AI-powered platform designed to streamline and automate the reporting, verification, and resolution of civic issues and grievances.

## 🚀 Features

- **User Portal**: Submit complaints with text descriptions and image proofs. The AI automatically verifies the image, categorizes the issue, and prioritizes the complaint before routing it to the concerned authority.
- **AI & Physical Verification**: Ensures authenticity of complaints using AI image verification and multi-stage physical verification steps.
- **Nagar Sevak Dashboard**: A dedicated dashboard for local authorities and officials to manage and resolve their assigned complaints.
- **Admin Dashboard**: Comprehensive analytics, maps, and tracking of SLA (Service Level Agreement) breaches (highlighting "Black Zones" where issues are delayed).
- **Complaint Tracking**: Users can track their submitted complaints in real-time, just like tracking an e-commerce order.
- **Feedback System**: Rate the resolution of the complaint and share experiences to improve civic services.

## 🛠️ Technology Stack

- **Frontend/UI**: Streamlit
- **Backend/Logic**: Python
- **Database**: MySQL (`mysql-connector-python`)
- **AI/ML**: `scikit-learn`, `transformers`, `torch` (for image verification and text prediction)
- **Data Visualization & Mapping**: `pandas`, `plotly`, `folium`, `streamlit-folium`, `geopandas`

## ⚙️ Installation & Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-github-repo-url>
   cd <repository-folder>
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` in the root directory and add your local configuration details. Never commit `.env`; it is excluded by `.gitignore`.

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   The application will be accessible at `http://localhost:8501`.

## 📁 Project Structure

- `app.py`: Main Streamlit application entry point.
- `database.py`: Handles database connections and operations.
- `ai_engine.py`: Contains the AI/ML logic for categorization and verification.
- `email_service.py`: Handles email notifications.
- `pages/`: Contains the individual dashboard and portal pages (User, Admin, Nagar Sevak, etc.).
- `models/`: Directory for storing pre-trained AI models.
- `requirements.txt`: Python dependencies.
