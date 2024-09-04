from flask import Flask, render_template, request, send_file
import csv
import datetime
import io
import os
from datetime import datetime, timezone

app = Flask(__name__)


def convert_to_unix_milliseconds(date_string):
    date_string = date_string.strip()
    formats = [
        "%d-%m-%Y %H:%M:%S",  # 23-08-2024 11:00:00
        "%d-%m-%Y %I:%M:%S %p",  # 23-08-2024 11:00:00 AM
        "%Y-%m-%d %H:%M:%S",  # 2024-08-23 11:00:00
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            # Assume the input is in UTC, if not specified
            dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue

    return f"Error: Unable to parse '{date_string}'"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        if file and file.filename.endswith('.csv'):
            # Read the input CSV
            input_stream = io.StringIO(
                file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(input_stream)

            # Process the data
            output = io.StringIO()
            csv_output = csv.writer(output)
            csv_output.writerow(['Original DateTime', 'Unix Timestamp (ms)'])

            for row in csv_input:
                if row:  # Skip empty rows
                    original_date = row[0]
                    unix_time = convert_to_unix_milliseconds(original_date)
                    csv_output.writerow([original_date, unix_time])

            # Prepare the output file
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='converted_timestamps.csv'  # Changed from attachment_filename
            )

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
