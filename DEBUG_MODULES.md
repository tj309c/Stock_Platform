# Debug Modules & Logging (Developer Guide)

This short README explains how to use the debug logging features available in the app, including environment variables and dashboard controls for module-level debugging.

## Environment Variables

- `ANALYSIS_DEBUG` (boolean): set to `1`/`true`/`yes` to enable global DEBUG logging for the application.
  - Example (Windows cmd):
    - `set ANALYSIS_DEBUG=1`
  - Example (Linux / macOS):
    - `export ANALYSIS_DEBUG=1`
- `APP_LOG_LEVEL` (string): set root log level to `DEBUG`, `INFO`, `WARNING`, `ERROR`, etc. Default is `INFO`.
  - Example: `export APP_LOG_LEVEL=DEBUG`
- `ANALYSIS_DEBUG_MODULES` (comma-separated list): set modules to DEBUG specifically, e.g. `src.pipelines.get_fmp_data,src.pipelines.get_market_data`.
  - This allows selective tracing of module behaviors without making entire app logs verbose.

## Settings Dashboard (UI)

Open the app's Settings dashboard (⚙️) and use the following controls under "Per-Source Sentiment Weights" and the developer controls:

- `Enable detailed debug logs (session only)`: small checkbox that turns on DEBUG logging for the duration of the session.
- `Module-level debug loggers`: enter comma-separated module paths to enable DEBUG logging for those specific loggers for the current session.
  - Click **Apply module debuggers** to enable them for the session.
  - Click **Save module debuggers (persist)** to persist them to the `global` scope settings so that `AppConfig` will pick them up on startup.
  - Click **Clear persisted module debuggers** to remove the persisted setting from storage.

## Persisted settings & where they're stored

- The app uses `data/config/settings.json` for persisted scope settings when running in production/local mode.
- For tests (and isolated runs), we use a per-test or per-process unique settings file placed in the system temp directory, to avoid cross-run pollution.

## Troubleshooting & Tips

- If you expect a persisted module to be in DEBUG but don't see logs, make sure you saved module debuggers in the `global` scope or set `ANALYSIS_DEBUG_MODULES` environment variable.
- Use the **Show settings file path** and **Download settings file** buttons in the dashboard to inspect and export the active settings JSON.
- Use `Clear persisted settings file` only for debugging and local dev — this removes the persisted `settings.json` file and resets defaults.

## Example

Enable debug for the FMP module for a single session:

1. Open the Settings dashboard.
2. In "Module-level debug loggers", enter `src.pipelines.get_fmp_data`.
3. Click **Apply module debuggers**.

Persist debug module across runs:

1. Set `ANALYSIS_DEBUG_MODULES` environment variable in your environment OR
2. Enter module(s) in the dashboard and click **Save module debuggers (persist)**.

That’s it! These tools help diagnose issues while keeping the UI clean for users by only showing user-facing error messages on final failures for network/API calls.

## Security & Performance note

Be careful enabling debugging in production: verbose logs may include sensitive details, and increased logging can affect performance.
