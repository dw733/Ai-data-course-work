"""Static figures with direct labels, restrained colour and explicit visual hierarchy."""
from pathlib import Path
import json,textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter,PercentFormatter,MaxNLocator
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import networkx as nx

ACCENT='#087F8C';GREY='#B6C0C7';INK='#172D3D';MUTED='#637684';GRID='#E7EDF0'
MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov']
ROOT=Path(__file__).resolve().parents[1];CHARTS=ROOT/'charts';DATA=ROOT/'data'
CATALOG=[]

def theme():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':17,
        'axes.titleweight':'bold','axes.titlelocation':'left','axes.titlepad':19,
        'axes.labelsize':12,'axes.labelcolor':MUTED,'text.color':INK,
        'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':'#CFD9DF',
        'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,
        'axes.grid':False,'figure.facecolor':'white','axes.facecolor':'white',
        'svg.fonttype':'none','savefig.facecolor':'white'})

def style(ax,grid='y'):
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('#CFD9DF');ax.spines['bottom'].set_linewidth(.7)
    ax.tick_params(length=0,pad=8);ax.set_axisbelow(True)
    if grid:ax.grid(axis=grid,color=GRID,lw=.7)
    else:ax.grid(False)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:,.0f}'))

def save(fig,key,finding,alt,final=False):
    if not fig.get_constrained_layout():fig.tight_layout(pad=1.6)
    for ext in ['png','svg']:fig.savefig(CHARTS/f'{key}.{ext}',dpi=240,bbox_inches='tight')
    plt.close(fig)
    CATALOG.append({'key':key,'finding':finding,'alt':alt,'final':final})

def workload(ax,monthly,baseline,compact=False):
    x=np.arange(len(monthly));v=monthly.orders_per_calendar_day.to_numpy()
    ax.axvspan(7.5,10.5,color=ACCENT,alpha=.055,zorder=0)
    ax.axhline(baseline,color='#7E909B',ls=(0,(4,3)),lw=1.3,zorder=1)
    ax.plot(x[:8],v[:8],color='#8799A4',lw=2.4)
    ax.plot(x[7:],v[7:],color=ACCENT,lw=3.2)
    ax.scatter([10],[v[-1]],s=65,color=ACCENT,zorder=4)
    ax.set(xlim=(-.2,10.65),ylim=(0,110),ylabel='UK invoices per calendar day')
    ax.set_xticks(x[::2] if compact else x,[MONTHS[i] for i in (range(0,11,2) if compact else range(11))])
    ax.set_yticks([0,25,50,75,100]);style(ax)
    ax.text(.18,baseline+3.5,f'Jan-Aug: {baseline:.1f}/day',fontsize=12 if compact else 12.5,color=MUTED)
    ax.annotate(f'November: {v[-1]:.1f}/day',xy=(10,v[-1]),xytext=(5.2,96),
                fontsize=16 if compact else 15,fontweight='bold',color=ACCENT,
                arrowprops={'arrowstyle':'-','color':ACCENT,'lw':1.1},va='center')
    if not compact:ax.text(7.65,105,'Sep-Nov check',fontsize=10.5,color=MUTED)

def render_charts(d,uk,early,late,baskets,monthly,product,eligible,g,s):
    CATALOG.clear();theme();pilot=s['pilot_codes'];anchor=s['anchor'];labs=s['short_names'];e,l,t=s['periods']
    fig,ax=plt.subplots(figsize=(11,5.1));workload(ax,monthly,s['early_orders_per_calendar_day'])
    ax.set_title('Daily invoice workload rises into November')
    save(fig,'01_workload',f'November averaged {monthly.orders_per_calendar_day.iloc[-1]:.1f} UK invoices per calendar day, {s["november_daily_ratio"]:.2f} times the Jan-Aug average.',
        'Line chart of UK purchase invoices per calendar day in January-November 2011. Earlier months are muted, September-November is lightly shaded, the dashed January-August reference is directly labelled 40.4 per day, and November is directly labelled 82.7.',True)

    top=product.sort_values('orders',ascending=False).head(8).iloc[::-1]
    fig,ax=plt.subplots(figsize=(11,5.5));ax.barh(top.short_name,top.orders,height=.64,color=[ACCENT if c==anchor else GREY for c in top.index])
    for i,(c,row) in enumerate(top.iterrows()):
        txt=f'{row.orders:,}'+('  Pilot anchor' if c==anchor else '')
        ax.text(row.orders+28,i,txt,va='center',color=ACCENT if c==anchor else INK,fontsize=12,fontweight='bold' if c==anchor else 'normal')
    ax.set(xlim=(0,2500),xlabel='Distinct UK invoices containing product',title='The red jumbo bag is a frequent product with recurring companions')
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:,.0f}'));style(ax,'x');ax.yaxis.set_major_formatter(plt.FixedFormatter(top.short_name.tolist()))
    save(fig,'02_popularity','The heart tea-light holder leads invoice frequency, while the red jumbo bag is second.',
        'Eight sorted horizontal bars use product names and directly labelled counts. The red retrospot jumbo bag is teal and labelled Pilot anchor at 1,776 invoices. Other products and structural elements are muted.',True)

    partners=s['anchor_partners'][::-1];vals=[r['discovery_shared'] for r in partners]
    fig,ax=plt.subplots(figsize=(11,4.6));ax.barh([r['short_name'] for r in partners],vals,height=.6,color=[GREY]*3+[ACCENT])
    for i,v in enumerate(vals):ax.text(v+12,i,f'{v:,}'+('  Strongest link' if i==3 else ''),va='center',color=ACCENT if i==3 else INK,fontweight='bold' if i==3 else 'normal')
    ax.set(xlim=(0,745),xticks=[0,200,400,600],xlabel='Jan-Aug invoices with companion AND red jumbo bag',title='Pink polkadot is the red bag\'s strongest recurring companion');style(ax,'x');ax.set_yticks(range(4),[r['short_name'] for r in partners])
    save(fig,'03_companions','The red jumbo bag shares 512, 448, 430 and 362 discovery invoices with its four strongest eligible companions.',
        'Sorted companion bars show pink polkadot 512, Suki 448, vintage paisley 430 and baroque black/white 362 shared discovery invoices with the red jumbo bag. Teal and a direct Strongest link label identify the leading pair. Counts overlap in invoice identity.',True)

    rates=[e['anchor_companion_rate'],l['anchor_companion_rate']]
    fig,ax=plt.subplots(figsize=(10,5));ax.plot([0,1],rates,color='#9AABB5',lw=2.5)
    ax.scatter([0],[rates[0]],s=85,facecolors='white',edgecolors='#869AA6',lw=2,zorder=3);ax.scatter([1],[rates[1]],s=110,color=ACCENT,zorder=3)
    for i,v in enumerate(rates):
        ax.text(i,v+.065,f'{v:.1%}',ha='center',fontsize=19,fontweight='bold',color=ACCENT if i else MUTED)
        count=[e,l][i];ax.text(i,v-.09,f"{count['anchor_with_other']:,} / {count['anchor_baskets']:,} invoices",ha='center',fontsize=11,color=MUTED)
    ax.text(.5,.38,f'{(rates[0]-rates[1])*100:.1f} percentage points lower',ha='center',fontsize=12,color=INK)
    ax.set(xlim=(-.35,1.35),ylim=(0,1),ylabel='Share of red-bag invoices',title='The companion relationship persists in the later period')
    ax.set_xticks([0,1],['Jan-Aug selection','Sep-Nov check']);style(ax);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_yticks([0,.25,.5,.75,1])
    save(fig,'04_persistence',f'Red-bag companion share falls from {rates[0]:.1%} to {rates[1]:.1%}, but remains above half in the later period.',
        'Slopegraph retains a full 0-to-100 percent scale. The selection endpoint is muted at 71.7 percent, 838 of 1,168 invoices. The later endpoint is teal at 64.5 percent, 392 of 608. A direct annotation states the 7.3-percentage-point decrease.',True)

    counts=baskets.pilot_count.value_counts().reindex(range(6),fill_value=0)
    fig,ax=plt.subplots(figsize=(10,4.6));ax.bar(range(6),counts,color=[GREY,GREY]+[ACCENT]*4,width=.68)
    ax.set(xticks=range(6),xlabel='Distinct selected products in a UK invoice',ylabel='UK invoices',title='Multi-product invoices define the pilot opportunity');style(ax)
    ax.text(.98,.9,f"{t['multi_pilot_orders']:,} invoices contain 2+ selected products",ha='right',transform=ax.transAxes,color=ACCENT,fontsize=13,fontweight='bold')
    save(fig,'05_pilot_counts',f'{t["multi_pilot_orders"]:,} UK invoices contain at least two of the five selected products.',
        'Bars count invoices with zero through five selected products. The two-through-five subset is teal and its combined 1,564-invoice count is directly annotated.')

    fig,ax=plt.subplots(figsize=(10.5,6));pos=nx.circular_layout(g);deg=dict(g.degree(weight='weight'))
    edge_colours=[ACCENT if anchor in (a,b) else '#D3DDE2' for a,b in g.edges]
    nx.draw_networkx_edges(g,pos,ax=ax,edge_color=edge_colours,width=[g[a][b]['weight']/110 for a,b in g.edges],alpha=.7)
    nx.draw_networkx_nodes(g,pos,ax=ax,node_size=[3*(700+deg[c]*1.4) for c in g],node_color=[ACCENT if c==anchor else '#E5ECEF' for c in g],edgecolors=[ACCENT if c==anchor else '#AABAC4' for c in g],linewidths=[3 if c==anchor else 1 for c in g])
    label={'85099B':'Red\nretrospot','22386':'Pink\npolkadot','21931':'Suki','22411':'Vintage\npaisley','85099C':'Baroque\nblack/white'}
    for c,(x,y) in pos.items():ax.text(x,y,label.get(c,labs[c]),ha='center',va='center',fontsize=13,fontweight='bold' if c==anchor else 'normal',color='white' if c==anchor else INK)
    ax.set(xlim=(-1.42,1.42),ylim=(-1.3,1.32),title='The red bag connects the five-product group');ax.axis('off')
    fig.text(.055,.012,'Edge width: shared discovery invoices. Node area: displayed weighted degree plus a small base.\nTeal links connect to the anchor. Positions are schematic, not warehouse locations.',fontsize=10,color=MUTED)
    save(fig,'06_network',f'The selected five products form a network with {g.number_of_edges()} observed links.',
        'NetworkX graph uses readable product names inside five nodes. Teal anchor links and a thicker teal outline focus the red jumbo bag. Other relationships are light grey. Edge width encodes shared discovery invoices, and node area encodes displayed weighted degree plus a base.',True)

    international=s['all_orders']-s['uk_orders'];one=t['at_least_one_pilot']-t['multi_pilot_orders'];zero=s['uk_orders']-t['at_least_one_pilot']
    fig,ax=plt.subplots(figsize=(11,5));ax.axis('off');ax.set(xlim=(0,1.1),ylim=(0,1))
    ax.set_title('One in ten UK invoices contains multiple pilot products')
    ax.plot([.08,.08],[.11,.86],color='#CFD9DF',lw=1.5)
    for y in [.75,.11]:ax.plot([.08,.18],[y,y],color='#CFD9DF',lw=1.5)
    ax.plot([.28,.28],[.29,.68],color='#CFD9DF',lw=1.5)
    for y in [.59,.44,.29]:ax.plot([.28,.40],[y,y],color=ACCENT if y==.29 else '#CFD9DF',lw=2 if y==.29 else 1.5)
    ax.text(.03,.94,f"All retained invoices: {s['all_orders']:,}",fontsize=17,fontweight='bold',va='center')
    ax.text(.20,.75,f"United Kingdom: {s['uk_orders']:,}",fontsize=15,fontweight='bold',va='center')
    ax.text(.20,.11,f'International: {international:,}',fontsize=14,color=MUTED,va='center')
    for y,label,count in [(.59,'No selected products',zero),(.44,'Exactly one selected product',one),(.29,'Two or more selected products',t['multi_pilot_orders'])]:
        focal=y==.29;ax.scatter([.405],[y],s=40 if focal else 18,color=ACCENT if focal else '#ACBCC6')
        label_text=f'{label}: {count:,}' if not focal else f'2+ selected products: {count:,}\n10.0% of UK invoices'
        ax.text(.435,y,label_text,va='center',fontsize=14.3 if focal else 13,color=ACCENT if focal else INK,fontweight='bold' if focal else 'normal')
    save(fig,'07_hierarchy',f'The {t["multi_pilot_orders"]:,} multi-product pilot invoices represent {t["multi_pilot_share"]:.1%} of UK invoices.',
        f'An editable-data tree partitions {s["all_orders"]:,} invoices into {s["uk_orders"]:,} UK and {international:,} international. UK leaves are {zero:,} with none of the selected products, {one:,} with one, and {t["multi_pilot_orders"]:,} with at least two. The pilot leaf is teal and labelled 10.0 percent.',True)

    fig,axes=plt.subplots(1,2,figsize=(12,5.3),sharex=True,sharey=True,layout='constrained')
    for ax,mask,title in zip(axes,[product.price.lt(3),product.price.ge(3)],['Median price below GBP 3','Median price GBP 3 or above']):
        z=product.loc[mask];ax.scatter(z.orders,z.gross/1000,color='#9DADB7',s=15,alpha=.38,edgecolors='none')
        if anchor in z.index:
            x=product.loc[anchor,'orders'];y=product.loc[anchor,'gross']/1000
            ax.scatter([x],[y],facecolors='white',edgecolors=ACCENT,s=120,lw=2,zorder=4)
            ax.annotate('Red jumbo bag',xy=(x,y),xytext=(x-680,y+15),fontsize=12,color=ACCENT,fontweight='bold',arrowprops={'arrowstyle':'-','color':ACCENT,'lw':1})
        ax.set(xlabel='Distinct UK invoices',title=title);style(ax)
    axes[0].set_ylabel('Gross purchase value (GBP thousands)')
    save(fig,'08_multivariate','Frequency, gross purchase value and median price answer different product questions.',
        'Two scatterplot facets share both scales and divide products by median unit price. Context points are muted. An outlined point and direct red-bag label identify the anchor without colour alone.',True)

    inv=uk.drop_duplicates('InvoiceNo');days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    h=inv.groupby(['Weekday','Hour']).size().unstack(fill_value=0).reindex(days,fill_value=0)
    exposure=pd.Series(pd.date_range('2011-01-01','2011-11-30').day_name()).value_counts()
    h=h.div(exposure,axis=0).reindex(index=days,columns=range(7,18),fill_value=0)
    cm=LinearSegmentedColormap.from_list('retailflow_teal',['#F2F6F7','#C4E1E4',ACCENT])
    fig,ax=plt.subplots(figsize=(11,5));im=ax.imshow(h,cmap=cm,aspect='auto',vmin=0)
    ax.set_xticks(range(11),[f'{x:02d}:00' for x in range(7,18)],rotation=45,ha='right');ax.set_yticks(range(7),days)
    ax.set_xticks(np.arange(-.5,11,1),minor=True);ax.set_yticks(np.arange(-.5,7,1),minor=True);ax.grid(which='minor',color='white',lw=.8);ax.tick_params(which='both',length=0)
    y,x=np.unravel_index(np.argmax(h.to_numpy()),h.shape);peak=h.iloc[y,x]
    ax.add_patch(Rectangle((x-.5,y-.5),1,1,fill=False,edgecolor='white',lw=2.5));ax.text(x,y,f'{peak:.1f}',ha='center',va='center',color='white',fontweight='bold',fontsize=11)
    ax.set(xlabel='Source invoice hour',title=f'Highest invoice-entry cell: {days[y]}, {h.columns[x]:02d}:00')
    cb=fig.colorbar(im,ax=ax,pad=.025);cb.set_label('UK invoices per calendar weekday');cb.outline.set_visible(False)
    save(fig,'09_heatmap','Calendar-day denominators keep weekday/hour comparisons exposure-adjusted.',
        f'A single-hue teal heatmap encodes mean UK invoice counts by weekday and source hour. The highest cell, {days[y]} at {h.columns[x]:02d}:00, is outlined and directly labelled {peak:.1f}. Values describe invoice entry, not warehouse picking shifts.',True)

    fig,ax=plt.subplots(figsize=(10,4.5));v=baskets.gross;visible=(v<=1000).mean();ax.hist(v,bins=np.linspace(0,1000,41),color=GREY,edgecolor='white')
    ax.set(xlabel='Retained purchase value per invoice (GBP)',ylabel='UK invoices',title='Invoice values have a long upper tail')
    ax.text(.98,.94,f'{visible:.1%} of invoices shown\nValues above GBP 1,000 omitted from this view',ha='right',va='top',transform=ax.transAxes,fontsize=10,color=MUTED);style(ax)
    save(fig,'10_order_values','Large orders make gross-value averages a poor substitute for measuring picking time.',
        'Histogram of invoice purchase values from GBP 0 to 1,000. The visible proportion is labelled; all positive invoices remain in the analysis.')

    country=d.groupby('Country').InvoiceNo.nunique().sort_values(ascending=False).head(6).iloc[::-1]
    fig,ax=plt.subplots(figsize=(10.5,4.5));ax.barh(country.index,country.values,color=[ACCENT if c=='United Kingdom' else GREY for c in country.index],height=.65)
    ax.set(xlabel='Retained purchase invoices',title='UK invoices define the main operating scope');style(ax,'x');ax.set_yticks(range(len(country)),country.index)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:,.0f}'))
    save(fig,'11_country','The UK supplies most retained invoices, so the pilot analysis uses one market.', 'Horizontal bars compare the leading country invoice counts using one teal UK highlight and grey context.')

    check=[]
    for month,grp in baskets.groupby(baskets.date.dt.strftime('%Y-%m')):
        an=int(grp.has_anchor.sum());both=int(grp.anchor_with_other.sum());check.append({'month':month,'anchor':an,'with_other':both,'rate':both/an})
    frame=pd.DataFrame(check);frame.to_csv(DATA/'derived/pilot_monthly.csv',index=False)
    fig,ax=plt.subplots(figsize=(11,4.5));ax.axvspan(7.5,10.5,color=ACCENT,alpha=.055)
    ax.plot(range(11),frame.rate*100,color=ACCENT,lw=2.5);ax.set_xticks(range(11),MONTHS)
    ax.set(ylim=(0,100),ylabel='Red-bag invoices with a companion (%)',title='The relationship varies month by month');style(ax)
    save(fig,'12_monthly_persistence','Monthly shares vary, which supports a monitored pilot instead of assuming a fixed rate.',
        'Monthly companion shares use a 0-to-100 percent scale and lightly shade the fixed September-November check period.')

    z=product.loc[pilot].iloc[::-1]
    fig,ax=plt.subplots(figsize=(10.5,4.5));ax.barh([labs[c] for c in z.index],z.price,color=GREY,height=.6)
    ax.set(xlabel='Median recorded unit price (GBP)',title='Recorded prices answer a different question from picking effort');style(ax,'x');ax.set_yticks(range(5),[labs[c] for c in z.index])
    save(fig,'13_prices','The pilot products have similar recorded prices, but price does not measure walking or handling time.',
        'Five horizontal bars compare median recorded unit prices of the selected products. Price does not enter the product-selection rule.')

    with plt.style.context('default'):
        fig,ax=plt.subplots(figsize=(10,4.4));ax.bar([r['code'] for r in s['anchor_partners']],[r['discovery_shared'] for r in s['anchor_partners']]);ax.grid(True);ax.set_title('Default companion counts')
        save(fig,'14_default_companions','Default partner bars use the identical four discovery counts as the redesigned chart.', 'Default vertical bars preserve the four values before names, sorting, direct labels and one highlight.')
        fig,ax=plt.subplots(figsize=(10,4.4));ax.plot(monthly.Month,monthly.orders_per_calendar_day,marker='o');ax.grid(True);ax.tick_params(axis='x',rotation=45);ax.set_title('Default monthly rates')
        save(fig,'15_default_workload','The default and redesigned monthly displays retain the same eleven normalized rates.', 'Default line graph retains the eleven monthly rates before direct labels, restrained marks and a comparison-period band.')

    shares=[s['uk_orders']/s['all_orders'],1-s['uk_orders']/s['all_orders']]
    fig,ax=plt.subplots(figsize=(8,4.8));ax.pie(shares,labels=['United Kingdom','International'],autopct='%1.1f%%',colors=[ACCENT,GREY]);ax.set_title('Pie example: invoice market mix')
    save(fig,'16_pie_avoid','The pie shows composition but makes exact comparison less direct.', 'Two-slice pie of UK and international invoice shares, retained as the visual-to-avoid example.')
    fig,ax=plt.subplots(figsize=(9.5,3.8));ax.barh(['United Kingdom','International'],np.array(shares)*100,color=[ACCENT,GREY],height=.5);ax.invert_yaxis();ax.set(xlim=(0,100),xlabel='Share of retained purchase invoices (%)',title='A shared baseline clarifies the market split');style(ax,None);ax.set_yticks([0,1],['United Kingdom','International'])
    for i,v in enumerate(shares):ax.text(v*100+1,i,f'{v:.1%}',va='center',fontweight='bold' if i==0 else 'normal',color=ACCENT if i==0 else INK)
    save(fig,'17_pie_redesign','The redesigned bars retain the identical two shares and provide a common baseline.', 'Two horizontal bars replace the pie with a shared zero, printed percentages and one UK highlight.')

    fig,axd=plt.subplot_mosaic([['work','work','scope'],['work','work','check']],figsize=(12,6.8),layout='constrained',gridspec_kw={'width_ratios':[1,1,1.25],'hspace':.2,'wspace':.18})
    a=axd['work'];workload(a,monthly,s['early_orders_per_calendar_day'],compact=True);a.set_title('Daily workload roughly doubled',fontsize=17,pad=18)
    a.tick_params(labelsize=13);a.set_ylabel('UK invoices per calendar day',fontsize=13)
    a=axd['scope'];a.barh([0],[100],color='#E3EBEF',height=.32);a.barh([0],[t['multi_pilot_share']*100],color=ACCENT,height=.32)
    a.set(xlim=(0,100),ylim=(-.65,.65));a.set_title('Defined pilot scope',fontsize=16,pad=14);a.set_yticks([]);a.set_xticks([])
    for sp in a.spines.values():sp.set_visible(False)
    a.text(0,.44,f"{t['multi_pilot_orders']:,} UK invoices",fontsize=20,color=ACCENT,fontweight='bold')
    a.text(0,-.43,'10.0% contain 2+ selected products',fontsize=12.5,color=MUTED)
    a=axd['check'];a.barh([1,0],np.array(rates)*100,color=[GREY,ACCENT],height=.38);a.set(xlim=(0,100),ylim=(-.7,1.7));a.set_yticks([1,0],['Jan-Aug','Sep-Nov']);a.set_xticks([])
    a.tick_params(labelsize=13,length=0);a.set_title('Red-bag companion share',fontsize=16,pad=14)
    for sp in a.spines.values():sp.set_visible(False)
    for y,v in zip([1,0],rates):a.text(v*100+2,y,f'{v:.1%}',va='center',fontsize=16,fontweight='bold',color=ACCENT if y==0 else MUTED)
    save(fig,'20_story_overview','The largest panel establishes workload; two smaller panels show pilot scope and the later-period check.',
        'One large workload line occupies the left of a three-panel overview. The two smaller right panels show 1,564 UK invoices, or 10.0 percent, with multiple pilot products, and companion shares of 71.7 and 64.5 percent. Different measures remain in separate labelled panels.',True)

    from PIL import Image,ImageOps,ImageDraw,ImageFont
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
    for source,target,lines in [('03_companions','18_gestalt_companions',['Proximity: direct values stay next to their bars. Similarity: grey companions share one comparison.','Teal and bold identify the strongest link without relying on colour alone.']),('01_workload','19_gestalt_workload',['Continuity: the line preserves time order. Proximity: the November label points to its value.','Enclosure: a light band groups the later check period.'])]:
        im=Image.open(CHARTS/f'{source}.png').convert('RGB');o=ImageOps.expand(im,border=(0,0,0,110),fill='white');dr=ImageDraw.Draw(o)
        for i,line in enumerate(lines):dr.text((25,im.height+12+i*39),line,fill=INK,font=font)
        o.save(CHARTS/f'{target}.png')
    (CHARTS/'chart_catalogue.json').write_text(json.dumps(CATALOG,indent=2));pd.DataFrame(CATALOG).to_csv(CHARTS/'chart_catalogue.csv',index=False)
