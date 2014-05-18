import praw
import time
import logging

logging.basicConfig(filename='Dogecoin-tipper.log',level=logging.DEBUG)

user_agent = ("Dogecoin tipper 1.0 by /u/kaare8p"
		      "github.com/kaare8p/Dogecoin-tipper")
r = praw.Reddit(user_agent=user_agent)

user = 'DogeCoinTipperb'	
r.login(user, '')

already_done = set()
prawUsers =[user, 'dogetipbot', 'dogetipchecker', 'changetip', 'Dogeseedbot', 'Randomactofdogebot', 'TweetPoster']
prawWords =[":(", ":-(", ":'(", ":|"]

subreddit = r.get_subreddit('dogecoin')

counter = 0
amount = 9.8

comment_text = ("You seem sad, have some doge!\n\n"
		"+/u/dogetipbot %.1f doge\n\n"
		"Sorry for the small amount, every sad shibe have to get some!\n\n"
		"^^I'm ^^a ^^bot ^^built ^^for ^^sad ^^shibes. ^^Please ^^consider ^^donating ^^to ^^keep ^^me ^^running!\n" % amount)

def ratelimit(func, *args, **kwargs):
	while True:
		try:
			func(*args, **kwargs)
			break
		except praw.errors.RateLimitExceeded as error:
			print '\tSleeping for %d seconds' % error.sleep_time
			logging.info("\tSleeping for %d seconds" % error.sleep_time)
			time.sleep(error.sleep_time)

def check_balance():
	prawTerms = ['+tip sent']
	while True:
		messages = r.get_inbox('comments')
		for message in messages:
			op_subject = message.subject
			has_praw = any(string in op_subject for string in prawTerms)
			if has_praw:
				op_text = message.body
				op_line = op_text.splitlines()[2]
				s=''.join(i for i in op_line if i.isdigit() or i == ".")
				return float(s)

balance = check_balance()
tips = balance/amount

print ("\tEnough Doge for %.0f tips" % tips)
logging.info("\tEnough Doge for %.0f tips" % tips)

while True:
	comments = subreddit.get_comments(limit = 100)
	for comment in comments:
		
		counter += 1
		author = comment.author
		op_text = comment.body.lower()

		if author is None:
			has_praw_users = True
		else:
			has_praw_users = any(string in author.name for string in prawUsers)
		has_praw = any(string in op_text for string in prawWords)

		if comment.id not in already_done and not has_praw_users and has_praw and balance >= amount:
			ratelimit(comment.reply, comment_text)
			balance -= amount
			tips = balance/amount
			already_done.add(comment.id)

			print ("Posted comment. Balance: %.1f Enough for %.0f tips" % (balance, tips))
			logging.info("Posted comment. Balance: %.1f Enough for %.0f tips" % (balance, tips))

	if (counter > 500):
		print "\tChecking balance..."
		logging.info("\tChecking balance...")
		
		counter = 0
		time.sleep(20)
		balance = check_balance()
		
		if balance < amount:
			print ("Exiting due to lack of funds")
			logging.warning("Exiting due to lack of funds")
			exit()
		
		tips = balance/amount
		print ("\tEnough Doge for %.0f tips" % tips)
		logging.info("\tEnough Doge for %.0f tips" % tips)

	print ("\tSleeping for 100 seconds")
	logging.info("\tSleeping for 100 seconds")
	time.sleep(100)
