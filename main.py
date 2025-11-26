import datetime
from covid import Covid
import matplotlib
matplotlib.use('Agg')  # Must be set before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import gc

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def root():
    # Create a navigation page with buttons to other routes
    routes = [
        {
            'path': '/usavchina',
            'name': 'USA vs China COVID-19 Comparison',
            'description': 'Compare COVID-19 statistics between USA and China'
        },
        # You can add more routes here as you create them
        # {
        #     'path': '/another-route',
        #     'name': 'Another Comparison',
        #     'description': 'Description of another route'
        # }
    ]
    
    return render_template("index.html", routes=routes)

@app.route("/usavchina")
def covid_comparison_usa_v_china():
    # Initialize COVID data
    covid = Covid()
    
    try:
        usa = covid.get_status_by_country_name("usa")
        china = covid.get_status_by_country_name("china")
        
        # Extract data
        countries = [usa['country'], china['country']]
        confirmed = [usa['confirmed'], china['confirmed']]
        deaths = [usa['deaths'], china['deaths']]
        recovered = [usa['recovered'], china['recovered']]
        
        # Create the plot
        img = create_covid_plot(countries, confirmed, deaths, recovered)
        
        # Convert plot to base64 for embedding in HTML
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

         # Force cleanup
        del img
        gc.collect()
        
        return render_template('usa_v_china.html', 
                             chart_image=img_base64,
                             countries=countries,
                             usa_data=usa,
                             china_data=china)
    
    except Exception as e:
        return f"Error fetching COVID data: {str(e)}"

def create_covid_plot(countries, confirmed, deaths, recovered):
    """Create COVID-19 comparison plot and return as bytes"""
    # Set up the plot
    x = np.arange(len(countries))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 8))

    # Create bars for each category
    bars1 = ax.bar(x - width, confirmed, width, label='Confirmed', color='#1f77b4', alpha=0.8)
    bars2 = ax.bar(x, deaths, width, label='Deaths', color='#d62728', alpha=0.8)
    bars3 = ax.bar(x + width, recovered, width, label='Recovered', color='#2ca02c', alpha=0.8)

    # Customize the chart
    ax.set_xlabel('Countries', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Cases', fontsize=12, fontweight='bold')
    ax.set_title('COVID-19 Cases: USA vs China Comparison', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=12)
    ax.legend(fontsize=11)

    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold')

    add_value_labels(bars1)
    add_value_labels(bars2)
    add_value_labels(bars3)

    # Adjust y-axis to accommodate the highest value
    plt.ylim(0, max(confirmed) * 1.15)

    # Add grid for better readability
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    
    # Save plot to bytes buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()  # Close the figure to free memory
    plt.close('all')
    gc.collect()
    
    return img_buffer




if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)