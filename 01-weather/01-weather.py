import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from datetime import datetime, timedelta


st.title("Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API")  # noqa: E501

st.header("Шаг 1: Загрузка данных")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("Превью данных:")
    st.dataframe(data)
else:
    st.write("Пожалуйста, загрузите CSV-файл")

st.header("Шаг 2: Выбор города")

cities = [
    'New York',
    'London',
    'Paris',
    'Tokyo',
    'Moscow',
    'Sydney',
    'Berlin',
    'Beijing',
    'Rio de Janeiro',
    'Dubai',
    'Los Angeles',
    'Singapore',
    'Mumbai',
    'Cairo',
    'Mexico City',
]

selected_city = st.selectbox('Выберите город', cities)

st.header("Шаг 3: Ввод API ключа")

api_key = st.text_input('Введите ваш API-ключ', type='password')


def is_correct_api_key(api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={selected_city}&appid={api_key}'  # noqa: E501
    response = requests.get(url=url)
    return response.status_code == 200


if uploaded_file is not None and api_key is not None:
    if is_correct_api_key(api_key):
        st.success('API-ключ корректный.')
    else:
        st.error('Некорректный API-ключ. Пожалуйста, попробуйте снова')

st.header("Шаг 4: Анализ данных")

if uploaded_file is not None and data is not None:
    df_city = data.loc[data['city'] == selected_city]
    df_city.loc[:, 'timestamp'] = pd.to_datetime(df_city.timestamp)
    df_city.set_index('timestamp', inplace=True)

    df_season_mean = df_city.groupby('season').temperature.mean().to_frame()
    df_season_std = df_city.groupby('season').temperature.std().to_frame()

    df_description = df_season_mean.join(df_season_std, lsuffix='_mean', rsuffix='_std')  # noqa: E501
    st.dataframe(df_description)

    df_city['rolling_mean'] = df_city['temperature'].rolling(window='30d').mean()  # noqa: E501
    df_city['rolling_std'] = df_city['temperature'].rolling(window='30d').std()

    df_city['upper'] = df_city['rolling_mean'] + df_city['rolling_std']
    df_city['lower'] = df_city['rolling_mean'] - df_city['rolling_std']
    df_city.reset_index(inplace=True)

    fig = px.scatter(
        df_city,
        x='timestamp',
        y='temperature',
        title='Изменение температуры, скользящее среднее и стандартное отклонение',  # noqa: E501
        labels={'timestamp': 'Дата', 'temperature': 'Температура (°C)'},
        opacity=0.2
    )

    fig.add_scatter(
        x=df_city['timestamp'],
        y=df_city['rolling_mean'],
        mode='lines',
        name='30-дневное скользящее среднее',
        line=dict(color='red')
    )

    fig.add_trace(
        go.Scatter(
            x=list(df_city['timestamp']) + list(df_city['timestamp'][::-1]),
            y=list(df_city['upper']) + list(df_city['lower'][::-1]),
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.5)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='Стандартное отклонение'
        )
    )

    st.plotly_chart(fig)

    df_city['double_upper'] = df_city['rolling_mean'] + df_city['rolling_std'].mul(2)  # noqa: E501
    df_city['double_lower'] = df_city['rolling_mean'] - df_city['rolling_std'].mul(2)  # noqa: E501
    df_city['is_outlier'] = (df_city.temperature > df_city.double_upper) | (df_city.temperature < df_city.double_lower)  # noqa: E501

    inside = df_city[~df_city.is_outlier]
    outside = df_city[df_city.is_outlier]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=inside['timestamp'],
            y=inside['temperature'],
            mode='markers',
            name='В пределах 2 стандартных отклонений',
            marker=dict(color='rgba(0, 0, 255, 0.2)')
        )
    )

    fig.add_trace(
        go.Scatter(
            x=outside['timestamp'],
            y=outside['temperature'],
            mode='markers',
            name='Вне 2 стандартных отклонений',
            marker=dict(color='rgba(255, 0, 0, 1)')
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_city['timestamp'],
            y=df_city['rolling_mean'],
            mode='lines',
            name='30-дневное скользящее среднее',
            line=dict(color='red')
        )
    )

    fig.add_trace(
        go.Scatter(
            x=list(df_city['timestamp']) + list(df_city['timestamp'][::-1]),
            y=list(df_city['double_upper']) + list(df_city['double_lower'][::-1]),  # noqa: E501
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='Два стандартных отклонения'
        )
    )

    fig.update_layout(
        title='Температура в Москве с выделением отклоняющихся точек',
        xaxis_title='Дата',
        yaxis_title='Температура (°C)'
    )

    st.plotly_chart(fig)

    for season in df_city['season'].unique():
        season_data = df_city[df_city['season'] == season].copy()
        season_data['year'] = season_data['timestamp'].dt.year

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=season_data['timestamp'],
                y=season_data['temperature'],
                mode='markers',
                name='Temperature Points'
            )
        )

        shift_amount = {
            'winter': 0,
            'spring': 30,
            'summer': 60,
            'autumn': 120
        }[season]

        for year in season_data['year'].unique():
            yearly_data = season_data[season_data['year'] == year]

            shift_date = yearly_data['timestamp'].min() + timedelta(days=shift_amount)  # noqa: E501

            fig.add_trace(
                go.Box(
                    y=yearly_data['temperature'],
                    x=[shift_date] * len(yearly_data),
                    name=f'{year} Box',
                    boxpoints=False
                )
            )

        fig.update_layout(
            title=f'Temperature Data for {season.capitalize()}',
            xaxis_title='Дата',
            yaxis_title='Температура (°C)',
            template='plotly_white'
        )

        st.plotly_chart(fig)

st.header('Шаг 5: Текущая температура')

if api_key is not None and is_correct_api_key(api_key):
    df_mean = data.groupby(['city', 'season']).temperature.mean().to_frame()
    df_std = data.groupby(['city', 'season']).temperature.std().to_frame()

    df_mean_std = df_mean.join(df_std, lsuffix='_mean', rsuffix='_std').reset_index()  # noqa: E501

    month_to_season = {
        12: "winter", 1: "winter", 2: "winter",
        3: "spring", 4: "spring", 5: "spring",
        6: "summer", 7: "summer", 8: "summer",
        9: "autumn", 10: "autumn", 11: "autumn",
    }

    url = f'https://api.openweathermap.org/data/2.5/weather?q={selected_city}&appid={api_key}&units=metric'  # noqa: E501
    response = requests.get(url=url).json()
    temperature = response['main']['temp']

    historical_data = df_mean_std.loc[
        df_mean_std.city.eq(selected_city)
        & df_mean_std.season.eq(month_to_season[datetime.today().month])
    ].to_dict(orient='index').values()
    historical_data = list(historical_data)[0]

    upper = historical_data['temperature_mean'] + 2 * historical_data['temperature_std']  # noqa: E501
    lower = historical_data['temperature_mean'] - 2 * historical_data['temperature_std']  # noqa: E501

    st.write(f'Текущая температура: {round(temperature, 2)}°C')
    st.write(f'Диапазон допустимой температуры: {round(lower, 2)}°C --- {round(upper, 2)}°C')  # noqa: E501
    st.write('Температура в пределах нормы' if lower <= temperature <= upper else 'Температура вне нормы')  # noqa: E501
    st.write(f'Средняя температура за период: {round(historical_data["temperature_mean"], 2)}°C')  # noqa: E501
    st.write(f'Стандартное отклонение: {round(historical_data["temperature_std"], 2)}°C')  # noqa: E501
