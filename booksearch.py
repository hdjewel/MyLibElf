# from local_settings import OD_API_KEYS
import bookshare_apis
import sfpl_parse_html
import overdrive_apis
import model
import re

def get_bs_books(list_of_books, search_criteria):
	book_list = bookshare_apis.get_bookshare_books(search_criteria)
	if len(book_list) > 0:
		list_of_books.extend(book_list)
	#end if
	return list_of_books
#end def

def get_parsed_library_books(list_of_books, search_criteria):
	book_list = sfpl_parse_html.get_sfpl_books(search_criteria)
	if len(book_list) > 0:
		list_of_books.extend(book_list)
	#end if
	return list_of_books
#end def

def get_overdrive_books(list_of_books, search_criteria, od_library_rows):
	book_list = overdrive_apis.get_od_books(search_criteria, od_library_rows)
	if book_list is not None:
		if len(book_list) > 0:
			list_of_books.extend(book_list)
		#end if
	return list_of_books
#end def

def search(search_criteria, patron_id):
	print "in booksearch.py \n"
	list_of_books = []
	list_of_libraries = []
	od_library_rows = []
	list_of_libraries = model.get_patron_libraries(patron_id)

	for library_row in list_of_libraries:
		print "library row = ", library_row
		""" Call one of the 3 list_of_books subroutine depending on the url.

		"""
		book_list = []
		if library_row['url'] == 'www.bookshare.org':
			# print "no bs search done. = testing only"
			list_of_books = get_bs_books(list_of_books, search_criteria)
		elif library_row['url'] == 'sfpl.org':
			# print "no sfpl search done. = testing only"
			list_of_books = get_parsed_library_books(list_of_books, 
													  search_criteria)
		else: 
			if re.match('^api\.overdrive\.com', library_row['url']):
				od_library_rows.append(library_row)
			#end if
		#end if		
		if len(od_library_rows) > 0:
			book_list =[]	
			list_of_books = get_overdrive_books(list_of_books, search_criteria,
												od_library_rows)
		#end if
	#end for


	list_of_books.sort()

	return list_of_books
# end def

if __name__ == '__main__':
	search('Kellerman', '1')