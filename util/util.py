import yfinance as yf
import json
import sqlite3
from datetime import datetime
import pandas as pd
from datetime import timedelta
import yfinance as yf
from datetime import datetime
from dateutil.parser import parse
import calendar
import os


def save_from_data_json():
    conn = sqlite3.connect('stock_data2.sqlite3')

    # Create the StockData table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS StockData (
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_name TEXT,
            date DATE,
            interval TEXT,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume INTEGER,
            UNIQUE(stock_name, date, interval)
        )
    ''')


    import json

    # Open the file and load the data
    with open('data.json', 'r') as f:
        combined_data = json.load(f)

    # def get_ticker_data(stock):
    #     tickerData = yf.Ticker(stock+'.IS')
    #     tickerDf = tickerData.history(period='1d', start='2023-7-4', end='2024-7-4')
    #     return stock, tickerDf.to_dict()

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = executor.map(get_ticker_data, stocks)

    # combined_data = {}
    # for stock, data in results:
    #     combined_data[stock] = data

    # Convert timestamps to strings
    data_for_json = {}
    for stock in combined_data:
        data_for_json[stock] = {}
        for key in combined_data[stock]:
            if (key not in ['Dividends', 'Stock Splits','Volume']):
                data_for_json[stock][key] = {str(date): value for date, value in combined_data[stock][key].items()}

    # # Write the combined data to a JSON file
    # with open('data.json', 'r') as file:
    #     existing_data = json.load(file)
    #     existing_data.update(data_for_json)

    # with open('data.json', 'w') as file:
    #     json.dump(existing_data, file)

    # Insert the data into the StockData table
    interval = '1d'
    for stock, data in data_for_json.items():
        # Get all dates for this stock
        dates = data['Open'].keys()

        for date in dates:
            open_value = data['Open'][date]
            high_value = data['High'][date]
            low_value = data['Low'][date]
            close_value = data['Close'][date]
            date2 = datetime.fromisoformat(date).isoformat()
            # volume_value = data['Volume'][date]

            conn.execute('''
                INSERT INTO StockData (stock_name, date, interval, open, high, low, close)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (stock, date2,interval, open_value, high_value, low_value, close_value))
    # Commit the changes and close the connection
    conn.commit()
    conn.close()




def save_stocks_with_increase_rates():
        
    # Connect to the SQLite database
    conn = sqlite3.connect('stock_data2.sqlite3')

    # Create the StockData table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS StockData (
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_name TEXT,
            date DATE,
            interval TEXT,
            close FLOAT,
            increase_1d FLOAT,
            increase_1w FLOAT,
            increase_1m FLOAT,
            increase_3m FLOAT,
            increase_6m FLOAT,
            increase_1y FLOAT,
            increase_5y FLOAT,
            UNIQUE(stock_name, date, interval)
        )
    ''')

    stocks = ['A1CAP.IS','ACSEL.IS', 'ADEL.IS', 'ADESE.IS','ADGYO.IS','AEFES.IS','AFYON.IS','AGESA.IS','AGHOL.IS','AGROT.IS','AGYO.IS','AHGAZ.IS','AKBNK.IS','AKCNS.IS','AKENR.IS','AKFGY.IS','AKFYE.IS','AKGRT.IS','AKMGY.IS','AKSA.IS','AKSEN.IS','AKSGY.IS','AKSUE.IS','AKYHO.IS','ALARK.IS','ALBRK.IS','ALCAR.IS','ALCTL.IS','ALFAS.IS','ALGYO.IS','ALKA.IS','ALKIM.IS','ALMAD.IS','ALVES.IS','ANELE.IS','ANGEN.IS','ANHYT.IS','ANSGR.IS','ARASE.IS','ARCLK.IS','ARDYZ.IS','ARENA.IS','ARSAN.IS','ARTMS.IS','ARZUM.IS','ASELS.IS','ASGYO.IS','ASTOR.IS','ASUZU.IS','ATAGY.IS','ATAKP.IS','ATATP.IS','ATEKS.IS','ATLAS.IS','ATSYH.IS','AVGYO.IS','AVHOL.IS','AVOD.IS','AVPGY.IS','AVTUR.IS','AYCES.IS','AYDEM.IS','AYEN.IS','AYES.IS','AYGAZ.IS','AZTEK.IS','BAGFS.IS','BAKAB.IS','BALAT.IS','BANVT.IS','BARMA.IS','BASCM.IS','BASGZ.IS','BAYRK.IS','BEGYO.IS','BERA.IS','BEYAZ.IS','BFREN.IS','BIENY.IS','BIGCH.IS','BIMAS.IS','BINHO.IS','BIOEN.IS','BIZIM.IS','BJKAS.IS','BLCYT.IS','BMSCH.IS','BMSTL.IS','BNTAS.IS','BOBET.IS','BORLS.IS','BORSK.IS','BOSSA.IS','BRISA.IS','BRKO.IS','BRKSN.IS','BRKVY.IS','BRLSM.IS','BRMEN.IS','BRSAN.IS','BRYAT.IS','BSOKE.IS','BTCIM.IS','BUCIM.IS','BURCE.IS','BURVA.IS','BVSAN.IS','BYDNR.IS','CANTE.IS','CASA.IS','CATES.IS','CCOLA.IS','CELHA.IS','CEMAS.IS','CEMTS.IS','CEOEM.IS','CIMSA.IS','CLEBI.IS','CMBTN.IS','CMENT.IS','CONSE.IS','COSMO.IS','CRDFA.IS','CRFSA.IS','CUSAN.IS','CVKMD.IS','CWENE.IS','DAGHL.IS','DAGI.IS','DAPGM.IS','DARDL.IS','DENGE.IS','DERHL.IS','DERIM.IS','DESA.IS','DESPC.IS','DEVA.IS','DGATE.IS','DGGYO.IS','DGNMO.IS','DIRIT.IS','DITAS.IS','DJIST.IS','DMRGD.IS','DMSAS.IS','DNISI.IS','DOAS.IS','DOBUR.IS','DOCO.IS','DOFER.IS','DOGUB.IS','DOHOL.IS','DOKTA.IS','DURDO.IS','DYOBY.IS','DZGYO.IS','EBEBK.IS','ECILC.IS','ECZYT.IS','EDATA.IS','EDIP.IS','EGEEN.IS','EGEPO.IS','EGGUB.IS','EGPRO.IS','EGSER.IS','EKGYO.IS','EKIZ.IS','EKOS.IS','EKSUN.IS','ELITE.IS','EMKEL.IS','EMNIS.IS','ENERY.IS','ENJSA.IS','ENKAI.IS','ENSRI.IS','EPLAS.IS','ERBOS.IS','ERCB.IS','EREGL.IS','ERSU.IS','ESCAR.IS','ESCOM.IS','ESEN.IS','ETILR.IS','ETYAT.IS','EUHOL.IS','EUKYO.IS','EUPWR.IS','EUREN.IS','EUYO.IS','EYGYO.IS','FADE.IS','FENER.IS','FLAP.IS','FMIZP.IS','FONET.IS','FORMT.IS','FORTE.IS','FRIGO.IS','FROTO.IS','FZLGY.IS','GARAN.IS','GARFA.IS','GEDIK.IS','GEDZA.IS','GENIL.IS','GENTS.IS','GEREL.IS','GESAN.IS','GIPTA.IS','GLBMD.IS','GLCVY.IS','GLDTR.IS','GLRYH.IS','GLYHO.IS','GMSTR.IS','GMTAS.IS','GOKNR.IS','GOLTS.IS','GOODY.IS','GOZDE.IS','GRNYO.IS','GRSEL.IS','GRTRK.IS','GSDDE.IS','GSDHO.IS','GSRAY.IS','GUBRF.IS','GWIND.IS','GZNMI.IS','HALKB.IS','HATEK.IS','HATSN.IS','HDFGS.IS','HEDEF.IS','HEKTS.IS','HKTM.IS','HLGYO.IS','HTTBT.IS','HUBVC.IS','HUNER.IS','HURGZ.IS','ICBCT.IS','ICUGS.IS','IDGYO.IS','IEYHO.IS','IHAAS.IS','IHEVA.IS','IHGZT.IS','IHLAS.IS','IHLGM.IS','IHYAY.IS','IMASM.IS','INDES.IS','INFO.IS','INGRM.IS','INTEM.IS','INVEO.IS','INVES.IS','IPEKE.IS','ISATR.IS','ISBIR.IS','ISBTR.IS','ISCTR.IS','ISDMR.IS','ISFIN.IS','ISGSY.IS','ISGYO.IS','ISIST.IS','ISKPL.IS','ISKUR.IS','ISMEN.IS','ISSEN.IS','ISYAT.IS','IZENR.IS','IZFAS.IS','IZINV.IS','IZMDC.IS','JANTS.IS','KAPLM.IS','KAREL.IS','KARSN.IS','KARTN.IS','KARYE.IS','KATMR.IS','KAYSE.IS','KBORU.IS','KCAER.IS','KCHOL.IS','KENT.IS','KERVN.IS','KERVT.IS','KFEIN.IS','KGYO.IS','KIMMR.IS','KLGYO.IS','KLKIM.IS','KLMSN.IS','KLNMA.IS','KLRHO.IS','KLSER.IS','KLSYN.IS','KMPUR.IS','KNFRT.IS','KONKA.IS','KONTR.IS','KONYA.IS','KOPOL.IS','KORDS.IS','KOZAA.IS','KOZAL.IS','KRDMA.IS','KRDMB.IS','KRDMD.IS','KRGYO.IS','KRONT.IS','KRPLS.IS','KRSTL.IS','KRTEK.IS','KRVGD.IS','KSTUR.IS','KTLEV.IS','KTSKR.IS','KUTPO.IS','KUVVA.IS','KUYAS.IS','KZBGY.IS','KZGYO.IS','LIDER.IS','LIDFA.IS','LINK.IS','LKMNH.IS','LMKDC.IS','LOGO.IS','LRSHO.IS','LUKSK.IS','MAALT.IS','MACKO.IS','MAGEN.IS','MAKIM.IS','MAKTK.IS','MANAS.IS','MARBL.IS','MARKA.IS','MARTI.IS','MAVI.IS','MEDTR.IS','MEGAP.IS','MEGMT.IS','MEKAG.IS','MEPET.IS','MERCN.IS','MERIT.IS','MERKO.IS','METRO.IS','METUR.IS','MGROS.IS','MHRGY.IS','MIATK.IS','MIPAZ.IS','MMCAS.IS','MNDRS.IS','MNDTR.IS','MOBTL.IS','MOGAN.IS','MPARK.IS','MRGYO.IS','MRSHL.IS','MSGYO.IS','MTRKS.IS','MTRYO.IS','MZHLD.IS','NATEN.IS','NETAS.IS','NIBAS.IS','NTGAZ.IS','NTHOL.IS','NUGYO.IS','NUHCM.IS','OBAMS.IS','OBASE.IS','ODAS.IS','ODINE.IS','OFSYM.IS','ONCSM.IS','ORCAY.IS','ORGE.IS','ORMA.IS','OSMEN.IS','OSTIM.IS','OTKAR.IS','OTTO.IS','OYAKC.IS','OYAYO.IS','OYLUM.IS','OYYAT.IS','OZGYO.IS','OZKGY.IS','OZRDN.IS','OZSUB.IS','PAGYO.IS','PAMEL.IS','PAPIL.IS','PARSN.IS','PASEU.IS','PATEK.IS','PCILT.IS','PEGYO.IS','PEKGY.IS','PENGD.IS','PENTA.IS','PETKM.IS','PETUN.IS','PGSUS.IS','PINSU.IS','PKART.IS','PKENT.IS','PLTUR.IS','PNLSN.IS','PNSUT.IS','POLHO.IS','POLTK.IS','PRDGS.IS','PRKAB.IS','PRKME.IS','PRZMA.IS','PSDTC.IS','PSGYO.IS','QNBFB.IS','QNBFL.IS','QUAGR.IS','RALYH.IS','RAYSG.IS','REEDR.IS','RNPOL.IS','RODRG.IS','RTALB.IS','RUBNS.IS','RYGYO.IS','RYSAS.IS','SAFKR.IS','SAHOL.IS','SAMAT.IS','SANEL.IS','SANFM.IS','SANKO.IS','SARKY.IS','SASA.IS','SAYAS.IS','SDTTR.IS','SEGYO.IS','SEKFK.IS','SEKUR.IS','SELEC.IS','SELGD.IS','SELVA.IS','SEYKM.IS','SILVR.IS','SISE.IS','SKBNK.IS','SKTAS.IS','SKYLP.IS','SKYMD.IS','SMART.IS','SMRTG.IS','SNGYO.IS','SNICA.IS','SNKRN.IS','SNPAM.IS','SODSN.IS','SOKE.IS','SOKM.IS','SONME.IS','SRVGY.IS','SUMAS.IS','SUNTK.IS','SURGY.IS','SUWEN.IS','TABGD.IS','TARKM.IS','TATEN.IS','TATGD.IS','TAVHL.IS','TBORG.IS','TCELL.IS','TDGYO.IS','TEKTU.IS','TERA.IS','TETMT.IS','TEZOL.IS','TGSAS.IS','THYAO.IS','TKFEN.IS','TKNSA.IS','TLMAN.IS','TMPOL.IS','TMSN.IS','TNZTP.IS','TOASO.IS','TRCAS.IS','TRGYO.IS','TRILC.IS','TSGYO.IS','TSKB.IS','TSPOR.IS','TTKOM.IS','TTRAK.IS','TUCLK.IS','TUKAS.IS','TUPRS.IS','TUREX.IS','TURGG.IS','TURSG.IS','UFUK.IS','ULAS.IS','ULKER.IS','ULUFA.IS','ULUSE.IS','ULUUN.IS','UMPAS.IS','UNLU.IS','USAK.IS','USDTR.IS','UZERB.IS','VAKBN.IS','VAKFN.IS','VAKKO.IS','VANGD.IS','VBTYZ.IS','VERTU.IS','VERUS.IS','VESBE.IS','VESTL.IS','VKFYO.IS','VKGYO.IS','VKING.IS','VRGYO.IS','X030S.IS','X100S.IS','XBANA.IS','XBANK.IS','XBLSM.IS','XELKT.IS','XFINK.IS','XGIDA.IS','XGMYO.IS','XHARZ.IS','XHOLD.IS','XILTM.IS','XINSA.IS','XKAGT.IS','XKMYA.IS','XKOBI.IS','XKURY.IS','XMADN.IS','XMANA.IS','XMESY.IS','XSADA.IS','XSANK.IS','XSANT.IS','XSBAL.IS','XSBUR.IS','XSDNZ.IS','XSGRT.IS','XSIST.IS','XSIZM.IS','XSKAY.IS','XSKOC.IS','XSKON.IS','XSPOR.IS','XSTKR.IS','XTAST.IS','XTCRT.IS','XTEKS.IS','XTM25.IS','XTMTU.IS','XTRZM.IS','XTUMY.IS','XU030.IS','XU050.IS','XU100.IS','XUHIZ.IS','XULAS.IS','XUMAL.IS','XUSIN.IS','XUSRD.IS','XUTEK.IS','XUTUM.IS','XYLDZ.IS','XYORT.IS','XYUZO.IS','YAPRK.IS','YATAS.IS','YAYLA.IS','YBTAS.IS','YEOTK.IS','YESIL.IS','YGGYO.IS','YGYO.IS','YKBNK.IS','YKSLN.IS','YONGA.IS','YUNSA.IS','YYAPI.IS','YYLGD.IS','Z30EA.IS','Z30KE.IS','Z30KP.IS','ZEDUR.IS','ZELOT.IS','ZGOLD.IS','ZOREN.IS','ZPBDL.IS','ZPLIB.IS','ZPT10.IS','ZPX30.IS','ZRE20.IS','ZRGYO.IS','ZTM15.IS']
    # Download the stock data
    yf_stock_daily_data = yf.download(stocks, start='2004-03-07')

    for stock in stocks:
        # Get the closing prices for the stock
        data = yf_stock_daily_data['Close'][stock].dropna()
        
        today_data = data.loc[data.index.strftime('%Y-%m-%d') == '2024-04-16']
        
        for i in range(len(today_data)):
            # Get the date and closing price
            date = today_data.index[i].strftime('%Y-%m-%d')

            close = today_data[i]

            # Get the date 1 week ago or the latest date before that
            one_week_ago = today_data.index[i] - pd.DateOffset(weeks=1)
            last_valid_date_one_week = data.index.asof(one_week_ago)

            # Calculate the 1-week increase
            if pd.notnull(last_valid_date_one_week):
                increase_1w = (close - data[last_valid_date_one_week]) / data[last_valid_date_one_week]
            else:
                increase_1w = None

            one_day_ago = today_data.index[i] - pd.DateOffset(days=1)
            last_valid_date_one_day = data.index.asof(one_day_ago)

            # Calculate the 1-day increase
            if pd.notnull(last_valid_date_one_day):
                increase_1d = (close - data[last_valid_date_one_day]) / data[last_valid_date_one_day]
            else:
                increase_1d = None

            one_month_ago = today_data.index[i] - pd.DateOffset(months=1)
            last_valid_date_one_month = data.index.asof(one_month_ago)

            # Calculate the 1-month increase
            if pd.notnull(last_valid_date_one_month):
                increase_1m = (close - data[last_valid_date_one_month]) / data[last_valid_date_one_month]
            else:
                increase_1m = None
            
            three_month_ago = today_data.index[i] - pd.DateOffset(months=3)
            last_valid_date_three_month = data.index.asof(three_month_ago)

            # Calculate the 3-month increase
            if pd.notnull(last_valid_date_three_month):
                increase_3m = (close - data[last_valid_date_three_month]) / data[last_valid_date_three_month]
            else:
                increase_3m = None

            six_month_ago = today_data.index[i] - pd.DateOffset(months=6)
            last_valid_date_six_month = data.index.asof(six_month_ago)

            # Calculate the 6-month increase
            if pd.notnull(last_valid_date_six_month):
                increase_6m = (close - data[last_valid_date_six_month]) / data[last_valid_date_six_month]
            else:
                increase_6m = None

            one_year_ago = today_data.index[i] - pd.DateOffset(years=1)
            last_valid_date_one_year = data.index.asof(one_year_ago)

            # Calculate the 1-year increase
            if pd.notnull(last_valid_date_one_year):
                increase_1y = (close - data[last_valid_date_one_year]) / data[last_valid_date_one_year]
            else:
                increase_1y = None

            five_year_ago = today_data.index[i] - pd.DateOffset(years=5)
            last_valid_date_five_year = data.index.asof(five_year_ago)

            # Calculate the 5-year increase
            if pd.notnull(last_valid_date_five_year):
                increase_5y = (close - data[last_valid_date_five_year]) / data[last_valid_date_five_year]
            else:
                increase_5y = None



            # Insert the data into the database
            try:

                conn.execute('''
                    INSERT INTO StockData (stock_name, date, interval, close, increase_1d, increase_1w, increase_1m, increase_3m, increase_6m, increase_1y, increase_5y)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (stock, date, '1d', close, increase_1d, increase_1w, increase_1m, increase_3m, increase_6m, increase_1y, increase_5y))
            except Exception as e:
                print(e)
                print(stock, date, '1d', close, increase_1d, increase_1w, increase_1m, increase_3m, increase_6m, increase_1y, increase_5y)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# save_stocks_with_increase_rates()

def save_to_json2():
    import concurrent.futures
    stocks = ['A1CAP.IS','ACSEL.IS', 'ADEL.IS', 'ADESE.IS','ADGYO.IS','AEFES.IS','AFYON.IS','XU100.IS']
    
    def get_ticker_data(stock):
        tickerData = yf.Ticker(stock+'.IS')
        tickerDf = tickerData.history(period='1d', start='2023-7-4', end='2024-7-4')
        return stock, tickerDf.to_dict()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(get_ticker_data, stocks)

    combined_data = {}
    for stock, data in results:
        combined_data[stock] = data
    # # Write the combined data to a JSON file
    # with open('data.json', 'r') as file:
    #     existing_data = json.load(file)
    #     existing_data.update(data_for_json)

    # with open('data.json', 'w') as file:
    #     json.dump(existing_data, file)


def save_stocks_to_json():
    today = datetime.now().strftime("%Y-%m-%d")

    one_year_earlier = (parse(today) - timedelta(days=370)).strftime("%Y-%m-%d")
    stocks = ['A1CAP.IS','ACSEL.IS', 'ADEL.IS', 'ADESE.IS','ADGYO.IS','AEFES.IS','AFYON.IS','XU100.IS']
              #'AGESA.IS','AGHOL.IS','AGROT.IS','AGYO.IS','AHGAZ.IS','AKBNK.IS','AKCNS.IS','AKENR.IS','AKFGY.IS','AKFYE.IS','AKGRT.IS','AKMGY.IS','AKSA.IS','AKSEN.IS','AKSGY.IS','AKSUE.IS','AKYHO.IS','ALARK.IS','ALBRK.IS','ALCAR.IS','ALCTL.IS','ALFAS.IS','ALGYO.IS','ALKA.IS','ALKIM.IS','ALMAD.IS','ALVES.IS','ANELE.IS','ANGEN.IS','ANHYT.IS','ANSGR.IS','ARASE.IS','ARCLK.IS','ARDYZ.IS','ARENA.IS','ARSAN.IS','ARTMS.IS','ARZUM.IS','ASELS.IS','ASGYO.IS','ASTOR.IS','ASUZU.IS','ATAGY.IS','ATAKP.IS','ATATP.IS','ATEKS.IS','ATLAS.IS','ATSYH.IS','AVGYO.IS','AVHOL.IS','AVOD.IS','AVPGY.IS','AVTUR.IS','AYCES.IS','AYDEM.IS','AYEN.IS','AYES.IS','AYGAZ.IS','AZTEK.IS','BAGFS.IS','BAKAB.IS','BALAT.IS','BANVT.IS','BARMA.IS','BASCM.IS','BASGZ.IS','BAYRK.IS','BEGYO.IS','BERA.IS','BEYAZ.IS','BFREN.IS','BIENY.IS','BIGCH.IS','BIMAS.IS','BINHO.IS','BIOEN.IS','BIZIM.IS','BJKAS.IS','BLCYT.IS','BMSCH.IS','BMSTL.IS','BNTAS.IS','BOBET.IS','BORLS.IS','BORSK.IS','BOSSA.IS','BRISA.IS','BRKO.IS','BRKSN.IS','BRKVY.IS','BRLSM.IS','BRMEN.IS','BRSAN.IS','BRYAT.IS','BSOKE.IS','BTCIM.IS','BUCIM.IS','BURCE.IS','BURVA.IS','BVSAN.IS','BYDNR.IS','CANTE.IS','CASA.IS','CATES.IS','CCOLA.IS','CELHA.IS','CEMAS.IS','CEMTS.IS','CEOEM.IS','CIMSA.IS','CLEBI.IS','CMBTN.IS','CMENT.IS','CONSE.IS','COSMO.IS','CRDFA.IS','CRFSA.IS','CUSAN.IS','CVKMD.IS','CWENE.IS','DAGHL.IS','DAGI.IS','DAPGM.IS','DARDL.IS','DENGE.IS','DERHL.IS','DERIM.IS','DESA.IS','DESPC.IS','DEVA.IS','DGATE.IS','DGGYO.IS','DGNMO.IS','DIRIT.IS','DITAS.IS','DJIST.IS','DMRGD.IS','DMSAS.IS','DNISI.IS','DOAS.IS','DOBUR.IS','DOCO.IS','DOFER.IS','DOGUB.IS','DOHOL.IS','DOKTA.IS','DURDO.IS','DYOBY.IS','DZGYO.IS','EBEBK.IS','ECILC.IS','ECZYT.IS','EDATA.IS','EDIP.IS','EGEEN.IS','EGEPO.IS','EGGUB.IS','EGPRO.IS','EGSER.IS','EKGYO.IS','EKIZ.IS','EKOS.IS','EKSUN.IS','ELITE.IS','EMKEL.IS','EMNIS.IS','ENERY.IS','ENJSA.IS','ENKAI.IS','ENSRI.IS','EPLAS.IS','ERBOS.IS','ERCB.IS','EREGL.IS','ERSU.IS','ESCAR.IS','ESCOM.IS','ESEN.IS','ETILR.IS','ETYAT.IS','EUHOL.IS','EUKYO.IS','EUPWR.IS','EUREN.IS','EUYO.IS','EYGYO.IS','FADE.IS','FENER.IS','FLAP.IS','FMIZP.IS','FONET.IS','FORMT.IS','FORTE.IS','FRIGO.IS','FROTO.IS','FZLGY.IS','GARAN.IS','GARFA.IS','GEDIK.IS','GEDZA.IS','GENIL.IS','GENTS.IS','GEREL.IS','GESAN.IS','GIPTA.IS','GLBMD.IS','GLCVY.IS','GLDTR.IS','GLRYH.IS','GLYHO.IS','GMSTR.IS','GMTAS.IS','GOKNR.IS','GOLTS.IS','GOODY.IS','GOZDE.IS','GRNYO.IS','GRSEL.IS','GRTRK.IS','GSDDE.IS','GSDHO.IS','GSRAY.IS','GUBRF.IS','GWIND.IS','GZNMI.IS','HALKB.IS','HATEK.IS','HATSN.IS','HDFGS.IS','HEDEF.IS','HEKTS.IS','HKTM.IS','HLGYO.IS','HTTBT.IS','HUBVC.IS','HUNER.IS','HURGZ.IS','ICBCT.IS','ICUGS.IS','IDGYO.IS','IEYHO.IS','IHAAS.IS','IHEVA.IS','IHGZT.IS','IHLAS.IS','IHLGM.IS','IHYAY.IS','IMASM.IS','INDES.IS','INFO.IS','INGRM.IS','INTEM.IS','INVEO.IS','INVES.IS','IPEKE.IS','ISATR.IS','ISBIR.IS','ISBTR.IS','ISCTR.IS','ISDMR.IS','ISFIN.IS','ISGSY.IS','ISGYO.IS','ISIST.IS','ISKPL.IS','ISKUR.IS','ISMEN.IS','ISSEN.IS','ISYAT.IS','IZENR.IS','IZFAS.IS','IZINV.IS','IZMDC.IS','JANTS.IS','KAPLM.IS','KAREL.IS','KARSN.IS','KARTN.IS','KARYE.IS','KATMR.IS','KAYSE.IS','KBORU.IS','KCAER.IS','KCHOL.IS','KENT.IS','KERVN.IS','KERVT.IS','KFEIN.IS','KGYO.IS','KIMMR.IS','KLGYO.IS','KLKIM.IS','KLMSN.IS','KLNMA.IS','KLRHO.IS','KLSER.IS','KLSYN.IS','KMPUR.IS','KNFRT.IS','KONKA.IS','KONTR.IS','KONYA.IS','KOPOL.IS','KORDS.IS','KOZAA.IS','KOZAL.IS','KRDMA.IS','KRDMB.IS','KRDMD.IS','KRGYO.IS','KRONT.IS','KRPLS.IS','KRSTL.IS','KRTEK.IS','KRVGD.IS','KSTUR.IS','KTLEV.IS','KTSKR.IS','KUTPO.IS','KUVVA.IS','KUYAS.IS','KZBGY.IS','KZGYO.IS','LIDER.IS','LIDFA.IS','LINK.IS','LKMNH.IS','LMKDC.IS','LOGO.IS','LRSHO.IS','LUKSK.IS','MAALT.IS','MACKO.IS','MAGEN.IS','MAKIM.IS','MAKTK.IS','MANAS.IS','MARBL.IS','MARKA.IS','MARTI.IS','MAVI.IS','MEDTR.IS','MEGAP.IS','MEGMT.IS','MEKAG.IS','MEPET.IS','MERCN.IS','MERIT.IS','MERKO.IS','METRO.IS','METUR.IS','MGROS.IS','MHRGY.IS','MIATK.IS','MIPAZ.IS','MMCAS.IS','MNDRS.IS','MNDTR.IS','MOBTL.IS','MOGAN.IS','MPARK.IS','MRGYO.IS','MRSHL.IS','MSGYO.IS','MTRKS.IS','MTRYO.IS','MZHLD.IS','NATEN.IS','NETAS.IS','NIBAS.IS','NTGAZ.IS','NTHOL.IS','NUGYO.IS','NUHCM.IS','OBAMS.IS','OBASE.IS','ODAS.IS','ODINE.IS','OFSYM.IS','ONCSM.IS','ORCAY.IS','ORGE.IS','ORMA.IS','OSMEN.IS','OSTIM.IS','OTKAR.IS','OTTO.IS','OYAKC.IS','OYAYO.IS','OYLUM.IS','OYYAT.IS','OZGYO.IS','OZKGY.IS','OZRDN.IS','OZSUB.IS','PAGYO.IS','PAMEL.IS','PAPIL.IS','PARSN.IS','PASEU.IS','PATEK.IS','PCILT.IS','PEGYO.IS','PEKGY.IS','PENGD.IS','PENTA.IS','PETKM.IS','PETUN.IS','PGSUS.IS','PINSU.IS','PKART.IS','PKENT.IS','PLTUR.IS','PNLSN.IS','PNSUT.IS','POLHO.IS','POLTK.IS','PRDGS.IS','PRKAB.IS','PRKME.IS','PRZMA.IS','PSDTC.IS','PSGYO.IS','QNBFB.IS','QNBFL.IS','QUAGR.IS','RALYH.IS','RAYSG.IS','REEDR.IS','RNPOL.IS','RODRG.IS','RTALB.IS','RUBNS.IS','RYGYO.IS','RYSAS.IS','SAFKR.IS','SAHOL.IS','SAMAT.IS','SANEL.IS','SANFM.IS','SANKO.IS','SARKY.IS','SASA.IS','SAYAS.IS','SDTTR.IS','SEGYO.IS','SEKFK.IS','SEKUR.IS','SELEC.IS','SELGD.IS','SELVA.IS','SEYKM.IS','SILVR.IS','SISE.IS','SKBNK.IS','SKTAS.IS','SKYLP.IS','SKYMD.IS','SMART.IS','SMRTG.IS','SNGYO.IS','SNICA.IS','SNKRN.IS','SNPAM.IS','SODSN.IS','SOKE.IS','SOKM.IS','SONME.IS','SRVGY.IS','SUMAS.IS','SUNTK.IS','SURGY.IS','SUWEN.IS','TABGD.IS','TARKM.IS','TATEN.IS','TATGD.IS','TAVHL.IS','TBORG.IS','TCELL.IS','TDGYO.IS','TEKTU.IS','TERA.IS','TETMT.IS','TEZOL.IS','TGSAS.IS','THYAO.IS','TKFEN.IS','TKNSA.IS','TLMAN.IS','TMPOL.IS','TMSN.IS','TNZTP.IS','TOASO.IS','TRCAS.IS','TRGYO.IS','TRILC.IS','TSGYO.IS','TSKB.IS','TSPOR.IS','TTKOM.IS','TTRAK.IS','TUCLK.IS','TUKAS.IS','TUPRS.IS','TUREX.IS','TURGG.IS','TURSG.IS','UFUK.IS','ULAS.IS','ULKER.IS','ULUFA.IS','ULUSE.IS','ULUUN.IS','UMPAS.IS','UNLU.IS','USAK.IS','USDTR.IS','UZERB.IS','VAKBN.IS','VAKFN.IS','VAKKO.IS','VANGD.IS','VBTYZ.IS','VERTU.IS','VERUS.IS','VESBE.IS','VESTL.IS','VKFYO.IS','VKGYO.IS','VKING.IS','VRGYO.IS','X030S.IS','X100S.IS','XBANA.IS','XBANK.IS','XBLSM.IS','XELKT.IS','XFINK.IS','XGIDA.IS','XGMYO.IS','XHARZ.IS','XHOLD.IS','XILTM.IS','XINSA.IS','XKAGT.IS','XKMYA.IS','XKOBI.IS','XKURY.IS','XMADN.IS','XMANA.IS','XMESY.IS','XSADA.IS','XSANK.IS','XSANT.IS','XSBAL.IS','XSBUR.IS','XSDNZ.IS','XSGRT.IS','XSIST.IS','XSIZM.IS','XSKAY.IS','XSKOC.IS','XSKON.IS','XSPOR.IS','XSTKR.IS','XTAST.IS','XTCRT.IS','XTEKS.IS','XTM25.IS','XTMTU.IS','XTRZM.IS','XTUMY.IS','XU030.IS','XU050.IS','XU100.IS','XUHIZ.IS','XULAS.IS','XUMAL.IS','XUSIN.IS','XUSRD.IS','XUTEK.IS','XUTUM.IS','XYLDZ.IS','XYORT.IS','XYUZO.IS','YAPRK.IS','YATAS.IS','YAYLA.IS','YBTAS.IS','YEOTK.IS','YESIL.IS','YGGYO.IS','YGYO.IS','YKBNK.IS','YKSLN.IS','YONGA.IS','YUNSA.IS','YYAPI.IS','YYLGD.IS','Z30EA.IS','Z30KE.IS','Z30KP.IS','ZEDUR.IS','ZELOT.IS','ZGOLD.IS','ZOREN.IS','ZPBDL.IS','ZPLIB.IS','ZPT10.IS','ZPX30.IS','ZRE20.IS','ZRGYO.IS','ZTM15.IS']
    all_data = yf.download(stocks, start=one_year_earlier, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
    # Convert the dataframe to JSON
    json_data = all_data.to_json(orient='index')

    # Convert the JSON back to a dataframe
    df_from_json = pd.read_json(json_data, orient='index')


    print(df_from_json)
    print(all_data.equals(df_from_json))

    json_data = all_data.to_json(orient='split')

    # Convert the JSON back to a dataframe
    df_from_json = pd.read_json(json_data, orient='split')
    print(all_data.equals(df_from_json))
    
    # json_data = all_data.to_json(orient='table')
    # # Convert the JSON back to a dataframe
    # df_from_json = pd.read_json(json_data, orient='table')
    # print(all_data.equals(df_from_json))

    json_data = all_data.to_json(orient='records')
    # Convert the JSON back to a dataframe
    df_from_json = pd.read_json(json_data, orient='records')
    print(all_data.equals(df_from_json))
    
    json_data = all_data.to_json("plain.json")
    # Convert the JSON back to a dataframe
    df_from_json = pd.read_json("plain.json", orient='index')
    print(all_data.equals(df_from_json))

    


# save_stocks_to_json()
