# HSU Early Warning System – End-to-End Project

## 1. Overview

**Course:** IS‑5960 Masters Research Project  
**Institution:** Saint Louis University  
**Team:** Team Infinite – Group 6  
**Use Case:** Student Retention Analytics for Horizon State University (HSU)

This repository contains two tightly connected parts:

- **Machine Learning Pipeline (root folder):**
  - Builds a Random Forest model to predict student dropout risk
  - Achieves **≈94% accuracy** and **≈93% AUC‑ROC**
  - Generates risk scores and explanations from realistic synthetic data

- **Streamlit Web Application (`HSU-Streamlit-App/`):**
  - Full early‑warning platform for **students**, **advisors**, and **admins**
  - Uses CSV exports / model outputs to drive interactive dashboards
  - Fully role‑based, production‑style UI with 10 pages

This README documents **both** the ML pipeline and the Streamlit system, including
installation, data, architecture, pages, credentials, and deployment.

---

## 2. Repository Structure

```text
Sai_Krishna/
├── Data/                      # ML pipeline raw data (large CSVs)
├── ml_pipeline/               # (if present) helper scripts & results
├── models/                    # Trained ML artifacts (root project)
├── results/                   # ML evaluation outputs (figures, reports)
├── requirements_ml.txt        # Dependencies for ML pipeline
├── run_ml_pipeline.py         # Main ML training / evaluation script
├── production_predict.py      # Weekly / batch prediction script
├── show_model_accuracy.py     # Quick model performance viewer
├── HSU-Streamlit-App/         # Complete Streamlit web application
│   ├── app.py                 # Premium landing page
│   ├── pages/                 # All Streamlit pages (multi‑page app)
│   │   ├── 0_🔐_Login.py
│   │   ├── 0_✨_SignUp.py
│   │   ├── 1_🏠_Dashboard.py        # Advisor dashboard
│   │   ├── 2_👥_Students.py         # Student directory
│   │   ├── 3_📊_Analytics.py        # Analytics dashboard
│   │   ├── 4_🎓_Student_Portal.py   # Student portal (7 tabs)
│   │   ├── 5_👔_Admin_Portal.py     # Admin portal
│   │   ├── 6_🎯_ML_Predictions.py   # ML predictions UI
│   │   └── 7_📝_Interventions.py    # Intervention management
│   ├── utils/
│   │   ├── auth.py             # Role‑based authentication
│   │   ├── data_loader.py      # Cached CSV loaders
│   │   ├── premium_design.py   # Shared premium styling
│   │   ├── intervention_manager.py, email_service.py, ...
│   ├── Data_Web/              # Web‑app CSV data (150 students)
│   ├── models/                # Deployed RF model + scaler + metadata
│   ├── requirements.txt       # Web‑app dependencies
│   └── various *.md guides    # Detailed status & feature docs
└── README.md                  # This file (end‑to‑end project README)
```

---

## 3. Data Sources

The project is built on synthetic but **realistic** higher‑ed data.

### Core Tables (used by both ML & Web App)

Located under **`HSU-Streamlit-App/Data_Web/`** for the app, and under
`Data/` or separate ML data folders for the pipeline (often larger versions).

- **students.csv** – 150 students (web app) / up to 10,000 for ML
  - `StudentID`, `BannerID`, `FirstName`, `LastName`, `Email`, `Gender`,
    `Classification`, `FirstGenerationStudent`, `InternationalStudent`,
    `HighSchoolGPA`, `AdmissionDate`, etc.
- **risk_scores.csv** – model output / synthetic risk labels
  - `StudentID`, `OverallRiskScore` (0‑1), `RiskCategory` (Critical/High/Medium/Low)
- **enrollments.csv** – course enrollment history
  - `StudentID`, `CourseID`, `Status` (Active/Completed)
- **courses.csv** – course catalog
  - `CourseID`, `CourseCode`, `CourseName`, `Credits`, `Department`
- **grades.csv** – 65k+ grade rows for the app; hundreds of thousands for ML
  - `EnrollmentID`, `AssignmentType`, `PointsEarned`, `PointsPossible`, `GradePercentage`
- **attendance.csv** – weekly attendance per enrollment
- **logins.csv** – LMS login events
- **payments.csv** – financial data (amounts, balances, holds, aid)
- **counseling.csv** – counseling visits (date, concern type, severity)
- **terms.csv**, **departments.csv**, **faculty.csv** – supporting metadata

The **Streamlit app** accesses these via `utils.data_loader.load_*` with
`@st.cache_data` for performance.

---

## 4. Machine Learning Pipeline (Root Project)

The ML side builds a Random Forest classifier to predict **student dropout risk**.

### 4.1 Feature Engineering

Approx. **69 engineered features** across:

- **Demographics:** gender, classification, first‑gen, international, HS GPA
- **Academics:** cumulative GPA, failures, course load, midterm average, etc.
- **Engagement:** logins, session duration, attendance rates
- **Financial:** balance, aid, payment history, holds
- **Wellness:** counseling visits, crisis flags, severity
- **Pathways & interactions:** 5 dropout pathways + combined indicators

### 4.2 Model

```python
RandomForestClassifier(
    n_estimators=150,
    max_depth=6,
    min_samples_split=30,
    min_samples_leaf=15,
    max_features="sqrt",
    class_weight="balanced",
    random_state=42,
)
```

- **Class imbalance:** handled via SMOTE / class weighting
- **Explainability:** SHAP plots and feature importance CSVs

### 4.3 Performance (Representative)

- **Accuracy:** ~94.3%
- **Precision:** ~97.1%
- **Recall:** ~77.4% (tuned for recall range 75–85%)
- **F1‑Score:** ~86.1%
- **AUC‑ROC:** ~93.2%

Decision thresholds map to risk categories used by the web app
(`High`, `Medium`, `Low`) and stored in `risk_scores.csv`.

### 4.4 Running the ML Pipeline

From the **project root (`Sai_Krishna/`)**:

```bash
# 1. Create & activate a virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate

# 2. Install ML dependencies
pip install -r requirements_ml.txt

# 3. Train / evaluate model
python run_ml_pipeline.py

# 4. View accuracy summary
python show_model_accuracy.py

# 5. Generate production predictions (batch)
python production_predict.py
```

Outputs are saved under `models/` and `results/`.

---

## 5. Streamlit Web Application (`HSU-Streamlit-App`)

The web app is a **multi‑role early warning system** with 10 pages and
role‑based navigation.

### 5.1 Installation & Local Run

From the **`HSU-Streamlit-App/`** folder:

```bash
cd HSU-Streamlit-App

# (Inside same or new virtualenv)
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at **http://localhost:8501**.

### 5.2 Roles & Demo Credentials

Built‑in demo users (configured in `utils/auth.py`):

- **Student Demo**  
  Email: `student1@hsu.edu`  
  Password: `student123`

- **Advisor Demo**  
  Email: `advisor@hsu.edu`  
  Password: `advisor123`

- **Admin Demo**  
  Email: `admin@hsu.edu`  
  Password: `admin123`

Additional **database students** from `Data_Web/students.csv` can log in with:

- **Email:** value from the `Email` column  
- **Password:** `password123` (for all dataset students; see `LOGIN_INSTRUCTIONS.md`)

### 5.3 High‑Level Page Map

- **Landing Page (`app.py`)** – Premium marketing‑style landing page
- **0_🔐_Login.py** – Central login form + role‑based redirect
- **0_✨_SignUp.py** – Demo registration form (no real DB persistence)
- **1_🏠_Dashboard.py** – Advisor dashboard
- **2_👥_Students.py** – Student directory & profiles
- **3_📊_Analytics.py** – Cohort analytics & equity charts
- **4_🎓_Student_Portal.py** – Student self‑service portal (7 tabs)
- **5_👔_Admin_Portal.py** – Admin‑level cohort & system analytics
- **6_🎯_ML_Predictions.py** – Single & batch ML predictions
- **7_📝_Interventions.py** – Intervention logging & analytics

Role access is enforced via `utils.auth.require_role`.

---

## 6. Key App Calculations

Most metrics are computed on the fly from CSVs via `utils.data_loader`.

- **GPA (per student):**

  ```python
  gpa = student_grades["GradePercentage"].mean() / 25
  # 0–100% → 0–4.0 scale
  ```

- **Displayed Risk Score:**

  ```python
  df["RiskScore"] = df["OverallRiskScore"] * 100  # to 0–100
  ```

- **Credits & Progress (approx.):**

  ```python
  credits = completed_courses * 3
  degree_progress = credits / 120 * 100
  ```

These are reused consistently across Student Portal, Advisor Dashboard,
Students Directory, Analytics, and Admin Portal.

---

## 7. Streamlit Pages – Functional Summary

### 7.1 Landing Page (`app.py`)

- Premium hero section (problem, solution, impact)  
- Big **Sign In** and **Sign Up** calls‑to‑action  
- No sidebar (hidden via CSS)

### 7.2 Login & Sign Up

- **Login (`0_🔐_Login.py`)**
  - Email/password authentication via `utils.auth.authenticate_user`
  - Sets `st.session_state["role"]` and redirects by role

- **Sign Up (`0_✨_SignUp.py`)**
  - Collects basic info & role for demo purposes

### 7.3 Student Portal (`4_🎓_Student_Portal.py`)

For logged‑in **students** only.

- Gradient header with name, GPA, classification
- 4 stat cards: GPA, Active Courses, Credits Earned, Degree Progress
- **Tabs:**
  - *My Courses* – course names (from `courses.csv`), grades from `grades.csv`
  - *Academic Progress* – GPA trend & progress visuals
  - *Goals & Milestones* – achievements based on GPA/credits/logins
  - *My Finances* – balance, payments, aid, holds from `payments.csv`
  - *Resources* – static help content
  - *Appointments* – counseling visits from `counseling.csv`
  - *Notifications* – GPA / attendance / financial / achievement alerts

### 7.4 Advisor Dashboard (`1_🏠_Dashboard.py`)

For **advisors & admins**.

- Header with quick actions (email, export, alerts, logout)
- Gradient risk cards: counts for Critical/High/Medium/Low
- Search by name or StudentID; filter by risk & classification & first‑gen
- Student cards showing GPA, risk score, enrollments, logins, counseling, etc.
- Risk distribution donut chart and summary metrics

### 7.5 Students Directory (`2_👥_Students.py`)

- Full table of students (150 rows) with calculated GPA & risk
- Filters: risk level, classification, name/ID search
- Click‑through profile with tabs:
  - Academic, Engagement, Financial, Wellness, Analytics
- CSV export of filtered cohort

### 7.6 Analytics (`3_📊_Analytics.py`)

- KPI row: total students, retention estimate, avg GPA, at‑risk count
- 7+ charts: risk distribution, GPA histogram, risk by classification,
  first‑gen gaps, international comparison, etc.

### 7.7 Admin Portal (`5_👔_Admin_Portal.py`)

For **admins only**.

- Executive header and KPI cards
- Tabs for cohort analytics, equity analysis, intervention tracking,
  system reports, and configuration (risk thresholds, notifications)

### 7.8 ML Predictions (`6_🎯_ML_Predictions.py`)

- **Single Prediction:** show RF‑derived risk score & category per student
- **Batch Predictions:** generate cohort‑level table from `students`+`risk_scores`
  with GPA, 0–100 risk score, and intervention flags; CSV export + summary

### 7.9 Interventions (`7_📝_Interventions.py`)

- Log interventions, view history (from `counseling.csv`), analyze success
- Handles date formatting issues robustly for `st.dataframe`

---

## 8. Authentication & Roles

Implemented in **`HSU-Streamlit-App/utils/auth.py`**:

- SHA‑256 password hashing (`hashlib`)
- In‑memory `DEMO_USERS` for advisor/admin/demo students
- Dynamic lookup of students by email from `students.csv`  
  (standard password `password123` for dataset students)
- Session‑based role storage and helpers:
  - `require_authentication()`, `require_role()`
  - `get_current_user()`, `get_student_id()`
  - `display_user_info()` sidebar profile & logout

Role access matrix (simplified):

| Page              | Student | Advisor | Admin |
|-------------------|:------:|:------:|:-----:|
| Landing           | ✅      | ✅      | ✅    |
| Login / SignUp    | ✅      | ✅      | ✅    |
| Student Portal    | ✅      | ❌      | ❌    |
| Advisor Dashboard | ❌      | ✅      | ✅    |
| Students / Analytics / ML / Interventions | ❌ | ✅ | ✅ |
| Admin Portal      | ❌      | ❌      | ✅    |

---

## 9. Deployment (Example: Streamlit Community Cloud)

1. Push `HSU-Streamlit-App` folder to GitHub (already done in
   `madhudheeravath/HSU-Early-Warning-System`).
2. Go to <https://share.streamlit.io/> and create a new app:
   - Repository: `madhudheeravath/HSU-Early-Warning-System`
   - Main file: `HSU-Streamlit-App/app.py` (or root `app.py` depending on repo)
3. Set Python version & use `requirements.txt` from `HSU-Streamlit-App/`.
4. Deploy – Streamlit Cloud will build and host the app with a public URL.

Alternative options (Heroku, Render) are documented in
`HSU-Streamlit-App/DEPLOYMENT_GUIDE.md` and `QUICK_DEPLOY.md`.

---

## 10. Testing Checklist

Minimal end‑to‑end validation steps:

1. **ML Pipeline**  
   - Run `python run_ml_pipeline.py` and confirm metrics & artifacts are created.

2. **Web App – Local**  
   - Start: `streamlit run app.py` from `HSU-Streamlit-App/`  
   - Login as:
     - Student: `student1@hsu.edu` / `student123`
     - Advisor: `advisor@hsu.edu` / `advisor123`
     - Admin: `admin@hsu.edu` / `admin123`
   - Navigate all 10 pages and confirm data loads without errors.

3. **Student Dataset Logins**  
   - Take any email from `Data_Web/students.csv`  
   - Login with that email + `password123`  
   - Confirm Student Portal reflects that student’s GPA, risk, courses, etc.

4. **Batch Predictions**  
   - On ML Predictions page, run batch predictions and export CSV.

5. **Interventions**  
   - Log a new intervention and verify it appears in the table and charts.

More exhaustive test cases are documented in
`HSU-Streamlit-App/FINAL_SYSTEM_STATUS.md` and `COMPLETE_SYSTEM_GUIDE.md`.

---

## 11. Technology Stack

- **Language:** Python 3.10–3.12  
- **Web Framework:** Streamlit  
- **ML:** scikit‑learn (Random Forest), joblib  
- **Data:** pandas, NumPy  
- **Visualization:** Plotly, Matplotlib, Seaborn  
- **Other:** SHAP, imbalanced‑learn (for ML side)

---

## 12. Credits & License

**Team Infinite – Group 6**  
Saint Louis University – IS‑5960 Masters Research Project

This project is intended for **educational and demonstration purposes**.
Please do not use the synthetic data as real student data or for
production decision‑making without proper review, validation, and
compliance checks.

---

*HSU Early Warning System – Helping students succeed through data‑driven interventions.*

