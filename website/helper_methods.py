from datetime import timedelta
from .models import StockData, db, Holidays
import yfinance as yf
from datetime import datetime
from dateutil.parser import parse

def data_exists_in_db():
    """
    Check if the database has any data
    """

    return StockData.query.first() is not None

def fullfill_db():
    """
    Fill the database with the data of the last 5 years
    """
    print("LOG: fullfilling database")

    today = datetime.now().strftime("%Y-%m-%d")

    five_years_earlier = (parse(today) - timedelta(days=1850)).strftime("%Y-%m-%d")
    stocks = ['A1CAP.IS','ACSEL.IS', 'ADEL.IS', 'ADESE.IS','ADGYO.IS','AEFES.IS','AFYON.IS','AGESA.IS','AGHOL.IS','AGROT.IS','AGYO.IS','AHGAZ.IS','AKBNK.IS'
                      ,'XU100.IS']
    all_data = yf.download(stocks, start=five_years_earlier, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
    
    #region understand holidays and add to holidays table
    # get first date in data
    first_date = all_data.index[0].strftime("%Y-%m-%d")
    yesterday = (parse(today) - timedelta(days=1)).strftime("%Y-%m-%d")
    all_dates_in_data = set(all_data.index.strftime("%Y-%m-%d"))
    holiday_data = []
    # for from the first date to yesterday, check if there is a data
    for i in range((parse(yesterday) - parse(first_date)).days):
        date = (parse(first_date) + timedelta(days=i)).strftime("%Y-%m-%d") 
        # check if that date exists in the data
        if date not in all_dates_in_data:
            holiday_data.append(Holidays(date=date, is_holiday=True))
        else:
            holiday_data.append(Holidays(date=date, is_holiday=False))
    Holidays.add_all(holiday_data)
    #endregion
    
    
    stocks_data_to_add_to_db = []
    latest_day_in_data = all_data.index[-1].strftime("%Y-%m-%d")
    all_data_close = all_data['Close']
    for stock in stocks:
        for i, (date, close_price) in enumerate(all_data_close[stock].items()):
            # if the date is the latest date in the data, we will calculate the increase value
            datestr = date.strftime("%Y-%m-%d")
            if(latest_day_in_data == datestr):
                stock_data = StockData(stock_name=stock)
                stock_data.date = datestr
                stock_data.close = close_price
                previous_day_close = all_data['Close'][stock].iloc[i-1]
                increase_1d = (stock_data.close - previous_day_close) / previous_day_close
                stock_data.increase_1d = increase_1d
                previous_week_close = all_data['Close'][stock].iloc[i-7]
                stock_data.increase_1w = (stock_data.close - previous_week_close) / previous_week_close
                previous_month_close = all_data['Close'][stock].iloc[i-30]
                stock_data.increase_1m = (stock_data.close - previous_month_close) / previous_month_close
                previous_3m_close = all_data['Close'][stock].iloc[i-91]
                stock_data.increase_3m = (stock_data.close - previous_3m_close) / previous_3m_close
                previous_6m_close = all_data['Close'][stock].iloc[i-182]
                stock_data.increase_6m = (stock_data.close - previous_6m_close) / previous_6m_close
                previous_1y_close = all_data['Close'][stock].iloc[i-365]
                stock_data.increase_1y = (stock_data.close - previous_1y_close) / previous_1y_close
                previous_5y_close = all_data['Close'][stock].iloc[i-1826]
                stock_data.increase_5y = (stock_data.close - previous_5y_close) / previous_5y_close
                stocks_data_to_add_to_db.append(stock_data)
            else:
                stock_data = StockData(stock_name=stock)
                stock_data.date = datestr
                # stock_data.interval = "1d"
                stock_data.close = close_price
                stocks_data_to_add_to_db.append(stock_data)
    StockData.add_all(stocks_data_to_add_to_db)
    print("LOG: database fullfilled")

def update_stock_data_in_db(app, update_even_if_holiday):

    # We need to check if the database needs an update, because this method is called by different sources
    # if today is holiday, we will not update the database 
    # but if the request is coming from the user, we have to update the datase

    with app.app_context():
        try:
            if(not data_exists_in_db()):
                fullfill_db()
            
            if (not update_even_if_holiday and (is_holiday(datetime.now().strftime("%Y-%m-%d") or not is_working_hour(datetime.now().hour, datetime.now().minute)))):
                return
            
            # last_working_day = datetime.now().strftime("%Y-%m-%d") # initially today
            # if( (datetime.now().hour < 10 or (datetime.now().hour == 10 and datetime.now().minute < 16))): # if morning hours, we will get the data of yesterday
            #     last_working_day = (parse(last_working_day) - timedelta(days=1)).strftime("%Y-%m-%d")
            # if (is_holiday(last_working_day)): # if today is holiday, we will get the data of the last working day
            #     last_working_day = get_last_work_day(last_working_day)
            # one_day_earlier = (parse(last_working_day) - timedelta(days=1)).strftime("%Y-%m-%d")
            # if(is_holiday(one_day_earlier)):
            #     one_day_earlier = get_last_work_day(one_day_earlier) # for one day, we will return the difference between the last working day and the working day before it
            # today = datetime.now().strftime("%Y-%m-%d")

            # # for other dates, we will return the difference for specific days
            # one_week_earlier = get_next_work_day((parse(today) - timedelta(days=7)).strftime("%Y-%m-%d"))
            # one_month_earlier = get_next_work_day((parse(today) - timedelta(days=30)).strftime("%Y-%m-%d"))
            # six_months_earlier = get_next_work_day((parse(today) - timedelta(days=183)).strftime("%Y-%m-%d"))
            # one_year_earlier = get_next_work_day((parse(today) - timedelta(days=365)).strftime("%Y-%m-%d"))
            # five_years_earlier = get_next_work_day((parse(today) - timedelta(days=1826)).strftime("%Y-%m-%d"))
            # twenty_years_earlier = get_next_work_day((parse(today) - timedelta(days=7304)).strftime("%Y-%m-%d"))

            # stocks = ['A1CAP.IS','ACSEL.IS', 'ADEL.IS', 'ADESE.IS','ADGYO.IS','AEFES.IS','AFYON.IS','AGESA.IS','AGHOL.IS','AGROT.IS','AGYO.IS','AHGAZ.IS','AKBNK.IS'
            #           ,'XU100.IS'] #TODO: check the db first
            # #,'AKCNS.IS','AKENR.IS','AKFGY.IS','AKFYE.IS','AKGRT.IS','AKMGY.IS','AKSA.IS','AKSEN.IS','AKSGY.IS','AKSUE.IS','AKYHO.IS','ALARK.IS','ALBRK.IS','ALCAR.IS','ALCTL.IS','ALFAS.IS','ALGYO.IS','ALKA.IS','ALKIM.IS','ALMAD.IS','ALVES.IS','ANELE.IS','ANGEN.IS','ANHYT.IS','ANSGR.IS','ARASE.IS','ARCLK.IS','ARDYZ.IS','ARENA.IS','ARSAN.IS','ARTMS.IS','ARZUM.IS','ASELS.IS','ASGYO.IS','ASTOR.IS','ASUZU.IS','ATAGY.IS','ATAKP.IS','ATATP.IS','ATEKS.IS','ATLAS.IS','ATSYH.IS','AVGYO.IS','AVHOL.IS','AVOD.IS','AVPGY.IS','AVTUR.IS','AYCES.IS','AYDEM.IS','AYEN.IS','AYES.IS','AYGAZ.IS','AZTEK.IS','BAGFS.IS','BAKAB.IS','BALAT.IS','BANVT.IS','BARMA.IS','BASCM.IS','BASGZ.IS','BAYRK.IS','BEGYO.IS','BERA.IS','BEYAZ.IS','BFREN.IS','BIENY.IS','BIGCH.IS','BIMAS.IS','BINHO.IS','BIOEN.IS','BIZIM.IS','BJKAS.IS','BLCYT.IS','BMSCH.IS','BMSTL.IS','BNTAS.IS','BOBET.IS','BORLS.IS','BORSK.IS','BOSSA.IS','BRISA.IS','BRKO.IS','BRKSN.IS','BRKVY.IS','BRLSM.IS','BRMEN.IS','BRSAN.IS','BRYAT.IS','BSOKE.IS','BTCIM.IS','BUCIM.IS','BURCE.IS','BURVA.IS','BVSAN.IS','BYDNR.IS','CANTE.IS','CASA.IS','CATES.IS','CCOLA.IS','CELHA.IS','CEMAS.IS','CEMTS.IS','CEOEM.IS','CIMSA.IS','CLEBI.IS','CMBTN.IS','CMENT.IS','CONSE.IS','COSMO.IS','CRDFA.IS','CRFSA.IS','CUSAN.IS','CVKMD.IS','CWENE.IS','DAGHL.IS','DAGI.IS','DAPGM.IS','DARDL.IS','DENGE.IS','DERHL.IS','DERIM.IS','DESA.IS','DESPC.IS','DEVA.IS','DGATE.IS','DGGYO.IS','DGNMO.IS','DIRIT.IS','DITAS.IS','DJIST.IS','DMRGD.IS','DMSAS.IS','DNISI.IS','DOAS.IS','DOBUR.IS','DOCO.IS','DOFER.IS','DOGUB.IS','DOHOL.IS','DOKTA.IS','DURDO.IS','DYOBY.IS','DZGYO.IS','EBEBK.IS','ECILC.IS','ECZYT.IS','EDATA.IS','EDIP.IS','EGEEN.IS','EGEPO.IS','EGGUB.IS','EGPRO.IS','EGSER.IS','EKGYO.IS','EKIZ.IS','EKOS.IS','EKSUN.IS','ELITE.IS','EMKEL.IS','EMNIS.IS','ENERY.IS','ENJSA.IS','ENKAI.IS','ENSRI.IS','EPLAS.IS','ERBOS.IS','ERCB.IS','EREGL.IS','ERSU.IS','ESCAR.IS','ESCOM.IS','ESEN.IS','ETILR.IS','ETYAT.IS','EUHOL.IS','EUKYO.IS','EUPWR.IS','EUREN.IS','EUYO.IS','EYGYO.IS','FADE.IS','FENER.IS','FLAP.IS','FMIZP.IS','FONET.IS','FORMT.IS','FORTE.IS','FRIGO.IS','FROTO.IS','FZLGY.IS','GARAN.IS','GARFA.IS','GEDIK.IS','GEDZA.IS','GENIL.IS','GENTS.IS','GEREL.IS','GESAN.IS','GIPTA.IS','GLBMD.IS','GLCVY.IS','GLDTR.IS','GLRYH.IS','GLYHO.IS','GMSTR.IS','GMTAS.IS','GOKNR.IS','GOLTS.IS','GOODY.IS','GOZDE.IS','GRNYO.IS','GRSEL.IS','GRTRK.IS','GSDDE.IS','GSDHO.IS','GSRAY.IS','GUBRF.IS','GWIND.IS','GZNMI.IS','HALKB.IS','HATEK.IS','HATSN.IS','HDFGS.IS','HEDEF.IS','HEKTS.IS','HKTM.IS','HLGYO.IS','HTTBT.IS','HUBVC.IS','HUNER.IS','HURGZ.IS','ICBCT.IS','ICUGS.IS','IDGYO.IS','IEYHO.IS','IHAAS.IS','IHEVA.IS','IHGZT.IS','IHLAS.IS','IHLGM.IS','IHYAY.IS','IMASM.IS','INDES.IS','INFO.IS','INGRM.IS','INTEM.IS','INVEO.IS','INVES.IS','IPEKE.IS','ISATR.IS','ISBIR.IS','ISBTR.IS','ISCTR.IS','ISDMR.IS','ISFIN.IS','ISGSY.IS','ISGYO.IS','ISIST.IS','ISKPL.IS','ISKUR.IS','ISMEN.IS','ISSEN.IS','ISYAT.IS','IZENR.IS','IZFAS.IS','IZINV.IS','IZMDC.IS','JANTS.IS','KAPLM.IS','KAREL.IS','KARSN.IS','KARTN.IS','KARYE.IS','KATMR.IS','KAYSE.IS','KBORU.IS','KCAER.IS','KCHOL.IS','KENT.IS','KERVN.IS','KERVT.IS','KFEIN.IS','KGYO.IS','KIMMR.IS','KLGYO.IS','KLKIM.IS','KLMSN.IS','KLNMA.IS','KLRHO.IS','KLSER.IS','KLSYN.IS','KMPUR.IS','KNFRT.IS','KONKA.IS','KONTR.IS','KONYA.IS','KOPOL.IS','KORDS.IS','KOZAA.IS','KOZAL.IS','KRDMA.IS','KRDMB.IS','KRDMD.IS','KRGYO.IS','KRONT.IS','KRPLS.IS','KRSTL.IS','KRTEK.IS','KRVGD.IS','KSTUR.IS','KTLEV.IS','KTSKR.IS','KUTPO.IS','KUVVA.IS','KUYAS.IS','KZBGY.IS','KZGYO.IS','LIDER.IS','LIDFA.IS','LINK.IS','LKMNH.IS','LMKDC.IS','LOGO.IS','LRSHO.IS','LUKSK.IS','MAALT.IS','MACKO.IS','MAGEN.IS','MAKIM.IS','MAKTK.IS','MANAS.IS','MARBL.IS','MARKA.IS','MARTI.IS','MAVI.IS','MEDTR.IS','MEGAP.IS','MEGMT.IS','MEKAG.IS','MEPET.IS','MERCN.IS','MERIT.IS','MERKO.IS','METRO.IS','METUR.IS','MGROS.IS','MHRGY.IS','MIATK.IS','MIPAZ.IS','MMCAS.IS','MNDRS.IS','MNDTR.IS','MOBTL.IS','MOGAN.IS','MPARK.IS','MRGYO.IS','MRSHL.IS','MSGYO.IS','MTRKS.IS','MTRYO.IS','MZHLD.IS','NATEN.IS','NETAS.IS','NIBAS.IS','NTGAZ.IS','NTHOL.IS','NUGYO.IS','NUHCM.IS','OBAMS.IS','OBASE.IS','ODAS.IS','ODINE.IS','OFSYM.IS','ONCSM.IS','ORCAY.IS','ORGE.IS','ORMA.IS','OSMEN.IS','OSTIM.IS','OTKAR.IS','OTTO.IS','OYAKC.IS','OYAYO.IS','OYLUM.IS','OYYAT.IS','OZGYO.IS','OZKGY.IS','OZRDN.IS','OZSUB.IS','PAGYO.IS','PAMEL.IS','PAPIL.IS','PARSN.IS','PASEU.IS','PATEK.IS','PCILT.IS','PEGYO.IS','PEKGY.IS','PENGD.IS','PENTA.IS','PETKM.IS','PETUN.IS','PGSUS.IS','PINSU.IS','PKART.IS','PKENT.IS','PLTUR.IS','PNLSN.IS','PNSUT.IS','POLHO.IS','POLTK.IS','PRDGS.IS','PRKAB.IS','PRKME.IS','PRZMA.IS','PSDTC.IS','PSGYO.IS','QNBFB.IS','QNBFL.IS','QUAGR.IS','RALYH.IS','RAYSG.IS','REEDR.IS','RNPOL.IS','RODRG.IS','RTALB.IS','RUBNS.IS','RYGYO.IS','RYSAS.IS','SAFKR.IS','SAHOL.IS','SAMAT.IS','SANEL.IS','SANFM.IS','SANKO.IS','SARKY.IS','SASA.IS','SAYAS.IS','SDTTR.IS','SEGYO.IS','SEKFK.IS','SEKUR.IS','SELEC.IS','SELGD.IS','SELVA.IS','SEYKM.IS','SILVR.IS','SISE.IS','SKBNK.IS','SKTAS.IS','SKYLP.IS','SKYMD.IS','SMART.IS','SMRTG.IS','SNGYO.IS','SNICA.IS','SNKRN.IS','SNPAM.IS','SODSN.IS','SOKE.IS','SOKM.IS','SONME.IS','SRVGY.IS','SUMAS.IS','SUNTK.IS','SURGY.IS','SUWEN.IS','TABGD.IS','TARKM.IS','TATEN.IS','TATGD.IS','TAVHL.IS','TBORG.IS','TCELL.IS','TDGYO.IS','TEKTU.IS','TERA.IS','TETMT.IS','TEZOL.IS','TGSAS.IS','THYAO.IS','TKFEN.IS','TKNSA.IS','TLMAN.IS','TMPOL.IS','TMSN.IS','TNZTP.IS','TOASO.IS','TRCAS.IS','TRGYO.IS','TRILC.IS','TSGYO.IS','TSKB.IS','TSPOR.IS','TTKOM.IS','TTRAK.IS','TUCLK.IS','TUKAS.IS','TUPRS.IS','TUREX.IS','TURGG.IS','TURSG.IS','UFUK.IS','ULAS.IS','ULKER.IS','ULUFA.IS','ULUSE.IS','ULUUN.IS','UMPAS.IS','UNLU.IS','USAK.IS','USDTR.IS','UZERB.IS','VAKBN.IS','VAKFN.IS','VAKKO.IS','VANGD.IS','VBTYZ.IS','VERTU.IS','VERUS.IS','VESBE.IS','VESTL.IS','VKFYO.IS','VKGYO.IS','VKING.IS','VRGYO.IS','X030S.IS','X100S.IS','XBANA.IS','XBANK.IS','XBLSM.IS','XELKT.IS','XFINK.IS','XGIDA.IS','XGMYO.IS','XHARZ.IS','XHOLD.IS','XILTM.IS','XINSA.IS','XKAGT.IS','XKMYA.IS','XKOBI.IS','XKURY.IS','XMADN.IS','XMANA.IS','XMESY.IS','XSADA.IS','XSANK.IS','XSANT.IS','XSBAL.IS','XSBUR.IS','XSDNZ.IS','XSGRT.IS','XSIST.IS','XSIZM.IS','XSKAY.IS','XSKOC.IS','XSKON.IS','XSPOR.IS','XSTKR.IS','XTAST.IS','XTCRT.IS','XTEKS.IS','XTM25.IS','XTMTU.IS','XTRZM.IS','XTUMY.IS','XU030.IS','XU050.IS','XU100.IS','XUHIZ.IS','XULAS.IS','XUMAL.IS','XUSIN.IS','XUSRD.IS','XUTEK.IS','XUTUM.IS','XYLDZ.IS','XYORT.IS','XYUZO.IS','YAPRK.IS','YATAS.IS','YAYLA.IS','YBTAS.IS','YEOTK.IS','YESIL.IS','YGGYO.IS','YGYO.IS','YKBNK.IS','YKSLN.IS','YONGA.IS','YUNSA.IS','YYAPI.IS','YYLGD.IS','Z30EA.IS','Z30KE.IS','Z30KP.IS','ZEDUR.IS','ZELOT.IS','ZGOLD.IS','ZOREN.IS','ZPBDL.IS','ZPLIB.IS','ZPT10.IS','ZPX30.IS','ZRE20.IS','ZRGYO.IS','ZTM15.IS']
            # latest_data_from_yfinance = yf.download(stocks, start=last_working_day, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
            # data_from_db_for_one_day_earlier = StockData.query.filter(StockData.date == one_day_earlier).all()
            # data_from_db_for_one_week_earlier = StockData.query.filter(StockData.date == one_week_earlier).all()
            # data_from_db_for_one_month_earlier = StockData.query.filter(StockData.date == one_month_earlier).all()
            # data_from_db_for_six_months_earlier = StockData.query.filter(StockData.date == six_months_earlier).all()
            # data_from_db_for_one_year_earlier = StockData.query.filter(StockData.date == one_year_earlier).all()
            # data_from_db_for_five_years_earlier = StockData.query.filter(StockData.date == five_years_earlier).all()
            # data_from_db_for_twenty_years_earlier = StockData.query.filter(StockData.date == twenty_years_earlier).all()

            # if(len(data_from_db_for_one_day_earlier)==0):
            #     data_for_one_day_earlier = yf.download(stocks, start=one_day_earlier, end=(parse(one_day_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
            #     stock_data = StockData(stock_name="XU100.IS")
            #     StockData.add(stock_data)

            # data_for_one_week_earlier = yf.download(stocks, start=one_week_earlier, end=(parse(one_week_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
            # data_for_one_month_earlier = yf.download(stocks, start=one_month_earlier, end=(parse(one_month_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
            # data_for_six_months_earlier = yf.download(stocks, start=six_months_earlier, end=(parse(six_months_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
            # data_for_one_year_earlier = yf.download(stocks, start=one_year_earlier, end=(parse(one_year_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
            # data_for_five_years_earlier = yf.download(stocks, start=five_years_earlier, end=(parse(five_years_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
            # data_for_twenty_years_earlier = yf.download(stocks, start=twenty_years_earlier, end=(parse(twenty_years_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))

            # for stock in stocks:
                
            #     stock_data = StockData(stock_name=stock) #TODO: what if the data does not exist
            #     stock_data.date = today
            #     stock_data.interval = "1d"
            #     stock_data.close = latest_data_from_yfinance['Close'][stock].iloc[-1]
            #     stock_data.increase_1d = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_day_earlier['Close'][stock].iloc[-1]) / data_for_one_day_earlier['Close'][stock].iloc[-1]
            #     stock_data.increase_1w = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_week_earlier['Close'][stock].iloc[-1]) / data_for_one_week_earlier['Close'][stock].iloc[-1]
            #     stock_data.increase_1m = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_month_earlier['Close'][stock].iloc[-1]) / data_for_one_month_earlier['Close'][stock].iloc[-1]
            #     stock_data.increase_3m = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_six_months_earlier['Close'][stock].iloc[-1]) / data_for_six_months_earlier['Close'][stock].iloc[-1]
            #     stock_data.increase_6m = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_year_earlier['Close'][stock].iloc[-1]) / data_for_one_year_earlier['Close'][stock].iloc[-1]
            #     stock_data.increase_1y = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_five_years_earlier['Close'][stock].iloc[-1]) / data_for_five_years_earlier['Close'][stock].iloc[-1]
            #     stock_data.increase_5y = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_twenty_years_earlier['Close'][stock].iloc[-1]) / data_for_twenty_years_earlier['Close'][stock].iloc[-1]
            #     StockData.add(stock_data)
        except Exception as e:
            print("ERROR_OCCURED:", e)
            return


def is_working_hour(hour, minute):
    """
    Check if the given hour is between 9:45 and 18:30
    """

    if hour < 9 or hour > 18:
        return False
    if hour == 9 and minute < 45:
        return False
    if hour == 18 and minute > 30:
        return False
    return True

def get_next_work_day(date):
    """
    Get the next work day after the given date
    date must be in "yyyy-MM-dd" format
    returns date as string in "yyyy-MM-dd" format
    returns the given date if it is not a holiday
    """
    if parse(date) > datetime.now():
        raise ValueError("ERROR: The given date is later than today.")
    
    while is_holiday(date):
        date = (parse(date) + timedelta(days=1)).strftime("%Y-%m-%d")
    return date

def get_last_work_day(date):
    """
    Get the last work day before the given date
    date must be in "yyyy-MM-dd" format
    returns date as string in "yyyy-MM-dd" format
    returns the given date if it is not a holiday

    """

    while is_holiday(date):
        date = (parse(date) - timedelta(days=1)).strftime("%Y-%m-%d")
    return date


def is_holiday(date):
    """
    Check if the given date is a holiday.
    ##### please use string format "yyyy-MM-dd"
    returns false for later dates
    """

    if(parse(date).weekday() >= 5):
        return True
    if(parse(date) > datetime.now()): # the date has not come yet, this should not enter here, just in case returned false
        raise ValueError("ERROR: The given date is later than today.")
 
    
    does_date_exist = Holidays.does_date_exist(date)
    if(does_date_exist):
        return Holidays.is_holiday(date)
    does_xu100_data_exist = check_is_holiday_from_xu100(date)
    if(does_xu100_data_exist):
        Holidays.add(Holidays(date=date, is_holiday=False))
        return False
    if 10 < datetime.now().hour < 18: # The data does not exist even though it is working hour # TODO: check if the date is today or later
        Holidays.add(Holidays(date=date, is_holiday=True))
        return True
    return True

def check_is_holiday_from_xu100(date):
    """
    uses yfinance to check if xu100 data exists for the date
    date must be in "yyyy-MM-dd" format
    checks the local db also first
    """
    # Check if today is a holiday
    date_parsed = parse(date)
    one_day_later = date_parsed + timedelta(days=1)
    xu100_from_db = StockData.query.filter(StockData.stock_name == "XU100.IS" and StockData.date == date)
    if xu100_from_db.first() is not None:
        return False
    data = yf.download('XU100.IS', start=date, end=one_day_later)
    return not data.empty # If the data is empty, it means that the date is a holiday


# region Tests

def test_is_holiday():
    dates_and_expected_results = [
        ("2024-04-10", True),
        ("2024-04-11", True),
        ("2024-04-12", True),
        ("2024-04-13", True),
        ("2024-04-14", True),
        ("2024-04-15", False),
        ("2024-04-16", False),
        ("2024-04-17", False),
        ("2024-04-09", False),
        ("2024-04-08", False),
        ("2024-04-07", True)
       ]
    for date, expected_result in dates_and_expected_results:
        assert is_holiday(date) == expected_result

#endregion