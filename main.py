from flask import Flask, render_template, request, jsonify,redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Define the scope and load credentials from the JSON file
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('D:\zabuza\pythonProject\data\secreatekey.json', scope)
gc = gspread.authorize(credentials)

# Open the Google Sheet by title
spreadsheet = gc.open('student')
worksheet = spreadsheet.get_worksheet(0)  # Adjust the index as needed

@app.route('/')
def index():
    unique_list = []
    for cell in worksheet.range('C2:C140'):
        if cell.value not in unique_list and cell.value != '-' and cell.value != '':
            unique_list.append(cell.value)
    # print(unique_list)
    return render_template('index.html', unique_list=unique_list)

@app.route('/get_project_details', methods=['POST'])
def get_project_details():
    project_name = request.form['project_name']
    data = worksheet.get_all_records()
    project_details = [project for project in data if project['Project Name'] == project_name]

    if not project_details:
        return jsonify({'error': 'Project not found'})
    else:
        return jsonify({'project_details': project_details})

@app.route('/update_project', methods=['GET', 'POST'])
def update_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        developer = request.form['developer']
        task = request.form['task']
        status = request.form['status']

        # Find and update the row in the Google Sheet
        data = worksheet.get_all_records()
        updated = False

        for index, row in enumerate(data, start=2):  # Start from the second row (headers in the first row)
            if row['Project Name'] == project_name and row['Developer'] == developer:
                worksheet.update_acell(f'A{index}', task)  # Update the 'Task' column (assuming it's column 'C')
                worksheet.update_acell(f'D{index}', status)  # Update the 'Status' column (assuming it's column 'D')


                updated = True
                break

        if updated:
            return redirect(url_for('index'))

    else:
        project_name = request.args.get('project_name')
        developer = request.args.get('developer')

        return render_template('update.html', project_name=project_name, developer=developer)

if __name__ == '__main__':
    app.run(debug=True)

