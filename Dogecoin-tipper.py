# -*- coding: utf-8 -*-
import praw
import time
import logging
from pprint import pprint

# Basic configuration
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
	messages = r.get_inbox('comments')
	
	for message in messages:
		op_subject = message.subject
		
		if op_subject = '+tip sent':
			op_text = message.body
			op_line = op_text.splitlines()[2]
			s=''.join(i for i in op_line if i.isdigit() or i == ".")
			
			return float(s)

# Check for donations, and thanks if any is present
def check_donations():
	prawTerms = ['+/u/dogetipbot']
	messages = r.get_unread('comments')
	
	for message in messages:
		op_text = message.body
		author = message.author

		has_praw = any(string in op_text for string in prawTerms)
		if has_praw and author.name != 'dogetipbot' and message.id not in open('already_done.txt').read():
			with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % message.id)
			ratelimit(message.reply, 'Thank you for tipping! This will help me cheer up other shibes, and will raise the amount i tip! very generosity')
			
			print ("Posted reply to a donation")
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
		parent = r.get_info(thing_id=parent_id)
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

print ("\tTip set at %.1f doge" % amount)
print ("\tEnough Doge for %.0f tips" % tips)

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

		if not has_praw_users and has_praw and balance >= amount and comment.id not in open('already_done.txt').read():
			
			if author.name in open('userlist.txt').read():
				print("User %s have already received tip!" % author.name)

			elif check_parent(comment.parent_id, comment.link_id):
				print("User %s commented a comment from the bot!" % author.name) 

			else:
				ratelimit(comment.reply, comment_text)
				balance -= amount
				tips = tips_remaining(balance)
				with open('userlist.txt', 'a') as userlist:
					userlist.write("%s\n" % author.name)

				print ("Posted comment. Balance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))
	
			with open('already_done.txt', 'a') as already_done:
				already_done.write("%s\n" % comment.id)
			

	# If 200 or more comments parsed, check the balance to account for tips and calculate new tip
	if (counter >= 200):
		print "\tChecking balance and new tip amount..."

		counter = 0
		balance = check_balance()

		amount = calculate_tip(balance)
		comment_text = ("You seem sad, have some doge!\n\n"
				"+/u/dogetipbot %.1f doge\n\n"
				"The amount i tip is entirely based on donations!\n\n"
				"^^I'm ^^a ^^bot ^^built ^^for ^^sad ^^shibes. ^^Please ^^consider ^^donating ^^to ^^keep ^^me ^^running! ^^[Creator](http://www.reddit.com/user/kaare8p/) ^^[GitHub](https://github.com/kaare8p/Dogecoin-tipper)\n" % amount)
		
		if balance < amount:
			print ("Exiting due to lack of funds")
			exit()
		
		tips = tips_remaining(balance)
		print ("\tBalance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))

	check_donations()
	print ("\tSleeping for 100 seconds")
	time.sleep(100)
