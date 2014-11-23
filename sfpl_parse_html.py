import requests
from local_settings import BS_API_KEY
from pyquery import PyQuery as pq

def get_sfpl_books(search_criteria):
    """ The following commands return parses the San Francisco Library's HTML to
    	 search for books.

     """
    print "in sfpl_parse_html.py\n"
    list_of_books = get_books(search_criteria)
    list_of_books.sort()    
    return list_of_books
#end def

def get_book_cnt(sfpl_books_list_html):
	""" search the HTML for the record containing the number of books found 

	"""
	tag_index = 0
	i_tags = sfpl_books_list_html('.browseSearchtoolMessage i')
	if len(i_tags) > 0:
		book_count = i_tags[tag_index].text.split().pop(tag_index)
	else:
		book_count = 0
	return book_count
#end def

def parse_title_author(book_detail_html):
	loop_cnt = 1
	book_data = {}
	html_tags = book_detail_html('td .bibInfoData strong')
	for i in html_tags:
		if loop_cnt == 1:
			i.text = i.text.strip(' / ')
			i.text = i.text.replace(' [electronic resource]', '')
			i.text = i.text.replace(' / by', '')
			book_data['title'] = i.text
		elif loop_cnt == 2:
			i.text = i.text.replace(' [electronic resource]', '')			
			name = i.text
		elif loop_cnt == 3:
			i.text = i.text.replace(' [electronic resource]', '')
			book_data['author'] = name + " " + i.text
		loop_cnt = loop_cnt + 1
	# print "author tile = ", book_data
	return book_data
#end def

def parse_book_cover(book_detail_html, book_data):
	i_tags = book_detail_html('div .resourcebox img[src]')
	book_data['images'] = i_tags[0].attrib['src']
	# print "images =", book_data, '\n'
	return book_data	
#end def

def get_book_details(sfpl_book_detail_url):

	response_data = requests.get(sfpl_book_detail_url)
	book_detail_html = pq(response_data.content)

	book_data = parse_title_author(book_detail_html)
	book_data = parse_book_cover(book_detail_html, book_data)
	book_data['availableToDownload'] = '1'

	return book_data
#end def
def get_author_books(sfpl_books_list_html):
	# search the HTML for the records containing the book detail url
	books_urls_in_href = sfpl_books_list_html.find('.briefCitRow  td[align="left"] a[href]')

	# find the SF Public Library and OverDrive detail records
	list_of_books = []
	loop_cnt = 1
	sfpl_book_cnt = 0
	for book_url_in_href in books_urls_in_href:

		if loop_cnt == 1 :
			book_dict = {}
			if book_url_in_href.attrib['href'] == '/screens/ratings.html':
				loop_cnt = 0
			else:
				sfpl_book_detail_url = "http://sflib1.sfpl.org%s" % book_url_in_href.attrib['href']
				sfpl_book_cnt = sfpl_book_cnt + 1
				# print sfpl_book_detail_url, "\n"
				book_dict = get_book_details(sfpl_book_detail_url)
				# print "book row = ", book_dict
				list_book = [book_dict]
				list_of_books.extend(list_book)
			#end if
		elif loop_cnt == 4:
			loop_cnt = 0
		#end if
		loop_cnt = loop_cnt + 1
	#end for


	print " sfpl book count = ", sfpl_book_cnt

	return list_of_books
#end def

def get_books(search_criteria):
	list_of_books =[]

	preped_search_criteria = search_criteria.replace(' ', '+')

	sfpl_url = 'http://sflib1.sfpl.org/search~S1/?searchtype=X&searcharg='
	sfpl_url = sfpl_url + preped_search_criteria
	sfpl_url = sfpl_url + '+ebook&searchscope=1&sortdropdown=-&SORT=DZ&extended=0&SUBMIT=Search&availlim=1&searchlimits='
	print sfpl_url, "\n"

	# make a get call to SF Public Library
	response_data = requests.get(sfpl_url)
	# use PyQuery to create the HTML
	sfpl_books_list_html = pq(response_data.content)

	book_count = get_book_cnt(sfpl_books_list_html)
	print "book count from search page = ", book_count
	if book_count == 0:
		print "no books found at SF Public Library"
	else:
		list_of_books = get_author_books(sfpl_books_list_html)
		print "\n\n"
		print "nbr of books in list", len(list_of_books), "\n"

	""" add logic to check the number of books parsed against the
		 book_count value
		 """

	""" The returned list of books are a dictionary of the following keys:
	     publisher ,  isbn13 ,  author ,  availableToDownload ,  title , 
	 briefSynopsis ,  dtbookSize ,  images ,  freelyAvailable ,  id ,
	 downloadFormat
	"""

	return list_of_books
# end def

def main():
	search_criteria = ('Faye Kellerman')
	list_of_books = get_sfpl_books(search_criteria)

	print "\n list in main = \n", list_of_books

# end def

if __name__ == '__main__':

	main()