# -*- coding: utf-8 -*-
import praw
import time
import logging
from praw.errors import ExceptionList, APIException, InvalidCaptcha, InvalidUser, RateLimitExceeded
from requests.exceptions import HTTPError

# Basic configuration
logging.basicConfig(filename='tipper.log', level=logging.INFO)

user_agent = ("Dogecoin tipper 1.0 by /u/kaare8p"
		      "github.com/kaare8p/Dogecoin-tipper")
r = praw.Reddit(user_agent=user_agent)
user = 'DogeCoinTipperb'	
r.login(user, '')

# Avoid comments from these users
prawUsers =[user, 'dogetipbot', 'dogetipchecker', 'changetip', 'Dogeseedbot', 'Randomactofdogebot', 'TweetPoster', 'DogeHelpBot', 'DogeHelpBot', 'keywordtipbot', 'mohland']
prawWords =[":(", ":-(", ":'(", ":|"]

subreddit = r.get_subreddit('dogecoin')

counter = 0

#Log to file while printing to console
def log(level, msg):
	print msg
	if level == 'warning':
		logging.warning("%s:%s" % (time.ctime(), msg))
	else:
		logging.info("%s:%s" % (time.ctime(), msg))

# Ensures compliance with reddit api rules
def api_call(func, *args, **kwargs):
	while True:
		try:
			return func(*args, **kwargs)
			break
		except APIException as error:
			log('warning', "\tapi_call() failed: failed (%s)" % str(error))
			return False
		except ExceptionList as errorlist:
			for error in errorlist:
				log('warning', "\tapi_call() failed: failed (%s)" % str(error))
			return False
		except HTTPError as error:
			if str(error) == "403 Client Error: Forbidden":
				log('warning', "\tapi_call() failed: 403 forbidden")
				return False
			log('warning', "\tHTTP error %s raised, sleeping for 30 seconds" % str(error))
			pass
		except RateLimitExceeded as error:
			logging('warning', '\tRateLimitExceeded: Sleeping for %d seconds' % error.sleep_time)
			time.sleep(error.sleep_time)
			pass
		except Exception as error:
			raise
# Calculate the tip
def calculate_tip(balance):
	if balance <= 2000:
		return float(10)
	elif balance > 2000 and balance <= 10000:
		return balance/200
	elif balance > 10000:
		return float(50)

# Check how many doge is left on the bots account
def check_balance():
	messages = api_call(r.get_inbox, 'comments')
	for message in messages:
		op_subject = message.subject
		
		if op_subject == '+tip sent' or op_subject == '+tip received':
			op_text = message.body
			op_line = op_text.splitlines()[2]
			s=''.join(i for i in op_line if i.isdigit() or i == ".")
			
			return float(s)

# Check for donations, and thanks if any is present
def check_donations():
	prawTerms = ['+/u/dogetipbot']
	messages = api_call(r.get_unread, 'comments')
	
	for message in messages:
		op_text = message.body
		author = message.author

		has_praw = any(string in op_text for string in prawTerms)
		if has_praw and author.name != 'dogetipbot' and message.id not in open('already_done.txt').read():
			with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % message.id)
			api_call(message.reply, 'Thank you for tipping! This will help me cheer up other shibes, and will raise the amount i tip! very generosity')
			
			log('info', "\tPosted reply to a donation")
	return

def tips_remaining(balance):
	count = 0
	while balance > 10:
		if balance <= 2000:
			balance -= 10
			count += 1
		elif balance > 2000 and balance <= 10000:
			balance -= balance/200
			count += 1
		elif balance > 10000:
			balance -= 50
			count += 1
	return count

#Do not tip replies to own comments
def check_parent(parent_id, link_id):
	if parent_id != link_id:
		parent = api_call(r.get_info, thing_id=parent_id)
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
	comments = api_call(subreddit.get_comments, limit = 3000)
	# Check for sad comments, and tip 'amount' doge if found
	for comment in comments:
		counter += 1
		author = comment.author
		op_text = comment.body.lower()

		if author is None:
			has_praw_users = True
		else:
			has_praw_users = any(string in author.name for string in prawUsers)
		has_praw = any(string in op_text for string in prawWords)

		if not has_praw_users and has_praw and balance >= amount and comment.id not in open('already_done.txt').read():
			if author.name in open('userlist.txt').read():
				log('info', "\tUser %s have already received tip!" % author.name)

			elif check_parent(comment.parent_id, comment.link_id):
				log('info', "\tUser %s commented a comment from the bot!" % author.name) 

			else:
				api_call(comment.reply, comment_text)
				balance -= amount
				tips = tips_remaining(balance)
				with open('userlist.txt', 'a') as userlist:
					userlist.write("%s\n" % author.name)

				log('info', "\tPosted comment. Balance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))
	
			with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % comment.id)
			
	# If 200 or more comments parsed, check the balance to account for tips and calculate new tip
	if (counter >= 600):
		counter = 0
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

	check_donations()
	time.sleep(300)
