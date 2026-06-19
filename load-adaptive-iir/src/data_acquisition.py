import os
import zipfile
import urllib.request
import ssl
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Bypass SSL verification for Binance downloads on some macOS setups
ssl._create_default_https_context = ssl._create_unverified_context

LOBSTER_EVENT_TYPES = {
    1: 'New Limit Order',
    2: 'Cancellation (Partial)',
    3: 'Deletion (Total)',
    4: 'Execution (Visible)',
    5: 'Execution (Hidden)',
    7: 'Trading Halt'
}

def load_tick_series(source: str, symbol: str, date_range: tuple, data_dir: str = 'data') -> pd.DataFrame:
    """
    Loads and processes tick data from LOBSTER or Binance into a unified DataFrame.
    """
    data_dir = Path(data_dir)
    raw_dir = data_dir / 'raw'
    processed_dir = data_dir / 'processed'
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    date_str = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    out_path = processed_dir / f"{source}_{symbol}_{date_str}.parquet"

    if out_path.exists():
        print(f"Loading cached processed data from {out_path}")
        return pd.read_parquet(out_path)

    if source.lower() == 'binance':
        df = _load_binance(symbol, start_date, end_date, raw_dir)
    elif source.lower() == 'lobster':
        df = _load_lobster(symbol, start_date, end_date, raw_dir)
    else:
        raise ValueError(f"Unknown source: {source}")

    print(f"Saving processed data to {out_path}")
    df.to_parquet(out_path, index=False)
    return df

def _load_binance(symbol: str, start_date, end_date, raw_dir: Path) -> pd.DataFrame:
    dfs = []
    dates = pd.date_range(start_date, end_date)
    for date in tqdm(dates, desc="Loading Binance data"):
        date_str = date.strftime('%Y-%m-%d')
        filename = f"{symbol}-trades-{date_str}.zip"
        url = f"https://data.binance.vision/data/spot/daily/trades/{symbol}/{filename}"
        zip_path = raw_dir / filename

        if not zip_path.exists():
            try:
                urllib.request.urlretrieve(url, zip_path)
            except Exception as e:
                print(f"Failed to download {url}: {e}")
                continue

        with zipfile.ZipFile(zip_path, 'r') as z:
            csv_name = [n for n in z.namelist() if n.endswith('.csv')][0]
            with z.open(csv_name) as f:
                # Binance trades CSV has 7 columns
                df = pd.read_csv(f, names=['trade Id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
                dfs.append(df)
        
    if not dfs:
        raise ValueError("No data loaded from Binance for the given dates.")
        
    full_df = pd.concat(dfs, ignore_index=True)
    
    # §3.2: Verify timestamp units by checking value magnitude.
    # From Jan 2025, Binance SPOT timestamps are in microseconds; before that, milliseconds.
    # Column order verified against the README shipped in the downloaded zip.
    first_time = full_df['time'].iloc[0]
    if first_time > 1e15:
        # microseconds → seconds
        full_df['timestamp'] = full_df['time'] / 1e6
    else:
        # milliseconds → seconds
        full_df['timestamp'] = full_df['time'] / 1e3

        
    full_df['price'] = full_df['price'].astype(float)
    full_df = full_df.sort_values('timestamp').drop_duplicates(subset=['timestamp', 'price'])
    
    return full_df[['timestamp', 'price']].reset_index(drop=True)

def _load_lobster(symbol: str, start_date, end_date, raw_dir: Path) -> pd.DataFrame:
    """
    Loads LOBSTER data from local CSVs. Requires manual download.
    Assumes files are named {symbol}_{date}_message_1.csv and {symbol}_{date}_orderbook_1.csv
    """
    dfs = []
    dates = pd.date_range(start_date, end_date)
    
    msg_cols = ['Time', 'Type', 'Order_ID', 'Size', 'Price', 'Direction']
    ob_cols = ['Ask_Price_1', 'Ask_Size_1', 'Bid_Price_1', 'Bid_Size_1']
    PRICE_SCALE = 10000.0 
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        msg_files = list(raw_dir.glob(f"{symbol}_{date_str}_message*.csv"))
        ob_files = list(raw_dir.glob(f"{symbol}_{date_str}_orderbook*.csv"))
        
        if not msg_files or not ob_files:
            continue
            
        msg_df = pd.read_csv(msg_files[0], names=msg_cols)
        ob_df = pd.read_csv(ob_files[0], names=ob_cols, usecols=[0,1,2,3])
        
        combined = pd.concat([msg_df, ob_df], axis=1)
        combined['price'] = (combined['Ask_Price_1'] + combined['Bid_Price_1']) / (2.0 * PRICE_SCALE)
        
        day_start = date.timestamp()
        combined['timestamp'] = day_start + combined['Time']
        
        dfs.append(combined)

    if not dfs:
        raise ValueError("No LOBSTER data found. Please place CSVs in data/raw.")
        
    full_df = pd.concat(dfs, ignore_index=True)
    full_df = full_df.sort_values('timestamp').drop_duplicates(subset=['timestamp', 'price'])
    
    return full_df[['timestamp', 'price']].reset_index(drop=True)
