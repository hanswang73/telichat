'''
- This ChatTree is a subtree of the "TMC.py" ChatTree and is responsible for the specific implementation of the "book flights" business
- You can execute "python ./ichatdef/firstapp/py_chattree/TMC_book_flights.py" in the server's project directory to generate "TMC_book_flights.html", download it locally and open it with a browser, you can see the topology structure of the entire ChatTree and related code information
'''

# -------------------------------------------------------------------------------------
# Standard code header for every python ChatTree file
# -------------------------------------------------------------------------------------
 
import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)
from chattree_def import *

chattree = ChatTree()

# -------------------------------------------------------------------------------------
# Data definitions and helper functions
# -------------------------------------------------------------------------------------

import re, datetime, random

'''
Required condition fields
    flight date
    flight departure city
    flight landing city
Optional condition fields
    flight departure airport        --- "no limit to departure airport" means no limit or anything can be done
    flight landing airport          --- "no limit to landing airport" means no limit or anything can be done
    airline                         --- "no limit to airline" means no limit or anything can be done
    flight is direct or connecting  --- "no limit to direct or connecting" means no limit or anything can be done, there is an intent branch that is "no limit to direct or connecting"
    flight departure time period    --- "no limit to departure time period" means no limit or anything can be done, there is an intent branch that is "no limit to departure time period"
Special fields (both conditions and targets)
    flight cabin class              --- As a condition, if there is no value, it means that it is "not limit to cabin class"; as a target, it is a required field
Target field
    flight number
(Other) Result fields
    flight departure time
    flight landing time
    price
Auxiliary fields
    number of passengers
    passenger information
'''

_airline_dict = { # ["code", price factor]
    "American Airlines": ["AA", 1.12],
    "Delta Air Lines": ["DL", 1.10],
    "United Airlines": ["UA", 1.08],
    "Southwest Airlines": ["WN", 1.00], # 基准点
    "Alaska Airlines": ["AS", 1.05],
    "JetBlue Airways": ["B6", 1.04],
    "Hawaiian Airlines": ["HA", 1.15],
    "Spirit Airlines": ["NK", 0.78],
    "Frontier Airlines": ["F9", 0.75],
    "Allegiant Air": ["G4", 0.82],
    "Sun Country Airlines": ["SY", 0.88],
    "Avelo Airlines": ["XP", 0.70],
    "Breeze Airways": ["MX", 0.85],
    "SkyWest Airlines": ["OO", 1.05],
    "Envoy Air": ["MQ", 1.02],
    "Republic Airways": ["YX", 1.03],
    "Mesa Airlines": ["YV", 0.98],
    "PSA Airlines": ["OH", 1.01],
    "Piedmont Airlines": ["PT", 1.02],
    "Horizon Air": ["QX", 1.06],
    "Silver Airways": ["3M", 1.20],
    "Cape Air": ["9K", 1.35],
}

_city_airport_dict = {
    "New York City": ["John F. Kennedy (JFK)", "LaGuardia (LGA)", "Newark Liberty (EWR)"],
    "Los Angeles": ["Los Angeles International (LAX)"],
    "Chicago": ["O'Hare (ORD)", "Midway (MDW)"],
    "San Francisco": ["San Francisco International (SFO)"],
    "Seattle": ["Seattle-Tacoma (SEA)"],
    "Atlanta":["Hartsfield-Jackson Atlanta (ATL)"],
    "Dallas":["Dallas/Fort Worth (DFW)", "Dallas Love Field (DAL)"],
    "Houston":["George Bush Intercontinental (IAH)", "William P. Hobby (HOU)"],
    "Washington, D.C.":["Dulles (IAD)", "Ronald Reagan Washington National (DCA)"],
    "Boston":["Logan International (BOS)"],
    "Miami": ["Miami International (MIA)"],
    "Orlando":["Orlando International (MCO)", "Orlando Sanford (SFB)"],
    "Denver": ["Denver International (DEN)"],
    "Phoenix": ["Phoenix Sky Harbor (PHX)", "Phoenix-Mesa Gateway (AZA)"],
    "Las Vegas": ["Harry Reid (LAS)"],
    "Philadelphia": ["Philadelphia International (PHL)"],
    "Detroit": ["Detroit Metropolitan (DTW)"],
    "Minneapolis":["Minneapolis-Saint Paul (MSP)"],
    "San Diego": ["San Diego International (SAN)"],
    "Tampa":["Tampa International (TPA)"],
    "Portland": ["Portland International (PDX)"],
    "Charlotte": ["Charlotte Douglas (CLT)"],
    "St. Louis": ["St. Louis Lambert (STL)"],
    "Baltimore": ["Baltimore/Washington (BWI)"],
    "Salt Lake City":["Salt Lake City International (SLC)"],
    "Austin": ["Austin-Bergstrom (AUS)"],
    "Nashville": ["Nashville International (BNA)"],
    "San Jose":["Norman Y. Mineta San Jose (SJC)"],
    "New Orleans": ["Louis Armstrong New Orleans (MSY)"],
    "Pittsburgh": ["Pittsburgh International (PIT)"],
    "Raleigh": ["Raleigh-Durham (RDU)"],
    "Cincinnati": ["Cincinnati/Northern Kentucky (CVG)"],
    "Cleveland":["Cleveland Hopkins (CLE)"],
    "Kansas City": ["Kansas City International (MCI)"],
    "Indianapolis":["Indianapolis International (IND)"],
    "Milwaukee": ["Milwaukee Mitchell (MKE)"],
    "Columbus":["John Glenn Columbus (CMH)"],
    "San Antonio": ["San Antonio International (SAT)"],
    "Sacramento": ["Sacramento International (SMF)"],
    "Fort Lauderdale":["Fort Lauderdale-Hollywood (FLL)"],
    "West Palm Beach": ["Palm Beach International (PBI)"],
    "Fort Myers": ["Southwest Florida International (RSW)"],
    "Jacksonville":["Jacksonville International (JAX)"],
    "Memphis": ["Memphis International (MEM)"],
    "Louisville": ["Louisville Muhammad Ali (SDF)"],
    "Richmond": ["Richmond International (RIC)"],
    "Norfolk": ["Norfolk International (ORF)"],
    "Omaha":["Eppley Airfield (OMA)"],
    "Oklahoma City": ["Will Rogers World (OKC)"],
    "Tulsa": ["Tulsa International (TUL)"],
    "Albuquerque":["Albuquerque International Sunport (ABQ)"],
    "Tucson": ["Tucson International (TUS)"],
    "El Paso": ["El Paso International (ELP)"],
    "Honolulu":["Daniel K. Inouye (HNL)"],
    "Anchorage": ["Ted Stevens Anchorage (ANC)"],
    "Boise": ["Boise Airport (BOI)"],
    "Reno":["Reno/Tahoe International (RNO)"],
    "Spokane": ["Spokane International (GEG)"],
    "Des Moines": ["Des Moines International (DSM)"],
    "Little Rock":["Bill and Hillary Clinton National (LIT)"],
    "Birmingham": ["Birmingham-Shuttlesworth (BHM)"],
    "Huntsville": ["Huntsville International (HSV)"],
    "Buffalo": ["Buffalo Niagara (BUF)"],
    "Hartford": ["Bradley International (BDL)"],
    "Providence":["Rhode Island T. F. Green (PVD)"],
    "Manchester": ["Manchester-Boston (MHT)"],
    "Dayton":["Dayton International (DAY)"],
    "Akron": ["Akron-Canton (CAK)"],
    "Grand Rapids": ["Gerald R. Ford (GRR)"],
    "Madison":["Dane County Regional (MSN)"],
    "Green Bay": ["Green Bay Austin Straubel (GRB)"],
    "Fargo": ["Hector International (FAR)"],
    "Sioux Falls":["Sioux Falls Regional (FSD)"],
    "Billings": ["Billings Logan (BIL)"],
    "Missoula": ["Missoula Montana (MSO)"],
    "Bozeman":["Bozeman Yellowstone (BZN)"],
    "Colorado Springs": ["Colorado Springs (COS)"],
    "Oakland":["San Francisco Bay Oakland (OAK)"],
    "Santa Ana": ["John Wayne (SNA)"],
    "Ontario": ["Ontario International (ONT)"],
    "Burbank": ["Hollywood Burbank (BUR)"],
    "Long Beach": ["Long Beach (LGB)"],
    "Fresno": ["Fresno Yosemite (FAT)"],
    "Wichita": ["Wichita Dwight D. Eisenhower (ICT)"],
    "Lexington":["Blue Grass (LEX)"],
    "Savannah": ["Savannah/Hilton Head (SAV)"],
    "Charleston": ["Charleston International (CHS)"],
    "Columbia":["Columbia Metropolitan (CAE)"],
    "Greenville": ["Greenville-Spartanburg (GSP)"],
    "Myrtle Beach": ["Myrtle Beach International (MYR)"],
    "Asheville":["Asheville Regional (AVL)"],
    "Greensboro": ["Piedmont Triad (GSO)"],
    "Roanoke": ["Roanoke-Blacksburg (ROA)"],
    "Pensacola":["Pensacola International (PNS)"],
    "Key West": ["Key West International (EYW)"],
    "Mobile": ["Mobile Regional (MOB)"],
    "Jackson":["Jackson-Medgar Wiley Evers (JAN)"],
    "Baton Rouge": ["Baton Rouge Metropolitan (BTR)"],
    "Shreveport": ["Shreveport Regional (SHV)"],
    "Corpus Christi":["Corpus Christi International (CRP)"]
}

# Generate a simulated flight database
_flight_databse = []
def generate_flight_database():
    global _flight_databse
    _flight_databse = []
    rng = random.Random(20260304) # Fixed the number 20260304 so that the flight database generated by running this function is the same every time, which is convenient for debugging and testing.
    cabin_factor = {
        "economy class": 1.00,
        "super economy class": 1.20,
        "business class": 2.10,
        "first class": 3.20,
    }
    cities = list(_city_airport_dict.keys())
    base_date = datetime.date.today()
    direct_flight = True
    for day_offset in range(31):
        flight_date = base_date + datetime.timedelta(days=day_offset)
        flight_date_str = flight_date.strftime("%Y-%m-%d")
        for departure_city in cities[:4]: # for the sake of execution efficiency, only generate flight data for the first 4 cities, in actual application, this restriction can be removed so that flight data for all cities can be generated
            for landing_city in cities[:4]: # for the sake of execution efficiency, only generate flight data for the first 4 cities, in actual application, this restriction can be removed so that flight data for all cities can be generated
                if departure_city == landing_city:
                    continue
                for airline in list(_airline_dict.keys())[:4]: # for the sake of execution efficiency, only generate flight data for the first 4 airlines, in actual application, this restriction can be removed so that flight data for all airlines can be generated
                    for i in range(8): # Each route has 8 flights per day per airline, spread out at different times of the day
                        dep_hour = rng.randint(0, 23)
                        dep_minute = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
                        departure_dt = datetime.datetime.combine(
                            flight_date,
                            datetime.time(hour=dep_hour, minute=dep_minute),
                        )
                        prefix = _airline_dict.get(airline, ["XX",1.00])[0]
                        flight_number = f"{prefix}{rng.randint(1000, 9999)}"
                        direct_or_connecting = "direct" if direct_flight else "connecting"
                        direct_flight = not direct_flight
                        duration_hours = rng.randint(2, 5) if direct_or_connecting == "direct" else rng.randint(4, 10)
                        duration_minutes = rng.choice([0, 10, 20, 30, 40, 50])
                        arrival_dt = departure_dt + datetime.timedelta(hours=duration_hours, minutes=duration_minutes)
                        route_base_price = rng.randint(380, 1800)
                        connecting_discount = 0.92 if direct_or_connecting == "connecting" else 1.00
                        cabin_infos = []
                        for cabin_name, factor in cabin_factor.items():
                            jitter = rng.uniform(0.95, 1.08)
                            price = int(route_base_price * _airline_dict.get(airline, ["XX",1.00])[1] * factor * connecting_discount * jitter)
                            price = max(200, (price // 10) * 10)
                            if cabin_name == "super economy class" and rng.random() < 0.7: # 70% of flights don't have super economy class class cabins
                                continue
                            if cabin_name == "first class" and rng.random() < 0.8: # 80% of flights don't have first class cabins
                                continue
                            cabin_infos.append({
                                "flight cabin class": cabin_name,
                                "price": price,
                            })
                        _flight_databse.append({
                            "airline": airline,
                            "flight number": flight_number,
                            "flight date": flight_date_str,
                            "flight departure time": departure_dt.strftime("%Y-%m-%d %H:%M"),
                            "flight landing time": arrival_dt.strftime("%Y-%m-%d %H:%M"),
                            "flight departure city": departure_city,
                            "flight landing city": landing_city,
                            "flight departure airport": rng.choice(_city_airport_dict[departure_city]),
                            "flight landing airport": rng.choice(_city_airport_dict[landing_city]),
                            "flight is direct or connecting": direct_or_connecting,
                            "cabin price information": cabin_infos,
                        })
generate_flight_database()

def get_time_slot_by_hhmm(hhmm):
    hour = int(hhmm.split(":")[0])
    r = []
    if hour <= 5 or hour >= 22:
        r += ["wee hours"]
    if 4 <= hour <= 9:
        r += ["early morning"]
    if 7 <= hour <= 12:
        r += ["mid-morning"]
    if 11 <= hour <= 14:
        r += ["noon"]
    if 12 <= hour <= 18:
        r += ["afternoon"]
    if 16 <= hour <= 20:
        r += ["evening"]
    if hour >= 19 or hour <= 6:
        r += ["night"]
    return r

# -------------------------------------------------------------------------------------
# The definition part of the ChatTree node (except the trigger node)
# -------------------------------------------------------------------------------------

# start node and related functions
def reset_flight_cabin_class(ctx): # When the user requests to cancel the restriction on cabin class, relevant processing will be carried out
    if ctx["{flight_cabin_class}"].state() != -1:
        del ctx["{flight_cabin_class}"]
def reset_flight_departure_airport(ctx): # When {flight_departure_city} changes, perform related processing
    if ctx["{flight_departure_city}"].as_str() in _city_airport_dict:
        if ctx["{flight_departure_airport}"].as_str() not in _city_airport_dict[ctx["{flight_departure_city}"].as_str()]:
            ctx["{flight_departure_airport}"] = "no limit to departure airport"
def reset_flight_landing_airport(ctx): # When {flight_landing_city} changes, perform related processing
    if ctx["{flight_landing_city}"].as_str() in _city_airport_dict:
        if ctx["{flight_landing_airport}"].as_str() not in _city_airport_dict[ctx["{flight_landing_city}"].as_str()]:
            ctx["{flight_landing_airport}"] = "no limit to landing airport"
def reset_flight_number(ctx): # When the user requests to reselect a flight number, or when fields such as {flight_date}, {flight_departure_city}, {flight_landing_city}, {flight_departure_airport}, {flight_landing_airport}, {airline}, {flight_is_direct_or_connecting}, {flight_departure_time_period} change, relevant processing is performed
    if ctx["{flight_number}"].state() == 1: # state of having value
        # First determine if {flight_number} has a value and its corresponding flight information and related InfoItems are consistent, then do not delete {flight_number}, otherwise delete it again
        flight_number = ctx["{flight_number}"].as_str()
        matched_flight = None
        for flight in _flight_databse:
            if flight["flight number"] == flight_number:
                matched_flight = flight
                break
        if matched_flight is not None:
            if (matched_flight["flight date"] == ctx["{flight_date}"].as_str() and
                matched_flight["flight departure city"] == ctx["{flight_departure_city}"].as_str() and
                matched_flight["flight landing city"] == ctx["{flight_landing_city}"].as_str() and
                (ctx["{flight_departure_airport}"].as_str() == "no limit to departure airport" or matched_flight["flight departure airport"] == ctx["{flight_departure_airport}"].as_str()) and
                (ctx["{flight_landing_airport}"].as_str() == "no limit to landing airport" or matched_flight["flight landing airport"] == ctx["{flight_landing_airport}"].as_str()) and
                (ctx["{airline}"].as_str() == "no limit to airline" or matched_flight["airline"] == ctx["{airline}"].as_str()) and
                (ctx["{flight_is_direct_or_connecting}"].as_str() == "no limit to direct or connecting" or matched_flight["flight is direct or connecting"] == ctx["{flight_is_direct_or_connecting}"].as_str()) and
                (ctx["{flight_departure_time_period}"].as_str() == "no limit to departure time period" or ctx["{flight_departure_time_period}"].as_str() in get_time_slot_by_hhmm(matched_flight["flight departure time"].split(" ")[-1]))):
                return # The flight information is consistent, do not delete {flight_number}
        del ctx["{flight_number}"] # Deletion here means that the user has mentioned it before, but now the value of the InfoItem has changed. The flight number mentioned before may not be applicable, so delete it and return it to the unmentioned state.
        if ctx["{flight_cabin_class}"].state() == 1:
            del ctx["{flight_cabin_class}"] # In the same way, if the flight number is deleted, the previously mentioned flight class may not be applicable, so delete it and return it to the unmentioned state.
start_node = chattree.create_node( "#start#", {
    "on_infoitem_change_trigger":[
        { "infoitem":["{flight_departure_city}"], "function":reset_flight_departure_airport },
        { "infoitem":["{flight_landing_city}"], "function":reset_flight_landing_airport },
        { "infoitem":["{flight_date}","{flight_departure_city}","{flight_landing_city}","{flight_departure_airport}","{flight_landing_airport}","{airline}","{flight_is_direct_or_connecting}","{flight_departure_time_period}"], "function":reset_flight_number }, # Note that there is no {flight_cabin_class} here
    ],
    "intent_trigger":[
        {"intent":"To reselect flight number", "intent_constraint":"and no specific flight number was specified.", "function":reset_flight_number},
        {"intent":"No more restrictions on flight class", "function":reset_flight_cabin_class},
    ]
})

# 询问flight date
ask_flight_date_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_date}",
    "infoitem_constraint":"The format must be converted to YYYY-MM-DD",
    "infoitem_modifier":["required","repeat","explicit"],
    "system_question":["Which day do you need to book a flight ticket?","What date do you need to book a ticket for?","May I ask what month and day you need to book your flight ticket?","<Ask the user for the flight date they need to book>"],
    "node_comment":"Must input {flight_date}", # Displayed in the generated HTML topology map (the same below)
})

# Determine whether the flight date is legal and related functions
def check_if_flight_date_invalid(ctx):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", ctx["{flight_date}"].as_str()):
        ctx["{flight_date_error_message}"] = "Flight date \"" + ctx["{flight_date}"].as_str() + "\" format error"
        return True # means invalid
    try:
        datetime.date.fromisoformat(ctx["{flight_date}"].as_str())
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if ctx["{flight_date}"].as_str() < curr_date:
            ctx["{flight_date_error_message}"] = "Flight date \"" + ctx["{flight_date}"].as_str() + "\" cannot be a date in the past"
            return True
        date1 = datetime.datetime.strptime(curr_date, "%Y-%m-%d")
        date2 = datetime.datetime.strptime(ctx["{flight_date}"].as_str(), "%Y-%m-%d")
        diff_days = (date2 - date1).days
        if diff_days > 30:
            ctx["{flight_date_error_message}"] = "Flight date \"" + ctx["{flight_date}"].as_str() + "\" cannot be a date after 30 days"
            return True
        return False # Indicates valid
    except ValueError:
        ctx["{flight_date_error_message}"] = "Flight date \"" + ctx["{flight_date}"].as_str() + "\" format error"
        return True
check_if_flight_date_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_flight_date_invalid,
    "node_comment":"Check the format and validity of the flight date. It must be in YYYY-MM-DD format\nand cannot be a date in the past or a date 30 days later.",
})

# Prompts user that flight date is wrong
inform_user_if_flight_date_invalid_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{flight_date_error_message}",
})

# After the above prompts, ask again about the flight date.
ask_flight_date_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{flight_date}",
})

# Inquire about flight departure city
ask_flight_departure_city_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_departure_city}",
    "infoitem_modifier":["required","repeat","explicit"],
    "infoitem_options":list(_city_airport_dict.keys()),
    "infoitem_options_modifier":['open_ended'],
    "system_question":"Which city does the flight depart from?",
    "node_comment":"Must input {flight_departure_city}",
})

# Determine whether the flight departure city is legal and related functions
def check_if_flight_departure_city_invalid(ctx):
    if ctx["{flight_departure_city}"].as_str() not in _city_airport_dict:
        ctx["{flight_city_error_message}"] = "Sorry, we do not support '" + ctx["{flight_departure_city}"].as_str() + "' as flight city"
        return True # indicate invalid
    return False # indicate valid
check_if_flight_departure_city_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_flight_departure_city_invalid,
    "node_comment":"Check if {flight_departure_city} is in the list of supported cities",
})

# Prompts user that flight departure city is wrong
inform_user_if_flight_departture_city_invalid_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{flight_city_error_message}",
})

# After the above prompts, ask again the city where the flight will take off.
ask_flight_departure_city_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{flight_departure_city}",
})

# Ask for flight landing city
ask_flight_landing_city_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_landing_city}",
    "infoitem_synonym":["{which_city_to_fly_to}"],
    "infoitem_modifier":["required","repeat","explicit"],
    "infoitem_options":list(_city_airport_dict.keys()), 
    "infoitem_options_modifier":['open_ended'],
    "system_question":"Which city are you flying to?",
    "node_comment":"Must input {flight_landing_city}",
})

# Determine whether the flight landing city is legal and related functions
def check_if_flight_landing_city_invalid(ctx):
    if ctx["{flight_landing_city}"].as_str() not in _city_airport_dict:
        ctx["{flight_city_error_message}"] = "Sorry, we do not support '" + ctx["{flight_landing_city}"].as_str() + "' as flight city"
        return True # means invalid
    return False # means valid
check_if_flight_landing_city_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_flight_landing_city_invalid,
    "node_comment":"Check if {flight_landing_city} is in the list of supported cities",
})

# Prompts user that flight landing city is wrong
inform_user_if_flight_landing_city_invalid_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{flight_city_error_message}",
})

# After the above prompts, ask again about the city where the flight will land.
ask_flight_landing_city_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{flight_landing_city}",
})

# Set the user preference value (if any) or the default value "no limit", and set the preference prompt content (if any)
def set_default_and_prefered_value(ctx):
    preference_tips = ""
    if ctx["{flight_departure_airport}"].state() != 1:
        ctx["{flight_departure_airport}"] = "no limit to departure airport"
    if ctx["{flight_landing_airport}"].state() != 1:
        ctx["{flight_landing_airport}"] = "no limit to landing airport"
    if ctx["{airline}"].state() != 1:
        ctx["{airline}"] = "American Airlines" # The assumption here is that the default value is set based on the habit of obtaining the user's historical orders based on the "Startup InfoItem" {User ID} and judging by certain deterministic rules.
        preference_tips += "American Airlines, "
    if ctx["{flight_is_direct_or_connecting}"].state() != 1:
        ctx["{flight_is_direct_or_connecting}"] = "direct" # The assumption here is that the default value is set based on the habit of obtaining the user's historical orders based on the "Startup InfoItem" {User ID} and judging by certain deterministic rules.
        preference_tips += "direct, "
    if ctx["{flight_departure_time_period}"].state() != 1:
        ctx["{flight_departure_time_period}"] = "no limit to departure time period"
    if preference_tips != "":
        ctx["{flight_booking_preference_tips}"] = "Based on your previous booking habits, we default to: \"" + preference_tips[:-1] + "\", "
    else:
        ctx["{flight_booking_preference_tips}"] = ""
    #-------------------------------- No preference prompts will be made below
    if ctx["{number_of_passengers}"].state() != 1:
        ctx["{number_of_passengers}"] = 1
set_default_and_prefered_value_node = chattree.create_node( "#activity#execute_script", {
    "function":set_default_and_prefered_value,
    "node_comment":"Set the default value 'no limit to ...' or user preference value (and set the preference prompt content):\n{flight_departure_airport}, {flight_landing_airport}, {airline}, {flight_is_direct_or_connecting}, {flight_departure_time_period}\n\nSet the default value: {number_of_passengers}=1",
})

# Determine whether there is a preference prompt that needs to be told to the user's condition node
judge_if_has_preference_tips_node = chattree.create_node( "#condition#script", {
    "function":lambda ctx: ctx["{flight_booking_preference_tips}"].as_str() != "",
})

# If there is a preference prompt that needs to be told to the user, tell the user
show_preference_tips_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{flight_booking_preference_tips}",
})

# Inquire about flight departure airport
ask_flight_departure_airport_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_departure_airport}",
    "infoitem_modifier":["repeat","explicit"],
    "infoitem_options" : [airport for airports in _city_airport_dict.values() for airport in airports] + ["no limit to departure airport"],
    "infoitem_options_modifier" : ['open_ended'],
    "system_question":"Which airport are you departing from?",
    "node_comment":"The default value or preference value has been preset before\nAI will not take the initiative to ask questions, but the user can take the initiative to mention it",
})

# Determine whether the flight departure airport is legal and related functions
def check_if_flight_departure_airport_invalid(ctx):
    if ctx["{flight_departure_airport}"].as_str() == "no limit to departure airport":
        return False # means valid
    assert ctx["{flight_departure_city}"].as_str() in _city_airport_dict
    if ctx["{flight_departure_airport}"].as_str() not in _city_airport_dict[ctx["{flight_departure_city}"].as_str()]:
        ctx["{flight_airport_error_message}"] = "Sorry, '" + ctx["{flight_departure_city}"].as_str() + "' currently only support " + str(_city_airport_dict[ctx["{flight_departure_city}"].as_str()])[1:-1] + " airport"
        return True # means invalid
    return False # means valid
check_if_flight_departure_airport_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_flight_departure_airport_invalid,
    "node_comment":"Check whether {flight_departure_airport} is in the corresponding airport list of {flight_departure_city}",
})

# Prompts user that flight departure airport is wrong
inform_user_if_flight_departure_airport_invalid_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{flight_airport_error_message}",
})

# Determine whether there is only one airport in the corresponding airport list of {flight_departure_city}. If there is only one airport, then directly set it to the value of {flight_departure_airport} without letting the user choose.
check_if_only_one_airport_for_departure_city_node = chattree.create_node( "#condition#script", {
    "function":lambda ctx: len(_city_airport_dict[ctx["{flight_departure_city}"].as_str()]) == 1,
    "node_comment":"Check whether there is only one airport in the corresponding airport list of {flight_departure_city}. If there is only one airport, then set it directly to the value of {flight_departure_airport} without letting the user choose.",
})

# Set the only airport corresponding to {flight_departure_city} to the value of {flight_departure_airport}
def set_only_one_airport_for_departure_city(ctx):
    ctx["{flight_departure_airport}"] = _city_airport_dict[ctx["{flight_departure_city}"].as_str()][0]
set_only_one_airport_for_departure_city_node = chattree.create_node( "#activity#execute_script", {
    "function":set_only_one_airport_for_departure_city,
    "node_comment":"Set the only airport corresponding to {flight_departure_city} to the value of {flight_departure_airport}",
})

# Determine whether there is more than one airport in the corresponding airport list of {flight_departure_city}. If there is more than one airport, then the user needs to be allowed to choose.
check_if_not_only_one_airport_for_departure_city_node = chattree.create_node( "#condition#script", {
    "function":lambda ctx: len(_city_airport_dict[ctx["{flight_departure_city}"].as_str()]) > 1,
    "node_comment":"Check whether there is more than one airport in the corresponding {flight_departure_city} airport list. If there is more than one airport, then the user needs to choose",
})

# Re-question flight departure airport
ask_flight_departure_airport_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{flight_departure_airport}",
})

# Inquire about the airport where your flight will land
ask_flight_landing_airport_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_landing_airport}",
    "infoitem_synonym":["{which_airport_to_fly_to}"],
    "infoitem_modifier":["repeat","explicit"],
    "infoitem_options" : [airport for airports in _city_airport_dict.values() for airport in airports] + ["no limit to landing airport"],
    "infoitem_options_modifier" : ['open_ended'],
    "system_question":"Which airport will you land at?",
    "node_comment":"The default value or preference value has been preset before\nAI will not take the initiative to ask questions, but the user can take the initiative to mention it",
})

# Determine whether the flight landing airport is legal and related functions
def check_if_flight_landing_airport_invalid(ctx):
    if ctx["{flight_landing_airport}"].as_str() == "no limit to landing airport":
        return False # means valid
    assert ctx["{flight_landing_city}"].as_str() in _city_airport_dict
    if ctx["{flight_landing_airport}"].as_str() not in _city_airport_dict[ctx["{flight_landing_city}"].as_str()]:
        ctx["{flight_airport_error_message}"] = "Sorry, '" + ctx["{flight_landing_city}"].as_str() + "' currently only supports " + str(_city_airport_dict[ctx["{flight_landing_city}"].as_str()])[1:-1] + " airport"
        return True # means invalid
    return False # means valid
check_if_flight_landing_airport_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_flight_landing_airport_invalid,
    "node_comment":"Check whether {flight_landing_airport} is in the corresponding airport list of {flight_landing_city}",
})

# Prompts user that flight landing airport is wrong
inform_user_if_flight_landing_airport_invalid_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{flight_airport_error_message}",
})

# Determine whether there is only one airport in the corresponding airport list of {flight_landing_city}. If there is only one airport, then set it directly to the value of {flight_landing_airport} without letting the user choose.
check_if_only_one_airport_for_landing_city_node = chattree.create_node( "#condition#script", {
    "function":lambda ctx: len(_city_airport_dict[ctx["{flight_landing_city}"].as_str()]) == 1,
    "node_comment":"Check whether there is only one airport in the corresponding airport list of {flight_landing_city}. If there is only one airport, then set it directly to the value of {flight_landing_airport} without letting the user select it.",
})

# Set the value of the only airport corresponding to {flight_landing_city} to {flight_landing_airport}
def set_only_one_airport_for_landing_city(ctx):
    ctx["{flight_landing_airport}"] = _city_airport_dict[ctx["{flight_landing_city}"].as_str()][0]
set_only_one_airport_for_landing_city_node = chattree.create_node( "#activity#execute_script", {
    "function":set_only_one_airport_for_landing_city,
    "node_comment":"Set the only airport corresponding to {flight_landing_city} to the value of {flight_landing_airport}",
})

# Determine whether there is more than one airport in the corresponding {flight_landing_city} airport list. If there is more than one airport, then the user needs to choose
check_if_not_only_one_airport_for_landing_city_node = chattree.create_node( "#condition#script", {
    "function":lambda ctx: len(_city_airport_dict[ctx["{flight_landing_city}"].as_str()]) > 1,
    "node_comment":"Check whether there is more than one airport in the corresponding airport list of {flight_landing_city}. If there is more than one airport, then the user needs to be allowed to choose.",
})

# Re-question flight landing airport
ask_flight_landing_airport_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{flight_landing_airport}",
})

# Ask the airline
ask_flight_airline_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{airline}",
    "infoitem_modifier":["repeat","explicit"],
    "infoitem_options":list(_airline_dict.keys()) + ["no limit to airline"],
    "infoitem_options_modifier": ["open_ended"],
    "system_question":"Which airline to choose for your flight?",
    "node_comment":"The default value or preference value has been preset before\nAI will not take the initiative to ask questions, but the user can take the initiative to mention it",
})

# Determine whether the airline is legal and related functions
def check_if_flight_airlines_invalid(ctx):
    if ctx["{airline}"].as_str() == "no limit to airline":
        return False # means valid
    if ctx["{airline}"].as_str() not in list(_airline_dict.keys()):
        ctx["{airline_error_message}"] = "Sorry, we do not currently support '" + ctx["{airline}"].as_str() + "' as an airline"
        return True # means invalid
    return False # means valid
check_if_flight_airlines_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_flight_airlines_invalid,
    "node_comment":"Check if {airline} is in the list of supported airlines",
})

# Prompt user airline error
inform_user_if_flight_airlines_invalid_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{airline_error_message}",
})

# After the above prompts, ask the airline again
ask_flight_airlines_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{airline}",
})

# Ask if the flight is direct or connecting
ask_flight_direct_or_connecting_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_is_direct_or_connecting}",
    "infoitem_modifier":["repeat","explicit"],
    "system_question":"Is the flight a direct flight or a connecting flight?",
    "node_comment":"The default value or preference value has been preset before\nAI will not take the initiative to ask questions, but the user can take the initiative to mention it",
})

# Intent branch: no limit to direct or connecting
flight_direct_or_connecting_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"no limit to direct or connecting",
})

# Intent branch: direct
flight_direct_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"direct",
})

# Intent branch: connecting
flight_connecting_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"connecting",
})

# Ask about the flight departure time slot
ask_flight_departure_time_slot_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_departure_time_period}",
    "infoitem_modifier":["repeat","explicit"],
    "system_question":"At what time of day would you like your flight to take off?",
    "node_comment":"The default value or preference value has been preset before\nAI will not take the initiative to ask questions, but the user can take the initiative to mention it",
})

# Intent branch: no limit to departure time slot
all_time_slot_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"no limit to departure time period",
} )

# Intent branch: wee hours
early_morning_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"wee hours",
})

# Intent branch: early morning
morning_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"early morning",
})

# Intent branch: mid-morning
late_morning_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"mid-morning",
})

# Intent branch: noon
noon_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"noon",
})

# Intent branch: afternoon
afternoon_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"afternoon",
})

# Intent branch: evening
evening_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"evening",
})

# Intent branch: night
night_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"night",
})

# Ask for flight numbers and related functions (preparation before asking: filter flights according to the conditions provided by the user, generate a list of qualified flights and prompt information, etc.)
def before_ask_flight_number(ctx):
    matched_flights = []
    for flight in _flight_databse:
        if flight["flight date"] != ctx["{flight_date}"].as_str():
            continue
        if flight["flight departure city"] != ctx["{flight_departure_city}"].as_str():
            continue
        if flight["flight landing city"] != ctx["{flight_landing_city}"].as_str():
            continue
        if ctx["{flight_departure_airport}"].as_str() != "no limit to departure airport" and flight["flight departure airport"] != ctx["{flight_departure_airport}"].as_str():
            continue
        if ctx["{flight_landing_airport}"].as_str() != "no limit to landing airport" and flight["flight landing airport"] != ctx["{flight_landing_airport}"].as_str():
            continue
        if ctx["{airline}"].as_str() != "no limit to airline" and flight["airline"] != ctx["{airline}"].as_str():
            continue
        if ctx["{flight_is_direct_or_connecting}"].as_str() != "no limit to direct or connecting" and flight["flight is direct or connecting"] != ctx["{flight_is_direct_or_connecting}"].as_str():
            continue
        if ctx["{flight_departure_time_period}"].as_str() != "no limit to departure time period":
            dep_hhmm = flight["flight departure time"].split(" ")[-1]
            if ctx["{flight_departure_time_period}"].as_str() not in get_time_slot_by_hhmm(dep_hhmm):
                continue
        matched_flights.append(flight)
    matched_flights.sort(key=lambda item: item["flight departure time"])
    # ---------
    structured_rows = []
    flight_number_list = []
    for flight in matched_flights:
        cabin_prices = []
        for cabin_item in flight["cabin price information"]:
            if ctx["{flight_cabin_class}"].state() != -1 and cabin_item["flight cabin class"] != ctx["{flight_cabin_class}"].as_str():
                continue
            cabin_prices.append({
                "flight cabin class": cabin_item["flight cabin class"],
                "price": cabin_item["price"],
            })
        if len(cabin_prices) == 0:
            continue
        if flight["flight number"] not in flight_number_list:
            flight_number_list.append(flight["flight number"])
        for item in cabin_prices:
            structured_rows.append({
                "display": (
                    flight["flight number"] + ", " + 
                    flight["airline"] + ", " + 
                    flight["flight departure time"].split(" ")[-1] + "-" + 
                    flight["flight landing time"].split(" ")[-1] + ", " + 
                    flight["flight departure city"] + " " + flight["flight departure airport"] + " --> " + 
                    flight["flight landing city"] + " " + flight["flight landing airport"] + ", " + 
                    flight["flight is direct or connecting"] + ", " + 
                    item["flight cabin class"] + ", " + 
                    "$" + str(item["price"])
                ),
                "user_input": flight["flight number"] + ", " + item["flight cabin class"],
            })
    filter_conditions = [
        f"{ctx['{flight_date}'].as_str()} Fly from {ctx['{flight_departure_city}'].as_str()} to {ctx['{flight_landing_city}'].as_str()}",
    ]
    if ctx["{flight_departure_airport}"].as_str() != "no limit to departure airport":
        filter_conditions.append(f"Departure airport is {ctx['{flight_departure_airport}'].as_str()}")
    if ctx["{flight_landing_airport}"].as_str() != "no limit to landing airport":
        filter_conditions.append(f"Landing airport is {ctx['{flight_landing_airport}'].as_str()}")
    if ctx["{airline}"].as_str() != "no limit to airline":
        filter_conditions.append(f"{ctx['{airline}'].as_str()}")
    if ctx["{flight_is_direct_or_connecting}"].as_str() != "no limit to direct or connecting":
        filter_conditions.append(f"{ctx['{flight_is_direct_or_connecting}'].as_str()}")
    if ctx["{flight_departure_time_period}"].as_str() != "no limit to departure time period":
        filter_conditions.append(f"departure time period is {ctx['{flight_departure_time_period}'].as_str()}")
    if ctx["{flight_cabin_class}"].state() == 1:
        filter_conditions.append(f"{ctx['{flight_cabin_class}'].as_str()}")
    ctx["{flight_number_selection_prompt_information}"] = "Flights filtered by: " + ", ".join(filter_conditions) + "."
    ctx["{flight_number_list}"] = flight_number_list
    if len(flight_number_list) > 0:
        ctx["{flight_number_selection_prompt_information}"] = ctx["{flight_number_selection_prompt_information}"].as_str() + " Prices do not include insurance, fuel tax, and passenger facility charges."
        ctx["{flight_number_selection_structured_information}"] = structured_rows
        ctx["{question_about_flight_number}"] = "Please select a flight number?"
    else:
        ctx["{flight_number_selection_structured_information}"] = ""
        ctx["{question_about_flight_number}"] = "But there are no flights that meet the conditions, please modify the previous conditions."
ask_flight_number_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_number}",
    "infoitem_modifier":["required","repeat","explicit"],
    "system_question":"{question_about_flight_number}",
    "execute_script_before_asking":before_ask_flight_number, # Pay attention to this attribute
    "inform_user_before_asking":"{flight_number_selection_prompt_information}",     # Pay attention to this attribute
    "structured_output_before_asking":"{flight_number_selection_structured_information}", # Pay attention to this attribute
    "node_comment":"Based on the following InfoItems, eligible flight numbers, prices and other related information are listed for users to choose from:\n"
              "{flight_date}、{flight_departure_city}、{flight_landing_city}、{flight_departure_airport}、{flight_landing_airport}\n"
              "{airline}、{flight_is_direct_or_connecting}、{flight_departure_time_period}、{flight_cabin_class}\n"
              "When {flight_cabin_class} has no value (that is, the user has not mentioned it yet), it means 'no limit'. It may filter out some flight numbers and also affect the display of prices and other related information;\n"
              "Other InfoItems may be 'no limit to ...'\n"
              "Then depending on the situation, you can choose to return several lines of text or return structured data for the client to generate UI Widget",
})

# Determine whether the flight number entered by the user is in the list of eligible flight numbers
check_flight_number_invalid_node = chattree.create_node( "#condition#script", {
    "function":lambda ctx: ctx["{flight_number}"].as_str().strip() not in ctx["{flight_number_list}"].as_json(),
    "node_comment":"Check whether the {flight_number} selected by the user is in the list of eligible flight numbers",
})

# If the flight number entered by the user is not in the list of eligible flight numbers, the user is prompted to select a flight number in the list
inform_user_select_listed_flight_number_node = chattree.create_node( "#inform_user#", {
    "inform_content":"The flight number '{flight_number}' you selected is not in the list, please select a flight number from the list",
})

# If the flight number entered by the user is not in the list of eligible flight numbers, then clear the {flight_cabin_class} corresponding to the flight number entered by the user.
exec_script_to_clear_flight_cabin_class_node = chattree.create_node( "#activity#execute_script", {
    "function":reset_flight_cabin_class,
    "node_comment":"The flight number selected by the user is not in the list. After prompting the user to select a flight number in the list, clear {flight_cabin_class}",
})

# After the above prompts, ask again for the flight number.
ask_again_flight_number_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{flight_number}",
})

# Inquire about flight class
ask_flight_cabin_class_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{flight_cabin_class}",
    "infoitem_modifier":["required","repeat","explicit"],
    "system_question":"What class of cabin should I choose?",
})

# Note that there is no "no limit to cabin class" intention branch here. {flight_cabin_class} means "no limit" when it has no value.

# Intent branch: economy class
economy_cabin_class_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"economy class",
})

# Intent branch: super economy class
super_economy_cabin_class_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"super economy class",
})

# Intent branch: business class
business_cabin_class_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"business class",
})

# Intent branch: first class
first_cabin_class_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"first class",
})

# Determine whether the flight class entered by the user is in the class list of the flight corresponding to the flight number currently selected by the user, and related functions
def check_if_flight_cabin_class_invalid(ctx):
    assert ctx["{flight_number}"].state() == 1
    chosen_flight = None
    for flight in _flight_databse:
        if flight["flight number"] == ctx["{flight_number}"].as_str():
            chosen_flight = flight
            break
    assert chosen_flight is not None
    available_cabin_class_list = [item["flight cabin class"] for item in chosen_flight["cabin price information"]]
    if ctx["{flight_cabin_class}"].as_str() not in available_cabin_class_list:
        ctx["{flight_class_error_message}"] = "Sorry, the flight number \"" + ctx["{flight_number}"].as_str() + "\" you selected does not support \"" + ctx["{flight_cabin_class}"].as_str() + "\". The available cabin classes for this flight are: " + ", ".join(available_cabin_class_list) + ", please select again"
        return True # means invalid
    return False # means valid
check_if_flight_cabin_class_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_flight_cabin_class_invalid,
    "node_comment":"Check whether the {flight_cabin_class} entered by the user is in the class list of the flight corresponding to the current {flight_number}",
})

# If the flight class entered by the user is not in the class list of the flight corresponding to the flight number currently selected by the user, the user will be prompted to choose again.
inform_user_if_flight_cabin_class_invalid_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{flight_class_error_message}",
})

# After the above prompts, ask again about the flight class level.
ask_flight_cabin_class_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{flight_cabin_class}",
})

# Ask about the number of passengers
ask_number_of_passengers_of_flight_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{number_of_passengers}",
    "infoitem_constraint":"Cannot be 0, must be a positive integer",
    "infoitem_modifier":["required","repeat"],
    "system_question":"How many tickets are required for this reservation?",
    "node_comment":"The default value 1 was previously preset\nAI will not proactively ask questions, but users can proactively mention them.",
})

# ask passenger information
ask_flight_passenger_info_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{passenger_information}",
    "infoitem_constraint":"It includes the following 5 fields: 1. 'name' / if it refers to the user himself then the content is set to 'the person who made the reservation', 2. 'document type' / the content can only be 'REAL ID' or 'passport', 3. 'document number', 4. 'document expiration date' / the format should be converted to YYYY-MM-DD, 5. 'is it a child'",
    "infoitem_modifier":["json","required"], # Pay attention to the json modifier here
    "system_question":"Please tell me the information of the passenger, including name, document type, document number, and validity period of the document. If it is a child, please explain.",
    "node_comment":"You can enter one or more passenger information",
})

# Determine the completeness and correctness of the number of passengers and passenger information, as well as related functions
def check_if_passenger_info_invalid(ctx):
    flight_passenger_info = ctx["{passenger_information}"].as_json()
    assert len(flight_passenger_info) >= 1
    if ctx["{number_of_passengers}"].as_num() < len(flight_passenger_info):
        ctx["{number_of_passengers}"] = len(flight_passenger_info)
    elif ctx["{number_of_passengers}"].as_num() > len(flight_passenger_info):
        ctx["{passenger_information_error_message}"] = "The number of passengers you previously entered (or defaulted to) is " + str(ctx["{number_of_passengers}"].as_num()) + ", but you only provided " + str(len(flight_passenger_info)) + " passenger information, please add"
        return True # means inconsistency
    for passenger in flight_passenger_info:
        assert "name" in passenger
        if "TMC customers" in passenger["name"] or passenger["name"] == "the person who made the reservation" : # "TMC customers" is the user_role automatically set after system recognition, and "the person who made the reservation" is set in the previous InfoItem constraints.
            passenger["name"] = "Thomas Smith" # It is assumed here that the name of the current user obtained based on the startup InfoItem {user_ID} is "Thomas Smith"
        if "document type" not in passenger or passenger["document type"].strip() == "":
            if passenger["name"] == "William White": # Hypothetical historical passenger names
                passenger["document type"] = "REAL ID" # It is assumed here that the relevant information about historical passengers is obtained
            else:
                ctx["{passenger_information_error_message}"] = "Passenger " + passenger["name"] + "'s 'document type' is not provided, please re-enter (please also check carefully for other possible errors)"
                return True # means invalid
        if "document number" not in passenger or passenger["document number"].strip() == "":
            if passenger["name"] == "William White":
                passenger["document number"] = "79283763267" # It is assumed here that the relevant information about historical passengers is obtained
            else:
                ctx["{passenger_information_error_message}"] = "Passenger " + passenger["name"] + "'s 'document number' is not provided, please re-enter (please also check carefully for other possible errors)"
                return True # means invalid
        if "document expiration date" not in passenger or passenger["document expiration date"].strip() == "":
            if passenger["name"] == "William White":
                passenger["document expiration date"] = "2027-01-01" # It is assumed here that the relevant information about historical passengers is obtained
            else:
                ctx["{passenger_information_error_message}"] = "Passenger " + passenger["name"] + "'s 'document expiration date' is not provided, please re-enter (please also check carefully for other possible errors)"
                return True # means invalid
        if "is it a child" not in passenger:
            if passenger["name"] == "William White": # Hypothetical historical passenger names
                passenger["is it a child"] = False # It may also be True. It is assumed here that the relevant information of historical passengers is obtained.
            else:
                passenger["is it a child"] = False # If not stated, it is assumed that it is not a child.
        # Check the correctness of the document number below. You can add more checking rules for the document number by following the example.
        if passenger["document type"].upper() == "REAL ID" and not re.match(r"^[a-zA-Z]{0,1}[0-9]{7,12}$", passenger["document number"].strip()):
            ctx["{passenger_information_error_message}"] = "Passenger " + passenger["name"] + " document number " + passenger["document number"] + " is incorrect, please re-enter (please also check carefully for other possible errors)"
            return True # means invalid
        # Next, check the validity of the validity period of the document. You can follow the example to add more checking rules for the validity period of the document.
        if passenger["document type"].upper() == "REAL ID" and datetime.datetime.strptime(passenger["document expiration date"], "%Y-%m-%d").date() < (datetime.datetime.now().date() + datetime.timedelta(days=90)): # It is assumed here that the validity period of the document must be 90 days after the current date
            ctx["{passenger_information_error_message}"] = "The document expiration date " + passenger["document expiration date"] + " of passenger " + passenger["name"] + " has expired or is insufficient, please re-enter (please also check carefully for other possible errors)"
            return True # means invalid
        # There can be more checks here, and you can all "follow the gourd's example"
    ctx["{passenger_information}"] = flight_passenger_info # Rewrite the possibly modified passenger information back to ctx
    return False # means valid
check_if_passenger_info_invalid_node = chattree.create_node( "#condition#script", {
    "function":check_if_passenger_info_invalid,
    "node_comment":"Check whether there are any errors in the passenger information and handle it accordingly",
})

# If there is an error in the passenger information, the user will be prompted with specific error information.
inform_user_passenger_info_invalidation_node = chattree.create_node( "#inform_user#", {
    "inform_content":"{passenger_information_error_message}",
})

# After the above prompts, ask again for passenger information.
ask_passenger_info_again_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{passenger_information}",
})

# Summarize booking information, prompt users, and confirm with users whether everything is correct
def get_all_flight_booking_info(ctx):
    def to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ["true", "1", "yes", "是", "对", "y", "t"]
        if isinstance(value, (int, float)):
            return value != 0
        return False
    passenger_count = ctx["{number_of_passengers}"].as_num()
    assert passenger_count >= 1
    passenger_info_list = ctx["{passenger_information}"].as_json()
    assert len(passenger_info_list) >= 1
    assert len(passenger_info_list) == passenger_count
    chosen_flight = None
    assert ctx["{flight_number}"].state() == 1
    for flight in _flight_databse:
        if flight["flight number"] == ctx["{flight_number}"].as_str():
            chosen_flight = flight
            break
    assert chosen_flight is not None
    assert ctx["{flight_cabin_class}"].state() == 1
    cabin_price = None
    for item in chosen_flight["cabin price information"]:
        if item["flight cabin class"] == ctx["{flight_cabin_class}"].as_str():
            cabin_price = int(item["price"])
            break
    assert cabin_price is not None
    fuel_tax_adult = 100
    fuel_tax_child = 50
    facility_charge_adult = 50
    facility_charge_child = 0
    passenger_lines = []
    total_ticket_price = 0
    total_fuel_tax = 0
    total_facility_charge = 0
    for idx, passenger in enumerate(passenger_info_list, start=1):
        name = passenger.get("name", f"passenger-{idx}")
        is_child = to_bool(passenger.get("is it a child", None))
        assert is_child is not None
        id_type = passenger.get("document type", None)
        assert id_type is not None
        id_number = passenger.get("document number", None)
        assert id_number is not None
        id_validity_date = passenger.get("document expiration date", None)
        assert id_validity_date is not None
        ticket_price = int(cabin_price * (0.5 if is_child else 1.0))
        fuel_tax = fuel_tax_child if is_child else fuel_tax_adult
        facility_charge = facility_charge_child if is_child else facility_charge_adult
        subtotal = ticket_price + fuel_tax + facility_charge
        total_ticket_price += ticket_price
        total_fuel_tax += fuel_tax
        total_facility_charge += facility_charge
        passenger_type = "child" if is_child else "adult"
        passenger_lines.append(
            f"{idx}. {name} ({passenger_type}, {id_type}, {id_number}, {id_validity_date}) : price ${ticket_price} + fuel tax ${fuel_tax} + passenger facility charges ${facility_charge} = sum ${subtotal}"
        )
    total_price = total_ticket_price + total_fuel_tax + total_facility_charge
    summary_lines = [
        f"[flight information] flight number : {chosen_flight['flight number']} ({chosen_flight['airline']}), {chosen_flight['flight date']}, {chosen_flight['flight departure city']} {chosen_flight['flight departure airport']} --> {chosen_flight['flight landing city']} {chosen_flight['flight landing airport']}, from {chosen_flight['flight departure time']} to {chosen_flight['flight landing time']}, {chosen_flight['flight is direct or connecting']}, {ctx["{flight_cabin_class}"].as_str()}. ",
        f"[passengers and fare details] " + ", ".join(passenger_lines) + ". ",
        f"[cost summary] total fare : ${total_ticket_price}, total fuel tax : ${total_fuel_tax}, total passenger facility charges : ${total_facility_charge}, total amount payable : ${total_price}.",
    ]
    ctx["{summary_of_air_ticket_booking_information}"] = "\n".join(summary_lines)
ask_if_all_flight_booking_info_correct_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{are_all_flight_booking_information_correct}",
    "infoitem_modifier":["required","fixed","implicit"],
    "system_question":"Please confirm whether these ticket booking information are correct?",
    "execute_script_before_asking":get_all_flight_booking_info,
    "inform_user_before_asking":"{summary_of_air_ticket_booking_information}",
})

# Intent branch: The flight booking information is not all correct
not_all_flight_booking_info_correct_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"The flight booking information is not all correct",
})

# Intent branch: The flight booking information is correct
all_flight_booking_info_correct_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"The flight booking information is correct",
})

# After the above "The flight booking information is not all correct" intention branch, ask again whether all the flight booking information is correct.
ask_again_if_all_flight_booking_info_correct_node = chattree.create_node( "#activity#ask_again", {
    "infoitem":"{are_all_flight_booking_information_correct}",
})

# After the above "The flight booking information is correct" intention branch, submit the order and obtain the function of the payment link (the implementation here is just an example, the actual situation may require calling a third-party API, etc.)
def submit_order_and_get_payment_link(ctx):
    # Submit order
    pass
    # Get payment link
    ctx["{payment_link}"] = "https://www.example.com/payment_link?order_id=123456"
submit_order_and_get_payment_link_node = chattree.create_node( "#activity#execute_script", {
    "function":submit_order_and_get_payment_link,
})

# Prompts the user that the order has been submitted successfully and provides a payment link
provide_payment_link_node = chattree.create_node( "#inform_user#", {
    "inform_content":"Your order has been submitted successfully. Please click the following link to pay within 3 hours: {payment_link}",
})

# -------------------------------------------------------------------------------------
# (Except for subsequent trigger nodes) topological structure, ">>" indicates the connection relationship between nodes. The connection relationship here also determines the flow of the dialogue.
# -------------------------------------------------------------------------------------

start_node >> [
    ask_flight_date_node >> check_if_flight_date_invalid_node >> inform_user_if_flight_date_invalid_node >> ask_flight_date_again_node,
    ask_flight_departure_city_node >> check_if_flight_departure_city_invalid_node >> inform_user_if_flight_departture_city_invalid_node >> ask_flight_departure_city_again_node,
    ask_flight_landing_city_node >> check_if_flight_landing_city_invalid_node >> inform_user_if_flight_landing_city_invalid_node >> ask_flight_landing_city_again_node,
    set_default_and_prefered_value_node,
    judge_if_has_preference_tips_node >> show_preference_tips_node,
    ask_flight_departure_airport_node >> check_if_flight_departure_airport_invalid_node >> inform_user_if_flight_departure_airport_invalid_node >> [
        check_if_only_one_airport_for_departure_city_node >> set_only_one_airport_for_departure_city_node,
        check_if_not_only_one_airport_for_departure_city_node >> ask_flight_departure_airport_again_node
    ],
    ask_flight_landing_airport_node >> check_if_flight_landing_airport_invalid_node >> inform_user_if_flight_landing_airport_invalid_node >> [
        check_if_only_one_airport_for_landing_city_node >> set_only_one_airport_for_landing_city_node,
        check_if_not_only_one_airport_for_landing_city_node >> ask_flight_landing_airport_again_node
    ],
    ask_flight_airline_node >> check_if_flight_airlines_invalid_node >> inform_user_if_flight_airlines_invalid_node >> ask_flight_airlines_again_node,
    ask_flight_direct_or_connecting_node >> [
        flight_direct_or_connecting_intent_node,
        flight_direct_intent_node,
        flight_connecting_intent_node,
    ],
    ask_flight_departure_time_slot_node >> [
        all_time_slot_intent_node,
        early_morning_intent_node,
        morning_intent_node,
        late_morning_intent_node,
        noon_intent_node,
        afternoon_intent_node,
        evening_intent_node,
        night_intent_node,
    ],
    ask_flight_number_node >> check_flight_number_invalid_node >> inform_user_select_listed_flight_number_node >> exec_script_to_clear_flight_cabin_class_node >> ask_again_flight_number_node,
    ask_flight_cabin_class_node >> [
        economy_cabin_class_intent_node >> check_if_flight_cabin_class_invalid_node >> inform_user_if_flight_cabin_class_invalid_node >> ask_flight_cabin_class_again_node,
        super_economy_cabin_class_intent_node >> check_if_flight_cabin_class_invalid_node,
        business_cabin_class_intent_node >> check_if_flight_cabin_class_invalid_node,
        first_cabin_class_intent_node >> check_if_flight_cabin_class_invalid_node,
    ],
    ask_number_of_passengers_of_flight_node,
    ask_flight_passenger_info_node >> check_if_passenger_info_invalid_node >> inform_user_passenger_info_invalidation_node >> ask_passenger_info_again_node,
    ask_if_all_flight_booking_info_correct_node >> [
        not_all_flight_booking_info_correct_intent_node >> ask_again_if_all_flight_booking_info_correct_node,
        all_flight_booking_info_correct_intent_node >> submit_order_and_get_payment_link_node >> provide_payment_link_node,
    ],
]

# -------------------------------------------------------------------------------------
# Trigger class node definition
# -------------------------------------------------------------------------------------

# trigger node
trigger_node = chattree.create_node( "#trigger#", {})

# Trigger intent : Indicates that the user does not need to book a flight and wants to end the dialogue.
no_need_to_book_flight_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"Indicates that there is no need to book a flight ticket",
    "intent_constraint":"Including but not limited to 'Others have already made the reservation', 'The trip has been cancelled', 'Take the high-speed rail instead', etc.",
})

# Confirm if you want to end the dialogue
confirm_really_want_to_end_dialogue_node = chattree.create_node( "#single_turn_interact#", {
    "infoitem":"{whether_sure_to_end_the_dialogue}",
    "infoitem_modifier":["required","fixed","explicit"],
    "system_question":"Are you sure you don't need to book a flight? Do you want to end the dialogue?",
})

# Intent branch: Confirm to end dialogue
confirm_end_dialogue_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"Confirm to end dialogue",
})

# Intent branch: Not confirm to end dialogue
not_confirm_end_dialogue_intent_node = chattree.create_node( "#user_intent#", {
    "intent":"Not confirm to end dialogue",
})

# After the above "Confirm to end dialogue" intent branches, actually end the dialogue
terminate_node = chattree.create_node( "#activity#terminate", {} )

# -------------------------------------------------------------------------------------
# The topology of the trigger node, ">>" indicates the connection relationship between nodes, and the connection relationship here also determines the flow of the dialogue.
# -------------------------------------------------------------------------------------

trigger_node >> [
    no_need_to_book_flight_intent_node >> confirm_really_want_to_end_dialogue_node >> [
        confirm_end_dialogue_intent_node >> terminate_node,
        not_confirm_end_dialogue_intent_node
    ]
]

# -------------------------------------------------------------------------------------
# The standard end of every python ChatTree file, the code that renders the dialog tree into an HTML file
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    chattree.render(__file__)