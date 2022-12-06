#   Script per l'analisi descrittiva dei dataset CommunitySmells-SATD
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import seaborn as sn
import os





def boxplot(df,output):
    df.boxplot( column =['SATD_added_num','missing_links','org_silo','radio_silence'], grid = True)
    plt.savefig(output, bbox_inches="tight")
    plt.clf()



def line_plot(df,output):
    df['start-end'] = df.apply(lambda row: start_end(row), axis=1)
    df.plot(kind='line',x='start-end',y=['SATD_added_num','missing_links','org_silo','radio_silence'], figsize=(20, 5))
    plt.grid()
    plt.savefig(output, bbox_inches="tight")
    plt.clf() 

def start_end(str):
    return str['start_datetime'].split()[0]+"/"+str['end_datetime'].split()[0]



def correlation(df, output):
    
    columns = ['SATD_added_num','missing_links','org_silo','radio_silence']

    SATD_added_num = []
    missing_links = []
    org_silo = []
    radio_silence = []

    SATD_added_num_p = []
    missing_links_p = []
    org_silo_p = []
    radio_silence_p = []

    for c in columns:
        for c2 in columns:
            correlation, pvalue = spearmanr(df[c], df[c2])
            print(c+" "+c2+" : "+str(correlation)+" "+str(pvalue))
            
            if c == "SATD_added_num":
                SATD_added_num.append(correlation)
                SATD_added_num_p.append(pvalue)
            elif c == "org_silo":
                org_silo.append(correlation)
                org_silo_p.append(pvalue)
            elif c == "missing_links":
                missing_links.append(correlation)
                missing_links_p.append(pvalue)
            elif c == "radio_silence":
                radio_silence.append(correlation)
                radio_silence_p.append(pvalue)
    
    dict_corr = {'SATD_added_num':SATD_added_num,'missing_links':missing_links,'org_silo':org_silo,'radio_silence':radio_silence, 'columns':columns}

    dict_pvalue = {'SATD_added_num':SATD_added_num_p,'missing_links':missing_links_p,'org_silo':org_silo_p,'radio_silence':radio_silence_p, 'columns':columns}

    corr = pd.DataFrame(dict_corr)
    corr.set_index("columns", inplace = True)

    pvalues = pd.DataFrame(dict_pvalue)
    pvalues.set_index("columns", inplace = True)

    sn.heatmap(corr, annot=True)
    #plt.show()
    plt.savefig(output+".png", bbox_inches="tight")
    plt.clf()

    sn.heatmap(pvalues, annot=True)
    #plt.show()
    plt.savefig(output+"_pvalue.png", bbox_inches="tight")
    plt.clf()




def histogram(df,output):

    df['SATD_added_num'].hist(bins=15,grid=True,color='#86bf91', zorder=2, rwidth=0.9)
    #plt.show()
    plt.savefig(output+"_SATD_added_num_histogram.png", bbox_inches="tight")
    plt.clf()

    df['missing_links'].hist(bins=15,grid=True,color='#86bf91', zorder=2, rwidth=0.9)
    #plt.show()
    plt.savefig(output+"_missing_links_histogram.png", bbox_inches="tight")
    plt.clf()

    df['org_silo'].hist(bins=15,grid=True,color='#86bf91', zorder=2, rwidth=0.9)
    #plt.show()
    plt.savefig(output+"_org_silo_histogram.png", bbox_inches="tight")
    plt.clf()

    df['radio_silence'].hist(bins=15,grid=True,color='#86bf91', zorder=2, rwidth=0.9)
    #plt.show()
    plt.savefig(output+"_radio_silence_histogram.png", bbox_inches="tight")
    plt.clf()





if __name__ == "__main__":


    dataset_folder ='/home/stefano/SATD-Analysis/CommunitySmell/communitysmells_SATD_dataset/'
    boxplot_folder ='/home/stefano/SATD-Analysis/CommunitySmell/communitysmells_SATD_dataset/boxplot/'
    plot_folder='/home/stefano/SATD-Analysis/CommunitySmell/communitysmells_SATD_dataset/plot/'
    correlation_folder='/home/stefano/SATD-Analysis/CommunitySmell/communitysmells_SATD_dataset/correlation/'
    histogram_folder='/home/stefano/SATD-Analysis/CommunitySmell/communitysmells_SATD_dataset/histogram/'

    #   Scorriamo tutti i dataset contenuti nella cartella
    for f in os.scandir(dataset_folder):
        
        if f.name.endswith('.csv') :
            
            print('File: '+f.name)

            dataset = pd.read_csv(dataset_folder+f.name)

            #boxplot(dataset, boxplot_folder+f.name+'_boxplot.png')
            
            #if f.name != 'dataset_complete.csv':
                #line_plot(dataset, plot_folder+f.name+'_lineplot.png')
            
            #correlation(dataset,correlation_folder+f.name)        
            if f.name == 'dataset_complete.csv':
                histogram(dataset,histogram_folder+f.name)