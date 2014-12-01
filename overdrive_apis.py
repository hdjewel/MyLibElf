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
	# print "overdrive keys = ", keys, "\n"
	encoded_keys = base64.b64encode(keys)
	# print encoded_keys
	od_oauth_url = 'https://oauth.overdrive.com/token'
	headers = {'Host' : 'oauth.overdrive.com',
				'Authorization' : 'Basic %s' % encoded_keys,
				'Content-Type' : 'application/x-www-form-urlencoded;charset=UTF-8'}
	payload ={}
	payload = {'grant_type' : 'client_credentials'}
	response = requests.post(od_oauth_url, data=payload, headers=headers)
	# print response
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

	# print "\n\n repsonse data =", response_data, "\n\n"
	# print " overdrive url = ", response.url, "\n"
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
	# print "app fields = ", overdrive_client_app_fields, "\n"
	access_token = overdrive_client_app_fields['access_token']
	# print "od access token = ", od_client_app_access_token, "\n"
	# session['od_access_token'] = overdrive_client_app_fields['access_token'
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
	print "library_fields = ", library_fields, "\n"
	headers = {'Host' : 'api.overdrive.com',
	'Authorization' : 'Bearer %s' % access_token,
	'User-agent' : 'BookBlend', 'X-Forwarded-For' : '73.189.218.224'}
	lib_url = "https://" + library_fields['url']

	lib_response_data = requests.get(lib_url, headers=headers)
	print "library response_data == ", lib_response_data, "\n"
	# print lib_response_data.status_code, "  ==  ", lib_response_data.reason
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
	print "in search_for_books  "
	list_of_books = []
	list_book = []
	q = search_criteria
	limit = 300		# 25 by default 300 max
	offset = 0		# number of titles to skip
	formats = ""
	sort = "Author:desc" 		# :desc
	lastupdatetime = "" 
	series = "" 
	# http://api.overdrive.com/v1/collections/{collection token}/products?{parameters}
	# od_url=('http://api.overdrive.com/v1/collections/%s/products?%s' %
	# 			(OD_API_KEYS, search_criteria))
	search_parms = "?q=%s&limit=%s&offset=0&formats=%s&sort=%s" % (q, limit, 
																   formats, 
																   sort)
	od_url="%s%s" % (product_url, search_parms)

	print "overdrive url = ", od_url, "\n"
	od_url = od_url.replace(' ', '%20')
	book_response = requests.get(od_url, headers=headers)

	print "book serach response == ", book_response, "reason = ", book_response.reason, "\n"
	# print data.status_code, "  ==  ", data.reason
	if book_response.status_code == 401:
	    print "Patron is not authorize to use this library == ", od_url, "\n"
	elif book_response.status_code > 201:
		print "Get request failed == ", book_response.reason
	elif book_response.status_code == 200 or book_response.status_code == 201:
		print "Get request to get the Library product was successful", "\n"

		book_response_data = json.loads(book_response.content)
		print "OverDrive book count == ", book_response_data['totalItems'], "\n"

		# data = [ { "title": "20,000 Leagues under the Sea", "primaryCreator": { "role": "Author", "name": "Jules Verne" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{EE013A9B-53CC-45D2-95DA-EC50360B8E80\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/ee013a9b-53cc-45d2-95da-ec50360b8e80/availability", "type": "application/vnd.overdrive.api+json" } },
			     # { "title": "The Adventures of Sherlock Holmes", "primaryCreator": { "role": "Author", "name": "Sir Arthur Conan Doyle" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{76C1B7D0-17F4-4C05-8397-C66C17411584\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/76c1b7d0-17f4-4c05-8397-c66c17411584/availability", "type": "application/vnd.overdrive.api+json" } } ]

		# print data
		# for i in data:
		# 	print "\n\n data %d = \n %s" % i, data[i]
		# 	list_of_books.extend(data[i])	
		if book_response_data['totalItems'] > 0:
			products = book_response_data['products']
			for product in products:
				book_data = {}	
				# print "\n data product = \n", product
				book_data['images'] = product['images']['thumbnail']['href']
				book_data['title'] = product['title']
				book_data['author'] = product['primaryCreator']['name']
				book_data['availableToDownload'] = product['links']['availability']['href']
				book_data['id'] = product['id']
				book_data['metadata'] = product['links']['metadata']['href']
				book_data['origin'] = 'ODCOM'
				print "\n book_data = \n", book_data
				# if list_of_books == []:
				list_book = [book_data]
				# else:
				# 	list_book = book_data
				# print "\n made book_data an item in list_book \n", list_book
				# print "\n list of books before the extend = \n ", list_of_books
				list_of_books.extend(list_book)
				# print "\n list of books after the extend = \n ", list_of_books
			#end for
		#end if
	#end if

	return list_of_books
# end def

def get_list_of_checkouts():
	"""
	GET http://integration-patron.api.overdrive.com/v1/patrons/me/chcekouts
	User-Agent: {Your application}
	Authorization: Bearer {OAuth patron access token}
	Host: patron.api.overdrive.com
	"""
	headers = {'Host' : 'http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts',
			   'Authorization' : 'Bearer %s' % patron_access_token,
			   'User-agent' : 'BookBlend'}
	check_outs_url = 'http://integration-patron.api.overdrive.com/v1/patrons/me/checkouts'

	check_out_response = requests.get(check_outs_url, headers=headers)

	print "book serach response == ", check_out_response, "reason = ", check_out_response.reason, "\n"
	# print data.status_code, "  ==  ", data.reason
	if check_out_response.status_code == 401:
	    print "Patron is not authorize to use this library == ", od_url, "\n"
	elif check_out_response.status_code > 201:
		print "Get request failed == ", check_out_response.reason
	elif check_out_response.status_code == 200 or check_out_response.status_code == 201:
		print "Get request to get the Library product was successful", "\n"

		check_out_response_data = json.loads(check_out_response.content)
		print "OverDrive book count == ", check_out_response_data['totalItems'], "\n"

		# data = [ { "title": "20,000 Leagues under the Sea", "primaryCreator": { "role": "Author", "name": "Jules Verne" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{EE013A9B-53CC-45D2-95DA-EC50360B8E80\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/ee013a9b-53cc-45d2-95da-ec50360b8e80/availability", "type": "application/vnd.overdrive.api+json" } },
			     # { "title": "The Adventures of Sherlock Holmes", "primaryCreator": { "role": "Author", "name": "Sir Arthur Conan Doyle" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{76C1B7D0-17F4-4C05-8397-C66C17411584\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/76c1b7d0-17f4-4c05-8397-c66c17411584/availability", "type": "application/vnd.overdrive.api+json" } } ]

		# print data
		# for i in data:
		# 	print "\n\n data %d = \n %s" % i, data[i]
		# 	list_of_books.extend(data[i])	
		if check_out_response_data['totalItems'] > 0:
			books_on_check_out = check_out_response_data[1]
			for book_on_check_out in books_on_check_out:
				book_data = {}	
				# print "\n data book_on_check_out = \n", book_on_check_out
				book_data['id'] = book_on_check_out['reservedId']
				book_data['expires'] = book_on_check_out['expires']
				book_daat['metadata'] = book_on_check_out['links']['metadata']['href']
				book_data['origin'] = 'ODCOM'
				print "\n book_data = \n", book_data
				# if list_of_books == []:
				list_book = [book_data]
				# else:
				# 	list_book = book_data
				# print "\n made book_data an item in list_book \n", list_book
				# print "\n list of books before the extend = \n ", list_of_books
				list_of_books.extend(list_book)
				# print "\n list of books after the extend = \n ", list_of_books
			#end for
		#end if
	#end if

	return list_of_books
#end def

def checkin_book(book):
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
	
	print response.status_code, "  ==  ", response.reason
	if response.status_code > 204:
	    flash(("Action was not successful. %s == %s\n") % 
	            (response.status_code, response.reason))
	elif response.status_code == 204:
	    client_credentials = response.content
	    print "The book was checked in successfully."
	#end 

	return response.status_code
#end def

def checkout_book(book):
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
	#end 

	return response.status_code
#end def

def get_hold_list():
	"""
	GET http://patron.api.overdrive.com/v1/patrons/me/holds
	User-Agent: {Your application}
	Authorization: Bearer {OAuth patron access token}
	Host: patron.api.overdrive.com
	Connection: Keep-Alive
	"""
	headers = {'Host' : 'http://patron.api.overdrive.com/v1/patrons/me/holds',
			   'Authorization' : 'Bearer %s' % patron_access_token,
			   'User-agent' : 'BookBlend', 'Connection' : 'Keep-Alive'}
	holds_url = 'http://patron.api.overdrive.com/v1/patrons/me/holds'

	hold_response = requests.get(holds_url, headers=headers)

	print "book serach response == ", hold_response, "reason = ", hold_response.reason, "\n"
	# print data.status_code, "  ==  ", data.reason
	if hold_response.status_code == 401:
	    print "Patron is not authorize to use this library == ", od_url, "\n"
	elif hold_response.status_code > 201:
		print "Get request failed == ", hold_response.reason
	elif hold_response.status_code == 200 or hold_response.status_code == 201:
		print "The hold list was retreived successfully.", "\n"

		hold_response_data = json.loads(hold_response.content)
		print "OverDrive book count == ", hold_response_data['totalItems'], "\n"

		# data = [ { "title": "20,000 Leagues under the Sea", "primaryCreator": { "role": "Author", "name": "Jules Verne" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{EE013A9B-53CC-45D2-95DA-EC50360B8E80\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/ee013a9b-53cc-45d2-95da-ec50360b8e80/availability", "type": "application/vnd.overdrive.api+json" } },
			     # { "title": "The Adventures of Sherlock Holmes", "primaryCreator": { "role": "Author", "name": "Sir Arthur Conan Doyle" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{76C1B7D0-17F4-4C05-8397-C66C17411584\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/76c1b7d0-17f4-4c05-8397-c66c17411584/availability", "type": "application/vnd.overdrive.api+json" } } ]

		# print data
		# for i in data:
		# 	print "\n\n data %d = \n %s" % i, data[i]
		# 	list_of_books.extend(data[i])	
		if hold_response_data[0]['numberOfHolds'] > 0:
			books_on_hold = hold_response_data[1]
			for book_on_hold in books_on_hold:
				book_data = {}	
				# print "\n data book_on_hold = \n", book_on_hold
				book_data['id'] = book_on_hold['reservedId']
				book_data['expires'] = book_on_hold['holdExpires']
				book_daat['metadata'] = book_on_hold['links']['metadata']['href']
				book_data['origin'] = 'ODCOM'
				print "\n book_data = \n", book_data
				# if list_of_books == []:
				list_book = [book_data]
				# else:
				# 	list_book = book_data
				# print "\n made book_data an item in list_book \n", list_book
				# print "\n list of books before the extend = \n ", list_of_books
				list_of_books.extend(list_book)
				# print "\n list of books after the extend = \n ", list_of_books
			#end for
		#end if
	#end if

	return list_of_books
#end def

def put_book_on_hold(book):
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
	
	print response.status_code, "  ==  ", response.reason
	if response.status_code > 201:
	    flash(("Action was not successful. %s == %s\n") % 
	            (response.status_code, response.reason))
	elif response.status_code == 200 or response.status_code == 201:
	    client_credentials = response.content
	    print "The book was successfully placed on hold."
	#end 

	return response.status_code
#end def

def main():
	print "in overdrive apis "
	# list_of_books = search_for_books("Faye Kellerman")

	# print "\n\n list in main = \n", list_of_books
	# log_into_overdrive()
	get_od_books("Faye Kellerman, {'url': u'api.overdrive.com/v1/libraries/4425', 'access_token': None, 'name': u'OverDrive Integration library', 'patron': 1}")

# end def

if __name__ == '__main__':
	main()
