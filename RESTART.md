# How to Restart the App

## From Terminal (if you have it open)

1. Press `Ctrl+C` to stop the running app
2. Run: `python app.py`

## From Claude Code

Kill the existing process and restart:

```bash
lsof -ti:7860 | xargs kill -9; sleep 1 && /Users/ghassansalloum/Downloads/Development/voice-cloning/venv/bin/python /Users/ghassansalloum/Downloads/Development/voice-cloning/app.py
```

Or step by step:

```bash
# 1. Kill the process on port 7860
lsof -ti:7860 | xargs kill -9

# 2. Start the app with the virtual environment
/Users/ghassansalloum/Downloads/Development/voice-cloning/venv/bin/python /Users/ghassansalloum/Downloads/Development/voice-cloning/app.py
```

## Access the App

Open in browser: http://127.0.0.1:7860
