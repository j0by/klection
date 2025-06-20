from flask import Flask, render_template, send_from_directory
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Ensure we have a static directory for serving static files
os.makedirs('static', exist_ok=True)

@app.route('/')
def index():
    # Serve the main HTML file
    return send_from_directory('.', 'ac.html')

@app.route('/data/<path:filename>')
def serve_data(filename):
    # Serve files from the data directory
    return send_from_directory('data', filename)

@app.route('/maps/<path:filename>')
def serve_maps(filename):
    # Serve files from the maps directory
    return send_from_directory('maps', filename)

@app.route('/constituency/<int:ac_no>')
def get_constituency_data(ac_no):
    try:
        df = pd.read_csv('data/kerala_2021.csv')
        df_filtered = df[df['AC_No'] == ac_no].copy()

        if df_filtered.empty:
            return '<p class="text-red-500">No data found for this constituency.</p>', 404

        constituency_name = df_filtered['AC_Name'].iloc[0].title()
        df_sorted = df_filtered.sort_values(by='Total Votes', ascending=False)

        df_display = df_sorted[['Candidate', 'Party', 'Total Votes', '% of Votes']].copy()
        df_display['Candidate'] = df_display['Candidate'].str.title()
        df_display['Party'] = df_display['Party'].str.title()
        df_display.insert(0, 'Sl No', range(1, 1 + len(df_display)))

        # Manually build HTML table for precise styling
        table_header = '''
            <thead class="text-xs text-orange-700 bg-amber-100/50">
                <tr>
                    <th scope="col" class="px-6 py-3 font-semibold">Sl No</th>
                    <th scope="col" class="px-6 py-3 font-semibold">Candidate</th>
                    <th scope="col" class="px-6 py-3 font-semibold">Party</th>
                    <th scope="col" class="px-6 py-3 font-semibold text-right">Total Votes</th>
                    <th scope="col" class="px-6 py-3 font-semibold text-right">% of Votes</th>
                </tr>
            </thead>
        '''

        table_body_rows = []
        for _, row in df_display.iterrows():
            table_body_rows.append(f'''
                <tr class="bg-white/70 border-b border-amber-200">
                    <td class="px-6 py-4">{row['Sl No']}</td>
                    <td class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">{row['Candidate']}</td>
                    <td class="px-6 py-4">{row['Party']}</td>
                    <td class="px-6 py-4 text-right">{row['Total Votes']:,}</td>
                    <td class="px-6 py-4 text-right">{row['% of Votes']}</td>
                </tr>
            ''')

        table_body = f"<tbody>{''.join(table_body_rows)}</tbody>"

        table_html = f'''
            <div class="relative overflow-x-auto rounded-lg border border-amber-200">
                <table class="w-full text-sm text-left text-gray-500">
                    {table_header}
                    {table_body}
                </table>
            </div>
        '''

        return f'''
            <h2 class="text-2xl font-bold mb-4 text-orange-800">{constituency_name}</h2>
            {table_html}
        '''
    except Exception as e:
        return f'<p class="text-red-500">An error occurred: {e}</p>', 500

if __name__ == '__main__':
    # Create the data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Get port from environment variables with a default
    port = int(os.getenv('PORT', 5000))
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=port)