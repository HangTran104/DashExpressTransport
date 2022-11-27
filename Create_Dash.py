import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import *
from numpy import *
from datetime import datetime

def load_dataset():
  uploaded_file = st.file_uploader("Choose a file")
  data  = read_excel(uploaded_file, engine='openpyxl')
  return data

def data_cleaner(df):
  df['Thời Gian Tạo'] = to_datetime(df['Thời Gian Tạo'])
  df['Tỉnh / Thành Phố'] = df['Tỉnh / Thành Phố'].str.replace('Tỉnh ', '')
  df['Tỉnh / Thành Phố'] = df['Tỉnh / Thành Phố'].str.replace('Thành phố','TP.')
  df['Tỉnh / Thành Phố'] = df['Tỉnh / Thành Phố'].str.replace('Thành Phố','TP.')
  df['Vendor_code']= df['Đơn Vị Vận Chuyển'].str.extract('([A-Za-z]+)')[0]
  df['Actual']=df['Phí Vận Chuyển'] - df['Phí Đối Tác Thu']
  df['Mã Shop'] = df['Tên Shop'].str.extract('(\d+)')
  df['Tên Shop']=df['Tên Shop'].str.replace('(\d+\W+)', '', regex=True)
  df['month'] = df['Thời Gian Tạo'].apply(lambda x: str(x)[:7])
  df['date'] = df['Thời Gian Tạo'].dt.date
  df = df[df['Actual']>0]
  df['status_'] = df['Trạng Thái']
  df['status_'] = df['status_'].str.replace('Đã Trả Hàng Toàn Bộ','Trả hàng')
  df['status_'] = df['status_'].str.replace('Đã Trả Hàng Một Phần','Trả hàng')
  df['status_'] = df['status_'].str.replace('Đang Chuyển Kho Trả','Trả hàng')
  df['status_'] = df['status_'].str.replace('Đang Chuyển Kho Giao','Đang Thực hiện')
  df['status_'] = df['status_'].str.replace('Đang Giao Hàng','Đang Thực hiện')
  df['status_'] = df['status_'].str.replace('Đang Vận Chuyển','Đang Thực hiện')
  df['status_'] = df['status_'].str.replace('Xác Nhận Hoàn','Trả hàng')
  return df


def  dataset_survey(data):
  types = data.dtypes
  nuniques = data.nunique()
  nulls = data.isnull().sum()
  missing_ration = data.isnull().sum()/data.shape[0]*100
  uniques = data.apply(lambda x: x.unique())
  counts = data.apply(lambda x: x.count())
  df = concat([types, nuniques, nulls, missing_ration, counts, uniques], axis=1, sort=True)
  df.columns = ['types', 'nuniques','nulls','missing_ration', 'counts', 'uniques']
  return df.sort_values('nulls', ascending=False)
  


if __name__ == '__main__':
  st.title('Demo DashBoard')
  menu = ["Introduction", "DashBoardDemo"]
  choice = st.sidebar.selectbox('Menu', menu)
  if choice=='DataIntroduction':
    st.subheader("Business Introduction")
  elif choice=='DashBoardDemo':
    st.subheader('Demo Dashboard Of Revenue')
    df = load_dataset()
    
    st.subheader('Choose the status: ')
    status = st.multiselect('Option of Status: ', options=df['Trạng Thái'].unique())
    submit = st.button('Submit')
    min_date = df['Thời Gian Tạo'].min().date()
    max_date = df['Thời Gian Tạo'].max().date()

    a_date = st.date_input("Pick a date", (min_date,max_date))

    df = df[(df['Trạng Thái'].isin(status))&((df['date'] >a_date[0]) & (df['date'] < a_date[1]))]
    df = data_cleaner(df)
    st.subheader('Load DataFrame: ')
    st.dataframe(df.head())
    st.subheader('Data Description:')
    st.dataframe(dataset_survey(df))

    st.subheader('Now let view the summary dashboard: ')
    st.write(list(df['Trạng Thái'].unique()))
    
    # Summarize text
    fig0=plt.figure(figsize=(20,8))
    ax11 = plt.subplot(121)
    ax11.text(0.4,0.4, 'Total Amount', fontsize=45, fontweight='bold')
    ax11.text(0.5,0.3, '{0:,.2f}M'.format(df['Actual'].sum().round(2)/1000000), fontsize=40, fontweight='regular')
    plt.axis('off')
    ax12 = plt.subplot(122)
    ax12.text(0.4,0.4, 'Total Volume', fontsize=45, fontweight='bold')
    ax12.text(0.5,0.3, '{0:,.0f}'.format(df['Actual'].count().round(2)), fontsize=40, fontweight='regular')
    plt.axis('off')
    st.pyplot(fig0)
  
    # Summarize text
    st.subheader('Revenue by Vendor')
    
    fig1 = plt.figure(figsize=(20,8))
    # plt.suptitle('Revenue by Vendor')

    # Vendor parts
    ax1 = plt.subplot(131)
    ax1.pie(df['Vendor_code'].value_counts(), labels=df['Vendor_code'].value_counts().index, autopct='%.1f%%', shadow=True, textprops={"color":'k', 'fontsize':16, "fontweight":'bold'}, startangle=90, radius=1.2)
    # df
    sum_by_vendor = df.groupby(['Vendor_code', 'Mã Shop']).agg(
        tenshop=('Tên Shop', 'first'),
        tinh=('Tỉnh / Thành Phố', 'first'),
        month=('month', 'first'),
        revenue = ('Actual', 'sum'),
        count_orders = ('Tên Shop', 'count'),
        Tinh = ('Tỉnh / Thành Phố', 'first'),
        KL = ('Khối Lượng', 'sum')
    ).reset_index().sort_values(by='revenue', ascending=False)
    ax2=plt.subplot(132)
    sns.barplot(data=sum_by_vendor, x='Vendor_code', y='revenue', estimator=sum, ci=0, ax=ax2, palette='Blues_r')
    ax2.set_xticklabels(sum_by_vendor['Vendor_code'].unique(),rotation=90, fontsize=18)
    ax2.set_yticks(arange(0,15000000,2000000))
    ax2.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,15000000,2000000)], fontsize=18)
    sns.despine(top=True, bottom=False, right=True, left=False)
    ax2.set_title("Revenue by Vendor", fontsize=20, fontweight='bold')
    ax2.set_ylabel('Revenue', fontsize=18, fontweight='bold')
    ax2.set_xlabel('Tên Shop', fontsize=18, fontweight='bold')


    ax3=plt.subplot(133)
    sns.barplot(data=sum_by_vendor, x='Vendor_code', y='count_orders', estimator=sum, ci=0, ax=ax3, palette='Blues_r')
    ax3.set_xticklabels(sum_by_vendor['Vendor_code'].unique(),rotation=90, fontsize=18)
    ax3.set_yticks(arange(0,15000000,2000000))
    ax3.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,15000000,2000000)], fontsize=14)
    sns.despine(top=True, bottom=True, right=True, left=True)
    ax3.set_title("Volume by Vendor", fontsize=20, fontweight='bold')
    ax3.set_ylabel('Number of Orders', fontsize=18, fontweight='bold')
    ax3.set_xlabel('Tên Shop', fontsize=18, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig1)
    
    
    # Status parts
    st.write('Revenue by Status')

    # Status parts
    sum_by_status = df.groupby(['Trạng Thái']).agg(
    revenue = ('Actual', 'sum'),
    count_orders = ('Tên Shop', 'count'),
    KL = ('Khối Lượng', 'sum')
      ).reset_index().sort_values(by='revenue', ascending=False)
    fig2=plt.figure(figsize=(30,10))
    ax4 = plt.subplot(131)
    ax4.pie(sum_by_status['Trạng Thái'].value_counts(), labels=sum_by_status['Trạng Thái'].value_counts().index, autopct='%.1f%%', shadow=True, textprops={"color":'k', 'fontsize':20, "fontweight":'bold'}, explode=[i*0.1 for i in range(len(sum_by_status['Trạng Thái'].value_counts().index))], radius=1.2, startangle=90)

    ax41 = plt.subplot(132)
    sns.barplot(data=sum_by_status, x='Trạng Thái', y='revenue', estimator=sum, ci=0, ax=ax41, palette='Blues_r')
    ax41.set_xticklabels(sum_by_status['Trạng Thái'].unique(),rotation=90, fontsize=20)
    ax41.set_yticks(arange(0,14000000,2000000))
    ax41.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,14000000,2000000)], fontsize=20)
    ax41.set_title("Revenue by Status", fontsize=24, fontweight='bold')
    ax41.set_ylabel('Revenue', fontsize=20, fontweight='bold')
    ax41.set_xlabel('Status_', fontsize=20, fontweight='bold')

    ax42 = plt.subplot(133)
    sns.barplot(data=sum_by_status, x='Trạng Thái', y='count_orders', estimator=sum, ci=0, ax=ax42, palette='Blues_r')
    ax42.set_xticklabels(sum_by_status['Trạng Thái'].unique(),rotation=90, fontsize=20)
    ax42.set_title("Volume by Account and Vendor", fontsize=24, fontweight='bold')
    ax42.set_ylabel('Number of Orders', fontsize=20, fontweight='bold')
    ax42.set_xlabel('Tên Shop', fontsize=20, fontweight='bold')
    st.pyplot(fig2)

    # Revenue overtime
    fig3=plt.figure(figsize=(20,8))
    sns.lineplot(data=df.sort_values(by='month'), x='month', y='Actual', estimator=sum, marker='o', color='orange', hue='Vendor_code')
    plt.xticks(arange(0,12),df.sort_values(by='month')['month'].unique(), fontsize=18)
    plt.yticks(arange(0,7000000,1000000),[str(i/1000000)+'M' for i in arange(0,7000000,1000000)], fontsize=18)
    sns.despine(top=True, bottom=True, right=True, left=True)
    plt.title("Revenue over time by vendor", fontsize=20, fontweight='bold')
    plt.ylabel('Revenue', fontsize=18, fontweight='bold')
    plt.xlabel('Time', fontsize=18, fontweight='bold')
    plt.grid(axis='y', ls='--')
    
    st.pyplot(fig3)
    
    # Province
    fig4=plt.figure(figsize=(20,8))
    sns.barplot(data=sum_by_vendor.groupby('tinh').sum().reset_index()[['tinh', 'revenue']].sort_values(by='revenue',ascending=False), x='tinh', y='revenue', palette='Blues_r', estimator=sum)
    plt.xticks(rotation=90, fontsize=18)
    plt.yticks(arange(0,3000000,500000),[str(i/1000000)+'M' for i in arange(0,3000000,500000)], fontsize=20)
    # plt.yticks(labels=[str(i/1000000)+'M' for i in arange(0,3000000,500000)], fontsize=20)
    plt.title("Revenue by Province", fontsize=20, fontweight='bold')
    plt.ylabel('Revenue', fontsize=18, fontweight='bold')
    plt.xlabel('Province Name', fontsize=18, fontweight='bold')
    sns.despine(top=True, right=True)
    st.pyplot(fig4)
    
    # Shop
    # Tên Shop
    fig5=plt.figure(figsize=(30,10))
    ## df
    sum_by_shopcode = df.groupby(['Mã Shop']).agg(
        tenshop=('Tên Shop', 'first'),
        revenue = ('Actual', 'sum'),
        count_orders = ('Tên Shop', 'count'),
        Tinh = ('Tỉnh / Thành Phố', 'first'),
        KL = ('Khối Lượng', 'sum')
    ).reset_index().sort_values(by='revenue', ascending=False)
    ## Plot
    sns.barplot(data=sum_by_shopcode, x='tenshop', y='revenue', palette='Blues_r', estimator=sum)
    plt.xticks(rotation=90, fontsize=20)
    plt.yticks(arange(0,3000000,500000),[str(i/1000000)+'M' for i in arange(0,3000000,500000)])
    # ax7.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,3000000,500000)], fontsize=20)
    plt.title("Revenue by Account", fontsize=20, fontweight='bold')
    plt.ylabel('Revenue', fontsize=18, fontweight='bold')
    plt.xlabel('ShopName', fontsize=18, fontweight='bold')
    sns.despine(top=True, right=True)
    st.pyplot(fig5)




    
    




