from django.shortcuts import render
from django.http.response import HttpResponse
import arky.rest

ARK_FUND_SECRET = "not_much_of_a_secret_is_it_now"
ARK_FUND_CAMPAIGN_INIT_ADDR = "DNGWfoHyhYfmeJNqSPk2xb7BRm1btxyGaP"

# Begin code for encoding secret
import base64
def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

# End code for encoding secret


# Switch between different .net configurations for the remote ledgers
def use_permission_ledger():
	arky.rest.use("ark1")

def use_transaction_ledger():
	arky.rest.use("ark2")
# end

#Default ledger
use_permission_ledger()

def home(request):
	#Fetch all campaigns here, somehow
    return render(request, 'home.html')

def login(request):
	if request.method == "GET":
		if request.session.get('logged_in',False) == True:
			return render(request, 'home.html')
		else:
			return render(request, 'login.html')
	else:
		request.session['logged_in'] = True
		secret = request.POST['secret'].strip()
		request.session['secret'] = secret
		keys = arky.core.crypto.getKeys(secret)
		public_key = keys['publicKey']
		address = arky.core.crypto.getAddress(public_key)
		private_key = keys['privateKey']
		request.session['public_key'] = public_key.strip()
		request.session['privateKey'] = private_key.strip()
		request.session['address'] = address.strip()
		return render(request, 'home.html')	


def create_campaign(request):
	if request.session.get('logged_in',False) == False:
		return render(request, 'login.html')
	else:
		secret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
		keys = arky.core.crypto.getKeys(secret)
		public_key = keys['publicKey']
		address = arky.core.crypto.getAddress(public_key)
		private_key = keys['privateKey']
		encoded_secret = encode(ARK_FUND_SECRET, secret)
		campaign_info = request.POST['campaign_info'].trim()
		campaign_goal = request.POST['campaign_goal'].trim()
		campaign_date = request.POST['campaign_date'].trim()
		make_transaction(1, ARK_FUND_CAMPAIGN_INIT_ADDR, secret, encoded_secret)
		make_transaction(1, ARK_FUND_CAMPAIGN_INIT_ADDR, secret, campaign_info)
		make_transaction(1, ARK_FUND_CAMPAIGN_INIT_ADDR, secret, campaign_goal)
		make_transaction(1, ARK_FUND_CAMPAIGN_INIT_ADDR, secret, campaign_date)
		return render(request, 'home.html') #CHANGE THIS
def get_all_campaigns(request):
	#Campaign Blocks are present in ark1. Each campaign is given its own public
	pass



def get_all_blocks():
	all_transactions = []
	offset = 0
	limit = 50
	while True:
		transactions = arky.rest.GET.api.transactions(limit=limit, offset=offset*limit)
		all_transactions.extend(transactions['transactions'])
		if transactions['transactions'].size() < limit:
			break
		offset+=1
	return transactions





def make_transaction(amount, recipientId, secret, vendorField):
	arky.core.sendToken(amount=amount, recipientId=recipientId,secret=secret, vendorField=vendorField)





