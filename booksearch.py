# from local_settings import OD_API_KEYS
import bookshare_apis
import sfpl_parse_html
import overdrive_apis
import model

def get_bs_books(list_of_books, search_criteria):
	book_list = bookshare_apis.get_bookshare_books(search_criteria)
	if len(book_list) > 0:
		print "bs books = \n"
		for book in book_list:
			book_origin = "Bookshare"
			print "  ", book
			print "\n"
		#end for
		list_of_books.extend(book_list)
	#end if
	return list_of_books
#end def

def get_parsed_library_books(list_of_books, search_criteria):
	book_list = sfpl_parse_html.get_sfpl_books(search_criteria)
	if len(book_list) > 0:
		print "sfpl books = \n"
		for book in book_list:
			book_origin = "SF Public Library"
			print "  ", book
			print "\n"
		#end for
		list_of_books.extend(book_list)
	#end if
	return list_of_books
#end def

def get_overdrive_books(list_of_books, search_criteria, library_fields):
	book_list = overdrive_apis.get_od_books(search_criteria, library_fields)
	if book_list is not None:
		if len(book_list) > 0:
			print "OverDrive books = \n"
			for book in book_list:
				book_origin = "Overdrive books"
				print "  ", book
				print "\n"
			#end for
			list_of_books.extend(book_list)
		#end if
	return list_of_books
#end def

def search(search_criteria, patron_id):
	print "in booksearch.py \n"
	list_of_books = []
	list_of_libraries = []
	list_of_libraries = model.get_patron_libraries(patron_id)

	# book_list = overdrive_apis.search_for_books(search_criteria)
	# if len(book_list) > 0:
	# 	book_origin = "OverDrive"
	# 	print "od books = \n", book_list
	# 	print "\n"

	# 	list_of_books.extend(book_list)
	# #end if

	for library_row in list_of_libraries:
		print "library row = ", library_row
		""" Call one of the 3 list_of_books subroutine depending on the url.

		"""
		book_list = []
		if library_row['url'] == 'www.bookshare.org':
			list_of_books = get_bs_books(list_of_books, search_criteria)
		elif library_row['url'] == 'sfpl.org':
			list_of_books = get_parsed_library_books(list_of_books, 
													  search_criteria)
		else: 
			list_of_books = get_overdrive_books(list_of_books, search_criteria,
												library_row)
		#end if
	#end for
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
	search('Kellerman', '1')