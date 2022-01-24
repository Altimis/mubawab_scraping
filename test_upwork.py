import pytz
import pandas as pd
from pytrends.request import TrendReq
import calendar
import time
import datetime
import random
import numpy as np


class Trends:

    def __init__(self, kw_list, key_ref):
        self.UTC_tmz = pytz.utc
        self.IST_tmz = pytz.timezone('Asia/Kolkata')
        self.key_ref = "google news"
        self.year = 2021

        self.kw_list = kw_list
        self.key_ref = key_ref
        self.COUNTRY = "IN"
        self.CATEGORY = 0
        self.SEARCH_TYPE = ''

    def get_yearly_timescale(self):
        date_intervals_ls = []

        for mon in range(1, 13):
            _, num_days = calendar.monthrange(self.year, mon)
            date_intervals_ls.append(datetime.date(self.year, mon, 1).strftime("%Y-%m-%d"))  # First day of the month
            date_intervals_ls.append(
                datetime.date(self.year, mon, num_days).strftime("%Y-%m-%d"))  # Last day of the month

        return date_intervals_ls

    def get_normalised(self, df_kwset_interval):
        dates_col = df_kwset_interval['date']
        # Replace zeroes in key_ref by 1 for Normalisation
        df_kwset_interval[self.key_ref] = df_kwset_interval[key_ref].replace(0, 1)
        # Normalise with respect to key_ref
        df_kwset_interval.drop('date', axis=1, inplace=True)
        for col in df_kwset_interval:
            df_kwset_interval[col] = df_kwset_interval[col] / df_kwset_interval[key_ref]
        df_kwset_interval.reset_index()
        # Drop key_ref column
        df_kwset_interval.drop(self.key_ref, axis=1, inplace=True)

        return df_kwset_interval, dates_col

    def get_trends(self, i, kw_list, date_intervals_ls):

        pytrends = TrendReq(hl='en-US', tz=330)

        # Loop through the keywords in SET OF 4
        kwset_df_ls = []  # List to concat results of 4 keywords
        for cal in range(0, len(date_intervals_ls), 2):  # loop through months
            try:
                date_instance = date_intervals_ls[cal] + " " + date_intervals_ls[cal + 1]
                l = kw_list[i:(i + 4)]
                l.append(self.key_ref)  # Add up key_ref to set of kws for relative scores wrt to key_red
                print("Busy Requesting data.....")
                pytrends.build_payload(l,
                                       timeframe=date_instance,
                                       geo=self.COUNTRY,
                                       cat=self.CATEGORY,
                                       gprop=self.SEARCH_TYPE)
                df_kwset = pytrends.interest_over_time()
                df_kwset.reset_index(inplace=True)
                df_kwset.drop('isPartial', axis=1, inplace=True)

                kwset_df_ls.append(df_kwset)

            except IndexError:
                pass

        df_kwset_interval = pd.concat(kwset_df_ls)  # Form up resultant data frame of 4 Keywords
        # raw_name = "raw_dataset"+str("_")+str((i+4)//4)+".csv" #Serial naming
        # df_kwset_interval.to_csv(raw_name, index = False) #Get raw csv
        return df_kwset_interval

    def get_concatenated_from_list(self, df_concat_ls):
        maj_dataframe = pd.concat(df_concat_ls, axis=1)  # Form up resultant dataframe of all Keywords
        return maj_dataframe

    def get_concatenated_dates(self, maj_dataframe, dates_col):
        maj_dataframe = pd.concat((dates_col, maj_dataframe), axis=1)  # Join the dates column
        maj_dataframe.to_csv('concat_df.csv', index=False)  # Get resultant dataframe in csv
        return maj_dataframe

    def process_data(self):

        df_concat_ls = []
        i = 0
        date_intervals_ls = self.get_yearly_timescale()
        while i < len(kw_list):
            try:
                df_kwset_interval = self.get_trends(i, self.kw_list, date_intervals_ls)
                df_kwset_interval_norm, dates_col = self.get_normalised(df_kwset_interval)
                df_concat_ls.append(df_kwset_interval_norm)
                # Increment to index the next 4 keywords
                i += 4
                print("Sleeping...")
                # time.sleep(60) #sleep to avoid timeouts
                print('Awake!')
                j = str((i + 4) // 4)
                print("Keyword set No.{0} is running".format(j))
            except Exception as e:

                print(e, self.kw_list[i])
                print("sleeping for 55+ seconds")
                i += 4
                time.sleep(random.randrange(55, 75))
                maj_dataframe = self.get_concatenated_from_list(df_concat_ls)
                maj_dataframe = self.get_concatenated_dates(maj_dataframe, dates_col)

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


if __name__ == "__main__":
    kw_list = ["Aashirvaad", "Aavin", "Action Construction Equipment", "Aditya Birla Payments Bank", "AgniKul Cosmos",
               "Air Deccan", "Air India", "Air Ink", "Airtel digital TV", "Airtel Payments Bank",
               "Alembic Pharmaceuticals", "Alkem Laboratories", "Ambuja Cements", "Amco Batteries", "Amrapali Jewels",
               "Amrutanjan Healthcare", "Amul", "Anikspray", "Anokhi", "Apollo Tyres", "Aravind Laboratories",
               "Arise India", "Arre", "Arun Icecreams", "Ashok Leyland", "Asia MotorWorks", "Asian Paints",
               "Aurobindo Pharma", "Axis Bank", "Babool", "Bajaj Auto", "Bajaj Consumer Care", "Template:Bajaj Group",
               "Bajaj Nomarks", "Bakeys", "Balaji Wafers", "Balkrishna Industries", "Banas Dairy", "Bank of Baroda",
               "Bellatrix Aerospace", "BEML Limited", "Berger Paints", "Bharat Aluminium Company", "Bharat Biotech",
               "Bharat Heavy Electricals Limited", "Bharat Petroleum", "Bharti Airtel", "Bhima Jewellers",
               "Biba Apparels", "Binaca", "Biocon", "Birla Precision Technologies", "Birla Tyres", "Bisk Farm",
               "Bisleri", "Blue Dart Express", "Blue Star", "Boroline", "Borosil", "BPL Group", "Brand India",
               "The Brand Trust Report", "Brihan Maharashtra Sugar Syndicate Ltd.", "Brihans Natural Products",
               "Britannia Industries", "Cadila Pharmaceuticals", "Café Coffee Day", "Camlin Fine Sciences", "CARS24",
               "CEAT", "Celkon", "Century Plyboards", "Changalikodan", "Chelpark", "Chendamangalam Saree",
               "Ching's Secret", "Chinkara Motors", "Chitale Bandhu Mithaiwale", "Chlormint", "Cibaca", "Cipla",
               "Classmate", "Cords Cable Industries Limited", "Cosco", "Cromā", "Cyient", "D2h", "Dabur", "Dalda",
               "Delhivery", "Dipper", "Dish TV", "Dr. Reddy's Laboratories", "DSK Group", "DTDC", "Dwarkin", "Easyday",
               "Eicher Motors", "Ekart", "Emcure Pharmaceuticals", "Epic", "ErosSTX", "Escorts Limited",
               "Everest Spices", "Exide Industries", "FabFurnish", "Fabindia", "Fastrack", "Fevicol", "Fiama Di Wills",
               "Finolex Cables", "FirstCry", "Flipkart", "Force Motors", "Forest Essentials", "Funskool",
               "General Insurance Corporation of India", "Ghari Detergent", "Godrej & Boyce", "Godrej Group",
               "Godrej Interio", "Gogte Group", "Gold Spot", "Gyan Dairy", "Haathi Chaap", "Haldiram's", "Haldyn Glass",
               "Hamdard India", "Haptik", "Havells", "Havmor Ice Cream", "Hawkins Cookers", "HCL Technologies",
               "HDFC Bank", "Heritage Foods", "Hero Cycles", "Hero MotoCorp", "Hero Motors Company", "Hike Messenger",
               "Hindalco Industries", "Hindustan Aeronautics Limited", "Hindustan Motors",
               "Hindustan National Glass & Industries Limited", "Hindustan Pencils", "Hindustan Petroleum",
               "HLL Lifecare", "HMT", "Hoichoi", "Hradyesh", "I-shakti", "ICICI Bank", "ID Fresh Food", "Idea Cellular",
               "IFB Home Appliances", "Incredible India", "Indane", "Independent TV", "India's Most Attractive Brands",
               "IndiaMART", "Indian Overseas Bank", "IndiGo", "Indigo Paints", "Indosolar", "Indu Film", "Infosys",
               "Infosys Consulting", "Intas Pharmaceuticals", "Intex Technologies", "IYogi", "J. K. Organisation",
               "Jackson Records", "Jain Irrigation Systems", "Jaipan Industries", "Jaipur Watch Company",
               "Jayem Automotives", "Jaypee Group", "Jet Airways", "Jio", "Jio Payments Bank", "Joyalukkas",
               "JSW Cement", "Jumbo King", "K7 Total Security", "Kaja Beedi", "Kalnirnay", "Kalyan Jewellers",
               "Kama Ayurveda", "KamaSutra", "Kansai Nerolac Paints", "Karbonn Mobiles", "Kasaragod Saree",
               "Kaya Limited", "KEC International", "Kent RO Systems", "Kesoram Industries Ltd.", "Khadi Gramodyog",
               "Khadim's", "", "Khazana Jewellery", "Kingfisher", "Kirloskar Group", "Kisna Diamond Jewellery", "Klikk",
               "Sunita Kohli", "Kokuyo Camlin", "KRBL", "Kumbakonam Degree Coffee", "Kuthampully Saree",
               "Lakmé Cosmetics", "Lakshmi Machine Works", "Larsen & Toubro", "Lava International", "Levista",
               "Liberty Shoes", "Limeroad", "Limtex", "Linc Pen & Plastics", "Liril", "Lohia Machinery",
               "Lupin Limited", "Luxor", "LYF", "Mahindra Group", "Mahindra Two Wheelers", "Maiyas Beverages and Foods",
               "Malabar Gold and Diamonds", "Manjushree Technopack", "Mankind Pharma", "Max Group",
               "Max Ventures and Industries", "McDowell's No.1", "McDowell's No.1 Celebration", "MDH", "Meswak",
               "Metro Shoes", "Micromax Informatics", "Milk Mantra", "Mindtree", "Moods Condoms", "Mother Dairy", "MRF",
               "MTR Foods", "Mufti", "Murugappa Group", "MyG", "National Aluminium Company", "Natural Ice Cream",
               "Navayuga Engineering Company Limited", "Navi Group", "NBC Bearings", "Nilkamal Plastics",
               "Nippo Batteries", "Nirma", "Nirodh", "Nivia Sports", "NRB Bearing", "Nuziveedu Seeds", "Nykaa",
               "The Oberoi Group", "Old Monk", "Onida Electronics", "OnMobile", "Orb Energy", "Organic India",
               "Orient Electric", "The Oriental Insurance Company", "Oswald Labs", "Oyo Rooms",
               "P. N. Gadgil Jewellers", "Pankajakasthuri Herbals", "Parachute", "Parle Products", "Parle-G",
               "Patanjali Ayurved", "Paytm", "Paytm Payments Bank", "PC Jeweller", "Pepperfry", "Persistent Systems",
               "PhonePe", "Piramal Glass", "Planet Marathi OTT", "Premier", "Promise", "PTron", "Pulse",
               "Punjab Tractors Ltd.", "Quick Heal", "Rajesh Masala", "Ramco Cements", "Ramco Systems",
               "Ranbaxy Laboratories", "Rane group", "RBL Bank", "Realme 5", "Relaxo",
               "Template:Reliance Anil Dhirubhai Ambani Group", "ReNew Power", "Rolta", "Roots Industries",
               "Royal Enfield", "RRB Energy", "Rupa Company", "SAS Motors", "Satya Paul",
               "Savita Oil Technologies Limited", "SBM Bank India", "Seniority", "Seven", "Shakti Pumps",
               "Shalimar Paints", "ShopClues", "Simmtronics", "Sipani", "Siti Networks", "SIX5SIX", "Skipper Limited",
               "Skyroot Aerospace", "Smith & Jones instant noodles", "Snapdeal", "Sonalika Tractors", "Sonodyne",
               "Spice Digital", "SpiceJet", "Sterlite Technologies", "Stir Crazy Thane", "Stovekraft",
               "Su-Kam Power Systems", "Sun Direct", "Sun Pharma", "Suzlon", "Sylvania", "Taj Hotels",
               "Tally Solutions", "Tanishq", "Tata Cliq", "Tata Consumer Products", "Tata Group", "Tata Motors",
               "Tata Salt", "Tata Sky", "Thalangara Thoppi", "The Himalaya Drug Company", "Thermax", "The Times Group",
               "Times Internet", "Titan Company", "Torque Pharmaceuticals", "Torrent Cables", "Torrent Pharmaceuticals",
               "Tractors and Farm Equipment Limited", "Tribhovandas Bhimji Zaveri", "Trio", "TTK Prestige",
               "TVS Electronics", "TVS Motor Company", "TYKA Sports", "Ullu", "UltraTech Cement", "Uncle Chipps",
               "Unichem Laboratories", "Union Bank of India", "V-Guard Industries", "Vadilal", "Vallée de Vin", "Vi",
               "Vicco Group", "Videocon Group", "Vikram Solar", "VIP Industries", "Vistara", "VKC Footwear", "Voltas",
               "Voodoo Cream Liqueur", "VRL Group", "Wadia Group", "Wheel", "Wildcraft", "Wipro", "Wok Express",
               "Wooden Street", "Wow! Momo", "Xolo", "Yepme", "YU Televentures", "Zandu Realty", "Zeta",
               "Zinda Tilismath", "Zoho Corporation", "Zync Global"]
    kw_list.reverse()

    key_ref = "google news"
    a = Trends(kw_list=kw_list, key_ref=key_ref)
    result = a.process_data()