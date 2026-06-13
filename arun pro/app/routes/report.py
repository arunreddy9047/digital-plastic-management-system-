from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Volunteer, WasteCollection, WasteRecord
from app import db
import matplotlib
matplotlib.use('Agg') # Safe head-less rendering on server
import matplotlib.pyplot as plt
import os
from sqlalchemy import func
from app.auth_utils import admin_required

report_bp = Blueprint("report", __name__)

@report_bp.route("/report")
@login_required
@admin_required
def report():
    volunteers = Volunteer.query.all()
    
    # Try fetching from WasteCollection table first
    waste_data = WasteCollection.query.all()
    
    months = []
    values = []
    
    if waste_data:
        months = [w.month for w in waste_data]
        values = [w.collected_kg for w in waste_data]
    else:
        # Fallback: Query WasteRecord dynamically grouped by month (SQLite format)
        results = db.session.query(
            func.strftime('%Y-%m', WasteRecord.recorded_date).label('month'),
            func.sum(WasteRecord.quantity_kg)
        ).group_by('month').order_by('month').all()
        
        months = [r[0] for r in results]
        values = [float(r[1]) for r in results]
        
    # Check if we have data to plot
    chart_filename = None
    if months:
        try:
            plt.figure(figsize=(8, 4))
            plt.bar(months, values, color="#10b981") # emerald green
            plt.title("Monthly Waste Collection Performance (kg)", color="#f8fafc", fontsize=14, fontweight='bold')
            plt.xlabel("Month", color="#cbd5e1")
            plt.ylabel("Waste Collected (kg)", color="#cbd5e1")
            
            # Stylize the chart for dark/glassmorphism integration
            plt.gcf().patch.set_facecolor('#0f172a') # dark background
            ax = plt.gca()
            ax.set_facecolor('#1e293b')
            ax.spines['bottom'].set_color('#475569')
            ax.spines['top'].set_color('#475569')
            ax.spines['right'].set_color('#475569')
            ax.spines['left'].set_color('#475569')
            ax.tick_params(colors='#cbd5e1')
            ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#475569')
            ax.set_axisbelow(True)
            
            plt.tight_layout()
            
            # Ensure static folder exists
            static_dir = os.path.join("app", "static")
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)
                
            chart_path = os.path.join(static_dir, "waste_chart.png")
            if os.path.exists(chart_path):
                os.remove(chart_path)
            plt.savefig(chart_path, facecolor=plt.gcf().get_facecolor(), edgecolor='none')
            plt.close()
            chart_filename = "waste_chart.png"
        except Exception as e:
            print("Matplotlib generation failed:", e)
            
    # Format database data for table presentation
    table_waste_data = []
    if waste_data:
        table_waste_data = waste_data
    else:
        for m, val in zip(months, values):
            # Create a mock object for compatibility with the report template
            class MockWaste:
                def __init__(self, month, collected_kg):
                    self.month = month
                    self.collected_kg = int(collected_kg)
            table_waste_data.append(MockWaste(m, val))

    return render_template(
        "report.html",
        volunteers=volunteers,
        waste_data=table_waste_data,
        chart_file=chart_filename
    )
