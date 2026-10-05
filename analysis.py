def ema(v,n):
    if not v:return []
    k=2/(n+1); o=[v[0]]
    for x in v[1:]: o.append(x*k+o[-1]*(1-k))
    return o
def rsi(v,n=14):
    if len(v)<n+1:return 50.0
    g=[];l=[]
    for a,b in zip(v[-n-1:-1],v[-n:]):
        d=b-a;g.append(max(d,0));l.append(max(-d,0))
    ag=sum(g)/n;al=sum(l)/n
    return 100.0 if al==0 else 100-(100/(1+ag/al))
def atr(c,n=14):
    if len(c)<n+1:return max((x['high']-x['low'] for x in c),default=0)
    tr=[]
    for i in range(1,len(c)):
        x,p=c[i],c[i-1];tr.append(max(x['high']-x['low'],abs(x['high']-p['close']),abs(x['low']-p['close'])))
    return sum(tr[-n:])/n
def analyze(candles,min_score=78):
    c=list(reversed(candles))
    if len(c)<35:raise ValueError('Not enough closed candles')
    close=[x['close'] for x in c];vol=[x['volume'] for x in c];e9,e21,e50=ema(close,9),ema(close,21),ema(close,50);last=c[-1]
    rng=max(last['high']-last['low'],1e-12);body=abs(last['close']-last['open']);upper=last['high']-max(last['open'],last['close']);lower=min(last['open'],last['close'])-last['low']
    bull=last['close']>last['open'];bear=last['close']<last['open']; bodyp=body/rng*100; call=put=0;rc=[];rp=[]
    if e9[-1]>e21[-1]:call+=22;rc.append('EMA9 > EMA21')
    else:put+=22;rp.append('EMA9 < EMA21')
    if e21[-1]>e50[-1]:call+=14;rc.append('EMA21 above EMA50')
    elif e21[-1]<e50[-1]:put+=14;rp.append('EMA21 below EMA50')
    rv=rsi(close)
    if 52<=rv<=68:call+=15;rc.append(f'RSI {rv:.1f} bullish zone')
    elif 32<=rv<=48:put+=15;rp.append(f'RSI {rv:.1f} bearish zone')
    elif rv>70:put+=5;rp.append(f'RSI {rv:.1f} extended')
    elif rv<30:call+=5;rc.append(f'RSI {rv:.1f} extended')
    if bull and bodyp>=55:call+=16;rc.append('strong bullish candle')
    if bear and bodyp>=55:put+=16;rp.append('strong bearish candle')
    if lower/rng*100>=35 and bull:call+=7;rc.append('lower-wick rejection')
    if upper/rng*100>=35 and bear:put+=7;rp.append('upper-wick rejection')
    mom=close[-1]-close[-6]
    if mom>0:call+=10;rc.append('5-candle momentum up')
    elif mom<0:put+=10;rp.append('5-candle momentum down')
    av=sum(vol[-21:-1])/max(1,len(vol[-21:-1]))
    if av>0 and vol[-1]>av*1.15:
        if bull:call+=6;rc.append('volume expansion')
        elif bear:put+=6;rp.append('volume expansion')
    for n,w in [(5,4),(10,3),(20,3)]:
        seg=c[-n:];u=sum(x['close']>x['open'] for x in seg);d=n-u
        if u>d:call+=w;rc.append(f'{n}-candle cycle up')
        elif d>u:put+=w;rp.append(f'{n}-candle cycle down')
    side='CALL' if call>=put else 'PUT';raw=max(call,put);conf=max(50,min(99,round(55+raw*.45)));reasons=rc if side=='CALL' else rp
    return {'side':side,'confidence':conf,'trend':'Uptrend Follow' if side=='CALL' else 'Downtrend Follow','entry_price':last['close'],'candle':last,'rsi':rv,'atr':atr(c),'ema9':e9[-1],'ema21':e21[-1],'ema50':e50[-1],'reasons':reasons[:5],'eligible':conf>=min_score,'body_pct':bodyp,'volume':last['volume']}
