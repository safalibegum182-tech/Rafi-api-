from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()

def _int_set(value: str) -> set[int]:
    out=set()
    for p in (value or '').split(','):
        try:
            if p.strip(): out.add(int(p.strip()))
        except ValueError: pass
    return out

@dataclass(frozen=True)
class Settings:
    bot_token: str=os.getenv('BOT_TOKEN','')
    channel_id: int=int(os.getenv('CHANNEL_ID','-1004399158909'))
    admin_ids: set[int]=None
    owner_username: str=os.getenv('OWNER_USERNAME','@Smart_Method_Owner')
    data_api_url: str=os.getenv('DATA_API_URL','https://nexusairafipj.base44.app/functions/oandaData')
    otc_data_api_url: str=os.getenv('OTC_DATA_API_URL','')
    data_count: int=int(os.getenv('DATA_COUNT','3000'))
    min_payout: int=int(os.getenv('MIN_PAYOUT','80'))
    timezone: str=os.getenv('TIMEZONE','Asia/Dhaka')
    timeframe: str=os.getenv('TIMEFRAME','M1')
    auto_scan_seconds: int=int(os.getenv('AUTO_SCAN_SECONDS','15'))
    signal_min_score: int=int(os.getenv('SIGNAL_MIN_SCORE','78'))
    max_auto_signals_per_day: int=int(os.getenv('MAX_AUTO_SIGNALS_PER_DAY','5'))
    result_delay_seconds: int=int(os.getenv('RESULT_DELAY_SECONDS','65'))
    auto_post_default: bool=os.getenv('AUTO_POST_DEFAULT','0')=='1'
    min_signal_gap_seconds: int=int(os.getenv('MIN_SIGNAL_GAP_SECONDS','60'))
    request_timeout_seconds: int=int(os.getenv('REQUEST_TIMEOUT_SECONDS','12'))
    def __post_init__(self): object.__setattr__(self,'admin_ids',_int_set(os.getenv('ADMIN_IDS','')))
settings=Settings()
OTC_CATALOG=[('NZD/CHF',94),('GBP/NZD',93),('USD/EGP',93),('USD/INR',93),('USD/PHP',92),('USD/PKR',92),('NZD/CAD',91),('EUR/NZD',90),('NZD/JPY',89),('USD/BDT',85),('USD/MXN',85),('CAD/CHF',84),('USD/IDR',83),('USD/ZAR',82),('USD/ARS',81),('USD/COP',81)]
LIVE_PAIRS=['AUDCAD','AUDCHF','AUDJPY','AUDUSD','CADJPY','CHFJPY','EURAUD','EURCAD','EURCHF','EURGBP','EURJPY','GBPAUD','GBPCAD','GBPCHF','GBPJPY','GBPUSD','USDCAD','USDCHF','USDJPY','EURUSD']
