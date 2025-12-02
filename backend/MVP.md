Clone this repo using http replacing your workspace and ensureing that after changes are made it can be merged back into main, and does not have the error of a repo inside a repo https://github.com/Toasterfire-come/stock-scanner-complete/tree/v2mvp2.07

use the mvp.md and the to do list as well as the other files to finish all phases of the the mvp

Update both the real time price updater and daily EOD scanner to use one proxy setup and script that takes the list of proxys from https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&filterUpTime=90&filterLastChecked=10&speed=fast&limit=500&page=1&sort_by=lastChecked&sort_type=desc pulled at the start of market manager, delete all other proxy pullers and lists and only used the list from this api. Set the proxys as enviromental redir using something like 
os.environ['http_proxy] = proxy
as well as other features to ensure all trafic is redirected and use monotoring to switch this proxy upon the first rate limit or at 500  tickers 
then generate a list of all futures, indices, and nyse and nasdaq stocks included in hist data from yfinance then use this proxy setup to pull and iterate over this list untill we have the market data of these tickers and allows us to use that data to backtest so it needs to include setup for all time frames from 1 min 5min 15 min 1hr 4 hr and 1 day

