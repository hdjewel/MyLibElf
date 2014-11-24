# from local_settings import OD_API_KEYS
import requests

def log_into_overdrive():
	""" Get the OverDrive logon webpage

	"""
	overdrive_logon_url = 'https://sanfrancisco.libraryreserve.com/10/50/en/SignIn.htm?URL=Default%2ehtm'
	response_data = requests.get(overdrive_logon_url)
	overdrive_logon = pq(response_data.content)
	# Print response_data's content and URL as well as the cookies
	print( response_data.content)
	print( response_data.url)
	print( response_data.cookies)

	# Get the cookies for the cookie jar
	cookies = requests.utils.dict_from_cookiejar(response_data.cookies)
	""" Enter the login data for the OverDrive logon webpage to log into
		the libraries webpage.

	"""
	overdrive_login_url = 'https://sanfrancisco.libraryreserve.com/10/50/en/BANGAuthenticate.dll'
	payload = {'LibraryCardILS' : 'sanfran', 
			   'URL' : 'MyAccount.htm?PerPage=40',
			   'LibraryCardNumber' : '21223200358920',
			   'LibraryCardPIN' : '8300'}

	post_response_data = requests.post(overdrive_login_url, 
									   data=payload,
									   cookies=cookies)

	""" Add logic to handle any response in the post_response_data other
		 than the success code of 200.

	"""
	print(post_response_data)
	print(post_response_data.url)
	# add logic to get hold, wish, and checkout lists
#end def

def search_for_books(search_criteria):
	""" This gets a list of books from Overdrive

	Access a full list of titles of ebooks
	Navigate through paginated products using hypermedia links
	Filter results to return specific or sorted lists of titles

	"""
	q = search_criteria
	limit = 3		# 25 by default 300 max
	offset = 0		# number of titles to skip
	formats = ""
	sort = ':asc' 		# :desc
	lastupdatetime = "" 
	series = "" 
	http://api.overdrive.com/v1/collections/{collection token}/products?{parameters}
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
	list_of_books = search_for_books("Faye Kellerman")

	print "\n\n list in main = \n", list_of_books

# end def

if __name__ == '__main__':
	main()
