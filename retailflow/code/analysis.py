"""Rebuild RetailFlow from the unmodified UCI workbook. No sampling or model fitting."""
from pathlib import Path
from itertools import combinations
from collections import Counter
import hashlib, json, sys, importlib.metadata, textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT/'code') not in sys.path:
    sys.path.insert(0, str(ROOT/'code'))
DATA, CHARTS = ROOT/'data', ROOT/'charts'
for p in [DATA/'cleaned', DATA/'derived', CHARTS, ROOT/'appendices']:
    p.mkdir(parents=True, exist_ok=True)
ACCENT, GREY, INK = '#087F8C', '#AAB2B9', '#172D3D'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':17,
                     'axes.labelsize':12,'svg.fonttype':'none','figure.facecolor':'white'})

def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, default=lambda x: x.item() if hasattr(x,'item') else str(x)))

def clean_data():
    raw = pd.read_excel(DATA/'raw'/'Online Retail.xlsx', dtype={'InvoiceNo':str,'StockCode':str,'CustomerID':str})
    audit = []
    d = raw.copy()
    def keep(label, condition):
        nonlocal d
        old = len(d)
        d = d.loc[condition(d)].copy()
        audit.append({'step':label,'remaining':len(d),'removed':old-len(d)})
    audit.append({'step':'Source workbook','remaining':len(d),'removed':0})
    keep('Remove exact duplicate rows', lambda x: ~x.duplicated())
    d['InvoiceDate'] = pd.to_datetime(d.InvoiceDate, errors='coerce')
    keep('Valid invoice date', lambda x:x.InvoiceDate.notna())
    keep('Complete months Jan-Nov 2011', lambda x:(x.InvoiceDate>='2011-01-01') & (x.InvoiceDate<'2011-12-01'))
    keep('Positive non-cancelled purchase lines', lambda x:~x.InvoiceNo.str.upper().str.startswith('C') & (x.Quantity>0) & (x.UnitPrice>0))
    keep('Product-like stock codes', lambda x:x.StockCode.str.fullmatch(r'\d{5}[A-Za-z]?').fillna(False))
    keep('Known description and country', lambda x:x.Description.notna() & x.Country.notna())
    d['Description'] = d.Description.str.strip()
    d['CustomerID'] = d.CustomerID.fillna('Unknown')
    d['LineValueGBP'] = (d.Quantity*d.UnitPrice).round(2)
    d['Month'] = d.InvoiceDate.dt.strftime('%Y-%m')
    d['Date'] = d.InvoiceDate.dt.strftime('%Y-%m-%d')
    d['Hour'] = d.InvoiceDate.dt.hour
    d['Weekday'] = d.InvoiceDate.dt.day_name()
    d['Market'] = np.where(d.Country.eq('United Kingdom'),'United Kingdom','International')
    d['Period'] = np.where(d.InvoiceDate<'2011-09-01','Discovery: Jan-Aug','Confirmation: Sep-Nov')
    d.to_csv(DATA/'cleaned'/'purchase_lines.csv.gz',index=False,compression='gzip')
    pd.DataFrame(audit).to_csv(DATA/'derived'/'cleaning_audit.csv',index=False)
    return raw,d,audit

def basket_stats(d, products=None):
    # Each invoice counts at most once per product, independent of purchased quantity.
    sets = d.groupby('InvoiceNo').StockCode.agg(set)
    counts = Counter(c for s in sets for c in s)
    products = products or sorted(counts, key=lambda c:(-counts[c],c))[:30]
    chosen = set(products)
    pairs = Counter(pair for s in sets for pair in combinations(sorted(s & chosen),2))
    n = len(sets)
    rows=[]
    for (a,b),both in pairs.items():
        expected = counts[a]*counts[b]/n
        rows.append({'a':a,'b':b,'both':both,'a_baskets':counts[a],'b_baskets':counts[b],
                     'n_baskets':n,'support':both/n,'expected':expected,
                     'lift':both/expected,'b_given_a':both/counts[a],'a_given_b':both/counts[b]})
    return pd.DataFrame(rows),products,counts,n

CATALOG=[]
SHORT={'85099B':'Red retrospot','22386':'Pink polkadot','21931':'Suki','22411':'Vintage paisley','85099C':'Baroque black/white',
       '85123A':'Heart tea-light holder','47566':'Party bunting','22423':'Three-tier cake stand','20725':'Red lunch bag',
       '84879':'Bird ornaments','22720':'Pantry cake tins','22197':'Popcorn holder','20727':'Skull lunch bag','22383':'Suki lunch bag'}

def run():
    raw,d,audit=clean_data()
    uk=d.loc[d.Country.eq('United Kingdom')].copy()
    early=uk.loc[uk.InvoiceDate<'2011-09-01'];late=uk.loc[uk.InvoiceDate>='2011-09-01']
    pair,codes,early_counts,n=basket_stats(early)
    eligible=pair.loc[pair.both.ge(100)&pair.lift.ge(2)].sort_values(['both','lift','a','b'],ascending=[False,False,True,True])
    best=eligible.iloc[0];a,b=best.a,best.b
    anchor=sorted([a,b],key=lambda c:(-early_counts[c],c))[0]
    links=eligible.loc[eligible.a.eq(anchor)|eligible.b.eq(anchor)].head(4).copy()
    links['other']=[r.b if r.a==anchor else r.a for r in links.itertuples()]
    pilot=[anchor]+links.other.tolist();pset=set(pilot)
    assert len(pilot)==5
    names=d.groupby('StockCode').Description.agg(lambda x:x.mode().iloc[0]).to_dict()
    labels={c:SHORT.get(c,names[c]) for c in names}
    all_baskets=uk.groupby('InvoiceNo').agg(date=('InvoiceDate','min'),products=('StockCode',set),gross=('LineValueGBP','sum'))
    all_baskets['pilot_count']=all_baskets.products.map(lambda z:len(z&pset))
    all_baskets['has_anchor']=all_baskets.products.map(lambda z:anchor in z)
    all_baskets['anchor_with_other']=all_baskets.has_anchor&all_baskets.pilot_count.ge(2)
    all_baskets['period']=np.where(all_baskets.date<'2011-09-01','Jan-Aug','Sep-Nov')
    periods=[]
    for label,v in [('Jan-Aug',all_baskets.loc[all_baskets.period.eq('Jan-Aug')]),('Sep-Nov',all_baskets.loc[all_baskets.period.eq('Sep-Nov')]),('All',all_baskets)]:
        an=int(v.has_anchor.sum());other=int(v.anchor_with_other.sum());multi=int(v.pilot_count.ge(2).sum())
        periods.append({'period':label,'orders':len(v),'anchor_baskets':an,'anchor_with_other':other,'anchor_companion_rate':other/an,
                        'at_least_one_pilot':int(v.pilot_count.ge(1).sum()),'multi_pilot_orders':multi,'multi_pilot_share':multi/len(v)})
    monthly=uk.groupby('Month').agg(orders=('InvoiceNo','nunique'),gross=('LineValueGBP','sum')).reset_index()
    monthly['calendar_days']=[pd.Period(v).days_in_month for v in monthly.Month]
    monthly['orders_per_calendar_day']=monthly.orders/monthly.calendar_days
    early_daily=len(early.InvoiceNo.unique())/243
    product=uk.groupby('StockCode').agg(orders=('InvoiceNo','nunique'),quantity=('Quantity','sum'),gross=('LineValueGBP','sum'),price=('UnitPrice','median'))
    product['name']=[names[c] for c in product.index];product['short_name']=[labels[c] for c in product.index]
    top=product.sort_values(['orders','name'],ascending=[False,True]).head(8).reset_index()
    later_pairs,_,late_counts,late_n=basket_stats(late,codes)
    comparison=[]
    for r in links.itertuples():
        z=later_pairs.loc[(later_pairs.a.eq(r.a)&later_pairs.b.eq(r.b))].iloc[0]
        comparison.append({'code':r.other,'name':names[r.other],'short_name':labels[r.other],
                           'discovery_shared':int(r.both),'discovery_lift':r.lift,
                           'confirmation_shared':int(z.both),'confirmation_lift':z.lift})
    joint=pair.loc[pair.a.isin(pilot)&pair.b.isin(pilot)].sort_values(['both','a','b'],ascending=[False,True,True])
    g=nx.Graph()
    g.add_nodes_from(pilot)
    for r in joint.itertuples():g.add_edge(r.a,r.b,weight=int(r.both))
    deg=dict(g.degree(weight='weight'))
    nodes=[{'code':c,'name':names[c],'short_name':labels[c],'weighted_degree':int(deg[c]),'discovery_baskets':early_counts[c]} for c in pilot]
    out={'raw_rows':len(raw),'clean_rows':len(d),'uk_rows':len(uk),'uk_orders':len(all_baskets),'all_orders':d.InvoiceNo.nunique(),
         'variables':len(d.columns),'missing_customer_lines':int(d.CustomerID.eq('Unknown').sum()),'countries':d.Country.nunique(),
         'anchor':anchor,'pilot_codes':pilot,'names':{c:names[c] for c in pilot},'short_names':{c:labels[c] for c in pilot},
         'selection_top_products':codes,'eligible_pair_count':len(eligible),'anchor_partners':comparison,
         'periods':periods,'monthly':monthly.to_dict('records'),'early_orders_per_calendar_day':early_daily,
         'november_daily_ratio':float(monthly.iloc[-1].orders_per_calendar_day/early_daily),
         'top_products':top.to_dict('records'),'network_nodes':nodes,'network_edges':nx.to_pandas_edgelist(g).to_dict('records'),
         'audit':audit,'gross_purchase_value':float(d.LineValueGBP.sum())}
    for stem,frame in [('discovery_pairs',pair),('eligible_pairs',eligible),('confirmation_pairs',later_pairs),
                       ('uk_monthly',monthly),('uk_product_summary',product.reset_index()),
                       ('pilot_periods',pd.DataFrame(periods)),('pilot_products',pd.DataFrame(nodes)),
                       ('pilot_pair_check',pd.DataFrame(comparison)),('network_edges',nx.to_pandas_edgelist(g)),('network_nodes',pd.DataFrame(nodes))]:
        frame.to_csv(DATA/'derived'/f'{stem}.csv',index=False)
    export=all_baskets.drop(columns='products').reset_index();export.to_csv(DATA/'derived/uk_invoice_pilot_counts.csv',index=False)
    dump(DATA/'derived/summary.json',out);dump(ROOT/'appendices/deck_data.json',out)
    manifest=json.loads((DATA/'source_manifest.json').read_text())
    manifest.update(scope='Positive merchandise purchases in Jan-Nov 2011. UK invoice baskets. Select five-product picking pilot using Jan-Aug only, check Sep-Nov separately.',
                    analysis_revision='Warehouse picking-zone pilot, revised November 4, 2026',
                    changes='Original workbook unchanged. Same documented cleaning rules, plus derived order, pair and five-product pilot tables.')
    dump(DATA/'source_manifest.json',manifest)
    derived=[('pilot_count','derived integer','Distinct selected pilot products in a UK purchase invoice; from 0 to 5.'),
             ('has_anchor','derived boolean','Whether a UK invoice contains the red retrospot jumbo bag.'),
             ('anchor_with_other','derived boolean','Anchor invoice containing at least one of the other four selected products.'),
             ('orders_per_calendar_day','derived numeric','Distinct purchase invoices divided by calendar days in the complete month, including zero-order days.'),
             ('weighted_degree','derived count','Sum of shared-basket edge weights incident to a node in the displayed five-product network. Edges can overlap in invoice identity.')]
    pd.DataFrame(derived,columns=['field','type','definition']).to_csv(DATA/'derived_dictionary.csv',index=False)
    dump(ROOT/'code/versions.json',{p:importlib.metadata.version(p) for p in ['pandas','numpy','matplotlib','networkx','openpyxl','reportlab','nbformat','colorspacious']})
    make_charts(d,uk,early,late,all_baskets,monthly,product,eligible,g,out)
    print(json.dumps(out,indent=2,default=str));return out

def make_charts(d,uk,early,late,baskets,monthly,product,eligible,g,s):
    from visual_design import render_charts
    render_charts(d,uk,early,late,baskets,monthly,product,eligible,g,s)

if __name__=='__main__':run()
