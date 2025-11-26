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
covid = Covid()


@app.route("/")
def root():
    routes = [
        {
            'path': '/usavchina',
            'name': 'USA vs China',
            'description': 'Compare key COVID statistics between USA and China'
        },
        {
            'path': '/country/italy',
            'name': 'Italy COVID Statistics',
            'description': 'View detailed COVID statistics for Italy'
        },
    ]
    
    return render_template("index.html", routes=routes)

@app.route("/usavchina")
def covid_comparison_usa_v_china():
    
    try:
        usa = covid.get_status_by_country_name("usa")
        china = covid.get_status_by_country_name("china")
        
        # Extract data
        countries = [usa['country'], china['country']]
        confirmed = [usa['confirmed'], china['confirmed']]
        deaths = [usa['deaths'], china['deaths']]
        recovered = [usa['recovered'], china['recovered']]
        
        # Create the plot
        img = create_compcovid_plot(countries, confirmed, deaths, recovered)
        
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

def create_compcovid_plot(countries, confirmed, deaths, recovered):
    # Set up the plot
    x = np.arange(len(countries))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create bars for each category
    bars1 = ax.bar(x - width, confirmed, width, label='Confirmed', color='#1f77b4', alpha=0.8)
    bars2 = ax.bar(x, deaths, width, label='Deaths', color='#d62728', alpha=0.8)
    bars3 = ax.bar(x + width, recovered, width, label='Recovered', color='#2ca02c', alpha=0.8)

    # Customize the chart
    ax.set_xlabel('Countries', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Cases (millions)', fontsize=12, fontweight='bold')
    ax.set_title('COVID: USA vs China', fontsize=16, fontweight='bold')
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

def create_sc_plt_donut(country_data):
    # Extract data
    country_name = country_data['country']
    
    # Set up the plot - single subplot now
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create donut chart with all categories
    pie_categories = ['Active', 'Critical', 'Deaths', 'Recovered']
    pie_values = [
        country_data['active'],
        country_data['critical'],
        country_data['deaths'],
        country_data['recovered']
    ]
    pie_colors = ['#ff7f0e', '#d62728', '#2ca02c', '#9467bd']
    
    # Only show donut chart if there are values to display
    if sum(pie_values) > 0:
        # Calculate percentages
        total = sum(pie_values)
        
        # Create donut chart
        wedges, _, autotexts = ax.pie(pie_values, colors=pie_colors, startangle=90,
                                         autopct=lambda pct: f'{pct:.1f}%' if pct >= 1 else '',
                                         textprops={'fontsize': 10},
                                         wedgeprops={'width': 0.6})  # This makes it a donut
        
        # Make autopct text white and bold for better visibility
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        # Add center text with total and country info
        center_circle = plt.Circle((0,0), 0.3, fc='white')
        ax.add_artist(center_circle)
        ax.text(0, 0.1, f'{country_name}', ha='center', va='center', 
                fontsize=14, fontweight='bold')
        ax.text(0, -0.1, f'Total Cases:\n{total:,}', ha='center', va='center', 
                fontsize=11, fontweight='bold')
        
        # Create a legend with all statistics
        legend_labels = []
        for cat, val in zip(pie_categories, pie_values):
            legend_labels.append(f'{cat}: {val:,}')
        
        # Add confirmed cases to legend since it's not in the donut
        legend_labels.append(f"Confirmed: {country_data['confirmed']:,}")
        
        ax.legend(wedges, legend_labels,
                 title="COVID-19 Statistics",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1),
                 fontsize=10)
        
        ax.set_title(f'COVID Statistics: {country_name}', 
                    fontsize=16, fontweight='bold', pad=20)
        
    else:
        # If no data, show a message
        ax.text(0.5, 0.5, f'No data available\nfor {country_name}', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, fontweight='bold')
        ax.set_title(f'COVID-19 Statistics: {country_name}', fontsize=16, fontweight='bold')
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    # Save plot to bytes buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close(fig)  # Close the figure to free memory
    plt.close('all')
    gc.collect()
    
    return img_buffer

@app.route("/country/<country_name>")
def country_stats(country_name):
    
    try:
        country_data = covid.get_status_by_country_name(country_name.lower())
        
        # Create the plot
        img = create_sc_plt_donut(country_data)
        
        # Convert plot to base64 for embedding in HTML
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

        # Force cleanup
        del img
        gc.collect()
        
        return render_template('c_stats.html', 
                             chart_image=img_base64,
                             country_data=country_data)
    
    except Exception as e:
        return f"Error fetching COVID data for {country_name}: {str(e)}"




if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)