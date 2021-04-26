import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from functools import reduce
from utils.aggregations import aggregate_sentiment_per_day_per_country, aggregate_vol_per_day_per_country, \
    aggregate_stats_per_day_per_country

pd.options.mode.chained_assignment = None  # Removes copy warning

case_str = 'newCasesByPublishDate'
death_str = 'newDeathsByDeathDate'
event_str = 'Event'
MA_win = 7


#     df_stats = df_stats.reindex(index=df_stats.index[::-1])  # Flipping df as dates are wrong way round (needed for MA)


def select_df_between_dates(df, start, end):
    date_list = [str(date.date()) for date in pd.date_range(start=start, end=end).tolist()]
    df = df.loc[df['date'].isin(date_list)]
    return df


def get_sent_vol_traces(df_sent, df_num_tweets, sentiment_type, events, country):
    print(df_sent.columns, df_sent['region_name'])
    sent_trace = go.Scatter(x=df_sent.loc[df_sent['region_name'] == country, 'date'],
                            y=df_sent.loc[df_sent['region_name'] == country, sentiment_type],
                            name="{} 7 Day MA: Sentiment".format(country), text=events, textposition="bottom center"
                            )

    vol_trace = go.Scatter(x=df_num_tweets['date'], y=df_num_tweets[country],
                           name="{} 7 Day MA: Number of Tweets".format(country), text=events,
                           textposition="bottom center")
    return sent_trace, vol_trace


def get_stats_trace(data, events, country):
    case_trace = go.Scatter(x=data.loc[data['country'] == country, 'date'],
                            y=data.loc[data['country'] == country, case_str],
                            name="{} 7 Day MA: Covid Cases".format(country), text=events, textposition="bottom center")

    death_trace = go.Scatter(x=data.loc[data['country'] == country, 'date'],
                             y=data.loc[data['country'] == country, death_str],
                             name="{} 7 Day MA: Covid Deaths".format(country), text=events,
                             textposition="bottom center")
    return case_trace, death_trace


def plot_covid_stats(data, countries, events, start, end):
    df = select_df_between_dates(data, start, end)
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"secondary_y": True},
                                {"secondary_y": True}], [{"secondary_y": True},
                                                         {"secondary_y": True}]],
                        subplot_titles=('England', 'Scotland', 'NI', 'Wales'), vertical_spacing=0.25,
                        horizontal_spacing=0.3)
    for i, country in enumerate(countries):
        case_trace, death_trace = get_stats_trace(df, events, country)
        row, col = int((i / 2) + 1), (i % 2) + 1
        fig.add_trace(case_trace, secondary_y=False, row=row, col=col)
        fig.add_trace(death_trace, secondary_y=True, row=row, col=col)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.1,
        xanchor="right",
        x=1), height=750, autosize=True)
    fig.update_xaxes(title_text="Date", showgrid=False)
    fig.update_yaxes(title_text="Covid Cases", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Covid Deaths", secondary_y=True, showgrid=False)
    return fig


def plot_sentiment_vs_volume(df_sent, df_vol, sentiment_col, events, countries, start, end):
    df_vol = select_df_between_dates(df_vol, start, end)
    df_sent = select_df_between_dates(df_sent, start, end)
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{"secondary_y": True},
                                {"secondary_y": True}], [{"secondary_y": True},
                                                         {"secondary_y": True}]],
                        subplot_titles=('England', 'Scotland', 'NI', 'Wales'), vertical_spacing=0.25,
                        horizontal_spacing=0.3)
    for i, country in enumerate(countries):
        sent_trace, vol_trace = get_sent_vol_traces(df_sent, df_vol, sentiment_col, events, country)
        row, col = int((i / 2) + 1), (i % 2) + 1
        fig.add_trace(sent_trace, secondary_y=False, row=row, col=col)
        fig.add_trace(vol_trace, secondary_y=True, row=row, col=col)
        fig.update_yaxes(range=[-0.4, 0.4], row=row, col=col, secondary_y=False)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="right",
        x=1,
        itemsizing='constant'),
        height=750, autosize=True,
        margin=dict(l=20, r=20, t=80, b=20),
    )
    fig.update_xaxes(title_text="Date", showgrid=False)
    fig.update_yaxes(title_text="Sentiment(7MA)", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text="Tweet Volume", secondary_y=True, showgrid=False)

    return fig


def plot_hashtag_table(df):
    fig = go.Figure(data=[
        go.Table(
            header=dict(
                values=['Hashtag', 'Count'],
                align='left',
                fill_color='paleturquoise',
            ),
            columnwidth=[300, 80],
            cells=dict(values=[df.Hashtag, df.Count], align='left', height=40)
        )
    ])
    fig.update_layout(autosize=True, height=500, margin=dict(b=5, t=20, l=5, r=5))
    return fig


def plot_animated_sent(df_sent, df_vol, sentiment_column, events, dates_list):
    fig = go.Figure(frames=[go.Frame(data=[
        get_sent_vol_traces(
            select_df_between_dates(df_sent, dates_list[0], date), select_df_between_dates(df_vol, dates_list[0], date),
            sentiment_column, events,
            'England')[0],

        get_sent_vol_traces(
            select_df_between_dates(df_sent, dates_list[0], date), select_df_between_dates(df_vol, dates_list[0], date),
            sentiment_column, events,
            'Scotland')[0],
        get_sent_vol_traces(
            select_df_between_dates(df_sent, dates_list[0], date), select_df_between_dates(df_vol, dates_list[0], date),
            sentiment_column, events,
            'Northern Ireland')[0],
        get_sent_vol_traces(
            select_df_between_dates(df_sent, dates_list[0], date), select_df_between_dates(df_vol, dates_list[0], date),
            sentiment_column, events,
            'Wales')[0],

    ],
        name=str(i)  # you need to name the frame for the animation to behave properly
    )
        for i, date in enumerate(dates_list)]
    )

    fig.add_trace(get_sent_vol_traces(
        df_sent, df_vol,
        sentiment_column, events,
        'England')[0])

    fig.add_trace(get_sent_vol_traces(
        df_sent, df_vol,
        sentiment_column, events,
        'Scotland')[0]
                  )

    fig.add_trace(get_sent_vol_traces(
        df_sent, df_vol,
        sentiment_column, events,
        'Northern Ireland')[0]
                  )

    fig.add_trace(get_sent_vol_traces(
        df_sent, df_vol,
        sentiment_column, events,
        'Wales')[0]
                  )
    sliders = [
        {
            "pad": {"b": 10, "t": 60},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [[f.name], frame_args(0), {'frame': {'duration': 300, 'redraw': False},
                                                       'mode': 'immediate', 'transition': {'duration': 300}}],
                    "label": str(k),
                    "method": "animate",
                }
                for k, f in enumerate(fig.frames)
            ],
        }
    ]
    fig.update_layout(
        title='7 Day Moving Average of Tweet Sentiment for Each Country',
        height=600,
        autosize=True,
        scene=dict(
            yaxis=dict(range=[0.55, -0.55], autorange=False),
            aspectratio=dict(x=1, y=1, z=1),
        ),
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, frame_args(50)],
                        "label": "&#9654;",  # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;",  # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
        ],
        sliders=sliders,
        yaxis_range=[-0.45, 0.45],
        xaxis_title='Date',
        yaxis_title='7 Day MA Sentiment'

    )
    return fig


def plot_corr_mat(df):
    fig = px.scatter_matrix(df,
                            dimensions=['sentiment', 'volume', 'cases', 'deaths'],
                            color='country',
                            symbol='country'
                            )
    return fig


# def test_sublot_animation(agg_data, tweet_count_data, sentiment_column, countries, events, start, end):
#     dates_list = [str(date.date()) for date in pd.date_range(start=start, end=end).tolist()]
#     fig = make_subplots(rows=1, cols=1, specs=[[{'secondary_y': True}]])
#     fig.add_trace(get_sent_vol_traces(
#         format_df_ma_sent(agg_data, sentiment_column, start, start),
#         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                start),
#         sentiment_column, events,
#         'England')[0], secondary_y=True)
#
#     fig.add_trace(get_sent_vol_traces(
#         format_df_ma_sent(agg_data, sentiment_column, start, start),
#         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                start),
#         sentiment_column, events,
#         'Scotland')[0]
#                   , secondary_y=True)
#
#     fig.add_trace(get_sent_vol_traces(
#         format_df_ma_sent(agg_data, sentiment_column, start, start),
#         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                start),
#         sentiment_column, events,
#         'Northern Ireland')[0]
#                   , secondary_y=True)
#
#     fig.add_trace(get_sent_vol_traces(
#         format_df_ma_sent(agg_data, sentiment_column, start, start),
#         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                start),
#         sentiment_column, events,
#         'Wales')[0]
#                   , secondary_y=True)
#
#     frames = [dict(name=str(i),
#                    df=[get_sent_vol_traces(
#                        format_df_ma_sent(agg_data, sentiment_column, start, date),
#                        format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                               date),
#                        sentiment_column, events,
#                        'England')[0],
#
#                          get_sent_vol_traces(
#                              format_df_ma_sent(agg_data, sentiment_column, start, date),
#                              format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                                     date),
#                              sentiment_column, events,
#                              'Scotland')[0],
#                          get_sent_vol_traces(
#                              format_df_ma_sent(agg_data, sentiment_column, start, date),
#                              format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                                     date),
#                              sentiment_column, events,
#                              'Northern Ireland')[0],
#                          get_sent_vol_traces(
#                              format_df_ma_sent(agg_data, sentiment_column, start, date),
#                              format_df_ma_tweet_vol(tweet_count_data, countries, start,
#                                                     date),
#                              sentiment_column, events,
#                              'Wales')[0],
#                          ],
#                    traces=[0, 1, 2, 3])
#
#               for i, date in enumerate(dates_list)
#               ]
#     fig.update(frames=frames)
#     #
#     # fig_2 = go.Figure(frames=[go.Frame(df=[
#     #     get_sent_vol_traces(
#     #         format_df_ma_sent(agg_data, sentiment_column, start, date),
#     #         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#     #                                date),
#     #         sentiment_column, events,
#     #         'England')[0],
#     #
#     #     get_sent_vol_traces(
#     #         format_df_ma_sent(agg_data, sentiment_column, start, date),
#     #         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#     #                                date),
#     #         sentiment_column, events,
#     #         'Scotland')[0],
#     #     get_sent_vol_traces(
#     #         format_df_ma_sent(agg_data, sentiment_column, start, date),
#     #         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#     #                                date),
#     #         sentiment_column, events,
#     #         'Northern Ireland')[0],
#     #     get_sent_vol_traces(
#     #         format_df_ma_sent(agg_data, sentiment_column, start, date),
#     #         format_df_ma_tweet_vol(tweet_count_data, countries, start,
#     #                                date),
#     #         sentiment_column, events,
#     #         'Wales')[0],
#     #
#     # ],
#     #     name=str(i)  # you need to name the frame for the animation to behave properly
#     # )
#     #     for i, date in enumerate(dates_list)]
#     # )
#     sliders = [
#         {
#             "pad": {"b": 10, "t": 60},
#             "len": 0.9,
#             "x": 0.1,
#             "y": 0,
#             "steps": [
#                 {
#                     "args": [[f.name], frame_args(0), {'frame': {'duration': 300, 'redraw': False},
#                                                        'mode': 'immediate', 'transition': {'duration': 300}}],
#                     "label": str(k),
#                     "method": "animate",
#                 }
#                 for k, f in enumerate(fig.frames)
#             ],
#         }
#     ]
#     fig.update_layout(
#         title='7 Day Moving Average of Tweet Sentiment for Each Country',
#         height=600,
#         autosize=True,
#         scene=dict(
#             yaxis=dict(range=[0.55, -0.55], autorange=False),
#             aspectratio=dict(x=1, y=1, z=1),
#         ),
#         updatemenus=[
#             {
#                 "buttons": [
#                     {
#                         "args": [None, frame_args(50)],
#                         "label": "&#9654;",  # play symbol
#                         "method": "animate",
#                     },
#                     {
#                         "args": [[None], frame_args(0)],
#                         "label": "&#9724;",  # pause symbol
#                         "method": "animate",
#                     },
#                 ],
#                 "direction": "left",
#                 "pad": {"r": 10, "t": 70},
#                 "type": "buttons",
#                 "x": 0.1,
#                 "y": 0,
#             }
#         ],
#         sliders=sliders,
#         yaxis_range=[-0.45, 0.45],
#         xaxis_title='Date',
#         yaxis_title='7 Day MA Sentiment'
#     )


def frame_args(duration):
    return {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear"},
    }
