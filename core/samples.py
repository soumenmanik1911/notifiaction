"""Sample notifications for testing classifier and Focus Mode."""

import random

# category must match core.categorize.CATEGORIES
SAMPLES = [
    # work (20)
    {"message": "Please send the weekly status report by 5 PM today.", "app": "Slack", "sender": "Team Lead", "category": "work", "urgency": "High"},
    {"message": "Client review meeting in 30 minutes, join the call.", "app": "Teams", "sender": "Project Manager", "category": "work", "urgency": "High"},
    {"message": "Can you update the project timeline and share by tomorrow morning?", "app": "Gmail", "sender": "Manager", "category": "work", "urgency": "Medium"},
    {"message": "Standup notes are posted in the channel.", "app": "Slack", "sender": "Scrum Bot", "category": "work", "urgency": "Low"},
    {"message": "Reminder: submit expense report by end of day Friday.", "app": "Gmail", "sender": "Finance Team", "category": "work", "urgency": "Medium"},
    {"message": "Build pipeline failed, please check when free.", "app": "Slack", "sender": "CI Bot", "category": "work", "urgency": "Medium"},
    {"message": "Draft presentation uploaded for feedback.", "app": "Teams", "sender": "Colleague", "category": "work", "urgency": "Low"},
    {"message": "Bhai call kar jaldi, client waiting on update.", "app": "WhatsApp", "sender": "Coworker", "category": "work", "urgency": "High"},
    {"message": "Kal tak assignment submit karna hai for the internal project review.", "app": "Slack", "sender": "Mentor", "category": "work", "urgency": "High"},
    {"message": "Please approve the leave request when you get time.", "app": "Gmail", "sender": "HR Desk", "category": "work", "urgency": "Low"},
    {"message": "Server maintenance window starts tonight.", "app": "Gmail", "sender": "IT Support", "category": "work", "urgency": "Medium"},
    {"message": "Meeting agenda shared for next week planning.", "app": "Teams", "sender": "Coordinator", "category": "work", "urgency": "Low"},
    {"message": "Urgent: production issue needs attention now.", "app": "Slack", "sender": "Oncall", "category": "work", "urgency": "High"},
    {"message": "Aaj ka report bhej do please before lunch.", "app": "WhatsApp", "sender": "Supervisor", "category": "work", "urgency": "Medium"},
    {"message": "Code review comments added to your pull request.", "app": "Gmail", "sender": "Reviewer", "category": "work", "urgency": "Low"},
    {"message": "Vendor contract renewal discussion scheduled tomorrow.", "app": "Teams", "sender": "Admin", "category": "work", "urgency": "Medium"},
    {"message": "Please join the all-hands meeting in 30 minutes.", "app": "Slack", "sender": "Office Bot", "category": "work", "urgency": "High"},
    {"message": "Quarterly goals document is ready to view.", "app": "Gmail", "sender": "Leadership", "category": "work", "urgency": "Low"},
    {"message": "Thoda jaldi feedback de do on the design draft.", "app": "Slack", "sender": "Designer", "category": "work", "urgency": "Medium"},
    {"message": "Travel request must be submitted by 5 PM today.", "app": "Gmail", "sender": "Travel Desk", "category": "work", "urgency": "High"},

    # family (20)
    {"message": "Mom: call me when you reach home.", "app": "WhatsApp", "sender": "Mom", "category": "family", "urgency": "Medium"},
    {"message": "Dad: dinner is ready, come soon.", "app": "WhatsApp", "sender": "Dad", "category": "family", "urgency": "Medium"},
    {"message": "Bhai call kar jaldi, need to talk.", "app": "WhatsApp", "sender": "Brother", "category": "family", "urgency": "High"},
    {"message": "Are we meeting grandparents this weekend?", "app": "WhatsApp", "sender": "Sister", "category": "family", "urgency": "Low"},
    {"message": "Mom: doctor appointment is tomorrow morning.", "app": "WhatsApp", "sender": "Mom", "category": "family", "urgency": "Medium"},
    {"message": "Family photo album link shared.", "app": "Gmail", "sender": "Cousin", "category": "family", "urgency": "Low"},
    {"message": "Papa asking if you booked the tickets.", "app": "WhatsApp", "sender": "Sister", "category": "family", "urgency": "Medium"},
    {"message": "Ghar jaldi aa jana, guests are coming.", "app": "WhatsApp", "sender": "Mom", "category": "family", "urgency": "Medium"},
    {"message": "Can you pick up groceries on your way home?", "app": "WhatsApp", "sender": "Dad", "category": "family", "urgency": "Low"},
    {"message": "Mom: sale at Big Bazaar", "app": "WhatsApp", "sender": "Mom", "category": "family", "urgency": "Low"},
    {"message": "Dadi wants to video call tonight.", "app": "WhatsApp", "sender": "Aunt", "category": "family", "urgency": "Low"},
    {"message": "Please confirm dinner plan by 7 PM today.", "app": "WhatsApp", "sender": "Brother", "category": "family", "urgency": "Medium"},
    {"message": "Mummy ne kaha hai khana time pe kha lena.", "app": "WhatsApp", "sender": "Sister", "category": "family", "urgency": "Low"},
    {"message": "Uncle is arriving at the station in 30 minutes.", "app": "WhatsApp", "sender": "Dad", "category": "family", "urgency": "High"},
    {"message": "Family group picnic photos uploaded.", "app": "WhatsApp", "sender": "Cousin", "category": "family", "urgency": "Low"},
    {"message": "Call me back, thoda urgent hai.", "app": "WhatsApp", "sender": "Mom", "category": "family", "urgency": "High"},
    {"message": "Birthday reminder for cousin next week.", "app": "Gmail", "sender": "Family Calendar", "category": "family", "urgency": "Low"},
    {"message": "Did you take your medicines today?", "app": "WhatsApp", "sender": "Dad", "category": "family", "urgency": "Medium"},
    {"message": "Aaj shaam ko ghar pe sab mil rahe hain.", "app": "WhatsApp", "sender": "Brother", "category": "family", "urgency": "Medium"},
    {"message": "Please send the address to aunt.", "app": "WhatsApp", "sender": "Mom", "category": "family", "urgency": "Low"},

    # shopping (20)
    {"message": "Your Amazon order has been shipped.", "app": "Amazon", "sender": "Amazon", "category": "shopping", "urgency": "Low"},
    {"message": "Flash sale ends tonight on selected items.", "app": "Flipkart", "sender": "Flipkart", "category": "shopping", "urgency": "Medium"},
    {"message": "Your Swiggy order is out for delivery.", "app": "Swiggy", "sender": "Swiggy", "category": "shopping", "urgency": "Medium"},
    {"message": "Zomato: your food will arrive in 20 minutes.", "app": "Zomato", "sender": "Zomato", "category": "shopping", "urgency": "Low"},
    {"message": "Price drop alert on your wishlist item.", "app": "Amazon", "sender": "Amazon Deals", "category": "shopping", "urgency": "Low"},
    {"message": "Limited time coupon expires today at midnight.", "app": "Flipkart", "sender": "Flipkart Offers", "category": "shopping", "urgency": "Medium"},
    {"message": "Your cart items are selling out fast.", "app": "Amazon", "sender": "Amazon", "category": "shopping", "urgency": "Low"},
    {"message": "Order delivered. Rate your experience.", "app": "Swiggy", "sender": "Swiggy", "category": "shopping", "urgency": "Low"},
    {"message": "Aaj raat tak sale hai, check kar lo.", "app": "Flipkart", "sender": "Flipkart", "category": "shopping", "urgency": "Medium"},
    {"message": "New arrivals in electronics you may like.", "app": "Amazon", "sender": "Amazon", "category": "shopping", "urgency": "Low"},
    {"message": "Zomato order ready for pickup in 10 minutes.", "app": "Zomato", "sender": "Zomato", "category": "shopping", "urgency": "Medium"},
    {"message": "Your refund has been initiated for recent order.", "app": "Flipkart", "sender": "Flipkart Support", "category": "shopping", "urgency": "Low"},
    {"message": "Grocery order scheduled for delivery tomorrow morning.", "app": "Amazon", "sender": "Amazon Fresh", "category": "shopping", "urgency": "Low"},
    {"message": "Swiggy: flat discount on your next meal today.", "app": "Swiggy", "sender": "Swiggy", "category": "shopping", "urgency": "Low"},
    {"message": "Payment pending for your cart, complete checkout by 9 PM today.", "app": "Flipkart", "sender": "Flipkart", "category": "shopping", "urgency": "Medium"},
    {"message": "Your package is arriving today.", "app": "Amazon", "sender": "Amazon", "category": "shopping", "urgency": "Medium"},
    {"message": "Weekend sale starts now on fashion.", "app": "Flipkart", "sender": "Flipkart", "category": "shopping", "urgency": "Low"},
    {"message": "Bhai order place kar diya kya? deal ends tonight.", "app": "WhatsApp", "sender": "Friend", "category": "shopping", "urgency": "Medium"},
    {"message": "Restaurant added a new combo you might like.", "app": "Zomato", "sender": "Zomato", "category": "shopping", "urgency": "Low"},
    {"message": "Delivery delayed, updated time shared in app.", "app": "Amazon", "sender": "Amazon", "category": "shopping", "urgency": "Low"},

    # college (20)
    {"message": "Assignment submission deadline is today at 11:59 PM.", "app": "Google Classroom", "sender": "Instructor", "category": "college", "urgency": "High"},
    {"message": "Kal tak assignment submit karna hai on the portal.", "app": "college portal", "sender": "Course Admin", "category": "college", "urgency": "High"},
    {"message": "Lecture slides for this week are uploaded.", "app": "Google Classroom", "sender": "Professor", "category": "college", "urgency": "Low"},
    {"message": "Midterm exam schedule posted on notice board.", "app": "college portal", "sender": "Exam Cell", "category": "college", "urgency": "Medium"},
    {"message": "Lab session moved to 2 PM tomorrow.", "app": "Teams", "sender": "Lab Instructor", "category": "college", "urgency": "Medium"},
    {"message": "Project report due Friday, submit via classroom.", "app": "Google Classroom", "sender": "Instructor", "category": "college", "urgency": "High"},
    {"message": "Library books due for return this week.", "app": "Gmail", "sender": "Library", "category": "college", "urgency": "Low"},
    {"message": "Guest lecture starts in 30 minutes in auditorium.", "app": "college portal", "sender": "Event Team", "category": "college", "urgency": "High"},
    {"message": "Attendance update available on portal.", "app": "college portal", "sender": "Admin", "category": "college", "urgency": "Low"},
    {"message": "Aaj class cancel hai, next class Monday ko.", "app": "WhatsApp", "sender": "Class Rep", "category": "college", "urgency": "Low"},
    {"message": "Quiz opens in 10 minutes on Google Classroom.", "app": "Google Classroom", "sender": "Instructor", "category": "college", "urgency": "High"},
    {"message": "Semester fee payment due Friday on college portal.", "app": "college portal", "sender": "Accounts Office", "category": "college", "urgency": "High"},
    {"message": "Workshop registration closes tomorrow.", "app": "Gmail", "sender": "Placement Cell", "category": "college", "urgency": "Medium"},
    {"message": "Notes share kar do yaar for today's lecture.", "app": "WhatsApp", "sender": "Classmate", "category": "college", "urgency": "Low"},
    {"message": "Internal marks have been published.", "app": "college portal", "sender": "Exam Cell", "category": "college", "urgency": "Low"},
    {"message": "Group project meeting in 30 minutes on Teams.", "app": "Teams", "sender": "Project Partner", "category": "college", "urgency": "High"},
    {"message": "Practical file submit karni hai by 5 PM today.", "app": "WhatsApp", "sender": "Class Rep", "category": "college", "urgency": "High"},
    {"message": "Scholarship form deadline is next Monday.", "app": "college portal", "sender": "Scholarship Office", "category": "college", "urgency": "Medium"},
    {"message": "New reading material added for next class.", "app": "Google Classroom", "sender": "Professor", "category": "college", "urgency": "Low"},
    {"message": "Campus event volunteer signup is open.", "app": "Gmail", "sender": "Student Council", "category": "college", "urgency": "Low"},

    # finance (20)
    {"message": "Your account was debited for a recent purchase.", "app": "bank SMS", "sender": "Bank Alert", "category": "finance", "urgency": "Low"},
    {"message": "Credit card bill payment due Friday.", "app": "Gmail", "sender": "Card Services", "category": "finance", "urgency": "High"},
    {"message": "UPI payment received successfully.", "app": "UPI apps", "sender": "UPI Alert", "category": "finance", "urgency": "Low"},
    {"message": "Monthly statement is now available.", "app": "Gmail", "sender": "Bank", "category": "finance", "urgency": "Low"},
    {"message": "EMI will be deducted tomorrow.", "app": "bank SMS", "sender": "Loan Center", "category": "finance", "urgency": "Medium"},
    {"message": "Low balance alert on your savings account.", "app": "bank SMS", "sender": "Bank Alert", "category": "finance", "urgency": "Medium"},
    {"message": "Salary credited to your account.", "app": "bank SMS", "sender": "Payroll", "category": "finance", "urgency": "Low"},
    {"message": "Your OTP is 000000. Do not share", "app": "bank SMS", "sender": "Bank Alert", "category": "finance", "urgency": "High"},
    {"message": "Your exam fee payment failed", "app": "UPI apps", "sender": "Payment App", "category": "finance", "urgency": "High"},
    {"message": "Auto-pay for subscription scheduled today.", "app": "Gmail", "sender": "Billing", "category": "finance", "urgency": "Medium"},
    {"message": "UPI se payment bhej diya hai, check kar lo.", "app": "WhatsApp", "sender": "Friend", "category": "finance", "urgency": "Low"},
    {"message": "Electricity bill due by 5 PM today.", "app": "Gmail", "sender": "Utility Provider", "category": "finance", "urgency": "High"},
    {"message": "Insurance premium payment reminder for this week.", "app": "Gmail", "sender": "Insurance", "category": "finance", "urgency": "Medium"},
    {"message": "Transaction declined, please retry.", "app": "UPI apps", "sender": "UPI Alert", "category": "finance", "urgency": "Medium"},
    {"message": "Cashback credited to your wallet.", "app": "UPI apps", "sender": "Payment App", "category": "finance", "urgency": "Low"},
    {"message": "Bhai paise transfer kar de, thoda urgent hai.", "app": "WhatsApp", "sender": "Brother", "category": "finance", "urgency": "High"},
    {"message": "Fixed deposit maturity notice for next month.", "app": "Gmail", "sender": "Bank", "category": "finance", "urgency": "Low"},
    {"message": "Card spending limit updated successfully.", "app": "bank SMS", "sender": "Card Services", "category": "finance", "urgency": "Low"},
    {"message": "Rent payment due Friday, do not forget.", "app": "Gmail", "sender": "Landlord", "category": "finance", "urgency": "High"},
    {"message": "Refund processed to your original payment method.", "app": "UPI apps", "sender": "Payment App", "category": "finance", "urgency": "Low"},

    # social (20)
    {"message": "Someone liked your recent photo.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "You have a new follower.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "Friend tagged you in a story.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "Group chat: movie plan tonight?", "app": "WhatsApp", "sender": "Friends Group", "category": "social", "urgency": "Low"},
    {"message": "New comment on your post.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "Bhai online aa, game start karte hain.", "app": "WhatsApp", "sender": "Friend", "category": "social", "urgency": "Low"},
    {"message": "Event invite: meetup this weekend.", "app": "Gmail", "sender": "Community Group", "category": "social", "urgency": "Medium"},
    {"message": "Your friend shared a reel with you.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "Train ticket booking reminder for trip tomorrow.", "app": "IRCTC", "sender": "IRCTC", "category": "social", "urgency": "Medium"},
    {"message": "IRCTC: chart prepared for your journey.", "app": "IRCTC", "sender": "IRCTC", "category": "social", "urgency": "Medium"},
    {"message": "Weekend cricket match in 30 minutes, are you coming?", "app": "WhatsApp", "sender": "Friends Group", "category": "social", "urgency": "Medium"},
    {"message": "Someone mentioned you in a comment.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "Party photos from last night are up.", "app": "Instagram", "sender": "Friend", "category": "social", "urgency": "Low"},
    {"message": "Aaj shaam ko call pe baat karte hain.", "app": "WhatsApp", "sender": "Friend", "category": "social", "urgency": "Low"},
    {"message": "IRCTC: ticket confirmation for your upcoming travel.", "app": "IRCTC", "sender": "IRCTC", "category": "social", "urgency": "Low"},
    {"message": "Live stream starting now from your favorite creator.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "Group poll: choose dinner spot by 6 PM today.", "app": "WhatsApp", "sender": "Friends Group", "category": "social", "urgency": "Medium"},
    {"message": "Friend request from a classmate.", "app": "Instagram", "sender": "Instagram", "category": "social", "urgency": "Low"},
    {"message": "IRCTC: boarding reminder for train departing in 2 hours.", "app": "IRCTC", "sender": "IRCTC", "category": "social", "urgency": "High"},
    {"message": "Kal milte hain, plan confirm kar de.", "app": "WhatsApp", "sender": "Friend", "category": "social", "urgency": "Low"},
]

_bags = {}
_last = {}


def _key(category):
    return category if category else "__all__"


def _pool(category):
    if category:
        return [s for s in SAMPLES if s["category"] == category]
    return list(SAMPLES)


def next_sample(category=None, last=None):
    """Return a sample from a shuffle bag; no repeats until exhausted, never same twice in a row."""
    key = _key(category)
    pool = _pool(category)
    if not pool:
        return None
    bag = _bags.get(key)
    if not bag:
        bag = list(pool)
        random.shuffle(bag)
        _bags[key] = bag
    prev = last if last is not None else _last.get(key)
    # avoid returning same as prev twice in a row
    if len(bag) == 1:
        pick = bag.pop()
        if prev is not None and pick is prev and len(pool) > 1:
            # refill to find different
            bag = [s for s in pool if s is not prev]
            random.shuffle(bag)
            pick = bag.pop()
    else:
        pick = bag.pop()
        if prev is not None and pick is prev:
            other = bag.pop()
            bag.append(pick)
            random.shuffle(bag)
            pick = other
    if not bag:
        bag = list(pool)
        random.shuffle(bag)
        _bags[key] = bag
    _last[key] = pick
    return pick
