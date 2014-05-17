import praw
import time
from pprint import pprint

def ratelimit(func, *args, **kwargs):
	while True:
		try:
			func(*args, **kwargs)
			break
		except praw.errors.RateLimitExceeded as error:
			print '\tSleeping for %d seconds' % error.sleep_time
			time.sleep(error.sleep_time)


def main():
	user_agent = ("Dogecoin tipper 1.0 by /u/kaare8p"
		      "github.com/kaare8p/Dogecoin-tipper")
	r = praw.Reddit(user_agent=user_agent)

	user = 'kaare8p'	
	r.login(user, 'askl12')

	already_done = set()
	prawUsers =[user, 'dogetipbot', 'dogetipchecker']

	subreddit = r.get_subreddit('rbottesting121')
	counter = 0
	while True:
		comments = subreddit.get_comments(limit = 19)
	
		for comment in comments:
	
			author = comment.author
			if (author is None):
				has_praw = True
			else:
				has_praw = any(string in author.name for string in prawUsers)

			if comment.id not in already_done and not has_praw:
				counter = counter + 1
				ratelimit(comment.reply, "I'm testing my Tipping bot, have some Doge!\n\n+/u/dogetipbot 5 doge")
				already_done.add(comment.id)
				print ("Commented %s" % comment)
				print ("Number %d" % counter)

		print ("\tSleeping for 10 seconds")	
		time.sleep(10)

if __name__ == '__main__':
	main()
