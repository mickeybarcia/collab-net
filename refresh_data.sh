python data/charts_scrape.py 
python data/build_net.py 
curl -n -X DELETE https://api.heroku.com/apps/collab-net/dynos \n -H "Content-Type: application/json" \n -H "Accept: application/vnd.heroku+json; version=3" \n -H "Authorization: Bearer ${AUTH_TOKEN}"