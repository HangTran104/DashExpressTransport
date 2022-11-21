import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import *
from numpy import *
import matplotlib.gridspec as gc

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
  


def create_full_charts(data_frame, labels): 
  fig = plt.figure(figsize=(40,90), dpi=300)
  spec = gc.GridSpec(nrows=6, ncols = 3)


  # Summarize text
  ax11 = fig.add_subplot(spec[0,1])
  ax11.text(0.4,0.4, 'Total Amount', fontsize=45, fontweight='bold')
  ax11.text(0.5,0.3, '{0:,.2f}M'.format(data_frame['Actual'].sum().round(2)/1000000), fontsize=40, fontweight='regular')
  plt.axis('off')
  ax12 = fig.add_subplot(spec[0,2])
  ax12.text(0.4,0.4, 'Total Volume', fontsize=45, fontweight='bold')
  ax12.text(0.5,0.3, '{0:,.0f}'.format(data_frame['Actual'].count().round(2)), fontsize=40, fontweight='regular')
  plt.axis('off')
  # Vendor parts
  ax1 = fig.add_subplot(spec[1,0])
  ax1.pie(data_frame['Vendor_code'].value_counts(), labels=data_frame['Vendor_code'].value_counts().index, autopct='%.1f%%', shadow=True, textprops={"color":'k', 'fontsize':20, "fontweight":'bold'}, startangle=90, radius=0.7)
  # df
  sum_by_vendor = data_frame.groupby(['Vendor_code', 'Mã Shop']).agg(
      tenshop=('Tên Shop', 'first'),
      tinh=('Tỉnh / Thành Phố', 'first'),
      month=('month', 'first'),
      revenue = ('Actual', 'sum'),
      count_orders = ('Tên Shop', 'count'),
      Tinh = ('Tỉnh / Thành Phố', 'first'),
      KL = ('Khối Lượng', 'sum')
  ).reset_index().sort_values(by='revenue', ascending=False)
  ax2=fig.add_subplot(spec[1,1])
  sns.barplot(data=sum_by_vendor, x='Vendor_code', y='revenue', estimator=sum, ci=0, ax=ax2, palette='Blues_r')
  ax2.set_xticklabels(sum_by_vendor['Vendor_code'].unique(),rotation=90, fontsize=20)
  ax2.set_yticks(arange(0,15000000,2000000))
  ax2.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,15000000,2000000)], fontsize=20)
  ax2.set_title("Revenue by Account and Vendor", fontsize=24, fontweight='bold')
  ax2.set_ylabel('Revenue', fontsize=20, fontweight='bold')
  ax2.set_xlabel('Tên Shop', fontsize=20, fontweight='bold')


  ax3=fig.add_subplot(spec[1,2])
  sns.barplot(data=sum_by_vendor, x='Vendor_code', y='count_orders', estimator=sum, ci=0, ax=ax3, palette='Blues_r')
  ax3.set_xticklabels(sum_by_vendor['Vendor_code'].unique(),rotation=90, fontsize=20)
  # ax3.set_yticklabels(fontsize=20)
  ax3.set_title("Volume by Account and Vendor", fontsize=24, fontweight='bold')
  ax3.set_ylabel('Number of Orders', fontsize=20, fontweight='bold')
  ax3.set_xlabel('Tên Shop', fontsize=20, fontweight='bold')

  # Status parts

  sum_by_status = data_frame.groupby(['Trạng Thái']).agg(
    revenue = ('Actual', 'sum'),
    count_orders = ('Tên Shop', 'count'),
    KL = ('Khối Lượng', 'sum')
    ).reset_index().sort_values(by='revenue', ascending=False)
  ax4 = fig.add_subplot(spec[2,0])
  ax4.pie(data_frame['status_'].value_counts(), labels=data_frame['status_'].value_counts().index, autopct='%.1f%%', shadow=True, textprops={"color":'k', 'fontsize':20, "fontweight":'bold'}, explode=[i*0.1 for i in range(len(labels))], radius=0.7, startangle=90)

  ax41 = fig.add_subplot(spec[2,1])
  sns.barplot(data=sum_by_status, x='Trạng Thái', y='revenue', estimator=sum, ci=0, ax=ax41, palette='Blues_r')
  ax41.set_xticklabels(sum_by_status['Trạng Thái'].unique(),rotation=90, fontsize=20)
  ax41.set_yticks(arange(0,14000000,2000000))
  ax41.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,14000000,2000000)], fontsize=20)
  ax41.set_title("Revenue by Status", fontsize=24, fontweight='bold')
  ax41.set_ylabel('Revenue', fontsize=20, fontweight='bold')
  ax41.set_xlabel('Status', fontsize=20, fontweight='bold')

  ax42 = fig.add_subplot(spec[2,2])
  sns.barplot(data=sum_by_status, x='Trạng Thái', y='count_orders', estimator=sum, ci=0, ax=ax42, palette='Blues_r')
  ax42.set_xticklabels(sum_by_status['Trạng Thái'].unique(),rotation=90, fontsize=20)
  # ax42.set_yticklabels(fontsize=20)
  ax42.set_title("Volume by Status", fontsize=24, fontweight='bold')
  ax42.set_ylabel('Number of Orders', fontsize=20, fontweight='bold')
  ax42.set_xlabel('Status', fontsize=20, fontweight='bold')


  ax5 = fig.add_subplot(spec[3, :])
  p=sns.lineplot(data=data_frame.sort_values(by='month'), x='month', y='Actual', estimator=sum, marker='o', color='orange', hue='Vendor_code',ax=ax5)
  ax5.set_xticks(arange(0,12))
  ax5.set_xticklabels(labels=p.get_xticklabels(), fontsize=20)
  ax5.set_yticks(arange(0,7000000,1000000))
  ax5.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,7000000,1000000)], fontsize=20)

  ax5.set_title("Revenue over time by vendor", fontsize=24, fontweight='bold')
  ax5.set_ylabel('Revenue', fontsize=20, fontweight='bold')
  ax5.set_xlabel('Time', fontsize=20, fontweight='bold')
  plt.legend(title='Vendor Code', fontsize=20, edgecolor='k', title_fontsize=20, labelspacing=0.8)
  plt.grid(axis='y', ls='--')

  # Province
  ax6 = fig.add_subplot(spec[4,:])
  sns.barplot(data=sum_by_vendor.groupby('tinh').sum().reset_index()[['tinh', 'revenue']].sort_values(by='revenue',ascending=False), x='tinh', y='revenue', palette='Blues_r', estimator=sum, ax=ax6)
  ax6.set_xticklabels(sum_by_vendor.groupby('tinh').sum().reset_index()[['tinh', 'revenue']].sort_values(by='revenue',ascending=False)['tinh'].unique(),rotation=90, fontsize=20)
  ax6.set_yticks(arange(0,3000000,500000))
  ax6.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,3000000,500000)], fontsize=20)
  ax6.set_title("Revenue by Province", fontsize=24, fontweight='bold')
  ax6.set_ylabel('Revenue', fontsize=20, fontweight='bold')
  ax6.set_xlabel('Province Name', fontsize=20, fontweight='bold')

  # Tên Shop
  ax7 = fig.add_subplot(spec[5,:])
  ## df
  sum_by_shopcode = data_frame.groupby(['Mã Shop']).agg(
      tenshop=('Tên Shop', 'first'),
      revenue = ('Actual', 'sum'),
      count_orders = ('Tên Shop', 'count'),
      Tinh = ('Tỉnh / Thành Phố', 'first'),
      KL = ('Khối Lượng', 'sum')
  ).reset_index().sort_values(by='revenue', ascending=False)

  ## Plot
  sns.barplot(data=sum_by_shopcode, x='tenshop', y='revenue', palette='Blues_r', estimator=sum, ax=ax7)
  ax7.set_xticklabels(sum_by_shopcode['tenshop'].unique(),rotation=90, fontsize=20)
  ax7.set_yticks(arange(0,3000000,500000))
  ax7.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,3000000,500000)], fontsize=20)
  ax7.set_title("Revenue by Account", fontsize=24, fontweight='bold')
  ax7.set_ylabel('Revenue', fontsize=20, fontweight='bold')
  ax7.set_xlabel('ShopName', fontsize=20, fontweight='bold')

  sns.despine(top=True, bottom=False, right=True, left=False)
  plt.tight_layout()
  





if __name__ == '__main__':
  st.title('Demo DashBoard')
  menu = ["Introduction", "DashBoardDemo"]
  choice = st.sidebar.selectbox('Menu', menu)
  if choice=='DataIntroduction':
    st.subheader("Business Introduction")
  elif choice=='DashBoardDemo':
    st.subheader('Demo Dashboard Of Revenue')
    data_frame = load_dataset()
    
    st.subheader('Choose the status: ')
    status = st.multiselect('Option of Status: ', options=data_frame['Trạng Thái'].unique())
    submit = st.button('Submit')

    data_frame = data_frame[data_frame['Trạng Thái'].isin(status)]
    data_frame = data_cleaner(data_frame)
    st.subheader('Load DataFrame: ')
    st.dataframe(data_frame.head())
    st.subheader('Data Description:')
    st.dataframe(dataset_survey(data_frame))

    st.subheader('Now let view the summary dashboard: ')
    st.write(list(data_frame['Trạng Thái'].unique()))
#     pyplot(create_full_charts(data_frame=data_frame, labels=data['Trạng Thái'].unique()))
    st.pyplot(create_full_charts(data_frame=data_frame, labels=data_frame['Trạng Thái'].unique()))
#     fig = plt.figure(figsize=(40,96))
#     spec = gc.GridSpec(nrows=6, ncols = 3)


#     # Summarize text
#     ax11 = fig.add_subplot(spec[0,1])
#     ax11.text(0.4,0.4, 'Total Amount', fontsize=45, fontweight='bold')
#     ax11.text(0.5,0.3, '{0:,.2f}M'.format(data_frame['Actual'].sum().round(2)/1000000), fontsize=40, fontweight='regular')
#     plt.axis('off')
#     ax12 = fig.add_subplot(spec[0,2])
#     ax12.text(0.4,0.4, 'Total Volume', fontsize=45, fontweight='bold')
#     ax12.text(0.5,0.3, '{0:,.0f}'.format(data_frame['Actual'].count().round(2)), fontsize=40, fontweight='regular')
#     plt.axis('off')
#     # Vendor parts
#     ax1 = fig.add_subplot(spec[1,0])
#     ax1.pie(data_frame['Vendor_code'].value_counts(), labels=data_frame['Vendor_code'].value_counts().index, autopct='%.1f%%', shadow=True, textprops={"color":'k', 'fontsize':20, "fontweight":'bold'}, startangle=90, radius=0.7)
#     # df
#     sum_by_vendor = data_frame.groupby(['Vendor_code', 'Mã Shop']).agg(
#         tenshop=('Tên Shop', 'first'),
#         tinh=('Tỉnh / Thành Phố', 'first'),
#         month=('month', 'first'),
#         revenue = ('Actual', 'sum'),
#         count_orders = ('Tên Shop', 'count'),
#         Tinh = ('Tỉnh / Thành Phố', 'first'),
#         KL = ('Khối Lượng', 'sum')
#     ).reset_index().sort_values(by='revenue', ascending=False)
#     ax2=fig.add_subplot(spec[1,1])
#     sns.barplot(data=sum_by_vendor, x='Vendor_code', y='revenue', estimator=sum, ci=0, ax=ax2, palette='Blues_r')
#     ax2.set_xticklabels(sum_by_vendor['Vendor_code'].unique(),rotation=90, fontsize=20)
#     ax2.set_yticks(arange(0,15000000,2000000))
#     ax2.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,15000000,2000000)], fontsize=20)
#     ax2.set_title("Revenue by Account and Vendor", fontsize=24, fontweight='bold')
#     ax2.set_ylabel('Revenue', fontsize=20, fontweight='bold')
#     ax2.set_xlabel('Tên Shop', fontsize=20, fontweight='bold')


#     ax3=fig.add_subplot(spec[1,2])
#     sns.barplot(data=sum_by_vendor, x='Vendor_code', y='count_orders', estimator=sum, ci=0, ax=ax3, palette='Blues_r')
#     ax3.set_xticklabels(sum_by_vendor['Vendor_code'].unique(),rotation=90, fontsize=20)
#     # ax3.set_yticklabels(fontsize=20)
#     ax3.set_title("Volume by Account and Vendor", fontsize=24, fontweight='bold')
#     ax3.set_ylabel('Number of Orders', fontsize=20, fontweight='bold')
#     ax3.set_xlabel('Tên Shop', fontsize=20, fontweight='bold')

#     # Status parts

#     sum_by_status = data_frame.groupby(['Trạng Thái']).agg(
#       revenue = ('Actual', 'sum'),
#       count_orders = ('Tên Shop', 'count'),
#       KL = ('Khối Lượng', 'sum')
#       ).reset_index().sort_values(by='revenue', ascending=False)
#     ax4 = fig.add_subplot(spec[2,0])
#     ax4.pie(data_frame['status_'].value_counts(), labels=data_frame['status_'].value_counts().index, autopct='%.1f%%', shadow=True, textprops={"color":'k', 'fontsize':20, "fontweight":'bold'}, explode=[i*0.1 for i in range(len(data_frame['status_'].value_counts().index))], radius=0.7, startangle=90)

#     ax41 = fig.add_subplot(spec[2,1])
#     sns.barplot(data=sum_by_status, x='Trạng Thái', y='revenue', estimator=sum, ci=0, ax=ax41, palette='Blues_r')
#     ax41.set_xticklabels(sum_by_status['Trạng Thái'].unique(),rotation=90, fontsize=20)
#     ax41.set_yticks(arange(0,14000000,2000000))
#     ax41.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,14000000,2000000)], fontsize=20)
#     ax41.set_title("Revenue by Status", fontsize=24, fontweight='bold')
#     ax41.set_ylabel('Revenue', fontsize=20, fontweight='bold')
#     ax41.set_xlabel('Status', fontsize=20, fontweight='bold')

#     ax42 = fig.add_subplot(spec[2,2])
#     sns.barplot(data=sum_by_status, x='Trạng Thái', y='count_orders', estimator=sum, ci=0, ax=ax42, palette='Blues_r')
#     ax42.set_xticklabels(sum_by_status['Trạng Thái'].unique(),rotation=90, fontsize=20)
#     # ax42.set_yticklabels(fontsize=20)
#     ax42.set_title("Volume by Status", fontsize=24, fontweight='bold')
#     ax42.set_ylabel('Number of Orders', fontsize=20, fontweight='bold')
#     ax42.set_xlabel('Status', fontsize=20, fontweight='bold')


#     ax5 = fig.add_subplot(spec[3, :])
#     p=sns.lineplot(data=data_frame.sort_values(by='month'), x='month', y='Actual', estimator=sum, marker='o', color='orange', hue='Vendor_code',ax=ax5)
#     ax5.set_xticks(arange(0,12))
#     ax5.set_xticklabels(labels=p.get_xticklabels(), fontsize=20)
#     ax5.set_yticks(arange(0,7000000,1000000))
#     ax5.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,7000000,1000000)], fontsize=20)

#     ax5.set_title("Revenue over time by vendor", fontsize=24, fontweight='bold')
#     ax5.set_ylabel('Revenue', fontsize=20, fontweight='bold')
#     ax5.set_xlabel('Time', fontsize=20, fontweight='bold')
#     plt.legend(title='Vendor Code', fontsize=20, edgecolor='k', title_fontsize=20, labelspacing=0.8)
#     plt.grid(axis='y', ls='--')

#     # Province
#     ax6 = fig.add_subplot(spec[4,:])
#     sns.barplot(data=sum_by_vendor.groupby('tinh').sum().reset_index()[['tinh', 'revenue']].sort_values(by='revenue',ascending=False), x='tinh', y='revenue', palette='Blues_r', estimator=sum, ax=ax6)
#     ax6.set_xticklabels(sum_by_vendor.groupby('tinh').sum().reset_index()[['tinh', 'revenue']].sort_values(by='revenue',ascending=False)['tinh'].unique(),rotation=90, fontsize=20)
#     ax6.set_yticks(arange(0,3000000,500000))
#     ax6.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,3000000,500000)], fontsize=20)
#     ax6.set_title("Revenue by Province", fontsize=24, fontweight='bold')
#     ax6.set_ylabel('Revenue', fontsize=20, fontweight='bold')
#     ax6.set_xlabel('Province Name', fontsize=20, fontweight='bold')

#     # Tên Shop
#     ax7 = fig.add_subplot(spec[5,:])
#     ## df
#     sum_by_shopcode = data_frame.groupby(['Mã Shop']).agg(
#         tenshop=('Tên Shop', 'first'),
#         revenue = ('Actual', 'sum'),
#         count_orders = ('Tên Shop', 'count'),
#         Tinh = ('Tỉnh / Thành Phố', 'first'),
#         KL = ('Khối Lượng', 'sum')
#     ).reset_index().sort_values(by='revenue', ascending=False)

#     ## Plot
#     sns.barplot(data=sum_by_shopcode, x='tenshop', y='revenue', palette='Blues_r', estimator=sum, ax=ax7)
#     ax7.set_xticklabels(sum_by_shopcode['tenshop'].unique(),rotation=90, fontsize=20)
#     ax7.set_yticks(arange(0,3000000,500000))
#     ax7.set_yticklabels(labels=[str(i/1000000)+'M' for i in arange(0,3000000,500000)], fontsize=20)
#     ax7.set_title("Revenue by Account", fontsize=24, fontweight='bold')
#     ax7.set_ylabel('Revenue', fontsize=20, fontweight='bold')
#     ax7.set_xlabel('ShopName', fontsize=20, fontweight='bold')

#     sns.despine(top=True, bottom=False, right=True, left=False)
#     plt.tight_layout()
    
#     st.pyplot(fig)




