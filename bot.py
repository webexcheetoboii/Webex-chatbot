################################################################################################
#Getting public URL on which NGROK is listening to

term_output_json = os.popen('curl http://127.0.0.1:4040/api/tunnels').read()   
tunnel_info = json.loads(term_output_json)
public_url = tunnel_info['tunnels'][0]['public_url']
#public_nonsecure_url = tunnel_info['tunnels'][1]['public_url']

################################################################################################

#Empty list to compare if the Webhook already exists
webhook_list=[]
WbxAPI = "https://webexapis.com/"
auth_token = "<BOT ACCESS TOKEN>"
headers = {
"Authorization": "Bearer " + auth_token,
"Content-Type": "application/json"
}
#Listing all Webhooks
all_webhooks = requests.get(WbxAPI + "webhooks", headers=headers)
#Encode as JSON
j_all_webhooks = all_webhooks.json()
#Check if the Webhook URL already exists for this bot
for webhook_exists in j_all_webhooks['items']:
    webhook_list.append(webhook_exists['targetUrl'])
if public_url in webhook_list: 
	print("Webhook already exists") 
else:
	print("Webhook does not exist - Creating")
	payload = {
	    "name": "BOT_NAME", "targetUrl": public_url, "resource": "messages", "event": "all"
	}
	try:
		create_webhook = requests.post(WbxAPI + "v1/webhooks", headers=headers, json=payload)
		if create_webhook.status_code == 200:
			print ("Webhook registration success")
	except ConnectionError:
		print ("Webhook registration error") 
    

################################################################################################
app = Flask(__name__)
@app.route("/", methods=[ 'GET', 'POST' ])
def index():
	# Get the json data
    WebexData = request.get_json()
    
    #Retrieving Data ids
    message_id = WebexData[ "data" ][ "id" ]
    room_id = WebexData["data"]["roomId"]
    user_id = WebexData["data"]["personId"]
    email = WebexData["data"]["personEmail"]
    #Gets details of a specific message
    message_info = requests.get(WbxAPI + "messages/" + message_id, headers=headers)
    message_info = message_info.json()

    #Gets the bots own information
    get_own_details = requests.get(WbxAPI + "people/me", headers=headers)
    get_own_details = get_own_details.json()
    #Bot cannot respond to my its messages
    if message_info['personId'] != get_own_details['id']:
    	message_text = message_info[ "text" ]
    	send_response = check_message(message_text, room_id)
    	send_response = requests.post(WbxAPI + "messages", headers=headers, json=send_response)
    else:
    	return "Ignore selfbot messages"
    return "successfully responded"
  
#Function to reply 
def check_message(message_text, room_id):

	if message_text == "help":
		payload = {"roomId": room_id,"markdown": "Hello I am a bot I can do this and that",}
	else:
		payload = {"roomId": room_id,"text": "Hello! I did not understand that",}
	return payload

################################################################################################
#Run the server app 
if __name__ == "__main__":
	#Do not keep debug=True in production
    app.run(host='127.0.0.1', port=5000, use_reloader=True, debug=True)
