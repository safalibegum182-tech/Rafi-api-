import aiohttp
class MarketAPI:
    def __init__(self,settings): self.settings=settings
    async def fetch(self,pair,count=None,otc=False):
        url=self.settings.otc_data_api_url if otc else self.settings.data_api_url
        if not url: raise RuntimeError('No OTC data API configured.')
        timeout=aiohttp.ClientTimeout(total=self.settings.request_timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            async with s.get(url,params={'pair':pair.replace('/',''),'count':count or self.settings.data_count}) as r:
                r.raise_for_status(); payload=await r.json()
        out=[]
        for x in payload.get('data') or []:
            try: out.append({'pair':x.get('pair',pair.replace('/','')),'time':x.get('time'),'epoch':int(x.get('epoch',0)),'open':float(x['open']),'high':float(x['high']),'low':float(x['low']),'close':float(x['close']),'colour':str(x.get('colour','')).lower(),'payout':int(float(x.get('payout',0))),'volume':float(x.get('volume',0) or 0),'chart_open':bool(x.get('chart_open',False))})
            except (KeyError,TypeError,ValueError): pass
        return payload,out
    async def fetch_closed(self,pair,otc=False,count=300):
        p,d=await self.fetch(pair,count,otc); closed=[x for x in d if not x['chart_open']]; return p,(closed if closed else (d[1:] if len(d)>1 else d))
    async def discover_live(self,pairs):
        out=[]
        for pair in pairs:
            try:
                p,c=await self.fetch_closed(pair,count=120)
                if c: out.append({'pair':pair,'payout':max(x['payout'] for x in c),'latest':c[0],'candles':c,'ok':bool(p.get('success',True))})
            except Exception: pass
        return out
