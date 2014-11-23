# from local_settings import OD_API_KEYS
import overdrive_apis
import bookshare_apis
from sfpl_parse_html import get_sfpl_books
import sfpl_parse_html

def search(search_criteria):
	print "in booksearch.py \n"
	list_of_books =[]

	# book_list = overdrive_apis.search_for_books(search_criteria)
	# if len(book_list) > 0:
	# 	print "od books = \n", book_list
	# 	print "\n"

	# 	list_of_books.extend(book_list)
	# #end if
	book_list = bookshare_apis.get_bookshare_books(search_criteria)
	if len(book_list) > 0:
		print "bs books = \n"
		for book in book_list:
			print "  ", book
			print "\n"
		#end for
		list_of_books.extend(book_list)
	#end if

	book_list = get_sfpl_books(search_criteria)
	if len(book_list) > 0:
		print "sfpl books = \n"
		for book in book_list:
			print "  ", book
			print "\n"
		#end for
		list_of_books.extend(book_list)
	#end if
	# print "all books = \n", list_of_books
	
	# print "\n book list page fields = "
	# for row in list_of_books:
	# 	print "\n row = \n", row
	# 	print "image = ", row['images'], 
	# 	print "title = ", row['title'], 
	# 	print "author = ", row['author'],
	# 	print "available = ", row['availableToDownload']

	list_of_books.sort()

	return list_of_books
# end def

if __name__ == '__main__':
	search('Kellerman')