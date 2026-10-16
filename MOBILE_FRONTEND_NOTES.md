# Mobile-friendly frontend update

Only frontend presentation/layout changes were made. The existing Streamlit pages, login flow, database functions, AI models, complaint workflow, and role permissions are otherwise unchanged.

## Changes
- Shared responsive CSS is applied through `utils.render_sidebar()` across the app pages.
- Columns stack vertically on narrow screens; content, images, tables, buttons, forms, and map frames are constrained to the viewport.
- Inputs use a mobile-friendly font size and buttons have touch-friendly height.
- Sidebar starts collapsed to give phone screens more room; it remains available through Streamlit navigation.

## Security/data note
The original `.env`, `.git` history, Python cache files, and previously uploaded complaint images were not included in this package. Keep your actual `.env` and complaint records backed up separately; configure secrets in your hosting environment.

## Test before deploying
Check sign-in, registration, complaint submission, image upload, map pin selection, My Complaints, feedback, and officer/admin dashboards on a phone and desktop. Streamlit's own component rendering can vary slightly by browser and device.
