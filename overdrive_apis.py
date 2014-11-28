from local_settings import OD_API_CLIENT_KEY, OD_API_SECRET_KEY
import requests
import base64
import json

def log_into_overdrive():
	""" Get the OverDrive Client Credentials

	"""
	print "in log_into_overdrive function \n"
	overdrive_oauth_headers = {}
	overdrive_client_app_fields = {}
	# keys = '%s:%s' % (OD_API_CLIENT_KEY, OD_API_SECRET_KEY)
	# encoded_keys = base64.b64encode(keys)
	# overdrive_oauth_url = 'https://oauth.overdrive.com/token'
	# overdrive_oauth_headers['Host'] = 'oauth.overdrive.com'
	# overdrive_oauth_headers['Authorization'] = 'Basic %s' % encoded_keys
	# overdrive_oauth_headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'

	# overdrive_oauth_url = 'http://localhost:5001/token'

	# overdrive_oauth_headers = {'Host': 'oauth.overdrive.com', 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Authorization': 'Basic TE9SRVRUQVBPV0VMTDpNMVQzTUl3NmF+dmNvd3hqRU1SR0s0TjZHUUx4UWpWRA=='}
	# # overdrive_data = {'grant-type' : 'client_credentials'}
	# print "\n\n url = ", overdrive_oauth_url, "\n data = ", overdrive_data, "\n headers = ", overdrive_oauth_headers
	

	# response_data = requests.post(overdrive_oauth_url, data = overdrive_data,
	# 							  headers = overdrive_oauth_headers)


	keys = '%s:%s' % (OD_API_CLIENT_KEY, OD_API_SECRET_KEY)
	print keys
	encoded_keys = base64.b64encode(keys)
	print encoded_keys
	od_oauth_url = 'https://oauth.overdrive.com/token'
	headers = {'Host' : 'oauth.overdrive.com',
				'Authorization' : 'Basic %s' % encoded_keys,
				'Content-Type' : 'application/x-www-form-urlencoded;charset=UTF-8'}
	payload ={}
	payload = {'grant_type' : 'client_credentials'}
	response = requests.post(od_oauth_url, data=payload, headers=headers)
	print response
	response_data = json.loads(response.content)

	print "\n\n data =", response_data, "\n\n"

	print( "post response data for overdrive = ", response.content, "\n")
	print( " overdrive url = ", response.url, "\n")
	print( " overdrive access token = ", response_data['access_token'], "\n")

	overdrive_client_app_fields['url'] = response.url
	overdrive_client_app_fields['access_token'] = response_data['access_token']
	return overdrive_client_app_fields, response
#end def

def get_od_books(search_criteria, library_fields):
	""" get books for the given library_fields
	"""
	pass

#end def

def search_for_books(search_criteria):
	""" This gets a list of books from Overdrive

	Access a full list of titles of ebooks
	Navigate through paginated products using hypermedia links
	Filter results to return specific or sorted lists of titles

	"""
	q = search_criteria
	limit = 10		# 25 by default 300 max
	offset = 0		# number of titles to skip
	formats = ""
	sort = ':asc' 		# :desc
	lastupdatetime = "" 
	series = "" 
	# http://api.overdrive.com/v1/collections/{collection token}/products?{parameters}
	# od_url=('http://api.overdrive.com/v1/collections/%s/products?%s' %
	# 			(OD_API_KEYS, search_criteria))
	od_url="http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products"
	data = requests.get(od_url)
	status = '<Response [200]>'
	data = data.json()

	# data = [ { "title": "20,000 Leagues under the Sea", "primaryCreator": { "role": "Author", "name": "Jules Verne" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{EE013A9B-53CC-45D2-95DA-EC50360B8E80\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/ee013a9b-53cc-45d2-95da-ec50360b8e80/availability", "type": "application/vnd.overdrive.api+json" } },
		     # { "title": "The Adventures of Sherlock Holmes", "primaryCreator": { "role": "Author", "name": "Sir Arthur Conan Doyle" }, "images": { "thumbnail": { "href": "http://images.contentreserve.com/ImageType-200/2389-1/{76C1B7D0-17F4-4C05-8397-C66C17411584\}Img200.jpg", "type": "image/jpeg" } }, "availability": { "href": "http://api.overdrive.com/v1/collections/v1L1BYwAAAA2Q/products/76c1b7d0-17f4-4c05-8397-c66c17411584/availability", "type": "application/vnd.overdrive.api+json" } } ]

	list_of_books = []
	list_book = []
	# print data
	# for i in data:
	# 	print "\n\n data %d = \n %s" % i, data[i]
	# 	list_of_books.extend(data[i])	

	for row in data:
		dict_book = {}	
		print "\n data row = \n", row
		dict_book['images'] = row['images']['thumbnail']['href']
		dict_book['title'] = row['title']
		dict_book['author'] = row['primaryCreator']['name']
		dict_book['availableToDownload'] = row['availability']
		print "\n dict_book = \n", dict_book
		# if list_of_books == []:
		list_book = [dict_book]
		# else:
		# 	list_book = dict_book
		print "\n made dict_book an item in list_book \n", list_book
		print "\n list of books before the extend = \n ", list_of_books
		list_of_books.extend(list_book)
		print "\n list of books after the extend = \n ", list_of_books
	print "\n list in function = \n", list_of_books
	return list_of_books
# end def

def main():
	# list_of_books = search_for_books("Faye Kellerman")

	# print "\n\n list in main = \n", list_of_books
	log_into_overdrive()

# end def

if __name__ == '__main__':
	main()
