def prediction(stock, n_days):
    import numpy as np
    import yfinance as yf
    from sklearn.model_selection import train_test_split, GridSearchCV
    from sklearn.svm import SVR
    from datetime import date, timedelta
    import plotly.graph_objs as go

    
    df = yf.download(stock, period='2y')
    df.reset_index(inplace=True)  
    df['Date_ordinal'] = df['Date'].apply(lambda x: x.toordinal())  

   
    X = np.array(df[['Date_ordinal']])  
    Y = df['Close'].values.ravel()  

    
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.1, shuffle=False)

    
    gsc = GridSearchCV(
        estimator=SVR(kernel='rbf'), 
        param_grid={
            'C': [0.001, 0.01, 0.1, 1, 100, 1000], 
            'epsilon': [0.0001, 0.001, 0.01, 0.1, 1], 
            'gamma': [0.001, 0.01, 0.1, 1]
        },
        cv=5, 
        scoring='neg_mean_absolute_error', 
        n_jobs=-1
    )
    
    
    grid_result = gsc.fit(x_train, y_train)
    best_params = grid_result.best_params_
    best_svr = SVR(
        kernel='rbf', 
        C=best_params["C"], 
        epsilon=best_params["epsilon"], 
        gamma=best_params["gamma"]
    )
    
    
    best_svr.fit(x_train, y_train)

    
    last_date_ordinal = x_test[-1][0]
    future_dates = np.array([[last_date_ordinal + i] for i in range(1, n_days + 1)])
    
    
    future_dates_labels = [date.fromordinal(int(last_date_ordinal + i)) for i in range(1, n_days + 1)]

    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines+markers', name='Historical Data'))
    fig.add_trace(go.Scatter(x=df['Date'][len(x_train):], y=best_svr.predict(x_test), mode='lines', name='Test Prediction'))
    fig.add_trace(go.Scatter(x=future_dates_labels, y=best_svr.predict(future_dates), mode='lines+markers', name='Future Prediction'))
    
    fig.update_layout(
        title=f"Predicted Close Price for the next {n_days} days",
        xaxis_title="Date",
        yaxis_title="Close Price",
        template="plotly_white"
    )
    
    return fig
