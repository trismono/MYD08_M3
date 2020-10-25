#!/bin/sh

wget -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=3 "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MYD08_M3/2015/" --header "Authorization: Bearer dHJpc21vbm86ZEhKcGMyMXZibTlmWTJGdVpISmhMbXR5YVhOdVlVQjFibWt0YkdWcGNIcHBaeTVrWlE9PToxNjAzMzYwMTQ5OmNmNGMyNzBlNTVlMThiNWU4ZGI3ODE5MGIyZWRiN2QxNTA4OTc3ZTk" -P "/deos/trismonock/AEROSOL_PAPER/INPUT/"
