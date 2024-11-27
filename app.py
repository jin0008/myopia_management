from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io
import base64

# Initialize the Flask application
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        hospital_id = request.form['hospital_id']
        dob = request.form['dob']
        sex = request.form['sex']

        # Right Eye Data
        measurement_dates_right = request.form.getlist('measurement_date_right')
        axial_lengths_right = request.form.getlist('axial_length_right')

        # Left Eye Data
        measurement_dates_left = request.form.getlist('measurement_date_left')
        axial_lengths_left = request.form.getlist('axial_length_left')

        # Validate inputs
        if not hospital_id or not dob or not sex:
            error = "Please fill out all required fields."
            return render_template('index.html', error=error)

        try:
            # Process Right Eye Measurements
            measurements_right = []
            for date, length in zip(measurement_dates_right, axial_lengths_right):
                measurements_right.append((date, float(length)))

            # Process Left Eye Measurements
            measurements_left = []
            for date, length in zip(measurement_dates_left, axial_lengths_left):
                measurements_left.append((date, float(length)))

            # Generate graph
            graph_url, error = plot_longitudinal_data_dual(
                hospital_id, dob, measurements_right, measurements_left, sex
            )
            if error:
                return render_template('index.html', error=error)

            return render_template('result.html', graph_url=graph_url)
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            return render_template('index.html', error=error)

    return render_template('index.html')


def plot_longitudinal_data_dual(hospital_id, dob, measurements_right, measurements_left, sex):
    # Calculate ages and lengths for both eyes
    ages_right = [calculate_age(dob, m[0]) for m in measurements_right]
    lengths_right = [m[1] for m in measurements_right]

    ages_left = [calculate_age(dob, m[0]) for m in measurements_left]
    lengths_left = [m[1] for m in measurements_left]

    # Select the appropriate reference data
    if sex.lower() == "male":
        df_reference = df_males
        title = "Axial Length Percentile Curves (Males)"
    elif sex.lower() == "female":
        df_reference = df_females
        title = "Axial Length Percentile Curves (Females)"
    else:
        return None, "Invalid sex entered."

    # Plot the reference graph
    plt.figure(figsize=(12, 8))
    for column in df_reference.columns[1:]:
        plt.plot(df_reference["Age"], df_reference[column], label=f"{column}th Percentile", linestyle='--')

    # Plot the child's Right Eye longitudinal data
    plt.scatter(ages_right, lengths_right, color='blue', label=f"Right Eye {hospital_id}", zorder=5)
    plt.plot(ages_right, lengths_right, color='blue', linestyle='-', zorder=5)

    # Plot the child's Left Eye longitudinal data
    plt.scatter(ages_left, lengths_left, color='green', label=f"Left Eye {hospital_id}", zorder=5)
    plt.plot(ages_left, lengths_left, color='green', linestyle='-', zorder=5)

    # Add titles and labels
    plt.title(title, fontsize=16)
    plt.xlabel("Age (years)", fontsize=14)
    plt.ylabel("Axial Length (mm)", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(alpha=0.3)

    # Save the plot to a PNG image in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Encode the image to display in the template
    graph_url = base64.b64encode(img.getvalue()).decode()
    return graph_url, None
