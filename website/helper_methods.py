from datetime import timedelta
from .models import StockData, Holidays, XU100, db, UpdateToDb
import yfinance as yf
from datetime import datetime
from dateutil.parser import parse
import calendar
import os
import traceback
def data_exists_in_db():
    """
    Check if the database has any data
    """

    return StockData.query.first() is not None

def update_stock_data_in_db(app):

    # We need to check if the database needs an update, because this method is called by different sources
    # if today is holiday, we will not update the database 
    # but if the request is coming from the user, we have to update the datase

    with app.app_context():
        try:
            if (data_exists_in_db() and not is_working_hour(datetime.now().hour, datetime.now().minute)):
                return # if there is data and it is not working hour, let it go
            if((UpdateToDb.get_latest_update() is not None) and UpdateToDb.get_latest_update() > (datetime.now() - timedelta(minutes=15))):
                return # return if the latest update is within 15 minutes - only update every 15 minutes

            # either there is no data, or it needs an update

            last_working_day = datetime.now().strftime("%Y-%m-%d") # initially today
            if((datetime.now().hour < 10 or (datetime.now().hour == 10 and datetime.now().minute < 16))): # if morning hours, we will get the data of yesterday
                last_working_day = get_last_work_day((parse(last_working_day) - timedelta(days=1)).strftime("%Y-%m-%d"))

            one_day_earlier = get_last_work_day((parse(last_working_day) - timedelta(days=1)).strftime("%Y-%m-%d"))
            today = datetime.now().strftime("%Y-%m-%d")
            # for other dates, we will return the difference for specific days
            one_week_earlier = get_last_work_day((parse(today) - timedelta(days=7)).strftime("%Y-%m-%d"))
            one_month_earlier = get_last_work_day((parse(today) - timedelta(days=30)).strftime("%Y-%m-%d"))
            six_months_earlier = get_last_work_day((parse(today) - timedelta(days=183)).strftime("%Y-%m-%d"))
            one_year_earlier = get_last_work_day((parse(today) - timedelta(days=365)).strftime("%Y-%m-%d"))
            five_years_earlier = get_last_work_day((parse(today) - timedelta(days=1826)).strftime("%Y-%m-%d"))

            stocks = ['A1CAP.IS','ACSEL.IS', 'ADEL.IS', 'ADESE.IS','ADGYO.IS','AEFES.IS','AFYON.IS','AGESA.IS','AGHOL.IS','AGROT.IS','AGYO.IS','AHGAZ.IS','AKBNK.IS'
                      ,'XU100.IS'] #TODO: check the db first
            # #,'AKCNS.IS','AKENR.IS','AKFGY.IS','AKFYE.IS','AKGRT.IS','AKMGY.IS','AKSA.IS','AKSEN.IS','AKSGY.IS','AKSUE.IS','AKYHO.IS','ALARK.IS','ALBRK.IS','ALCAR.IS','ALCTL.IS','ALFAS.IS','ALGYO.IS','ALKA.IS','ALKIM.IS','ALMAD.IS','ALVES.IS','ANELE.IS','ANGEN.IS','ANHYT.IS','ANSGR.IS','ARASE.IS','ARCLK.IS','ARDYZ.IS','ARENA.IS','ARSAN.IS','ARTMS.IS','ARZUM.IS','ASELS.IS','ASGYO.IS','ASTOR.IS','ASUZU.IS','ATAGY.IS','ATAKP.IS','ATATP.IS','ATEKS.IS','ATLAS.IS','ATSYH.IS','AVGYO.IS','AVHOL.IS','AVOD.IS','AVPGY.IS','AVTUR.IS','AYCES.IS','AYDEM.IS','AYEN.IS','AYES.IS','AYGAZ.IS','AZTEK.IS','BAGFS.IS','BAKAB.IS','BALAT.IS','BANVT.IS','BARMA.IS','BASCM.IS','BASGZ.IS','BAYRK.IS','BEGYO.IS','BERA.IS','BEYAZ.IS','BFREN.IS','BIENY.IS','BIGCH.IS','BIMAS.IS','BINHO.IS','BIOEN.IS','BIZIM.IS','BJKAS.IS','BLCYT.IS','BMSCH.IS','BMSTL.IS','BNTAS.IS','BOBET.IS','BORLS.IS','BORSK.IS','BOSSA.IS','BRISA.IS','BRKO.IS','BRKSN.IS','BRKVY.IS','BRLSM.IS','BRMEN.IS','BRSAN.IS','BRYAT.IS','BSOKE.IS','BTCIM.IS','BUCIM.IS','BURCE.IS','BURVA.IS','BVSAN.IS','BYDNR.IS','CANTE.IS','CASA.IS','CATES.IS','CCOLA.IS','CELHA.IS','CEMAS.IS','CEMTS.IS','CEOEM.IS','CIMSA.IS','CLEBI.IS','CMBTN.IS','CMENT.IS','CONSE.IS','COSMO.IS','CRDFA.IS','CRFSA.IS','CUSAN.IS','CVKMD.IS','CWENE.IS','DAGHL.IS','DAGI.IS','DAPGM.IS','DARDL.IS','DENGE.IS','DERHL.IS','DERIM.IS','DESA.IS','DESPC.IS','DEVA.IS','DGATE.IS','DGGYO.IS','DGNMO.IS','DIRIT.IS','DITAS.IS','DJIST.IS','DMRGD.IS','DMSAS.IS','DNISI.IS','DOAS.IS','DOBUR.IS','DOCO.IS','DOFER.IS','DOGUB.IS','DOHOL.IS','DOKTA.IS','DURDO.IS','DYOBY.IS','DZGYO.IS','EBEBK.IS','ECILC.IS','ECZYT.IS','EDATA.IS','EDIP.IS','EGEEN.IS','EGEPO.IS','EGGUB.IS','EGPRO.IS','EGSER.IS','EKGYO.IS','EKIZ.IS','EKOS.IS','EKSUN.IS','ELITE.IS','EMKEL.IS','EMNIS.IS','ENERY.IS','ENJSA.IS','ENKAI.IS','ENSRI.IS','EPLAS.IS','ERBOS.IS','ERCB.IS','EREGL.IS','ERSU.IS','ESCAR.IS','ESCOM.IS','ESEN.IS','ETILR.IS','ETYAT.IS','EUHOL.IS','EUKYO.IS','EUPWR.IS','EUREN.IS','EUYO.IS','EYGYO.IS','FADE.IS','FENER.IS','FLAP.IS','FMIZP.IS','FONET.IS','FORMT.IS','FORTE.IS','FRIGO.IS','FROTO.IS','FZLGY.IS','GARAN.IS','GARFA.IS','GEDIK.IS','GEDZA.IS','GENIL.IS','GENTS.IS','GEREL.IS','GESAN.IS','GIPTA.IS','GLBMD.IS','GLCVY.IS','GLDTR.IS','GLRYH.IS','GLYHO.IS','GMSTR.IS','GMTAS.IS','GOKNR.IS','GOLTS.IS','GOODY.IS','GOZDE.IS','GRNYO.IS','GRSEL.IS','GRTRK.IS','GSDDE.IS','GSDHO.IS','GSRAY.IS','GUBRF.IS','GWIND.IS','GZNMI.IS','HALKB.IS','HATEK.IS','HATSN.IS','HDFGS.IS','HEDEF.IS','HEKTS.IS','HKTM.IS','HLGYO.IS','HTTBT.IS','HUBVC.IS','HUNER.IS','HURGZ.IS','ICBCT.IS','ICUGS.IS','IDGYO.IS','IEYHO.IS','IHAAS.IS','IHEVA.IS','IHGZT.IS','IHLAS.IS','IHLGM.IS','IHYAY.IS','IMASM.IS','INDES.IS','INFO.IS','INGRM.IS','INTEM.IS','INVEO.IS','INVES.IS','IPEKE.IS','ISATR.IS','ISBIR.IS','ISBTR.IS','ISCTR.IS','ISDMR.IS','ISFIN.IS','ISGSY.IS','ISGYO.IS','ISIST.IS','ISKPL.IS','ISKUR.IS','ISMEN.IS','ISSEN.IS','ISYAT.IS','IZENR.IS','IZFAS.IS','IZINV.IS','IZMDC.IS','JANTS.IS','KAPLM.IS','KAREL.IS','KARSN.IS','KARTN.IS','KARYE.IS','KATMR.IS','KAYSE.IS','KBORU.IS','KCAER.IS','KCHOL.IS','KENT.IS','KERVN.IS','KERVT.IS','KFEIN.IS','KGYO.IS','KIMMR.IS','KLGYO.IS','KLKIM.IS','KLMSN.IS','KLNMA.IS','KLRHO.IS','KLSER.IS','KLSYN.IS','KMPUR.IS','KNFRT.IS','KONKA.IS','KONTR.IS','KONYA.IS','KOPOL.IS','KORDS.IS','KOZAA.IS','KOZAL.IS','KRDMA.IS','KRDMB.IS','KRDMD.IS','KRGYO.IS','KRONT.IS','KRPLS.IS','KRSTL.IS','KRTEK.IS','KRVGD.IS','KSTUR.IS','KTLEV.IS','KTSKR.IS','KUTPO.IS','KUVVA.IS','KUYAS.IS','KZBGY.IS','KZGYO.IS','LIDER.IS','LIDFA.IS','LINK.IS','LKMNH.IS','LMKDC.IS','LOGO.IS','LRSHO.IS','LUKSK.IS','MAALT.IS','MACKO.IS','MAGEN.IS','MAKIM.IS','MAKTK.IS','MANAS.IS','MARBL.IS','MARKA.IS','MARTI.IS','MAVI.IS','MEDTR.IS','MEGAP.IS','MEGMT.IS','MEKAG.IS','MEPET.IS','MERCN.IS','MERIT.IS','MERKO.IS','METRO.IS','METUR.IS','MGROS.IS','MHRGY.IS','MIATK.IS','MIPAZ.IS','MMCAS.IS','MNDRS.IS','MNDTR.IS','MOBTL.IS','MOGAN.IS','MPARK.IS','MRGYO.IS','MRSHL.IS','MSGYO.IS','MTRKS.IS','MTRYO.IS','MZHLD.IS','NATEN.IS','NETAS.IS','NIBAS.IS','NTGAZ.IS','NTHOL.IS','NUGYO.IS','NUHCM.IS','OBAMS.IS','OBASE.IS','ODAS.IS','ODINE.IS','OFSYM.IS','ONCSM.IS','ORCAY.IS','ORGE.IS','ORMA.IS','OSMEN.IS','OSTIM.IS','OTKAR.IS','OTTO.IS','OYAKC.IS','OYAYO.IS','OYLUM.IS','OYYAT.IS','OZGYO.IS','OZKGY.IS','OZRDN.IS','OZSUB.IS','PAGYO.IS','PAMEL.IS','PAPIL.IS','PARSN.IS','PASEU.IS','PATEK.IS','PCILT.IS','PEGYO.IS','PEKGY.IS','PENGD.IS','PENTA.IS','PETKM.IS','PETUN.IS','PGSUS.IS','PINSU.IS','PKART.IS','PKENT.IS','PLTUR.IS','PNLSN.IS','PNSUT.IS','POLHO.IS','POLTK.IS','PRDGS.IS','PRKAB.IS','PRKME.IS','PRZMA.IS','PSDTC.IS','PSGYO.IS','QNBFB.IS','QNBFL.IS','QUAGR.IS','RALYH.IS','RAYSG.IS','REEDR.IS','RNPOL.IS','RODRG.IS','RTALB.IS','RUBNS.IS','RYGYO.IS','RYSAS.IS','SAFKR.IS','SAHOL.IS','SAMAT.IS','SANEL.IS','SANFM.IS','SANKO.IS','SARKY.IS','SASA.IS','SAYAS.IS','SDTTR.IS','SEGYO.IS','SEKFK.IS','SEKUR.IS','SELEC.IS','SELGD.IS','SELVA.IS','SEYKM.IS','SILVR.IS','SISE.IS','SKBNK.IS','SKTAS.IS','SKYLP.IS','SKYMD.IS','SMART.IS','SMRTG.IS','SNGYO.IS','SNICA.IS','SNKRN.IS','SNPAM.IS','SODSN.IS','SOKE.IS','SOKM.IS','SONME.IS','SRVGY.IS','SUMAS.IS','SUNTK.IS','SURGY.IS','SUWEN.IS','TABGD.IS','TARKM.IS','TATEN.IS','TATGD.IS','TAVHL.IS','TBORG.IS','TCELL.IS','TDGYO.IS','TEKTU.IS','TERA.IS','TETMT.IS','TEZOL.IS','TGSAS.IS','THYAO.IS','TKFEN.IS','TKNSA.IS','TLMAN.IS','TMPOL.IS','TMSN.IS','TNZTP.IS','TOASO.IS','TRCAS.IS','TRGYO.IS','TRILC.IS','TSGYO.IS','TSKB.IS','TSPOR.IS','TTKOM.IS','TTRAK.IS','TUCLK.IS','TUKAS.IS','TUPRS.IS','TUREX.IS','TURGG.IS','TURSG.IS','UFUK.IS','ULAS.IS','ULKER.IS','ULUFA.IS','ULUSE.IS','ULUUN.IS','UMPAS.IS','UNLU.IS','USAK.IS','USDTR.IS','UZERB.IS','VAKBN.IS','VAKFN.IS','VAKKO.IS','VANGD.IS','VBTYZ.IS','VERTU.IS','VERUS.IS','VESBE.IS','VESTL.IS','VKFYO.IS','VKGYO.IS','VKING.IS','VRGYO.IS','X030S.IS','X100S.IS','XBANA.IS','XBANK.IS','XBLSM.IS','XELKT.IS','XFINK.IS','XGIDA.IS','XGMYO.IS','XHARZ.IS','XHOLD.IS','XILTM.IS','XINSA.IS','XKAGT.IS','XKMYA.IS','XKOBI.IS','XKURY.IS','XMADN.IS','XMANA.IS','XMESY.IS','XSADA.IS','XSANK.IS','XSANT.IS','XSBAL.IS','XSBUR.IS','XSDNZ.IS','XSGRT.IS','XSIST.IS','XSIZM.IS','XSKAY.IS','XSKOC.IS','XSKON.IS','XSPOR.IS','XSTKR.IS','XTAST.IS','XTCRT.IS','XTEKS.IS','XTM25.IS','XTMTU.IS','XTRZM.IS','XTUMY.IS','XU030.IS','XU050.IS','XU100.IS','XUHIZ.IS','XULAS.IS','XUMAL.IS','XUSIN.IS','XUSRD.IS','XUTEK.IS','XUTUM.IS','XYLDZ.IS','XYORT.IS','XYUZO.IS','YAPRK.IS','YATAS.IS','YAYLA.IS','YBTAS.IS','YEOTK.IS','YESIL.IS','YGGYO.IS','YGYO.IS','YKBNK.IS','YKSLN.IS','YONGA.IS','YUNSA.IS','YYAPI.IS','YYLGD.IS','Z30EA.IS','Z30KE.IS','Z30KP.IS','ZEDUR.IS','ZELOT.IS','ZGOLD.IS','ZOREN.IS','ZPBDL.IS','ZPLIB.IS','ZPT10.IS','ZPX30.IS','ZRE20.IS','ZRGYO.IS','ZTM15.IS']
            data_from_db_for_one_day_earlier = StockData.query.filter(StockData.date == one_day_earlier).all()
            data_from_db_for_one_week_earlier = StockData.query.filter(StockData.date == one_week_earlier).all()
            data_from_db_for_one_month_earlier = StockData.query.filter(StockData.date == one_month_earlier).all()
            data_from_db_for_six_months_earlier = StockData.query.filter(StockData.date == six_months_earlier).all()
            data_from_db_for_one_year_earlier = StockData.query.filter(StockData.date == one_year_earlier).all()
            data_from_db_for_five_years_earlier = StockData.query.filter(StockData.date == five_years_earlier).all()

            

            if(len(data_from_db_for_one_day_earlier)==0):
                data_for_one_day_earlier = yf.download(stocks, start=one_day_earlier, end=(parse(one_day_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
                stock_datas = []
                for stock in stocks:
                    stock_data = StockData(stock_name=stock)
                    stock_data.date = one_day_earlier
                    stock_data.close = data_for_one_day_earlier['Close'][stock].iloc[-1]
                    stock_datas.append(stock_data)
                StockData.add_all(stock_datas)
            
            if(len(data_from_db_for_one_week_earlier)==0):
                data_for_one_week_earlier = yf.download(stocks, start=one_week_earlier, end=(parse(one_week_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
                stock_datas = []
                for stock in stocks:
                    stock_data = StockData(stock_name=stock)
                    stock_data.date = one_week_earlier
                    stock_data.close = data_for_one_week_earlier['Close'][stock].iloc[-1]
                    stock_datas.append(stock_data)
                StockData.add_all(stock_datas)
            
            if(len(data_from_db_for_one_month_earlier)==0):
                data_for_one_month_earlier = yf.download(stocks, start=one_month_earlier, end=(parse(one_month_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
                stock_datas = []
                for stock in stocks:
                    stock_data = StockData(stock_name=stock)
                    stock_data.date = one_month_earlier
                    stock_data.close = data_for_one_month_earlier['Close'][stock].iloc[-1]
                    stock_datas.append(stock_data)
                StockData.add_all(stock_datas)
            
            if(len(data_from_db_for_six_months_earlier)==0):
                data_for_six_months_earlier = yf.download(stocks, start=six_months_earlier, end=(parse(six_months_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
                stock_datas = []
                for stock in stocks:
                    stock_data = StockData(stock_name=stock)
                    stock_data.date = six_months_earlier
                    stock_data.close = data_for_six_months_earlier['Close'][stock].iloc[-1]
                    stock_datas.append(stock_data)
                StockData.add_all(stock_datas)
            
            if(len(data_from_db_for_one_year_earlier)==0):
                data_for_one_year_earlier = yf.download(stocks, start=one_year_earlier, end=(parse(one_year_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
                stock_datas = []
                for stock in stocks:
                    stock_data = StockData(stock_name=stock)
                    stock_data.date = one_year_earlier
                    stock_data.close = data_for_one_year_earlier['Close'][stock].iloc[-1]
                    stock_datas.append(stock_data)
                StockData.add_all(stock_datas)
            
            if(len(data_from_db_for_five_years_earlier)==0):
                data_for_five_years_earlier = yf.download(stocks, start=five_years_earlier, end=(parse(five_years_earlier) + timedelta(days=1)).strftime("%Y-%m-%d"))
                stock_datas = []
                for stock in stocks:
                    stock_data = StockData(stock_name=stock)
                    stock_data.date = five_years_earlier
                    stock_data.close = data_for_five_years_earlier['Close'][stock].iloc[-1]
                    stock_datas.append(stock_data)
                StockData.add_all(stock_datas)
            
            data_from_db_for_last_working_day = StockData.query.filter(StockData.date == last_working_day).all() 
            data_from_db_for_one_day_earlier = StockData.query.filter(StockData.date == one_day_earlier).all()
            data_from_db_for_one_week_earlier = StockData.query.filter(StockData.date == one_week_earlier).all()
            data_from_db_for_one_month_earlier = StockData.query.filter(StockData.date == one_month_earlier).all()
            data_from_db_for_six_months_earlier = StockData.query.filter(StockData.date == six_months_earlier).all()
            data_from_db_for_one_year_earlier = StockData.query.filter(StockData.date == one_year_earlier).all()
            data_from_db_for_five_years_earlier = StockData.query.filter(StockData.date == five_years_earlier).all()

            latest_data_from_yfinance = yf.download(stocks, start=last_working_day, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
            
            stock_datas = []
            # save latest data to db
            for stock in stocks:
                if(stock in map(lambda it: it.stock_name, data_from_db_for_last_working_day)):
                    stock_data = next((item for item in data_from_db_for_last_working_day if item.stock_name == stock), None)

                else:    
                    stock_data = StockData(stock_name=stock)
                    stock_data.date = today
                    stock_data.interval = "1d"
                stock_data.close = latest_data_from_yfinance['Close'][stock].iloc[-1]
                stock_data.increase_1d = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_day_earlier['Close'][stock].iloc[-1]) / data_for_one_day_earlier['Close'][stock].iloc[-1]
                stock_data.increase_1w = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_week_earlier['Close'][stock].iloc[-1]) / data_for_one_week_earlier['Close'][stock].iloc[-1]
                stock_data.increase_1m = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_month_earlier['Close'][stock].iloc[-1]) / data_for_one_month_earlier['Close'][stock].iloc[-1]
                stock_data.increase_6m = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_six_months_earlier['Close'][stock].iloc[-1]) / data_for_six_months_earlier['Close'][stock].iloc[-1]
                stock_data.increase_1y = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_one_year_earlier['Close'][stock].iloc[-1]) / data_for_one_year_earlier['Close'][stock].iloc[-1]
                stock_data.increase_5y = (latest_data_from_yfinance['Close'][stock].iloc[-1] - data_for_five_years_earlier['Close'][stock].iloc[-1]) / data_for_five_years_earlier['Close'][stock].iloc[-1]
                stock_datas.append(stock_data)
            StockData.add_all(stock_datas)
            
            #region XU100 RECORD
            # get the data of XU100
            all_data = yf.download('XU100.IS', start=one_year_earlier, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
            xu100_data = all_data['Close']
            # get date of the latest price
            latest_price_date = xu100_data.index[-1].strftime("%Y-%m-%d")
            # get latest price
            latest_price = xu100_data.iloc[-1]
            # get the highest price ever in the data
            # but firstly we will filter to only last year
            high_prices = all_data['High']
            last_year_data = high_prices[high_prices.index >= (datetime.now() - timedelta(days=500))]
            highest_price = last_year_data.max()
            # get the date of the highest price
            highest_price_date = last_year_data.idxmax().strftime("%Y-%m-%d")
            
            # get todays highest price
            todays_highest_price = all_data['High'].iloc[-1]
            # add the data to db

            # all_time_high_usd = 510.37 # HARD CODED, since it is so hard for this record to get broken, may update in 3 years
            # date_of_all_time_high_usd = "2013-05-17"
            xu100 = XU100(latest_price_date=latest_price_date, 
                        last_record=highest_price, 
                        last_record_date=highest_price_date, 
                        latest_update_date=datetime.now(),
                        latest_price=latest_price,
                        todays_highest_price=todays_highest_price,
                        #   all_time_high_usd=all_time_high_usd,
                        #   date_of_all_time_high_usd=date_of_all_time_high_usd
                        )
            XU100.add(xu100)

        #endregion

            UpdateToDb.set_latest_update()
        except Exception as e:
            print("ERROR_OCCURED:", e)
            traceback.print_exc()
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
    TODO: create a better way, this is not efficient
    """
    if parse(date) > datetime.now():
        return None
    
    while check_is_holiday(date):
        date = (parse(date) + timedelta(days=1)).strftime("%Y-%m-%d")
    return date

def get_last_work_day(date):
    """
    Get the last work day before the given date
    date must be in "yyyy-MM-dd" format
    returns date as string in "yyyy-MM-dd" format
    returns the given date if it is not a holiday

    """

    while check_is_holiday(date):
        date = (parse(date) - timedelta(days=1)).strftime("%Y-%m-%d")
    return date


def check_is_holiday(date):
    """
    Check if the given date is a holiday.
    ##### please use string format "yyyy-MM-dd"
    returns false for later dates
    """

    if(parse(date).weekday() >= 5):
        return True
    if(parse(date) > datetime.now()): # the date has not come yet, you should not be checking if a later date is a holiday because we are not sure
        raise ValueError("ERROR: The given date is later than today.")
 
    
    does_date_exist = Holidays.does_date_exist(date)
    if(does_date_exist):
        return Holidays.check_is_holiday(date)
    does_xu100_data_exist = check_is_holiday_from_xu100(date)
    if(does_xu100_data_exist): # it is not a holiday, xu100 data exist
        Holidays.add(Holidays(date=date, is_holiday=True))
        return True
    if 10 < datetime.now().hour < 18: # The data does not exist even though it is working hour
        Holidays.add(Holidays(date=date, is_holiday=True))
        return True
    return False

def check_is_holiday_from_xu100(date):
    """
    uses yfinance to check if xu100 data exists for the date
    date must be in "yyyy-MM-dd" format
    checks the local db also first
    ##### returns true if the date is holiday
    """
    # Check if today is a holiday
    date_parsed = parse(date)
    one_day_later = date_parsed + timedelta(days=1)
    xu100_from_db = StockData.query.filter(StockData.stock_name == "XU100.IS" and StockData.date == date)
    if xu100_from_db.first() is not None:
        return False
    data = yf.download('XU100.IS', start=date, end=one_day_later)
    is_holiday = data.empty
    return is_holiday # If the data is empty, it means that the date is a holiday

def get_days_in_last_month():
    """
    returns how many days does the last month have
    """
    current_date = datetime.now()
    first_day_of_current_month = current_date.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    last_month = last_day_of_previous_month.month
    year_of_last_month = last_day_of_previous_month.year
    days_in_last_month = calendar.monthrange(year_of_last_month, last_month)[1]
    return days_in_last_month

# region Tests

def test_check_is_holiday():
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
        assert check_is_holiday(date) == expected_result

#endregion