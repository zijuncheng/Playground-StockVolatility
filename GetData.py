import datetime as dt
import time
import intrinio_sdk 
from intrinio_sdk.rest import ApiException
import math
import settings

sort_order = 'desc' # str | Sort by date `asc` or `desc` (optional) (default to desc)
page_size = 100 # int | The number of results to return (optional) (default to 100)
next_page = '' # str | Gets the next page of data from a previous API call (optional)

#api specific
#prod key
API_KEY = settings.API_KEY
intrinio_sdk.ApiClient().configuration.api_key['api_key'] =API_KEY 
security_api = intrinio_sdk.SecurityApi()

def get_data(start_time,end_time,tags,ticker,days_in_between):
    #check how many 3 months (90 days) there are in between the start time and the end time
    
    #start_time, string, starting date of target data window of extraction, in the format of Y-m-d
    #end_time, string, ending date of target data window of extraction, in the format of Y-m-d
    #tags, list, it's the list of data in demand, check https://data.intrinio.com/data-tags for more details
    #ticker,string, ticker of the stock in demand
    #days_in_between, integer, number of days you want to extract in bulk in a single request, it is always smaller than timedelta(end_time - start_time)
    #the function will calculate how many requests it needs to make based on this number, and loop over each request for each tag
    
    start_date_tmp = dt.datetime.strptime(start_time,'%Y-%m-%d')
    end_date_tmp = dt.datetime.strptime(end_time,'%Y-%m-%d')
    dd = (end_date_tmp - start_date_tmp).days
    loop_count = math.ceil(dd/days_in_between)
    #start with the starttime then loop over each 3 months
    tmp_start = start_date_tmp
    tmp_start_str = tmp_start.strftime('%Y-%m-%d')
    tag_lst = {}
    for i in range(loop_count):
        tmp_end =  tmp_start + dt.timedelta(days = days_in_between)
        tmp_end_str = tmp_end.strftime('%Y-%m-%d')
        #get the variables for each day in the 3 months
        for t in tags:
            try:
                api_response_tmp = security_api.get_security_historical_data(ticker, t, start_date=tmp_start_str, end_date=tmp_end_str, sort_order=sort_order, page_size=page_size)
                api_response_tmp = api_response_tmp.historical_data_dict
                if i>0:
                    #combine with the existing data
                    api_response_tmp = api_response_tmp + tag_lst[t]
                #keep updating the list of data
                tag_lst[t] = api_response_tmp
            except ApiException as e:
                print("Exception when calling SecurityApi->get_security_historical_data: %s\r\n" % e)

         #update time
        tmp_start = tmp_end + dt.timedelta(days = 1)
        tmp_start_str = tmp_start.strftime('%Y-%m-%d')
     
    return tag_lst