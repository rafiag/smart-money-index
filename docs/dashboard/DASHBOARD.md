# Dashboard Technical Specification

## Architecture
The dashboard follows a modular architecture to ensure maintainability and separation of concerns.

### Directory Structure
```
src/dashboard/
├── app.py           # Main entry point (Orchestrator)
├── components.py    # Reusable UI widgets (Sidebar, Header)
├── config.py        # Centralized constants (Colors, Texts)
├── data_loader.py   # Database interaction layer
└── utils.py         # Plotly chart generation logic
```

## Module Details

### 1. `config.py`
Contains all "hardcoded" values.
- **Colors**: Defined in `COLORS` dict (e.g., `#29B6F6` for Institutional).
- **Text**: Static strings like titles and explanations.
- **Settings**: Page layout and chart theme defaults.
> **Maintenance Tip**: Change colors here to update the entire app's theme.

### 2. `data_loader.py`
Handles data fetching and caching.
- Uses `st.cache_data` to minimize database hits.
- Fetches data using SQLAlchemy sessions.
- Joins `ZScore` and `Price` tables efficiently.

### 3. `utils.py`
Wraps `plotly.graph_objects`.
- **`create_divergence_chart`**: Generates the dual-axis figure.
- Applies the "Plotly Dark" theme and custom color overrides from `config.py`.

### 4. `components.py`
Encapsulates Streamlit layout logic.
- **`render_sidebar`**: Returns a dictionary of filter states, keeping `app.py` free of widget logic.

## Dependencies
- **Streamlit**: Web framework.
- **Plotly**: Data visualization.
- **Pandas**: Data formatting.
- **Properties**: SQLAlchemy ORM for data models.

## Future Improvements (Phase 2 & 3)
- **Live Updates**: Integrate `st.empty()` or `st.rerun()` loops for real-time data.
- **Advanced Scanning**: Add a "Leaderboard" page using `st.dataframe` with formatting.
