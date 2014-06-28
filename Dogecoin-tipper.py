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

# Search for smileys in subreddit dogecoin
prawWords =[":(", ":-(", ":'("]
subreddit = r.get_subreddit('dogecoin')

# Log to file while printing to console
def log(level, msg):
	print("%s:  %s" % (time.ctime(), msg))
	if level == 'warning':
		logging.warning("%s:  %s" % (time.ctime(), msg))
	else:
		logging.info("%s:  %s" % (time.ctime(), msg))

# Update comment text with new amount
def update_comment(amount): 
	return ("You seem sad, have some doge!\n\n"
		"+/u/dogetipbot %.1f doge\n\n"
		"The amount i tip is entirely based on donations!\n\n"
		"^^I'm ^^a ^^bot ^^built ^^for ^^sad ^^shibes." 
		" ^^[Creator](http://www.reddit.com/user/kaare8p/) ^^[GitHub](https://github.com/kaare8p/Dogecoin-tipper)"
		" ^^Make ^^me ^^ignore ^^your ^^future: ^^[Comments](%s), ^^[Threads](%s)."
		 % (amount, 'http://www.reddit.com/message/compose?to=DogeCoinTipperb&subject=unsubscribe&message=%2Bcomments', 'http://www.reddit.com/message/compose?to=DogeCoinTipperb&subject=unsubscribe&message=%2Bthreads'))

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
	counter = 0
	while balance > 10:
		if balance <= 2000:
			balance -= 10
			counter += 1
		elif balance > 2000 and balance <= 15000:
			balance -= balance/200
			counter += 1
		elif balance > 15000:
			balance -= 75
			counter += 1
	return counter

# Check how many doge is left on the bots account
def check_balance(send_message):
        result = None
        while result is None:
                try:
                        if send_message:
                                r.send_message('dogetipbot', 'history', '+history')
                        messages = r.get_inbox()
                        
                        for message in messages:
                                op_subject = message.subject
                                        
                                if op_subject == 're: history':
                                        op_text = message.body
                                        op_line = op_text.splitlines()[3]
                                        result=''.join(i for i in op_line if i.isdigit() or i == ".")
                                                
                                        return float(result)
                except (HTTPError, ConnectionError, RedirectException, Timeout, timeout) as error:
                        log('warning', "Check_balance()::Reddit is down (%s): Sleeping" % error)
                        time.sleep(30)
                        pass
                except RateLimitExceeded as error:
        	        log('warning', "Check_balance()::RateLimitExceeded, sleeping %d seconds" % error.sleep_time)
                        time.sleep(error.sleep_time)
                        pass
                except Exception as error:
        		log('warning', "Check_balance()::Error: %s" % error)
                        raise


# Check for donations and unsubscribe requests
def check_messages():
        try:
                counter = 0
                prawTerms = ['+/u/dogetipbot']
                messages = r.get_inbox(limit = 100)
                        
                for message in messages:
                        op_text = message.body
                        op_subject = message.subject
                        op_author = message.author

                        has_praw = any(string in op_text for string in prawTerms)

                        # If the message is a donation
                        if has_praw and op_author.name != 'dogetipbot' and message.id not in open('already_done.txt').read():
                                with open('already_done.txt', 'a') as already_done:
                                        already_done.write("%s\n" % message.id)
                                message.reply('Thank you for tipping! This will help me cheer up other shibes, and will raise the amount I tip! very generosity')
                                counter += 1
                                        
                                log('info', "Posted reply to a donation")

                        # If the message is an unsubscribe request
                        if op_subject == 'unsubscribe' and message.id not in open('already_done.txt').read():
                                if op_text == '+comments' or op_text == '+unsubscribe':
                                        with open('unsubscribe_comments.txt', 'a') as unsubscribe:
                                                unsubscribe.write("%s\n" % op_author.name)
                                        message.reply('You have been unsubscribed from the bot, all comments made by you will be ignored.')

                                        log('info', "Unsubscribed user %s from comments" % op_author.name)
                        
                                elif op_text == '+threads':
                                        with open('unsubscribe_threads.txt', 'a') as unsubscribe:
                                                unsubscribe.write("%s\n" % op_author.name)
                                        message.reply('You have been unsubscribed from the bot, all comments in threads made by you will be ignored.')

                                        log('info', "Unsubscribed user %s from threads" % op_author.name)

                                with open('already_done.txt', 'a') as already_done:
                                                already_done.write("%s\n" % message.id)

        except (HTTPError, ConnectionError, RedirectException, Timeout, timeout) as error:
                log('warning', "Check_messages()::Reddit is down (%s): Sleeping" % error)
                time.sleep(30)
                pass
        except RateLimitExceeded as error:
        	log('warning', "Check_messages()::RateLimitExceeded, sleeping %d seconds" % error.sleep_time)
                time.sleep(error.sleep_time)
                pass
        except Exception as error:
        	log('warning', "Check_messages()::Error: %s" % error)
                raise
        return counter

#Do not tip replies to own comments
def check_parent(parent_id, link_id):
        try:
                if parent_id != link_id:
                        parent = r.get_info(thing_id=parent_id)
                        op_author = parent.author
                        if op_author.name == user:
                                return True
        except (HTTPError, ConnectionError, RedirectException, Timeout, timeout) as error:
                log('warning', "Check_parent()::Reddit is down (%s): Sleeping" % error)
                time.sleep(30)
                pass
        except RateLimitExceeded as error:
        	log('warning', "Check_parent()::RateLimitExceeded, sleeping %d seconds" % error.sleep_time)
                time.sleep(error.sleep_time)
                pass
        except Exception as error:
        	log('warning', "Check_parent()::Error: %s" % error)
                raise
	return False

# Do not tip if author of link is unsubscribed
def check_op(link_id):
        try:
                submission = r.get_info(thing_id = link_id)
                op_author = submission.author.name

                if op_author in open('unsubscribe_threads.txt').read():
                        return True
        except (HTTPError, ConnectionError, RedirectException, Timeout, timeout) as error:
                log('warning', "Check_op()::Reddit is down (%s): Sleeping" % error)
                time.sleep(30)
                pass
        except RateLimitExceeded as error:
        	log('warning', "Check_op()::RateLimitExceeded, sleeping %d seconds" % error.sleep_time)
                time.sleep(error.sleep_time)
                pass
        except Exception as error:
        	log('warning', "Check_op()::Error: %s" % error)
                raise
	return False

# Update balance, sends message to dogetipbot if message is 1
def update_balance(message):
	balance = check_balance(message)

	if balance < calculate_tip(balance):
		log('warning', "Exiting due to lack of funds")
		exit()
		
	log('info', "\tBalance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips_remaining(balance), calculate_tip(balance)))

	return balance

# Initial balance and tip calculations
balance = update_balance(1)
check_balance_time = time.time()
amount = calculate_tip(balance)

comment_text = update_comment(amount)

# Main loop
while True:
        try:
                comments = subreddit.get_comments(limit = 100)
                # Check for sad comments, and tip 'amount' doge if found
                for comment in comments:
                        op_author = comment.author
                        op_text = comment.body.lower()

                        has_praw = any(string in op_text for string in prawWords)

                        if has_praw and balance >= amount and comment.id not in open('already_done.txt').read() and op_text != ':(':
                                # Deny if user has already received tip
                                if op_author.name in open('userlist.txt').read():
                                        log('info', "User %s already received tip!" % op_author.name)

                                # Deny if user is unsubscribed
                                elif op_author.name in open('unsubscribe_comments.txt').read():
                                        log('info', "User %s is unsubscribed from comments!" % op_author.name)

                                # Deny if user commented a comment from the bot
                                elif check_parent(comment.parent_id, comment.link_id):
                                        log('info', "User %s commented a comment from the bot!" % op_author.name) 

                                # Deny if op is unsubscribed
                                elif check_op(comment.link_id):
                                        log('info', "User %s commented on a thread whre op is unsubscribed!" % op_author.name)

                                # Else tip the user
                                else:
                                        comment.reply(comment_text)
                                        balance -= amount
                                        tips = tips_remaining(balance)
                                        with open('userlist.txt', 'a') as userlist:
                                                userlist.write("%s\n" % op_author.name)

                                        log('info', "Posted comment. Balance: %.1f Enough for %.0f tips, one tip is %.1f doge" % (balance, tips, amount))

                                with open('already_done.txt', 'a') as already_done:
                                        already_done.write("%s\n" % comment.id)
                        
                # If donation received, check the balance to account for it
                if (check_messages() != 0):
                        balance = update_balance(1)
                        check_balance_time = time.time()
                
                # If it's more than 10 minutes since +history message sent, check balance again
                if check_balance_time and time.time() - check_balance_time > 600:
                        balance = update_balance(0)
                        check_balance_time = 0
                        
                # If 500 or more users in userlist.txt delete file
                if sum(1 for line in open('userlist.txt')) > 500:
                        open('userlist.txt', 'w').close()

                        log('info', "Userlist.txt reset")

                # Calculate new tip
                amount = calculate_tip(balance)
                comment_text = update_comment(amount)	

                time.sleep(100)

        except (HTTPError, ConnectionError, RedirectException, Timeout, timeout) as error:
		log('warning', "Main()::Reddit is down (%s): Sleeping" % error)
		time.sleep(30)
		pass
	except RateLimitExceeded as error:
	        log('warning', "Main()::RateLimitExceeded, sleeping %d seconds" % error.sleep_time)
	        time.sleep(error.sleep_time)
	        pass
	except Exception as error:
		log('warning', "Main()::Error: %s" % error)
		raise
