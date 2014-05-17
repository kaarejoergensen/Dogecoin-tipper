import praw
import time
from pprint import pprint

user_agent = ("Dogecoin tipper 1.0 by /u/kaare8p"
		      "github.com/kaare8p/Dogecoin-tipper")
r = praw.Reddit(user_agent=user_agent)

user = 'kaare8p'	
r.login(user, '')

already_done = set()
prawUsers =[user, 'dogetipbot', 'dogetipchecker']

subreddit = r.get_subreddit('rbottesting121')
counter = 0
counter2 = 0
amount = 5


def ratelimit(func, *args, **kwargs):
	while True:
		try:
			func(*args, **kwargs)
			break
		except praw.errors.RateLimitExceeded as error:
			print '\tSleeping for %d seconds' % error.sleep_time
			time.sleep(error.sleep_time)

def check_balance():
	prawTerms = ['history']
	r.send_message('dogetipbot', 'history', '+history')
	while True:
		time.sleep(10)

		messages = r.get_unread('comments')
		for message in messages:
			op_subject = message.subject
			has_praw = any(string in op_subject for string in prawTerms)
			if has_praw:
				op_text = message.body
				op_line = op_text.splitlines()[3]
				s=''.join(i for i in op_line if i.isdigit() or i == ".")
				return float(s)

balance = check_balance()

while 1 > 2:
	comments = subreddit.get_comments(limit = 100)
	for comment in comments:

		author = comment.author
		if (author is None):
			has_praw = True
		else:
			has_praw = any(string in author.name for string in prawUsers)

		if comment.id not in already_done and not has_praw and balance >= amount:
			counter += 1
			ratelimit(comment.reply, "I'm testing my Tipping bot, have some Doge!\n\n+/u/dogetipbot %d doge" % amount)
			already_done.add(comment.id)
			print ("Commented %s" % comment)
			print ("Number %d" % counter)
			balance -= amount

	if (counter - counter2 > 25):
		counter2 = counter
		balance = check_balance()
		if balance < amount:
			print "\tExiting due to lack of funds")
			exit()
	print ("\tSleeping for 10 seconds")	
	time.sleep(10)
