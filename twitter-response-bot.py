import logging
import os
import twitter
import yaml

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.CRITICAL, datefmt='%Y-%m-%d %H:%M:%S')

def main():
  
  try:
    
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, 'r') as f:
      config = yaml.load(f)
  
  except:
    
    logging.critical("Unable to load %s" % config_path)
    sys.exit()
  
  try:

    twitterApi = twitter.Api(
      consumer_key='%s' % config["twitter"]["consumer_key"],
      consumer_secret='%s' % config["twitter"]["consumer_secret"],
      access_token_key='%s' % config["twitter"]["access_token_key"],
      access_token_secret='%s' % config["twitter"]["access_token_secret"])
    
  except:
    
    logging.critical("Unable to connect to twitter.")
    sys.exit()

  try:

    highest_id = None
    
    search_kwargs = dict()
    search_kwargs["term"] = config["search_phrase"]
    search_kwargs["result_type"] = "recent"
    try:
      search_kwargs["since_id"] = config["twitter"]["since_id"]
    except:
      pass

    tweets = twitterApi.GetSearch(**search_kwargs)

    for tweet in tweets:
            
      # Skip tweets that contain our abort phrase
      try:
        if config["abort_phrase"] in tweet.text.lower():
          continue
      except:
        pass
      
      # Don't respond to retweets
      if tweet.retweeted_status:
        continue
      
      # Track the most recent tweet (highest id)
      if tweet.id > highest_id:
        highest_id = tweet.id
      
      # Craft response
      response = "@%s %s" % (tweet.user.screen_name, config["response"])
      twitterApi.PostUpdate(response, in_reply_to_status_id="%s" % tweet.id)
    
    with open(config_path, "w") as f:
      
      if highest_id is not None:
        config["twitter"]["since_id"] = highest_id
      
      yaml.dump(config, f)

  except Exception as e:
    
    print e.message

    
main()