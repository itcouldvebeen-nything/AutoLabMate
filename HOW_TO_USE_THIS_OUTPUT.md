# How to Use This Output

This directory contains the complete AutoLabMate project ready to be copied into a GitHub repository.

---

## 📁 Project Structure

```
autolabmate/
├── frontend/              # Next.js web UI
│   ├── app/              # Next.js 14 app directory
│   ├── components/       # React components
│   ├── package.json      # Node dependencies
│   └── Dockerfile        # Container config
├── backend/              # FastAPI server & agents
│   ├── agents/          # Planner, Executor, Monitor
│   ├── tools/           # Vector DB, Calendar, GitHub
│   ├── database/        # SQLAlchemy models
│   ├── main.py          # API server
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Container config
├── tests/               # Test suites
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── conftest.py     # Pytest config
├── samples/            # Sample data & outputs
│   ├── sample_experiment.csv
│   └── expected_report.md
├── notebooks/          # Jupyter templates
│   └── template_analysis.ipynb
├── docs/              # Documentation
│   ├── SYSTEM_DESIGN.md
│   ├── INTERACTION_LOGS.md
│   └── DEPLOY.md
├── demo/              # Demo assets
│   └── video_script.md
├── docker-compose.yml  # Local orchestration
├── .github/workflows/  # CI/CD
│   └── ci.yml
├── README.md          # Main documentation
├── LICENSE            # MIT License
├── CONTRIBUTING.md    # Dev guide
└── CODE_OF_CONDUCT.md # Community rules
```

---

## 🚀 Quick Start

### Step 1: Create Repository

```bash
# Create new repository on GitHub
# Initialize locally
git init
git add .
git commit -m "Initial commit: AutoLabMate v1.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/autolabmate.git
git push -u origin main
```

### Step 2: Run Locally

```bash
# Clone (or use this directory)
git clone https://github.com/YOUR_USERNAME/autolabmate.git
cd autolabmate

# Copy environment template
cp .env.example .env

# Run with Docker
docker-compose up --build

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

### Step 3: Test with Sample Data

1. Open http://localhost:3000
2. Upload `samples/sample_experiment.csv`
3. Generate and execute plan
4. Download report

---

## 📝 Customization

### Before Submission

**1. Update Personal Information:**

```bash
# In README.md, replace:
[Your University]
[Your Department]
[your.email@university.edu]
[@yourusername]

# In SUBMISSION.md, replace:
[Your University]
[Your Department]

# In submission_email.txt, replace:
[Company Name] (each occurrence)
your.username
your.email@university.edu
[Your Phone Number]
```

**2. Update URLs:**

```bash
# In README.md, replace:
https://github.com/yourusername/autolabmate.git

# In submission_email.txt, replace:
https://github.com/yourusername/autolabmate
```

**3. Environment Variables (Optional):**

```bash
# If you have API keys, edit .env:
OPENAI_API_KEY=sk-your-real-key
PINECONE_API_KEY=your-real-key
GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/gcal.json
GITHUB_TOKEN=ghp-your-token

# Set MOCK_MODE=false to use real services
MOCK_MODE=false
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/unit -v
pytest tests/integration -v
pytest tests/ --cov

# Frontend tests (if implemented)
cd frontend
npm test
```

---

## 📦 Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md) for:
- Docker Compose (VPS)
- Vercel + Render (Serverless)
- Kubernetes (Enterprise)

---

## ✅ Submission Checklist

- [ ] All files copied to repository
- [ ] Personal information updated
- [ ] Repository URLs updated
- [ ] Tests pass (`pytest tests/`)
- [ ] Docker builds successfully
- [ ] Sample dataset works end-to-end
- [ ] README instructions followed
- [ ] Documentation reviewed
- [ ] Code committed and pushed
- [ ] Repository is public

---

## 🎬 Demo Video

Follow [demo/video_script.md](demo/video_script.md) to record:
- Screenshot 1: Upload interface
- Screenshot 2: Plan editor
- Screenshot 3: Execution logs
- Screenshot 4: Report preview

Or create placeholder screenshots using any design tool.

---

## 📧 Email Submission

Use [submission_email.txt](submission_email.txt) as template:
1. Fill in company name
2. Update repository links
3. Add personal contact info
4. Customize project details if needed
5. Send to reviewers

---

## 🔍 Verification

**Before Submitting:**

```bash
# 1. Run all tests
pytest tests/ -v

# 2. Start services
docker-compose up -d

# 3. Check health
curl http://localhost:8000/health
curl http://localhost:3000

# 4. Test workflow
# Upload sample_experiment.csv
# Generate plan
# Execute
# Download report

# 5. Check logs
docker-compose logs backend
docker-compose logs frontend
```

---

## 🐛 Troubleshooting

**Docker won't start:**
```bash
docker-compose down -v
docker-compose up --build
```

**Tests failing:**
```bash
# Install dependencies
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

**Port conflicts:**
```bash
# Edit docker-compose.yml
ports:
  - "8001:8000"  # Change host port
  - "3001:3000"
```

---

## 📚 Additional Resources

- **System Design:** [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md)
- **Deployment:** [docs/DEPLOY.md](docs/DEPLOY.md)
- **LLM Logs:** [docs/INTERACTION_LOGS.md](docs/INTERACTION_LOGS.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 💡 Tips

1. **No API Keys Required:** MOCK_MODE=true by default, so reviewers can run without credentials
2. **Fast Local Dev:** Use `docker-compose up` to start everything at once
3. **Test Independently:** Run backend or frontend separately if needed
4. **Check Logs:** All logs are visible in terminal or via `docker-compose logs`
5. **Customization:** Easy to extend with new analysis actions or integrations

---

## 📊 Project Statistics

- **Lines of Code:** ~4000+ (backend + frontend)
- **Files:** 50+ source files
- **Tests:** 20+ test cases
- **Documentation:** 5000+ words
- **Technologies:** 15+ frameworks/libraries

---

**You're all set! 🚀**

For questions or issues, check the documentation or open a GitHub Issue.

Good luck with your submission!

