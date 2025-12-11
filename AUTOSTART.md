# WebQuiz Auto-Start Setup

This guide explains how to configure WebQuiz to automatically start when your Mac boots.

## Quick Setup

### 1. Install the Launch Agent

Copy the launch agent to your LaunchAgents directory:

```bash
cp com.webquiz.plist ~/Library/LaunchAgents/
```

### 2. Load the Service

Start the service immediately:

```bash
launchctl load ~/Library/LaunchAgents/com.webquiz.plist
```

### 3. Verify It's Running

Check if the service is running:

```bash
launchctl list | grep webquiz
```

You should see output like:
```
12345  0  com.webquiz
```

Test by visiting: http://localhost:5666

## Managing the Service

### Check Status

```bash
launchctl list | grep webquiz
```

### Stop the Service

```bash
launchctl unload ~/Library/LaunchAgents/com.webquiz.plist
```

### Start the Service

```bash
launchctl load ~/Library/LaunchAgents/com.webquiz.plist
```

### Restart the Service

```bash
launchctl unload ~/Library/LaunchAgents/com.webquiz.plist
launchctl load ~/Library/LaunchAgents/com.webquiz.plist
```

### Disable Auto-Start

To prevent WebQuiz from starting at boot:

```bash
launchctl unload ~/Library/LaunchAgents/com.webquiz.plist
rm ~/Library/LaunchAgents/com.webquiz.plist
```

## View Logs

### Standard Output (Normal Logs)

```bash
tail -f ~/cc_projects/webquiz/logs/webquiz.log
```

### Error Logs

```bash
tail -f ~/cc_projects/webquiz/logs/webquiz.error.log
```

### View All Recent Logs

```bash
cat ~/cc_projects/webquiz/logs/webquiz.log
cat ~/cc_projects/webquiz/logs/webquiz.error.log
```

## What Happens at Boot

When your Mac starts:
1. macOS launchd reads `~/Library/LaunchAgents/com.webquiz.plist`
2. WebQuiz starts automatically (`RunAtLoad: true`)
3. If WebQuiz crashes, it automatically restarts (`KeepAlive: true`)
4. Logs are written to `~/cc_projects/webquiz/logs/`

## Troubleshooting

### Service Won't Start

1. Check the logs:
   ```bash
   cat ~/cc_projects/webquiz/logs/webquiz.error.log
   ```

2. Verify paths in the plist file are correct:
   ```bash
   cat ~/Library/LaunchAgents/com.webquiz.plist
   ```

3. Make sure the virtual environment exists:
   ```bash
   ls -la ~/cc_projects/webquiz/venv/bin/python
   ```

### Port Already in Use

If port 5666 is already in use, edit `app.py` and change the port:
```python
app.run(host='0.0.0.0', port=XXXX, debug=True)
```

Then restart the service:
```bash
launchctl unload ~/Library/LaunchAgents/com.webquiz.plist
launchctl load ~/Library/LaunchAgents/com.webquiz.plist
```

### Check for Permission Issues

The service runs as your user, so it should have all necessary permissions. If you encounter issues:

1. Check file ownership:
   ```bash
   ls -la ~/cc_projects/webquiz/
   ```

2. Verify .env file exists:
   ```bash
   cat ~/cc_projects/webquiz/.env
   ```

## Configuration Details

The launch agent configuration (`com.webquiz.plist`) includes:

- **Label:** Unique identifier for the service
- **ProgramArguments:** Python interpreter and script to run
- **WorkingDirectory:** Where to run the script from
- **RunAtLoad:** Start automatically at boot
- **KeepAlive:** Restart if it crashes
- **StandardOutPath:** Where to write normal logs
- **StandardErrorPath:** Where to write error logs
- **EnvironmentVariables:** System PATH including Homebrew

## Advanced: Delayed Start

If you want WebQuiz to start 60 seconds after boot (to wait for network):

1. Edit the plist file:
   ```bash
   nano ~/Library/LaunchAgents/com.webquiz.plist
   ```

2. Add before `</dict>`:
   ```xml
   <key>StartInterval</key>
   <integer>60</integer>
   ```

3. Reload:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.webquiz.plist
   launchctl load ~/Library/LaunchAgents/com.webquiz.plist
   ```

## Security Note

This setup runs WebQuiz only when you're logged in. For a true system-wide service that runs before login, you would need to use `/Library/LaunchDaemons/` instead, but this is not recommended for this application.
