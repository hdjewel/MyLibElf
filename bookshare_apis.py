import requests
from local_settings import BS_API_KEY

def get_bookshare_books(search_criteria):
    """ The following commands work in python to return 3 book per page from
     the Bookshare API

     """
    print "\n in bookshare_apis.py \n"
    limit = 3
    bs_url=('https://api.bookshare.org/book/search/author/%s/page/1/limit/%d/format/json?api_key=%s'
        % (search_criteria, limit,  BS_API_KEY))
    status = requests.get(bs_url)
    # print "\n\n"
    # print status

    # look for a convert from unicode 
    response_data = status.json()
    list_of_books = response_data['bookshare']['book']['list']['result']
    for i in range(0,len(list_of_books)):
        author = ''
        print len(list_of_books[i]['author'])
        for n in list_of_books[i]['author']:
            author = author + ", " + n
            #end for
        list_of_books[i]['author'] = author.lstrip(',')
    #end for
    """ The returned list of books are a dictionary of the following keys:
    
     publisher ,  isbn13 ,  author ,  availableToDownload ,  title , 
     briefSynopsis ,  dtbookSize ,  images ,  freelyAvailable ,  id ,
     downloadFormat
    """
    # count = 0
    # print "bs data = " "\n"
    # for book in list_of_books:
    #     if count < 2:
    #         print book
    #         print "\n"
    #         count = count + 1
    # print "\n\n"
    # This sorts the list of books "in place"
    list_of_books.sort()    
    return list_of_books
#end def