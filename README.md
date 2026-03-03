# 🏏 Cricklytics Pro - Advanced Cricket Analytics Dashboard

A professional Streamlit-based cricket analytics dashboard with **live API integration**, machine learning predictions, and interactive visualizations.

## ✨ Features

- ✅ **Live API Integration** - CricketData.org API support with automatic fallback
- ✅ **Machine Learning** - Logistic Regression for player form prediction
- ✅ **Interactive Dashboards** - 6 comprehensive sections with rich visualizations
- ✅ **Data Source Toggle** - Switch between live API and CSV data
- ✅ **Modern UI** - Gradient designs, animations, and responsive layout
- ✅ **Real-time Updates** - 5-minute cache for live data

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key (Optional)

Create a `.env` file in the project root:

```bash
CRICKETDATA_API_KEY=your_api_key_here
```

**Get your free API key:**
- Visit [CricketData.org](https://cricketdata.org)
- Sign up for a free account
- Copy your API key from the dashboard

> **Note:** The app works without an API key using CSV data as fallback.

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📊 Dashboard Sections

### 1. 📈 Dashboard Overview
- KPI cards (Total Players, Avg Batting, Total Runs, Total Wickets)
- Top 15 players by runs (bar chart)
- Performance scatter plot (Batting Avg vs Strike Rate)

### 2. 👤 Player Analysis
- Detailed individual player statistics
- Performance radar chart
- Form classification (Good/Average/Poor)

### 3. ⚖️ Player Comparison
- Compare 2-4 players side-by-side
- Comparison table and charts
- Runs, Batting Avg, Strike Rate comparisons

### 4. 📊 Team Statistics
- Overall team averages
- Distribution plots (Batting Avg, Strike Rate)
- Correlation heatmap
- Form distribution pie chart

### 5. 🤖 ML Prediction
- Logistic Regression model
- Model accuracy and performance metrics
- Confusion matrix
- Feature importance visualization

### 6. ⚙️ Settings
- Project information
- Tech stack details
- Dataset preview and download

## 🛠 Tech Stack

- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn (Logistic Regression)
- **Visualization:** Matplotlib, Seaborn, Plotly
- **API:** CricketData.org
- **UI Components:** streamlit-option-menu, streamlit-lottie

## 📁 Project Structure

```
Cricklytics/
├── app.py                    # Main Streamlit application
├── api_handler.py            # CricketData.org API integration
├── cricket_players.csv       # Fallback CSV data
├── requirements.txt          # Python dependencies
├── .env                      # API key (create this)
├── .env.example             # API key template
└── README.md                # This file
```

## 🔧 Configuration

### Data Source Toggle

In the sidebar, you can toggle between:
- **Live API Data** - Fetches real-time player statistics (requires API key)
- **CSV Data** - Uses local cricket_players.csv file

The app automatically falls back to CSV if the API fails.

### Cache Settings

- API data is cached for 5 minutes to reduce API calls
- CSV data is cached indefinitely until app restart

## 🧠 Machine Learning

### Model Details
- **Algorithm:** Logistic Regression (Multiclass)
- **Features:** Batting_Avg, Strike_Rate, Runs, Matches
- **Target:** Form_Label (Good/Average/Poor)
- **Preprocessing:** LabelEncoder + StandardScaler
- **Train/Test Split:** 80/20

### Form Classification Rules
- **Good:** Batting_Avg ≥ 45
- **Average:** 30 ≤ Batting_Avg < 45
- **Poor:** Batting_Avg < 30

### Impact Score Formula
```
Impact_Score = (Batting_Avg × Strike_Rate) / 100
```

## 🌐 API Integration

### Endpoints Used
- `GET /currentMatches` - Fetch current/recent matches
- `GET /match_info` - Get detailed match information
- `GET /players` - Search for players

### Rate Limiting
- Minimum 1 second between API requests
- Automatic retry on failure
- Graceful fallback to CSV data

### Error Handling
- Connection timeout (10 seconds)
- Invalid API key detection
- Empty response handling
- Automatic CSV fallback

## 🎨 UI/UX Features

- **Gradient Headers** - Eye-catching title with gradient text
- **KPI Cards** - Purple gradient cards with white text
- **Form Badges** - Color-coded pills (🟢 Green / 🟡 Yellow / 🔴 Red)
- **Lottie Animation** - Cricket-themed animation at the top
- **Sidebar Menu** - Icon-based navigation with hover effects
- **Responsive Layout** - Wide mode for maximum screen usage

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CRICKETDATA_API_KEY` | Your CricketData.org API key | Optional |

## 🐛 Troubleshooting

### API Not Working
1. Check your API key in `.env` file
2. Verify internet connection
3. Check API quota/limits
4. App will automatically use CSV fallback

### App Won't Start
1. Install all dependencies: `pip install -r requirements.txt`
2. Ensure Python 3.8+ is installed
3. Check for port conflicts (default: 8501)

### Data Not Loading
1. Ensure `cricket_players.csv` exists
2. Check file permissions
3. Verify CSV format matches expected columns

## 🎓 Use Cases

- ✅ College projects and presentations
- ✅ Resume portfolio showcase
- ✅ Cricket analytics research
- ✅ Learning Streamlit and ML
- ✅ API integration demonstration

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Developer

Built with ❤️ for cricket analytics enthusiasts

**Version:** 2.0.0 (Live API Integration)  
**Last Updated:** January 2026

---

## 🚀 Next Steps

1. Run the app: `streamlit run app.py`
2. Toggle to Live API mode (if you have an API key)
3. Explore the 6 dashboard sections
4. Download the dataset with ML predictions
5. Customize and extend as needed!

Enjoy analyzing cricket data! 🏏📊
