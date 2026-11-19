# HACKATHON ENVIRONMENT — SETUP NOTES

## 1. Basic Environment

- Operating System: Windows
- Python Version: 3.11.9
- Main Project Folder: `D:\ibm final`
- Virtual Environment: `.venv`
- IDE: VS Code
- Version Control: Git installed

### Resume the environment

Open the project folder in VS Code and run:

```powershell
.\.venv\Scripts\Activate.ps1
```

Check dependencies:

```powershell
python -m pip check
```

---

## 2. Installed Technologies

### Application Development
- Streamlit
- FastAPI
- Uvicorn
- Requests
- HTTPX
- Pydantic
- Python-dotenv

### AI and Agentic AI
- Google GenAI SDK
- IBM watsonx.ai SDK
- LangGraph
- LangChain Core

### RAG and Document Processing
- ChromaDB
- LangChain Community
- LangChain Text Splitters
- PyMuPDF
- PyPDF
- python-docx
- python-pptx
- openpyxl
- BeautifulSoup
- lxml

Note: Sentence Transformers was installed, but its import was blocked by Windows Application Control because PyTorch's DLL was blocked. Use API-based embeddings as an alternative when appropriate.

### Machine Learning
- Scikit-learn
- XGBoost
- LightGBM
- Statsmodels
- Imbalanced-learn
- Joblib

### Geospatial and Image Processing
- GeoPandas
- Shapely
- PyProj
- Folium
- Streamlit-Folium
- OpenCV

### Database
- PostgreSQL 18.6
- PostgreSQL Port: 5432
- Database: `hackathon_db`
- Python Database Libraries:
  - SQLAlchemy
  - Alembic
  - Psycopg

### Developer and Testing Tools
- Ruff
- Black
- Pytest
- Pytest-Asyncio
- Loguru
- Rich
- Tenacity

---

## 3. Database Information

PostgreSQL 18 is running on port 5432.

Existing databases:
- `examforge` — existing project database
- `postgres` — default PostgreSQL database
- `hackathon_db` — created for hackathon projects

Python database connection was tested successfully.

Database CRUD smoke test completed successfully.

Database credentials are stored in `.env`.

Never upload or share the actual `.env` file.

---

## 4. Completed Compatibility Tests

The following tests passed on this laptop:

- Python virtual environment
- Package dependency check
- Streamlit and FastAPI imports
- Gemini SDK import
- IBM watsonx.ai SDK import
- LangGraph import and workflow execution
- ChromaDB storage and retrieval
- Scikit-learn model training and prediction
- XGBoost and LightGBM imports
- PDF, Word, PowerPoint and Excel imports
- PostgreSQL connection and CRUD operations
- GeoPandas functionality
- Shapely geometry operations
- PyProj coordinate transformation
- Folium map creation
- OpenCV import
- Developer tools verification

No broken package requirements were reported at the last dependency check.

---

## 5. Files Already Created

- `.venv/` — Python virtual environment
- `.env` — private credentials and database configuration
- `.gitignore` — excludes private and unnecessary files
- `requirements.txt` — currently contains Streamlit version
- `requirements-lock-windows-py311.txt` — installed package snapshot
- `python-version.txt` — Python version record
- `dependency-check.txt` — dependency verification result
- `streamlit_smoke_test.py` — local Streamlit test
- `test_db.py` — PostgreSQL connection test
- `test_sqlalchemy.py` — SQLAlchemy connection test

---

## 6. API Configuration — Pending

### Google Gemini
- SDK installed.
- API key configuration/testing pending.
- Add `GEMINI_API_KEY` to `.env`.

### IBM Granite / watsonx.ai
- IBM SDK installed.
- API credentials and actual API testing pending.
- Required settings:
  - `WATSONX_API_KEY`
  - `WATSONX_URL`
  - `WATSONX_PROJECT_ID`
  - `WATSONX_MODEL_ID`

Previously used model ID: `ibm/granite-4-h-small`.

Verify model availability and project access before relying on it.

---

## 7. Deployment — Pending

- GitHub repository creation
- GitHub push
- Streamlit Community Cloud configuration
- Streamlit cloud deployment test
- Streamlit secrets configuration
- Optional FastAPI hosting test

Deployment was intentionally postponed until the hackathon.

---

## 8. Friend's Laptop — Pending Synchronisation

The friend's laptop also has Python 3.11 and the basic development environment.

Important limitation:
- Smart App Control is ON.
- Windows Code Integrity Event 3077 blocked Scikit-learn's compiled component.
- Do not disable Windows security just to install ML libraries.
- Use approved cloud ML or another working development environment if required.

Compare both environments and prepare compatible pinned dependencies.

Do not copy the `.venv` folder between laptops.

---

## 9. Remaining Preparation Tasks

1. Configure and test Gemini API.
2. Configure and test IBM Granite API.
3. Verify actual LangGraph integration with AI models.
4. Prepare reusable API integration examples.
5. Finish GitHub and Streamlit deployment preparation.
6. Synchronise both laptops.
7. Prepare efficient Bob IDE prompts.
8. Practise converting a small application into Streamlit.
9. Prepare a real-dataset discovery workflow.

---

## 10. Hackathon Day Strategy

Total hackathon time: 3 hours.

Planned allocation:
- First 2 hours: Build the working MVP.
- Final 1 hour: Deployment, testing and critical fixes.

Before building:
1. Read and analyse the problem statement.
2. Identify relevant real datasets.
3. Select the simplest suitable architecture.
4. Decide whether FastAPI is actually necessary.
5. Select the relevant AI, ML, RAG and database components.

Use Bob IDE to generate and implement the application.

Do not install every library again. Use the prepared environment and install only additional dependencies that the actual problem requires.

Never present synthetic data as real data or fabricated model predictions as genuine results.

---

## 11. Important Security Notes

- Never upload `.env` to GitHub.
- Never share API keys or PostgreSQL passwords.
- Keep `.venv` out of GitHub.
- Maintain a separate backup of important database data.
- Do not copy the local virtual environment to another laptop.
- Use Streamlit Secrets for cloud credentials.
