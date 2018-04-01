from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import arky.rest
import requests
import random
import string
import re

ARK_FUND_SECRET = "not_much_of_a_secret_is_it_now"
ARK_FUND_CAMPAIGN_INIT_ADDR = "DNGWfoHyhYfmeJNqSPk2xb7BRm1btxyGaP" #Gets updated below.
TOP_SECRET = "help"
SKIP_LENGTH = 69


# Begin code for encoding with keys (AES is slower but better for this)
import base64
def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return str(base64.urlsafe_b64encode("".join(enc).encode()).decode())

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

# End code for encoding secret


# Switch between different .net configurations for the remote ledgers
def use_permission_ledger():
	arky.rest.use("ark1") # 109

def use_transaction_ledger():
	arky.rest.use("ark2")
# end



# Default ledger
use_permission_ledger()
keys = arky.core.crypto.getKeys(TOP_SECRET)
public_key = keys['publicKey']
address = arky.core.crypto.getAddress(public_key)
ARK_FUND_CAMPAIGN_INIT_ADDR = address
print(ARK_FUND_CAMPAIGN_INIT_ADDR)
# end default setting



# Connecting with PostGres for quick query
# Connecting with PostGres for quick query

def get_dictionary_for_encoded_secret(encoded_secret):
    resp = requests.get('http://13.93.225.109:8857/get_campaign?key=%s' %(encoded_secret)).json()
    return resp

def insert_key_value_pair(encoded_secret, campaign_name, campaign_info, campaign_goal, campaign_date):
    resp = requests.post('http://13.93.225.109:8857/create_campaign', data={"key": encoded_secret,"name": campaign_name, "description": campaign_info, "goal": campaign_goal})
    if resp.content=='success':
        return True
    else:
        return False
# print get_dictionary_for_encoded_secret('test')
# print insert_key_value_pair('test4', 'test4', 'test4', 100, '20180401000748')
#end



# BlockChain Helpers
def get_all_transactions():
	all_transactions = []
	offset = 0
	limit = 50
	while True:
		transactions = arky.rest.GET.api.transactions(limit=limit, offset=offset*limit)
		all_transactions.extend(transactions['transactions'])
		if len(transactions['transactions']) < limit:
			break
		offset+=1
	return sorted(all_transactions, key=lambda k: k['timestamp']) 

def get_all_transactions_with_sender(sender_id):
	all_transactions = []
	offset = 0
	limit = 50
	while True:
		transactions = arky.rest.GET.api.transactions(senderId = sender_id, limit=limit, offset=offset*limit)
		all_transactions.extend(transactions['transactions'])
		if len(transactions['transactions']) < limit:
			break
		offset+=1
	return sorted(all_transactions, key=lambda k: k['timestamp'])

def make_transaction(amount, recipientId, secret, vendorField):
	arky.core.sendToken(amount=amount, recipientId=recipientId,secret=secret, vendorField=vendorField)


def get_all_campaigns():
	all_campaigns = []
	transactions = get_all_transactions_with_sender(ARK_FUND_CAMPAIGN_INIT_ADDR)
	# newlist = sorted(list_to_be_sorted, key=lambda k: k['name']) 
	# transactions = arky.rest.GET.api.transactions(senderId=ARK_FUND_CAMPAIGN_INIT_ADDR, limit=50, offset=31)['transactions']
	campaign_set = set()
	# print(len(transactions))
	for txn in transactions:
		campaign_address = txn['recipientId']
		if campaign_address in campaign_set:
			continue
		campaign_set.add(campaign_address)
		if "vendorField" in txn and re.search('[a-zA-Z]', txn['vendorField']):
			dict_to_be_appended = get_dictionary_for_encoded_secret(txn['vendorField'])
			print(dict_to_be_appended)
			all_campaigns.append(dict_to_be_appended)
	skip_entries = 7
	for i in range(len(all_campaigns)):
		if "description" in all_campaigns[i]:
			all_campaigns[i]['description'] = all_campaigns[i]['description'][:256]+" ... "

	return all_campaigns[skip_entries:]

# def seed_campaign(address):
# 	make_transaction(100000000, address, TOP_SECRET, "SEED")

def init_campaign_with_data(encoded_secret, address, campaign_name, campaign_info, campaign_goal, campaign_date):
	make_transaction(1, address, TOP_SECRET, encoded_secret)
	# make_transaction(1, address, TOP_SECRET, campaign_name)
	# make_transaction(1, address, TOP_SECRET, campaign_info)
	make_transaction(1, address, TOP_SECRET, campaign_goal)
	make_transaction(1, address, TOP_SECRET, campaign_date)

def get_balance_from_address(address):
	return int(arky.rest.GET.api.accounts.getBalance(address=address)['balance'])

def get_balance_from_public_key(public_key):
	address = arky.core.crypto.getAddress(public_key)
	get_balance_from_address(address)


def get_balance(secret):
	keys = arky.core.crypto.getKeys(secret)
	public_key = keys['publicKey']
	get_balance_from_public_key(public_key)


def get_investors(secret):
	#get all people who sent money to this address
	keys = arky.core.crypto.getKeys(secret)
	public_key = keys['publicKey']
	address = arky.core.crypto.getAddress(public_key)
	transactions = arky.rest.GET.api.transactions(recipientId=address)['transactions']
	address_value_pair_list = []
	for tnx in transactions:
		address_value_pair_list.append((tnx['senderId'],tnx['amount']))
	return address_value_pair_list
	

# end





# Rest Handlers

def home(request):
	#Fetch all campaigns here, somehow
	context_dictionary = {}
	context_dictionary['campaigns'] = get_all_campaigns()
	return render(request, 'home.html', context_dictionary)

def login(request):
	if request.method == "GET":
		if request.session.get('logged_in',False) == True:
			return redirect('/')
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
		return redirect('/')


def logout(request):
	request.session['logged_in'] = False
	return redirect('/login/')

@csrf_exempt
def create_campaign(request):
	if request.method == "POST":
		if not request.session.get('logged_in',False) == False:
			return render(request, 'login.html')
		else:
			secret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
			keys = arky.core.crypto.getKeys(secret)
			public_key = keys['publicKey']
			address = arky.core.crypto.getAddress(public_key)
			private_key = keys['privateKey']
			encoded_secret = encode(ARK_FUND_SECRET, secret)
			campaign_name = request.POST['campaign_name'].strip()
			campaign_info = request.POST['campaign_info'].strip()
			campaign_goal = request.POST['campaign_goal'].strip()
			campaign_date = request.POST['campaign_date'].strip()
			init_campaign_with_data(encoded_secret, address, campaign_name, campaign_info, campaign_goal, campaign_date)
			context_dictionary = {}
			# context_dictionary['encoded_secret'] = encoded_secret
			insert_key_value_pair(encoded_secret, campaign_name, campaign_info, campaign_goal, campaign_date)
			context_dict = get_dictionary_for_encoded_secret(encoded_secret)
			return render(request, 'campaign.html', context_dictionary)
	else:
		if request.session.get('logged_in',False) == False:
			return render(request, 'login.html')
		else:
			return render(request, 'create_campaign.html')


def campaign(request):
	encoded_secret = request.GET['campaign_id']
	context_dictionary = get_dictionary_for_encoded_secret(encoded_secret)
	secret = decode(ARK_FUND_SECRET, encoded_secret)
	context_dictionary['funding_completed'] = get_balance(secret)
	investor_list = get_investors(secret)
	context_dictionary['investors'] = investor_list
	context_dictionary['per'] = (int(context_dictionary['funding_completed'])*100) // int(context_dictionary['goal'])
	return render(request, 'campaign.html', context_dictionary)


def fund(request):
	# Switch to transaction ledger
	use_transaction_ledger()
	secret = request.POST['secret'].strip()
	amount = request.POST['amount'].strip()
	recipient = request.POST['recipient'].strip()
	make_transaction(amount, recipient, secret, "Transaction")
	use_permission_ledger()
	context_dictionary = {}
	context_dictionary['alert'] = "Funds have successfully been transfered to our escrow"
	return render(request, 'home.html', context_dictionary)


# end


