import matplotlib.pyplot as plt
import seaborn as sns
def apply_report_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        'font.size': 12,            
        'axes.titlesize': 16,  
        'axes.labelsize': 14,         
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'lines.linewidth': 2.5,       
        'figure.figsize': (12, 6),    
        'figure.autolayout': True     
    })