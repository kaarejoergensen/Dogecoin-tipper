# -*- coding: utf-8 -*-
import praw
import time
import logging

# Basic configuration
logging.basicConfig(filename='Dogecoin-tipper.log',level=logging.DEBUG)


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

# Ensures compliance with reddit api rules
def ratelimit(func, *args, **kwargs):
	while True:
		try:
			func(*args, **kwargs)
			break
		except praw.errors.RateLimitExceeded as error:
			print '\tSleeping for %d seconds' % error.sleep_time
			logging.info("\tSleeping for %d seconds" % error.sleep_time)
			time.sleep(error.sleep_time)

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
	prawTerms = ['+tip sent']
	messages = r.get_inbox('comments')
	
	for message in messages:
		op_subject = message.subject
		has_praw = any(string in op_subject for string in prawTerms)
		
		if has_praw:
			op_text = message.body
			op_line = op_text.splitlines()[2]
			s=''.join(i for i in op_line if i.isdigit() or i == ".")
			
			return float(s)

# Check for donations, and thanks if any is present
def check_tips():
	prawTerms = ['+/u/dogetipbot']
	messages = r.get_unread('comments')
	
	for message in messages:
		op_text = message.body
		author = message.author

		has_praw = any(string in op_text for string in prawTerms)
		if has_praw and author.name != 'dogetipbot' and message.id not in open('already_done').read():
			with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % message.id)
			ratelimit(message.reply, 'Thank you for tipping! This will help me cheer up other shibes, and will raise the amount i tip! very generosity')
			
			print ("Posted reply to a donation")
			logging.info("Posted reply to a donation")
	return
balance = check_balance()
amount = calculate_tip(balance)
tips = balance/amount

comment_text = ("You seem sad, have some doge!\n\n"
		"+/u/dogetipbot %.1f doge\n\n"
		"The amount i tip is entirely based on donations!\n\n"
		"^^I'm ^^a ^^bot ^^built ^^for ^^sad ^^shibes. ^^Please ^^consider ^^donating ^^to ^^keep ^^me ^^running! ^^[Creator](http://www.reddit.com/user/kaare8p/) ^^[GitHub](https://github.com/kaare8p/Dogecoin-tipper)\n" % amount)

print ("\tTip set at %.1f doge" % amount)
logging.info("\tTip set at %.1f doge" % amount)
print ("\tEnough Doge for %.0f tips" % tips)
logging.info("\tEnough Doge for %.0f tips" % tips)

# Main loop
while True:
	comments = subreddit.get_comments(limit = 100)
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

		if comment.id not in open('already_done.txt').read() and not has_praw_users and has_praw and balance >= amount:
			ratelimit(comment.reply, comment_text)
			balance -= amount
			tips = balance/amount
			with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % comment.id)

			print ("Posted comment. Balance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))
			logging.info("Posted comment. Balance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))

	# If 500 or more comments parsed, check the balance to account for tips and calculate new tip
	if (counter > 500):
		print "\tChecking balance and new tip amount..."
		logging.info("\tChecking balance and new tip amount...")

		counter = 0
		balance = check_balance()

		amount = calculate_tip(balance)
		comment_text = ("You seem sad, have some doge!\n\n"
				"+/u/dogetipbot %.1f doge\n\n"
				"The amount i tip is entirely based on donations!\n\n"
				"^^I'm ^^a ^^bot ^^built ^^for ^^sad ^^shibes. ^^Please ^^consider ^^donating ^^to ^^keep ^^me ^^running! ^^[Creator](http://www.reddit.com/user/kaare8p/) ^^[GitHub](https://github.com/kaare8p/Dogecoin-tipper)\n" % amount)
		
		if balance < amount:
			print ("Exiting due to lack of funds")
			logging.warning("Exiting due to lack of funds")
			exit()
		
		tips = balance/amount
		print ("\tBalance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))
		logging.info("\Balance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))

	check_tips()
	print ("\tSleeping for 100 seconds")
	logging.info("\tSleeping for 100 seconds")
	time.sleep(100)
