# LinkedIn Job Automation Agent

An intelligent automation agent that automates LinkedIn job search and application process using Python and Playwright.

## 🚀 Features

- **Automated Login**: Secure LinkedIn authentication
- **Smart Job Search**: Searches for "Product Manager" jobs in "India"
- **Intelligent Filtering**: Applies Date Posted (Past 24 hours) and Easy Apply filters
- **Smart Job Selection**: Skips already-applied jobs and finds available positions
- **Automatic Application**: Applies to jobs using LinkedIn's Easy Apply feature
- **Report Generation**: Creates Excel reports with application details
- **Robust Error Handling**: Comprehensive debugging and fallback mechanisms

## 📋 Prerequisites

- Windows 10/11
- Python 3.9+
- Git (for version control)
- LinkedIn account

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-agent-naukri.git
cd ai-agent-naukri
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
python -m playwright install
```

### 4. Configure Credentials
Create a `.env` file in the project root:
```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

**OR** Update `credentials.py` with your LinkedIn credentials:
```python
LINKEDIN_EMAIL = "your_email@example.com"
LINKEDIN_PASSWORD = "your_password"
```

## 🎯 Usage

### Run with Visible Browser (Recommended for testing)
```bash
python -m src.cli --headful
```

### Run in Headless Mode
```bash
python -m src.cli
```

### Custom Timeout
```bash
python -m src.cli --headful --timeout 45000
```

## 📁 Project Structure

```
ai-agent-naukri/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── automation_clean.py  # Main automation logic
│   ├── selectors.py        # CSS selectors for LinkedIn
│   ├── config.py           # Configuration management
│   └── report.py           # Excel report generation
├── reports/                # Generated Excel reports
├── credentials.py          # LinkedIn credentials
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔧 How It Works

1. **Login**: Authenticates with LinkedIn using provided credentials
2. **Navigate**: Goes to LinkedIn Jobs section
3. **Search**: Searches for "Product Manager" jobs in "India"
4. **Filter**: Applies "Past 24 hours" and "Easy Apply" filters
5. **Apply**: Finds the first available job and applies to it
6. **Report**: Generates an Excel report with application details

## 📊 Output

- **Debug Screenshots**: Automatically captured at each step
- **Excel Reports**: Generated in `reports/linkedin_job_<timestamp>.xlsx`
- **Console Logs**: Detailed debugging information

## ⚠️ Important Notes

- **Rate Limiting**: Use responsibly to avoid LinkedIn restrictions
- **Credentials**: Never commit your actual LinkedIn credentials to version control
- **Testing**: Always test with `--headful` mode first
- **Compliance**: Ensure compliance with LinkedIn's Terms of Service

## 🐛 Troubleshooting

### Common Issues:
1. **Login Failed**: Check credentials and network connection
2. **Element Not Found**: LinkedIn UI may have changed - update selectors
3. **Timeout Errors**: Increase timeout value or check network speed
4. **No Jobs Found**: Verify search criteria and filters

### Debug Mode:
The automation automatically captures debug screenshots and logs. Check the generated PNG files for visual debugging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes. Please ensure compliance with LinkedIn's Terms of Service and use responsibly.

## ⚡ Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/ai-agent-naukri.git
cd ai-agent-naukri
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
python -m playwright install

# 3. Configure credentials
# Edit credentials.py with your LinkedIn details

# 4. Run automation
python -m src.cli --headful
```

## 📞 Support

If you encounter any issues, please:
1. Check the debug screenshots
2. Review the console output
3. Ensure all dependencies are installed
4. Verify your LinkedIn credentials`