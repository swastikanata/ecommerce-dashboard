import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

def import_dataset():
    key_metrics = pd.read_csv('dashboard/key_metrics.csv')
    customer_summary = pd.read_csv('dashboard/customer_summary.csv')
    order_summary = pd.read_csv('dashboard/order_summary.csv')
    return key_metrics, customer_summary, order_summary

def plot_key_metrics(key_metrics):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig1 = px.line(key_metrics,'Bulan Pembelian','Total Harga Pesanan')
    fig2 = px.line(key_metrics,'Bulan Pembelian','Banyak Pesanan')
    fig2.update_traces(yaxis="y2", line_color='#FF7F0E')

    fig.add_traces(fig1.data + fig2.data)
    fig.update_layout(title="Total Pendapatan dan Banyak Order per Bulan")

    fig.update_xaxes(showgrid=False, title_text="Bulan")
    fig.update_yaxes(showgrid=False, title_text="Total Pendapatan (R$)", secondary_y=False, color="#1F77B4")
    fig.update_yaxes(showgrid=False, title_text="Banyak Pesanan", secondary_y=True, color="#FF7F0E")
    return fig

def plot_recency(customer_summary):
    viz_df = customer_summary.groupby('Pembelian Terakhir')['ID Pelanggan'].count().reset_index().rename(columns={'ID Pelanggan': 'Banyak Pelanggan'})
    fig = px.bar(
        viz_df, 
        'Pembelian Terakhir', 
        'Banyak Pelanggan',
        title="Pembelian Terakhir oleh Pelanggan",
        text_auto=True,
    )

    order = ['<= 1 day', '<= 1 week', '<= 1 month', '<= 6 months', '<= 1 year', '> 1 year']
    fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray': order})
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig

def plot_frequency(customer_summary):
    viz_df =  customer_summary.copy()
    viz_df['Banyak Pesanan'] = viz_df['Banyak Pesanan'].map(lambda x: x if (x == 1 or x == 2) else '>=3')
    viz_df = viz_df.groupby('Banyak Pesanan')['ID Pelanggan'].count().reset_index().rename(columns={'ID Pelanggan': 'Banyak Pelanggan'})

    fig = px.pie(
        viz_df, 
        'Banyak Pesanan', 
        'Banyak Pelanggan',
        title="Banyak Pesanan oleh Pelanggan",
    )
    
    return fig

def plot_monetary(customer_summary):
    fig = px.histogram(customer_summary['Total Harga Pesanan (R$)'], title="Total Harga Pesanan oleh Pelanggan",
                   ).update_traces(hovertemplate='Total Harga Pesanan=%{x}<br>Banyak Pelanggan=%{y}<extra></extra>')

    fig.update_layout(showlegend=False)
    fig.update_yaxes(showgrid=False)
    return fig

def plot_waktu_sampai(order_summary):
    viz_df = order_summary.groupby('Bulan Pembelian').agg({'Perkiraan Waktu Sampai (Hari)': 'mean', 'Waktu Sampai (Hari)': 'mean'})
    viz_df.index = viz_df.index.to_series().astype(str)
    viz_df = viz_df.reset_index()

    fig = px.line(
        viz_df,
        x='Bulan Pembelian', 
        y=viz_df.columns[1:3],
        title='Perbandingan Estimasi Waktu Sampai dengan Waktu Sebenarnya').update_traces(hovertemplate='Bulan Pembelian=%{x}<br>Waktu Sampai=%{y}<extra></extra>')
    fig.update_yaxes(showgrid=False, title_text="Waktu Sampai (Hari)")
    fig.update_xaxes(showgrid=False)
    return fig

def plot_review(order_summary):
    fig = px.box(order_summary,x='Skor Review', y='Waktu Sampai (Hari)', title="Sebaran Lama Waktu Sampai terhadap Rating")
    fig.update_yaxes(showgrid=False)
    return fig

key_metrics, customer_summary, order_summary = import_dataset()

st.title('Analisis E-Commerce')
st.caption('oleh Made Swastika Nata Negara')

tab1, tab2, tab3 = st.tabs(["1. Key Metrics", "2. RFM Pelanggan", "3. Waktu Sampai"])

with tab1:
    st.header("Performa E-commerce dari segi total pendapatan dan banyaknya order")
    col11, col12 = st.columns(2)

    total_pendapatan = 'R$ {:,}'.format(key_metrics['Total Harga Pesanan'].sum())
    col11.metric(label='Total Pendapatan', value=total_pendapatan)

    banyak_pesanan = key_metrics['Banyak Pesanan'].sum()
    col12.metric(label='Banyak Pesanan', value=banyak_pesanan)

    st.plotly_chart(plot_key_metrics(key_metrics), use_container_width=True)
    st.write("Performa e-commerce dari segi total pendapatan maupun banyaknya pesanan mengalami tren pengingkatan yang baik. Hal ini mengindikasikan bahwa bisnis berjalan dengan lancar.")
    
with tab2:
    st.header("Perilaku konsumen dari segi Recency, Frequency, dan Monetary (RFM)")
    st.plotly_chart(plot_recency(customer_summary), use_container_width=True)

    st.plotly_chart(plot_frequency(customer_summary), use_container_width=True)
    st.plotly_chart(plot_monetary(customer_summary), use_container_width=True)
    st.markdown("""
    Analisis RFM menunjukkan bahwa pelanggan termasuk dalam kategori low engagement. Hal ini ditunjukkan oleh:
    - Waktu terkahir belanja pelanggan cenderung lebih dari 6 bulan yang lalu
    - Pelanggan jarang melakukan transaksi berulang, di mana sebagian besar pelanggan hanya pernah berbelanja satu kali
    - Pelanggan melakukan pesanan terhadap barang di range harga rendah
    """)
    
    st.write("**Rekomendasi**: Gencarkan strategi marketing untuk menarik dan mempertahankan pelanggan.")

with tab3:
    st.header("Lama pesanan dapat sampai ke konsumen dan pengaruhnya")
    st.plotly_chart(plot_waktu_sampai(order_summary), use_container_width=True)
    st.write("Prediksi waktu sampai selalu lebih besar daripada waktu sampai sebenarnya. Ini meningkatkan risiko pelanggan tidak jadi berbelanja karena waktu sampai di e-commerce adalah faktor yang penting dalam keputusan pelanggan.")
    st.plotly_chart(plot_review(order_summary), use_container_width=True)
    st.write("Waktu sampai juga berpengaruh terhadap kepuasan pelanggan, di mana rating cenderung meningkat seiring berkurangnya lama waktu pesanan sampai.")
    st.write("**Rekomendasi**: Perbaiki model yang digunakan untuk membuat prediksi waktu sampai dan tingkatkan kinerja logistik untuk mengurangi lama waktu sampai pesanan.")