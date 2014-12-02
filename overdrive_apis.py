from local_settings import OD_API_CLIENT_KEY, OD_API_SECRET_KEY
import requests
import base64
import json

def log_into_overdrive():
	""" Get the OverDrive Client Credentials

	"""
	print "in log_into_overdrive function \n"

	overdrive_client_app_fields = {}

	keys = '%s:%s' % (OD_API_CLIENT_KEY, OD_API_SECRET_KEY)
	encoded_keys = base64.b64encode(keys)
	od_oauth_url = 'https://oauth.overdrive.com/token'
	headers = {'Host' : 'oauth.overdrive.com',
				'Authorization' : 'Basic %s' % encoded_keys,
				'Content-Type' : 'application/x-www-form-urlencoded;charset=UTF-8'}
	payload ={}
	payload = {'grant_type' : 'client_credentials'}
	response = requests.post(od_oauth_url, data=payload, headers=headers)
	""" add logic to handle error > 200 or 201 

    print response.status_code, "  ==  ", response.reason
    if response.status_code > 201:
        flash(("Action was not successful. %s == %s\n") % 
                (response.status_code, response.reason))
        return render_template('login.html')
    elif response.status_code == 200:
        return redirect('/main')
        client_credentials = response.content
    elif response.status_code == 201:
        print "Post to get access token was successful"
        return redirect('/main')

	"""

	response_data = json.loads(response.content)
	print " overdrive access token = ", response_data['access_token'], "\n"

	overdrive_client_app_fields['url'] = response.url
	overdrive_client_app_fields['access_token'] = response_data['access_token']

	return overdrive_client_app_fields, response
#end def

def get_od_books(search_criteria, od_library_rows):
	""" get books for the given overdrive library rows

	"""
	print " in get_od_books "
	book_lists = []
	overdrive_client_app_fields, response = log_into_overdrive()
	access_token = overdrive_client_app_fields['access_token']
	print response.status_code, "  ==  ", response.reason
	if response.status_code > 201:
	    flash(("Action was not successful. %s == %s\n") % 
	            (response.status_code, response.reason))
	elif response.status_code == 200 or response.status_code == 201:
	    client_credentials = response.content
	    print "Post to get access token was successful"
	#end 

	for library_fields in od_library_rows:
		book_list = []
		product_url, headers = get_library_product_url(library_fields, 
														access_token)
		book_list = search_for_books(search_criteria, product_url, headers)
		book_lists.extend(book_list)
	#end for
	print " number of books in book list == ", len(book_lists), "\n"
	return book_lists

#end def

def get_library_product_url(library_fields, access_token):
	print "in get library product url\n"
	headers = {'Host' : 'api.overdrive.com',
	'Authorization' : 'Bearer %s' % access_token,
	'User-agent' : 'BookBlend', 'X-Forwarded-For' : '73.189.218.224'}
	lib_url = "https://" + library_fields['url']

	lib_response_data = requests.get(lib_url, headers=headers)
	if lib_response_data.status_code > 201:
	    flash(("Action was not successful. %s == %s\n") % 
	            (lib_response_data.status_code, lib_response_data.reason))
	elif lib_response_data.status_code == 200 or lib_response_data.status_code == 201:
	    print "Get request to get the Library product was successful", "\n"
	#end if

	lib_response = json.loads(lib_response_data.content)
	product_url = lib_response['links']['products']['href']
	return product_url, headers
#end def

def search_for_books(search_criteria, product_url, headers):
	""" This gets a list of books from Overdrive

	Access a full list of titles of ebooks
	Navigate through paginated products using hypermedia links
	Filter results to return specific or sorted lists of titles

	"""
	print "od api in search_for_books  "
	list_of_books = []
	list_book = []
	q = search_criteria
	limit = 300		# 25 by default 300 max
	offset = 0		# number of titles to skip
	formats = ""
	sort = "Author:desc" 		# :desc
	lastupdatetime = "" 
	series = "" 
	search_parms = "?q=%s&limit=%s&offset=0&formats=%s&sort=%s" % (q, limit, 
																   formats, 
																   sort)
	od_url="%s%s" % (product_url, search_parms)

	print "overdrive url = ", od_url, "\n"
	od_url = od_url.replace(' ', '%20')
	book_response = requests.get(od_url, headers=headers)

	print "book search response == ", book_response, "reason = ", book_response.reason, "\n"
	if book_response.status_code == 401:
	    print "Patron is not authorize to use this library == ", od_url, "\n"
	elif book_response.status_code > 201:
		print "Get request failed == ", book_response.reason
	elif book_response.status_code == 200 or book_response.status_code == 201:
		print "Get request to get the a list of books was successful", "\n"

		book_response_data = json.loads(book_response.content)
		print "OverDrive book count == ", book_response_data['totalItems'], "\n"

		if book_response_data['totalItems'] > 0:
			products = book_response_data['products']
			for product in products:
				book_data = {}	
				book_data['images'] = product['images']['thumbnail']['href']
				book_data['title'] = product['title']
				book_data['author'] = product['primaryCreator']['name']
				book_data['availableToDownload'] = product['links']['availability']['href']
				book_data['id'] = product['id']
				book_data['metadata'] = product['links']['metadata']['href']
				book_data['origin'] = 'ODCOM'
				list_book = [book_data]
				list_of_books.extend(list_book)
			#end for
		#end if
	#end if

	return list_of_books
# end def

def get_checkout_data():
	list_of_books = []
	data = [ {u'primaryCreator': {u'role': u'Author', u'name': u'Wilkie Collins'},
			  u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/dc14453f-d6b4-436a-a3e9-2526c33ca47d/availability', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/dc14453f-d6b4-436a-a3e9-2526c33ca47d/metadata', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'title': u'The Woman in White', 
			  u'breifSynopsis': u'The Woman in White is credited with being the first of the sensation novels, and one of the finest examples of the genre. A young woman\'s husband defrauds her of her fortune, her identity and eventually her sanity. She is saved by her sister and a loyal man who loves her, and her two rescuers attempt to expose her husband. They meet a woman dressed all in white whose fate seems curiously intertwined with that of the young woman. In the tradition of the sensation novel, the story contravenes boundaries of class, identity and the private and public spheres.',
			  u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/2389-1/{DC14453F-D6B4-436A-A3E9-2526C33CA47D}Img200.jpg', u'type': u'image/jpeg'}}, 
			  u'id': u'dc14453f-d6b4-436a-a3e9-2526c33ca47d',
			  u'expires': u'17 days' 
				},
			 {u'primaryCreator': {u'role': u'Author', u'name': u'Sandra Brown'}, 
			  u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/0a8b4d8e-fd32-41ae-b6a1-6fb87362622c/availability', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/0a8b4d8e-fd32-41ae-b6a1-6fb87362622c/metadata', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'title': u'Breath of Scandal', 
			  u'breifSynopsis': u'On a rainy Southern night, Jade Sperry endured a young woman\'s worst nightmare at the hands of three local hell-raisers. Robbed of her youthful ideals and at the center of scandal and tragedy, Jade ran as far and as fast as she could. But she never forgot the sleepy "company town" where every man, woman, and child was dependent on one wealthy family. And she never forgot their spoiled son, who, with his two friends, changed her life forever. Someday, somehow, she would return, exact a just revenge and free herself from fear, and the powerful family that could destroy her.',
			  u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/0017-1/{0A8B4D8E-FD32-41AE-B6A1-6FB87362622C}Img200.jpg', u'type': u'image/jpeg'}}, 
			  u'id': u'0a8b4d8e-fd32-41ae-b6a1-6fb87362622c',
			  u'expires': u'17 days'
			    },

			  {u'primaryCreator': {u'role': u'Author', u'name': u'Zane Grey'}, 
			   u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/bf635d7c-3f0b-43fc-ac5b-ab527aca77a5/availability', u'type': u'application/vnd.overdrive.api+json'}, 
			   u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/bf635d7c-3f0b-43fc-ac5b-ab527aca77a5/metadata', u'type': u'application/vnd.overdrive.api+json'}, 
			   u'title': u'The Border Legion', 
			   u'breifSynopsis': u'The inspiration for several Western movies, Zane Grey\'s The Border Legion tells the tale of hardened gunslinger Jack Kells, who finds his gruff facade melting when he encounters Joan Randle, a spunky heroine who has been captured by a militia stationed near the Idaho border.',
			   u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/2389-1/{BF635D7C-3F0B-43FC-AC5B-AB527ACA77A5}Img200.jpg', u'type': u'image/jpeg'}}, 
			   u'id': u'bf635d7c-3f0b-43fc-ac5b-ab527aca77a5',
			   u'expires': u'16 days'			   
			    },
		     
			  {u'primaryCreator': {u'role': u'Author', u'name': u'John Grisham'}, 
			   u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/66732855-8205-4aa3-80a7-bcbcbbe75266/availability', u'type': u'application/vnd.overdrive.api+json'}, 
			   u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/66732855-8205-4aa3-80a7-bcbcbbe75266/metadata', u'type': u'application/vnd.overdrive.api+json'},
			   u'title': u'The Litigators', 
			   u'breifSynopsis': u'The partners at Finley & Figg often refer to themselves as a "boutique law firm." Boutique, as in chic, selective, and prosperous. Oscar Finley and Wally Figg are none of these things. They are a two-bit operation of ambulance chasers who bicker like an old married couple. Until change comes their way--or, more accurately, stumbles in. After leaving a fast-track career and going on a serious bender, David Zinc is sober, unemployed, and desperate enough to take a job at Finley & Figg.\nNow the firm is ready to tackle a case that could make the partners rich--without requiring them to actually practice much law. A class action suit has been brought against Varrick Labs, a pharmaceutical giant with annual sales of $25 billion, alleging that Krayoxx, its most popular drug, causes heart attacks. Wally smells money. All Finley & Figg has to do is find a handful of Krayoxx users to join the suit. It almost seems too good to be true . . . and it is.',
			   u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/0111-1/{66732855-8205-4AA3-80A7-BCBCBBE75266}Img200.jpg', u'type': u'image/jpeg'}},
			   u'id': u'66732855-8205-4aa3-80a7-bcbcbbe75266',
			   u'expires': u'16 days'			   
			    },
			  {u'primaryCreator': {u'role': u'Author', u'name': u'Dean Koontz'},
			   u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/e536770a-3227-47b8-b2ec-b8f988c10b53/availability', u'type': u'application/vnd.overdrive.api+json'},
			   u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/e536770a-3227-47b8-b2ec-b8f988c10b53/metadata', u'type': u'application/vnd.overdrive.api+json'},
			   u'title': u'Innocence (with bonus short story Wilderness)',
			   u'breifSynopsis': u'In Innocence, Dean Koontz blends mystery, suspense, and acute insight into the human soul in a masterfully told tale that will resonate with readers forever.\nHe lives in solitude beneath the city, an exile from society, which will destroy him if he is ever seen.\nShe dwells in seclusion, a fugitive from enemies who will do her harm if she is ever found.\nBut the bond between them runs deeper than the tragedies that have scarred their lives. Something more than chance--and nothing less than destiny--has brought them together in a world whose hour of reckoning is fast approaching.',
			   u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/0111-1/{E536770A-3227-47B8-B2EC-B8F988C10B53}Img200.jpg', u'type': u'image/jpeg'}}, 
			   u'id': u'e536770a-3227-47b8-b2ec-b8f988c10b53',
			   u'expires': u'16 days'
			    }
		     ]
	for book_on_check_out in data:
		list_book = []
		book_data = {}	
		book_data['id'] = book_on_check_out['id']
		book_data['author'] = book_on_check_out['primaryCreator']['name']
		book_data['metadata'] = book_on_check_out['metadata']['href']
		book_data['breifSynopsis'] = book_on_check_out['breifSynopsis']
		book_data['title'] = book_on_check_out['title']
		book_data['expires'] = book_on_check_out['expires']
		book_data['images'] = book_on_check_out['images']['thumbnail']['href']
		book_data['availableToDownload'] = book_on_check_out['availability']['href']
		book_data['origin'] = 'ODCOM'
		list_book = [book_data]
		list_of_books.extend(list_book)	
	#end for
	return list_of_books
#end def

def get_list_of_checkouts(no_token):
	"""
	GET http://integration-patron.api.overdrive.com/v1/patrons/me/chcekouts
	User-Agent: {Your application}
	Authorization: Bearer {OAuth patron access token}
	Host: patron.api.overdrive.com
	"""
	if no_token == 'Y':
		list_of_books = get_checkout_data()
		return list_of_books
	else:
		headers = {'Host' : 'http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts',
				   'Authorization' : 'Bearer %s' % patron_access_token,
				   'User-agent' : 'BookBlend'}
		check_outs_url = 'http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts'

		check_out_response = requests.get(check_outs_url, headers=headers)

		print "book serach response == ", check_out_response, "reason = ", check_out_response.reason, "\n"
		if check_out_response.status_code == 401:
		    print "Patron is not authorize to use this library == ", od_url, "\n"
		elif check_out_response.status_code > 201:
			print "Get request failed == ", check_out_response.reason
		elif check_out_response.status_code == 200 or check_out_response.status_code == 201:
			print "Get request to get a list of checked out books was successful", "\n"

			check_out_response_data = json.loads(check_out_response.content)
			print "OverDrive book count == ", check_out_response_data['totalItems'], "\n"

			if check_out_response_data['totalItems'] > 0:
				books_on_check_out = check_out_response_data[1]
				for book_on_check_out in data:
					list_book = []
					book_data = {}	
					book_data['id'] = book_on_check_out['id']
					book_data['author'] = book_on_check_out['primaryCreator']['name']
					book_data['metadata'] = book_on_check_out['metadata']['href']
					book_data['breifSynopsis'] = book_on_check_out['breifSynopsis']
					book_data['title'] = book_on_check_out['title']
					book_data['expires'] = book_on_check_out['expires']
					book_data['images'] = book_on_check_out['images']['thumbnail']['href']
					book_data['availableToDownload'] = book_on_check_out['availability']['href']
					book_data['origin'] = 'ODCOM'
					list_book = [book_data]
					list_of_books.extend(list_book)	
				#end for
			#end if
		#end if

		return list_of_books
	#end if
#end def

def checkin_book(book):
	""" this module handles the checkin_book function calls until the
		 overdrive patron_access_token can be used.
	"""
	no_token = 'Y'
	if no_token == 'Y':
		successful = 200
		return successful
	else:
		list_of_books = check_in_book(book)
		return list_of_books
	#end if
#end def

def check_in_book(book):
	"""
	DELETE http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts/{reserveId}
	User-Agent: {Your application}
	Authorization: Bearer {OAuth patron access token}
	Host: integration-patron.api.overdrive.com
	"""
	""" the access token and the project_url needs to be passed here somehow
		maybe as globals
	"""
	headers = {'Host' : 'http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts',
			   'Authorization' : 'Bearer %s' % patron_access_token,
			   'User-agent' : 'BookBlend', 'X-Forwarded-For' : '73.189.218.224',
			   	'Content-Type' : 'application/json; charset=utf-8', 
			   	'Content-Length' : 104, 'Expect' : '100-continue'}
	product_url = 'http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts' 
	pruduct_url = product_url + "/" + book['reserveId'] 

	response = requests.delete(product_url, headers=headers)
	response_data = json.loads(response.content)
	
	if response.status_code > 204:
	    flash(("Action was not successful. %s == %s\n") % 
	            (response.status_code, response.reason))
	elif response.status_code == 204:
	    client_credentials = response.content
	    print "The book was checked in successfully."
	#end if
	""" add logic to remove the book from the database
	"""

	return response.status_code
#end def

def checkout_book(book):
	""" this module handles the checkout_book function calls until the
		 overdrive patron_access_token can be used.
	"""
	no_token = 'Y'
	if no_token == 'Y':
		successful = 200
		return successful
	else:
		list_of_books = check_out_book(book)
		return list_of_books
	#end if
#end def

def check_out_book(book):
	"""
	POST http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts
	User-Agent: {Your application}
	Authorization: Bearer {OAuth patron access token}
	Content-Type: application/json; charset=utf-8
	Host: integration-patron.api.overdrive.com
	Content-Length: 104
	Expect: 100-continue

	{
	    "fields": [
	        {
	            "name": "reserveId",
	            "value": "0D85564B-A4B3-43D5-875D-1DF3CA06AE65"
	        },
	    ]
	}
	"""
	""" the access token and the project_url needs to be passed here somehow
		maybe as globals
	"""
	headers = {'Host' : 'http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts',
			   'Authorization' : 'Bearer %s' % patron_access_token,
			   'User-agent' : 'BookBlend', 'X-Forwarded-For' : '73.189.218.224',
			   	'Content-Type' : 'application/json; charset=utf-8', 
			   	'Content-Length' : 104, 'Expect' : '100-continue'}
	payload = {
			"fields": [
		        {
		            "name": "reserveId",
		            "value": book['id']
		        },
    		]
    }
	product_url = book['metadata']

	response = requests.post(product_url, data=payload, headers=headers)
	response_data = json.loads(response.content)
	
	print response.status_code, "  ==  ", response.reason
	if response.status_code > 201:
	    flash(("Action was not successful. %s == %s\n") % 
	            (response.status_code, response.reason))
	elif response.status_code == 200 or response.status_code == 201:
	    client_credentials = response.content
	    print "The book was checked out successfully."
	#end if
	""" add logic to put the book into the database in both the checkedout
		 data set as well remove the book from the holds data set.
	"""

	return response.status_code
#end def

def get_hold_data():
	list_of_books = []
	data = [ {u'primaryCreator': {u'role': u'Author', u'name': u'Donna Tartt'}, 
			  u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/98267aaa-9898-4ce3-86f8-678136cf5031/availability', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/98267aaa-9898-4ce3-86f8-678136cf5031/metadata', u'type': u'application/vnd.overdrive.api+json'},
			  u'title': u'The Little Friend', 
			  u'breifSynopsis': u'The second novel by Donna Tartt, bestselling author of The Goldfinch (winner of the 2014 Pulitzer Prize), The Little Friend is a grandly ambitious and utterly riveting novel of childhood, innocence and evil. ',
			  u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/0111-1/{98267AAA-9898-4CE3-86F8-678136CF5031}Img200.jpg', u'type': u'image/jpeg'}}, 
			  u'id': u'98267aaa-9898-4ce3-86f8-678136cf5031',
			  u'expires': u'#1 on 5 copies'
			    },
			 {u'primaryCreator': {u'role': u'Author', u'name': u'David Remnick'},
			  u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/a43f3999-8237-461c-83fe-1f70589bd3f4/availability', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/a43f3999-8237-461c-83fe-1f70589bd3f4/metadata', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'title': u'The Bridge: The Life and Rise of Barack Obama', 
			  u'breifSynopsis': 'In this nuanced and complex portrait of Barack Obama, Pulitzer Prize-winner David Remnick offers a thorough, intricate, and riveting account of the unique experiences that shaped our nation\'s first African American president.',
			  u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/0111-1/{A43F3999-8237-461C-83FE-1F70589BD3F4}Img200.jpg', u'type': u'image/jpeg'}},
			  u'id': u'a43f3999-8237-461c-83fe-1f70589bd3f4',
			  u'expires': u'#2 on 5 copies' 			  
			    },
			 {u'primaryCreator': {u'role': u'Author', u'name': u'Kami Garcia'}, 
			  u'availability': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/c0a4c5dc-4cb9-481b-aa03-6a0b8ca3cdff/availability', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'metadata': {u'href': u'http://api.overdrive.com/v1/collections/v1L1BBQ0AAA2_/products/c0a4c5dc-4cb9-481b-aa03-6a0b8ca3cdff/metadata', u'type': u'application/vnd.overdrive.api+json'}, 
			  u'title': u'Beautiful Redemption',
			  u'breifSynopsis': u'Ethan Wate has spent most of his life longing to escape the stiflingly small Southern town of Gatlin. He never thought he would meet the girl of his dreams, Lena Duchannes, who unveiled a secretive, powerful, and cursed side of Gatlin, hidden in plain sight. And he never could have expected that he would be forced to leave behind everyone and everything he cares about. So when Ethan awakes after the chilling events of the Eighteenth Moon, he has only one goal: to find a way to return to Lena and the ones he loves.\nBack in Gatlin, Lena is making her own bargains for Ethan\'s return, vowing to do whatever it takes -- even if that means trusting old enemies or risking the lives of the family and friends Ethan left to protect.\nWorlds apart, Ethan and Lena must once again work together to rewrite their fate, in this stunning finale to the Beautiful Creatures series.',
			  u'images': {u'thumbnail': {u'href': u'http://images.contentreserve.com/ImageType-200/0017-1/{C0A4C5DC-4CB9-481B-AA03-6A0B8CA3CDFF}Img200.jpg', u'type': u'image/jpeg'}}, 
			  u'id': u'c0a4c5dc-4cb9-481b-aa03-6a0b8ca3cdff',
			  u'expires': u'#2 on 1 copies'
			    }
		     ]
	for book_on_hold in data:
		list_book = []
		book_data = {}	
		book_data['id'] = book_on_hold['id']
		book_data['author'] = book_on_hold['primaryCreator']['name']
		book_data['metadata'] = book_on_hold['metadata']['href']
		book_data['breifSynopsis'] = book_on_hold['breifSynopsis']
		book_data['title'] = book_on_hold['title']
		book_data['expires'] = book_on_hold['expires']
		book_data['images'] = book_on_hold['images']['thumbnail']['href']
		book_data['availableToDownload'] = book_on_hold['availability']['href']
		book_data['origin'] = 'ODCOM'
		list_book = [book_data]
		list_of_books.extend(list_book)	
	#end for
	return list_of_books

#end def

def get_hold_list(no_token):
	"""
	GET http://patron.api.overdrive.com/v1/patrons/me/holds
	User-Agent: {Your application}
	Authorization: Bearer {OAuth patron access token}
	Host: patron.api.overdrive.com
	Connection: Keep-Alive
	"""
	if no_token == 'Y':
		list_of_books = get_hold_data()
		return list_of_books
	else:
		headers = {'Host' : 'http://patron.api.overdrive.com/v1/patrons/me/holds',
				   'Authorization' : 'Bearer %s' % patron_access_token,
				   'User-agent' : 'BookBlend', 'Connection' : 'Keep-Alive'}
		holds_url = 'http://patron.api.overdrive.com/v1/patrons/me/holds'

		hold_response = requests.get(holds_url, headers=headers)

		if hold_response.status_code == 401:
		    print "Patron is not authorize to use this library == ", od_url, "\n"
		elif hold_response.status_code > 201:
			print "Get request failed == ", hold_response.reason
		elif hold_response.status_code == 200 or hold_response.status_code == 201:
			print "The hold list was retreived successfully.", "\n"

			hold_response_data = json.loads(hold_response.content)
			print "OverDrive book count == ", hold_response_data['totalItems'], "\n"

			if hold_response_data[0]['numberOfHolds'] > 0:
				books_on_hold = hold_response_data[1]

				for book_on_hold in data:
					list_book = []
					book_data = {}	
					book_data['id'] = book_on_hold['id']
					book_data['author'] = book_on_hold['primaryCreator']['name']
					book_data['metadata'] = book_on_hold['metadata']['href']
					book_data['breifSynopsis'] = book_on_hold['breifSynopsis']
					book_data['title'] = book_on_hold['title']
					book_data['expires'] = book_on_hold['expires']
					book_data['images'] = book_on_hold['images']['thumbnail']['href']
					book_data['availableToDownload'] = book_on_hold['availability']['href']
					book_data['origin'] = 'ODCOM'
					list_book = [book_data]
					list_of_books.extend(list_book)
				#end for
			#end if
		#end if
	#end if
	return list_of_books

#end def
def put_book_on_hold(book):
	""" this module handles the put_book_on_hold function calls until the
		 overdrive patron_access_token can be used.
	"""
	no_token = 'Y'
	if no_token == 'Y':
		successful = 200
		return successful
	else:
		list_of_books = put_book_on_hold_list(book)
		return list_of_books
	#end if
#end def

def put_book_on_hold_list(book):
	"""
	POST http://patron.api.overdrive.com/v1/patrons/me/holds
	User-Agent: {Your application}
	Authorization: Bearer {OAuth patron access token}
	Content-Type: application/json; charset=utf-8
	Host: patron.api.overdrive.com
	Content-Length: 178
	Expect: 100-continue

	{
	    "fields": [
	        {
	            "name": "reserveId",
	            "value": "0D85564B-A4B3-43D5-875D-1DF3CA06AE65"
	        },
	        {
	            "name": "emailAddress",
	            "value": "YourEmailHere@overdrive.com"
	        }
	    ]
	}
	"""
	""" the access token and the project_url needs to be passed here somehow
		maybe as globals
	"""
	headers = {'Host' : 'http://patron.api.overdrive.com/v1/patrons/me/holds',
			   'Authorization' : 'Bearer %s' % patron_access_token,
			   'User-agent' : 'BookBlend', 'X-Forwarded-For' : '73.189.218.224',
			   	'Content-Type' : 'application/json; charset=utf-8', 
			   	'Content-Length' : 178, 'Expect' : '100-continue'}
	payload = {
			"fields": [
		        {
		            "name": "reserveId",
		            "value": book['id']
		        },
		        {
		            "name": "emailAddress",
		            "value": "loretta_powell@pobox.com"
		        }
    		]
    }
	product_url = book['metadata']

	response = requests.post(product_url, data=payload, headers=headers)
	response_data = json.loads(response.content)
	
	if response.status_code > 201:
	    flash(("Action was not successful. %s == %s\n") % 
	            (response.status_code, response.reason))
	elif response.status_code == 200 or response.status_code == 201:
	    client_credentials = response.content
	    print "The book was successfully placed on hold."
	#end if
	""" add logic to put the book into the database
	"""

	return response.status_code
#end def

def main():
	print "in overdrive apis "
	get_od_books("Faye Kellerman, {'url': u'api.overdrive.com/v1/libraries/4425', 'access_token': None, 'name': u'OverDrive Integration library', 'patron': 1}")

# end def

if __name__ == '__main__':
	main()
