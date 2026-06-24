import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from src.data_acquisition import load_tick_series

def load_expanded_dataset() -> dict[str, pd.DataFrame]:
    """
    Returns {"BTCUSDT": full_31day_df, "ETHUSDT": ..., ...}
    Each df has columns ['timestamp', 'price'], sorted, deduplicated
    """
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'BNBUSDT']
    dates = pd.date_range('2024-01-01', '2024-01-31')
    expanded_data = {}
    
    for symbol in symbols:
        dfs = []
        for date in tqdm(dates, desc=f"Loading {symbol}"):
            date_str = date.strftime('%Y-%m-%d')
            try:
                # `load_tick_series` expects tuple of ('YYYY-MM-DD', 'YYYY-MM-DD')
                df_day = load_tick_series('binance', symbol, (date_str, date_str))
                # Log ticks
                print(f"Loaded {len(df_day)} ticks for {symbol} on {date_str}")
                dfs.append(df_day)
            except Exception as e:
                print(f"Failed to load {symbol} on {date_str}: {e}")
                
        if not dfs:
            print(f"Warning: No data could be loaded for {symbol}")
            continue
            
        full_df = pd.concat(dfs, ignore_index=True)
        full_df = full_df.sort_values('timestamp').drop_duplicates(subset=['timestamp', 'price'])
        expanded_data[symbol] = full_df.reset_index(drop=True)
        
    return expanded_data

def get_regime_for_day(symbol: str, date: str) -> str:
    """
    Returns 'trending' | 'mean_reverting' | 'volatile'
    """
    df_path = Path("results/tables/regime_classification.csv")
    if not df_path.exists():
        raise ValueError("regime_classification.csv not generated yet.")
    regimes = pd.read_csv(df_path)
    # Ensure date formats match (e.g., YYYY-MM-DD)
    if isinstance(date, pd.Timestamp):
        date = date.strftime('%Y-%m-%d')
    res = regimes[(regimes['symbol'] == symbol) & (regimes['date'] == date)]
    if len(res) == 0:
        raise ValueError(f"No regime found for {symbol} on {date}")
    return res.iloc[0]['regime']

def compute_all_regimes(expanded_data: dict[str, pd.DataFrame]):
    """
    Compute and save market regime for each asset-day.
    """
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    records = []
    
    for symbol, df in expanded_data.items():
        # Convert timestamp to date string (UTC)
        dates = pd.to_datetime(df['timestamp'], unit='s').dt.strftime('%Y-%m-%d')
        df_with_dates = df.assign(date=dates)
        
        for date, group in df_with_dates.groupby('date'):
            if len(group) == 0:
                continue
                
            price_open = group['price'].iloc[0]
            price_close = group['price'].iloc[-1]
            price_max = group['price'].max()
            price_min = group['price'].min()
            tick_count = len(group)
            
            range_span = price_max - price_min
            if range_span == 0:
                regime = 'mean_reverting'
            else:
                displacement_ratio = abs(price_close - price_open) / range_span
                if displacement_ratio > 0.6:
                    regime = 'trending'
                elif displacement_ratio < 0.2:
                    regime = 'mean_reverting'
                else:
                    regime = 'volatile'
                    
            records.append({
                'symbol': symbol,
                'date': date,
                'regime': regime,
                'price_open': price_open,
                'price_close': price_close,
                'price_max': price_max,
                'price_min': price_min,
                'tick_count': tick_count
            })
            
    out_df = pd.DataFrame(records)
    out_df.to_csv("results/tables/regime_classification.csv", index=False)
    
    print("\nRegime Distribution:")
    print(out_df.groupby(['symbol', 'regime']).size().unstack(fill_value=0))
    print("\nTotal:")
    print(out_df['regime'].value_counts())

if __name__ == "__main__":
    print("Loading expanded dataset...")
    data = load_expanded_dataset()
    print("Computing market regimes...")
    compute_all_regimes(data)
