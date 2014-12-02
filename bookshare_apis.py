import requests
from local_settings import BS_API_KEY

def get_bookshare_books(search_criteria):
    """ The following commands work in python to return 3 book per page from
     the Bookshare API

     """
    print "\n in bookshare_apis.py \n"
    limit = 300
    bs_url=('https://api.bookshare.org/book/search/author/%s/page/1/limit/%d/format/json?api_key=%s'
        % (search_criteria, limit,  BS_API_KEY))
    status = requests.get(bs_url)
    print status

    # look for a convert from unicode 
    response_data = status.json
    book_list = response_data['bookshare']['book']['list']['result']
    for i in range(0,len(book_list)):
        author = ''
        for n in book_list[i]['author']:
            author = author + ", " + n
        #end for
        book_list[i]['origin'] = 'BSORG'
        book_list[i]['author'] = author.lstrip(',')
    #end for
    print "Bookshare book count = ", len(book_list), "\n"
    """ The returned list of books are a dictionary of the following keys:
    
         publisher ,  isbn13 ,  author ,  availableToDownload ,  title , 
         briefSynopsis ,  dtbookSize ,  images ,  freelyAvailable ,  id ,
         downloadFormat, origin
    """
    book_list.sort()    
    return book_list
#end def