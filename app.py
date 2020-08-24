import streamlit as st
import altair as alt
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import altair as alt
from vega_datasets import data


st.title('Chilean Research Team Recomendations')

st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: {1200}px;
        padding-top: {0}rem;
        padding-right: {5}rem;
        padding-left: {1}rem;
        padding-bottom: {0}rem;
    }}
    .reportview-container .main {{
        color: {'Grey'};
        background-color: {'#ffffff'};
    }}
</style>
""",
        unsafe_allow_html=True,
    )


df1=pd.read_csv('recom.csv')
df1['Date']=pd.to_datetime(df1['Date'])
df1['Account_Id']=pd.to_numeric(df1['Account_Id'])
igpa_inx=pd.read_csv('igpa.csv')

recom = pd.pivot_table(data=df1, index=['Issuer_Local_Industry','An_Name','Issuer_Compass_Alias','Type','Account_Id'],columns=['Date'], values=['Value'])

sc=st.sidebar.radio(
    'Searching Criteria:',
    ('Analyst','Industry'),index=0)
'Searching Criteria:',sc

if sc=='Analyst':
    a=0
else:
    a=1

recom=recom.droplevel(a)

recom.drop(['ANTARCHILE','QUINENCO','ORO BLANCO','SM CHILE','NORTEGRAN','EDELPA','INVERCAP','NUEVAPOLAR','SOQUICOM','FOSFOROS','MOLYMET',
           'GASCO','NAVIERA','VOLCAN','SANTA RITA','CEMENTOS','AQUACHILE','AUSTRALIS','ALMENDRAL','IAM','ILC'], level=1, axis=0,inplace=True)


#import plotly.express as px

indus=list(recom.index.get_level_values(0).unique())


option=st.sidebar.selectbox(
    'Select an option:',
    indus)
'You Selected:',option
i=option

@st.cache(suppress_st_warning=True)
def charter(i):

    recom2=recom[recom.columns[recom.columns.levels[1]>datetime.strptime('01/01/20', '%m/%d/%y')]] # selecciona mayores a una fecha
    ind=recom2.loc[i]
    xvals=list(ind.columns.get_level_values(1))
    igpa_inx['Date']=pd.to_datetime(igpa_inx['Date'])
    igpa_inx2=igpa_inx.set_index('Date')
    igpa_inx2=igpa_inx2.reindex(xvals)
    # igpa_v=np.array(igpa_inx2.value)/np.array(igpa_inx2.value)[0]

    companies=list(ind.index.get_level_values(0).unique())
    long=len(companies)//2+1

    return ind,companies,long,igpa_inx2,xvals

params=charter(option)

plt.figure(figsize=(10,4*params[2]))
for c, value in enumerate(params[1],1):
    
    company=params[0].loc[value]
    price=company.loc(axis=0)[:,[39]]
    price=price.T.fillna(method='ffill').loc['Value']

    company=params[0].loc[value]
    rec=company.loc(axis=0)[:,[43]]
    rec=rec.T.fillna(method='ffill').loc['Value']
        
    a=np.array(price.loc[:,'Actual'])
    e=np.array(price.loc[:,'Estimates'])
        
    rec1=rec.replace(0,np.nan)
    rec1=rec1.replace(-1,np.nan)
    buy=np.array(rec1)
    buy=buy*e

    rec2=rec.replace(1,np.nan)
    rec2=rec2.replace(-1,np.nan)
    rec2=rec2.replace(0,1)
    hold=np.array(rec2)
    hold=hold*e

    rec3=rec.replace(1,np.nan)
    rec3=rec3.replace(0,np.nan)
    rec3=rec3.replace(-1,1)
    sell=np.array(rec3)
    sell=sell*e
        
    igpa_v2=np.array(params[3].value)/np.array(params[3].value)[0]*a[0]
        
    datos=pd.DataFrame()
    datos['a']=price.Actual.loc[:,39]
    datos['rec']=rec
    datos['idx']=igpa_v2
    datos['a_var']=datos['a'].pct_change()*datos['rec']
    datos['idx_var']=datos['idx'].pct_change()*datos['rec']
    # datos['alpha']=datos['a_var']-datos['idx_var']
        #datos=datos.dropna()
    
    upside=round((price.loc[price.index.max()][1]/price.loc[price.index.max()][0]-1)*100,1)
    ret_idx=datos['idx_var'].sum()#.add(1).cumprod().iloc[-1]-1
    ret_acc=datos['a_var'].sum()#.add(1).cumprod().iloc[-1]-1
    # alpha_acum=(datos['alpha'].add(1).cumprod().iloc[-1]-1)*100
    alpha_acum=round((ret_acc-ret_idx)*100,1)

    plt.subplot(params[2],2,c)
    plt.title(str(value)+' \n (alpha ytd: '+str(alpha_acum)+'%)'+'\n (upside:'+str(upside)+'%)', size=10)

    plt.plot(params[4],igpa_v2, color='blue',alpha=1,linewidth=1,linestyle='--',label='igpa')
    plt.plot(params[4],a, color='black',alpha=0.8)
    plt.plot(params[4],e, color='grey',alpha=0.8, linestyle='--')
    plt.plot(params[4],buy, color='green',alpha=1,linewidth=3)
    plt.plot(params[4],hold, color='grey',alpha=1,linewidth=3)
    plt.plot(params[4],sell, color='red',alpha=1,linewidth=3)

    plt.tick_params(labelrotation=90,axis='x')
    plt.tick_params(labelsize=8)

    plt.legend()
    plt.tight_layout()
st.pyplot()



# recom2=recom[recom.columns[recom.columns.levels[1]>datetime.strptime('01/01/20', '%m/%d/%y')]] # selecciona mayores a una fecha
# ind=recom2.loc[i]
# xvals=list(ind.columns.get_level_values(1))
# igpa_inx['Date']=pd.to_datetime(igpa_inx['Date'])
# igpa_inx2=igpa_inx.set_index('Date')
# igpa_inx2=igpa_inx2.reindex(xvals)
#     # igpa_v=np.array(igpa_inx2.value)/np.array(igpa_inx2.value)[0]

# companies=list(ind.index.get_level_values(0).unique())
# long=len(companies)//2+1

# plt.figure(figsize=(10,4*long))
# for c, value in enumerate(companies,2):
    
#     company=ind.loc[value]
#     price=company.loc(axis=0)[:,[39]]
#     price=price.T.fillna(method='ffill').loc['Value']

#     company=ind.loc[value]
#     rec=company.loc(axis=0)[:,[43]]
#     rec=rec.T.fillna(method='ffill').loc['Value']
        
#     a=np.array(price.loc[:,'Actual'])
#     e=np.array(price.loc[:,'Estimates'])
        
#     rec1=rec.replace(0,np.nan)
#     rec1=rec1.replace(-1,np.nan)
#     buy=np.array(rec1)
#     buy=buy*e

#     rec2=rec.replace(1,np.nan)
#     rec2=rec2.replace(-1,np.nan)
#     rec2=rec2.replace(0,1)
#     hold=np.array(rec2)
#     hold=hold*e

#     rec3=rec.replace(1,np.nan)
#     rec3=rec3.replace(0,np.nan)
#     rec3=rec3.replace(-1,1)
#     sell=np.array(rec3)
#     sell=sell*e
        
#     igpa_v2=np.array(igpa_inx2.value)/np.array(igpa_inx2.value)[0]*a[0]
        
#     datos=pd.DataFrame()
#     datos['a']=price.Actual.loc[:,39]
#     datos['rec']=rec
#     datos['idx']=igpa_v2
#     datos['a_var']=datos['a'].pct_change()*datos['rec']
#     datos['idx_var']=datos['idx'].pct_change()*datos['rec']
#         #datos=datos.dropna()
    
#     upside=round((price.loc[price.index.max()][1]/price.loc[price.index.max()][0]-1)*100,1)
#     ret_idx=datos['idx_var'].add(1).cumprod().iloc[-1]-1
#     ret_acc=datos['a_var'].add(1).cumprod().iloc[-1]-1
#     alpha_acum=round((ret_acc-ret_idx)*100,1)

#     plt.subplot(long,2,c)
#     plt.title(str(value)+' \n (alpha ytd: '+str(alpha_acum)+'%)'+'\n (upside:'+str(upside)+'%)', size=10)

#     plt.plot(xvals,igpa_v2, color='blue',alpha=1,linewidth=1,linestyle='--',label='igpa')
#     plt.plot(xvals,a, color='black',alpha=0.8)
#     plt.plot(xvals,e, color='grey',alpha=0.8, linestyle='--')
#     plt.plot(xvals,buy, color='green',alpha=1,linewidth=3)
#     plt.plot(xvals,hold, color='grey',alpha=1,linewidth=3)
#     plt.plot(xvals,sell, color='red',alpha=1,linewidth=3)

#     plt.tick_params(labelrotation=90,axis='x')
#     plt.tick_params(labelsize=8)

#     plt.legend()
#     plt.tight_layout()
# st.pyplot()
