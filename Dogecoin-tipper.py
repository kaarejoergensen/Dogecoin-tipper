# -*- coding: utf-8 -*-
import praw
import time
import logging
from praw.errors import ExceptionList, APIException, InvalidCaptcha, InvalidUser, RateLimitExceeded, RedirectException
from requests.exceptions import HTTPError, ConnectionError, Timeout
from socket import timeout

# Basic configuration
logging.basicConfig(filename='tipper.log', level=logging.INFO)

user_agent = ("Dogecoin tipper 1.0 by /u/kaare8p"
		      "github.com/kaare8p/Dogecoin-tipper")
r = praw.Reddit(user_agent=user_agent)
user = 'DogeCoinTipperb'	
r.login(user, '')

# Avoid comments from these users
prawUsers =[user, 'dogetipbot', 'dogetipchecker', 'changetip', 'Dogeseedbot', 'Randomactofdogebot', 'TweetPoster', 'DogeHelpBot', 'DogeHelpBot', 'keywordtipbot', 'mohland', 'CreeperWithShades']
prawWords =[":(", ":-(", ":'(", ":|"]

subreddit = r.get_subreddit('dogecoin')

# Log to file while printing to console
def log(level, msg):
	print("%s:  %s" % (time.ctime(), msg))
	if level == 'warning':
		logging.warning("%s:  %s" % (time.ctime(), msg))
	else:
		logging.info("%s:  %s" % (time.ctime(), msg))

# Function for api-calls
def api(level, func, *args, **kwargs):
	while True:
		try:
			return func(*args, **kwargs)
			break
		except (HTTPError, ConnectionError, RedirectException, Timeout, timeout) as error:
			log('warning', "%s::Reddit is down (%s): Sleeping" % (level, error))
			time.sleep(30)
			pass
		except RateLimitExceeded as error:
	                log('warning', "%s::RateLimitExceeded, sleeping %d seconds" % (level, error.sleep_time))
	                time.sleep(error.sleep_time)
	                pass
		except Exception as error:
			log('warning', "%s::Error: %s" % (level, error))
			raise

# Calculate the tip
def calculate_tip(balance):
	if balance <= 2000:
		return float(10)
	elif balance > 2000 and balance <= 15000:
		return balance/200
	elif balance > 15000:
		return float(75)

# Calculate the amount of tips remaining
def tips_remaining(balance):
	count = 0
	while balance > 10:
		if balance <= 2000:
			balance -= 10
			count += 1
		elif balance > 2000 and balance <= 15000:
			balance -= balance/200
			count += 1
		elif balance > 15000:
			balance -= 75
			count += 1
	return count

# Check how many doge is left on the bots account
def check_balance():
	api('check_balance()', r.send_message, 'dogetipbot', 'history', '+history')
        messages = api('check_balance()', r.get_inbox)
	
	for message in messages:
		op_subject = message.subject
                        
		if op_subject == 're: history':
      			op_text = message.body
              		op_line = op_text.splitlines()[3]
	                result=''.join(i for i in op_line if i.isdigit() or i == ".")
                                
		        return float(result)

# Check for donations, and thanks if any is present
def check_donations():
	counter = 0
	prawTerms = ['+/u/dogetipbot']
        messages = api('check_donations()', r.get_inbox)
                
        for message in messages:
		op_text = message.body
		author = message.author

                has_praw = any(string in op_text for string in prawTerms)
                if has_praw and author.name != 'dogetipbot' and message.id not in open('already_done.txt').read():
	                with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % message.id)
                	api('check_donations', message.reply, 'Thank you for tipping! This will help me cheer up other shibes, and will raise the amount i tip! very generosity')
			counter += 1
                                
                       	log('info', "Posted reply to a donation")
	return counter


#Do not tip replies to own comments
def check_parent(parent_id, link_id):
	if parent_id != link_id:
        	parent = api('check_parent', r.get_info, thing_id=parent_id)
                author = parent.author
                if author.name == user:
	                return True
	return False

balance = check_balance()
amount = calculate_tip(balance)
tips = tips_remaining(balance)

comment_text = ("You seem sad, have some doge!\n\n"
		"+/u/dogetipbot %.1f doge\n\n"
		"The amount i tip is entirely based on donations!\n\n"
		"^^I'm ^^a ^^bot ^^built ^^for ^^sad ^^shibes. ^^Please ^^consider ^^donating ^^to ^^keep ^^me ^^running! ^^[Creator](http://www.reddit.com/user/kaare8p/) ^^[GitHub](https://github.com/kaare8p/Dogecoin-tipper)\n" % amount)

log('info', "\tTip set at %.1f doge" % amount)
log('info', "\tEnough Doge for %.0f tips" % tips)

# Main loop
while True:
	comments = api('Main', subreddit.get_comments, limit = 300)
	# Check for sad comments, and tip 'amount' doge if found
	for comment in comments:
		author = comment.author
		op_text = comment.body.lower()

		if author is None:
			has_praw_users = True
		else:
			has_praw_users = any(string in author.name for string in prawUsers)
		has_praw = any(string in op_text for string in prawWords)

		if not has_praw_users and has_praw and balance >= amount and comment.id not in open('already_done.txt').read():
			if author.name in open('userlist.txt').read():
				log('info', "User %s have already received tip!" % author.name)

			elif check_parent(comment.parent_id, comment.link_id):
				log('info', "User %s commented a comment from the bot!" % author.name) 

			else:
				api('Main', comment.reply, comment_text)
				balance -= amount
				tips = tips_remaining(balance)
				with open('userlist.txt', 'a') as userlist:
					userlist.write("%s\n" % author.name)

				log('info', "Posted comment. Balance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))

			with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % comment.id)
			
	# If donation received, check the balance to account for it and calculate new tip
	if (check_donations() != 0):
		balance = check_balance()

		amount = calculate_tip(balance)
		comment_text = ("You seem sad, have some doge!\n\n"
				"+/u/dogetipbot %.1f doge\n\n"
				"The amount i tip is entirely based on donations!\n\n"
				"^^I'm ^^a ^^bot ^^built ^^for ^^sad ^^shibes. ^^Please ^^consider ^^donating ^^to ^^keep ^^me ^^running! ^^[Creator](http://www.reddit.com/user/kaare8p/) ^^[GitHub](https://github.com/kaare8p/Dogecoin-tipper)\n" % amount)
		
		if balance < amount:
			log('info', "Exiting due to lack of funds")
			exit()
		
		tips = tips_remaining(balance)
		log('info', "\tBalance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))
	# If 500 or more users in userlist.txt delete file
	if sum(1 for line in open('userlist.txt')) > 500:
		open('userlist.txt', 'w').close()
		log('info', "Userlist.txt reset")

	time.sleep(300)
