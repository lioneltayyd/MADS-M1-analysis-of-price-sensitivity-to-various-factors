# %%
# Python modules. 
import pandas as pd 
import altair as alt 

# Custom configuration. 
from source.config.config import RECESSIONS 



# %%
def plot_heatmap(df:pd.DataFrame, x:str, y:str, z:str, factors:list, zlim:list=[0,1.5], format_text:str=".0f"): 

    # Example = (name_name_1) to ([name, name, 1]) to (name anem). 
    chart_title = " ".join( [s for s in z.split("_") if not s.isnumeric()] ) 

    # Filter the factors. 
    df_fil = df.loc[df["factor"].isin(factors), [x,y,z]] 

    # Base encoding. 
    base = alt.Chart(df_fil) \
        .encode(
            x=alt.X(
                f"{x}:N", 
                axis=alt.Axis(title="", titleFontSize=14, labelFontSize=10, labelAngle=0), 
            ),
            y=alt.Y(
                f"{y}:N", 
                axis=alt.Axis(title="", titleFontSize=14, labelFontSize=10), 
            ), 
            tooltip=[
                alt.Tooltip(f"{z}:Q", title=z, format=format_text), 
            ], 
        ) \
        .properties(title=chart_title, height=200, width=400) 

    # Visualisation approach. 
    heatmap = base \
        .mark_rect(opacity=1) \
        .encode(
            color=alt.Color(
                f"{z}:Q", 
                scale=alt.Scale(domain=zlim, scheme="blues", reverse=False),
                legend=alt.Legend(title="", direction="vertical"), 
            )
        ) 

    # Annotation. 
    text = base \
        .mark_text(baseline="middle") \
        .encode(text=alt.Text(f"{z}:Q", format=format_text)) \
        .properties(title=chart_title, height=200, width=400) 

    return (heatmap + text).interactive() 



# %%
def plot_timeseries(df:pd.DataFrame, x:str, tickers:list, factor:str, measure:str, format_text:str=".1f"): 

    # For concatnating multiple visuals. 
    combined_plot = alt.vconcat() 

    # Columns you to visualise.
    cols_to_vis = [x, "ticker", factor, measure]

    # Consolidate the recession dates. 
    df_recessions = pd.DataFrame(RECESSIONS) 

    # For adding horizontal line. 
    df_hline_hilo = pd.DataFrame(data={"upper": [1], "lower": [-1]})

    # Plot multiple visuals. 
    for ticker in tickers: 
        df_fil = df.loc[(df[factor] == 1) & (df["ticker"] == ticker), cols_to_vis] 

        # Base encoding. 
        base = alt.Chart(df_fil) \
            .encode(
                x=alt.X(
                    f"{x}:T", 
                    axis=alt.Axis(title="", titleFontSize=10, labelFontSize=10, labelAngle=0), 
                ),
                y=alt.Y(
                    f"{measure}:Q", 
                    axis=alt.Axis(title=measure, titleFontSize=10, labelFontSize=10), 
                ), 
                tooltip=[
                    alt.Tooltip(f"{measure}:Q", title=measure, format=format_text), 
                ], 
            ) \
            .properties(title=ticker, height=75, width=600) 

        # Visualisation approach. 
        scatter = base.mark_point(opacity=1, color="orange", filled=True, size=50) 

        # Add horizontal lines. 
        hline_hi = alt.Chart(df_hline_hilo) \
            .mark_rule(color="black") \
            .encode(y="upper") 

        hline_lo = alt.Chart(df_hline_hilo) \
            .mark_rule(color="black") \
            .encode(y="lower") 

        # Highlight recession period. 
        recess_debt = alt.Chart(df_recessions) \
            .transform_filter(alt.datum.recession == "DebtCrisis 2008") \
            .encode(x="date_start:T", x2="date_end:T") \
            .mark_rect(color="black", opacity=.2) 

        recess_covid = alt.Chart(df_recessions) \
            .transform_filter(alt.datum.recession == "Covid 2019") \
            .encode(x="date_start:T", x2="date_end:T") \
            .mark_rect(color="black", opacity=.2) 

        combined_plot &= (scatter + hline_hi + hline_lo + recess_debt + recess_covid).interactive() 

    return combined_plot



# %%
def plot_boxplot(df:pd.DataFrame, tickers:list, factor:str, measure:str, format_text:str=".1f"): 

    # For concatnating multiple visuals. 
    combined_plot = alt.vconcat() 

    # Columns you to visualise.
    cols_to_vis = ["ticker", factor, measure]

    # Plot multiple visuals. 
    for ticker in tickers: 
        # Altair is not able to plot data more than 5,000 rows.
        df_fil = df.loc[df["ticker"] == ticker, cols_to_vis] 
        sample_size = 5000 if df_fil.shape[0] >= 5000 else df_fil.shape[0] 
        df_fil = df_fil.sample(sample_size).copy() 

        # Base encoding. 
        base = alt.Chart(df_fil) \
            .encode(
                x=alt.X(
                    f"{measure}:Q", 
                    axis=alt.Axis(title=measure, titleFontSize=10, labelFontSize=10), 
                ), 
                y=alt.Y(
                    f"{factor}:N",  
                    axis=alt.Axis(title=factor, titleFontSize=10, labelFontSize=10, labelAngle=0), 
                ), 
            ) \
            .properties(title=ticker, height=100, width=400) 

        # Visualisation approach. 
        box = base.mark_boxplot() 

        combined_plot &= (box).interactive() 

    return combined_plot
