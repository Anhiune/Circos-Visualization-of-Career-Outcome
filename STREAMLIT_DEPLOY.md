# Streamlit Deployment

## Run locally

```powershell
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

## Publish publicly with Streamlit Community Cloud

1. Push this folder to GitHub.
2. Go to https://share.streamlit.io/
3. Create a new app and point it to:
   - Repository: your GitHub repo
   - Branch: your main branch
   - Main file path: `streamlit_app.py`
4. In advanced settings, set the Python requirements file to `requirements-streamlit.txt` if needed.

## When Streamlit is a good fit

- You want filters and a simple data viewer.
- You may keep updating the CSV and regenerate the diagram over time.
- You want a Python-based deployment instead of hand-writing HTML.

## Better alternative for this repo

If your goal is mainly to share the finished diagram publicly, a static site is simpler:

- GitHub Pages
- Netlify
- Vercel

Those are often better than Streamlit when you are mostly publishing a finished SVG/PNG plus a little explanatory text.
