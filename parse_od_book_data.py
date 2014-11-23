import requests
from local_settings import BS_API_KEY
from pyquery import PyQuery as pq

def get_sfpl_books(search_criteria):
    """ The following commands return parses the San Francisco Library's HTML to
    	 search for books.

     """
    list_of_books = get_author_books(search_criteria)
    list_of_books.sort()    
    return list_of_books
#end def

def get_author_books(search_criteria):

	preped_search_criteria = search_criteria.replace(' ', '+')

	sfpl_url = 'http://sflib1.sfpl.org/search~S1/?searchtype=X&searcharg='
	sfpl_url = sfpl_url + preped_search_criteria
	sfpl_url = sfpl_url + '+ebook&searchscope=1&sortdropdown=-&SORT=DZ&extended=0&SUBMIT=Search&searchlimits='
	print sfpl_url, "\n"

	# make a get call to SF Public Library
	response_data = requests.get(sfpl_url)
	# use PyQuery to create the HTML
	author_html = pq(response_data.content)
	# search the HTML for the record containing the number of books found
	tag_index = 0
	i_tags = author_html('.browseSearchtoolMessage i')
	print "i tag text ", i_tags[tag_index].text, "\n"
	book_count = i_tags[tag_index].text.split().pop(tag_index)

	# search the HTML for the records containing the book detail url
	books_urls_in_href = author_html.find('.briefCitRow  td[align="left"] a[href]')
	print len(books_urls_in_href), "\n"
	# Prints all the rows with url valed href attribute.
	# for book_url_in_href in books_urls_in_href[0:]:
	# 	print book_url_in_href.attrib, "\n"
	# print "\n\n"

	# find the SF Public Library and OverDrive detail records
	loop_cnt = 2
	sfpl_book_cnt = 0
	od_book_cnt = 0 
	for book_url_in_href in books_urls_in_href:
		print "loop_cnt = ", loop_cnt, "\n"
		od_books_url = "%s" % book_url_in_href.attrib['href']
		od_book_cnt = od_book_cnt + 1

		# make a get call to SF Public Library
		response_data = requests.get(od_books_url)
		# use PyQuery to create the HTML
		od_book_list_html = pq(response_data.content)

		#end if
		loop_cnt = loop_cnt + 4
	#end for
	print " overdrive book count  = ", od_book_cnt
	print "\n"







	""" add logic to check the number of books parsed against the
		 book_count value
		 """

	#>>> displayed output for text of returned rows
	#'Orwell, George.'
	# a_lines_index = 0
	# for a in a_lines:
	#     dict_of_rows{'a'} = a_lines_index
	#     a_lines_index = a_lines_index + 1

	# if search_criteria in dict_of_rows.keys():
	# 	print "found author = ", search_criteria
	# else:
	# 	print "haven't found the author's books yet"

	""" Maybe use 'fuzzy wuzzy' to find the closest matched row? """

	""" The returned list of books are a dictionary of the following keys:
	     publisher ,  isbn13 ,  author ,  availableToDownload ,  title , 
	 briefSynopsis ,  dtbookSize ,  images ,  freelyAvailable ,  id ,
	 downloadFormat
	"""
	# count = 0
	# print "bs data = "\n"
	# for book in list_of_books:
	#     if count < 2:
	#         print book
	#         print "\n"
	#         count = count + 1
	# print "\n\n"
	return list_of_books
# end def

def main():
	search_criteria = ('Faye Kellerman')
	list_of_books = get_sfpl_books(search_criteria)

	print "\n\n list in main = \n", list_of_books

# end def

if __name__ == '__main__':

	main()