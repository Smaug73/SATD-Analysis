
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt


def corr_gen(project_name):
    col_list = ['org_silo','missing_links','radio_silence','SATD_added_num','SATD_removed_num']
    df = pd.read_csv("/home/stefano/SATD-Analysis/CommunitySmell/communitysmells_SATD_dataset/"+project_name+"-communitysmell_satdnum_dataset.csv", usecols = col_list)
    corr_matrix=df.corr(method='pearson', min_periods=1)
    sn.heatmap(corr_matrix, annot=True)
    plt.show()