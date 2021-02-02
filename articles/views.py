from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
import pymongo
from datetime import datetime

client = pymongo.MongoClient('localhost', 27017 )
db = client['bci_data']
collection = db['articles']
cursor = collection.find()

# Create your views here.
def home(request):
    recentposts = collection.find()[0:8].sort([('datepublished', -1)])
    healthandrehab = collection.find({'$text':{'$search': "rehabilitation rehabilitate prosthetic limb stroke"}}).limit(7)
    communication = collection.find({'$text':{'$search': "communicate communication"}}).limit(7)
    implant = collection.find({'$text':{'$search': "invasive implant"}}).limit(7)


    context = {
        'recentposts':  list(recentposts),
        'healthandrehab': list(healthandrehab) ,
        'communication':list(communication),
        'implant':list(implant)
    }
    return render( request, 'articles/home.html', context)

def about(request):

    return render(request, 'articles/about.html')

def mostrecent(request):
    #Load 10 most recent articles by date
    searchresults = collection.find().sort([('datepublished', -1)]).limit(10)
    context = {
    'searchresults': searchresults
    }

    return render(request, 'articles/mostrecent.html', context)

def mostrecentapi(request):

    #Fetch next batch of 'most recent' articles (12 in each batch)
    searchresults = collection.find()[int(request.GET['startPoint']) : int(request.GET['endPoint'])].sort([('datepublished', -1)])

    context = {'searchresults': list(searchresults) }

    html = render_to_string('articles/mostrecentapi.html', context)

    return HttpResponse(html)


def search(request):


    #If assigned as True, show the subject's given article quote on search.html
    standard_search = True
    show_communication = False
    show_rehab = False
    show_invasive = False

    #Show advanced search result html-block when True
    advsearch_template = False

    #Variables to use in the URL when dates are selected
    url_from_date = None
    url_to_date = None

    is_open_access = ""



    ##If the 'fromdate' is included, it means the client is making an advanced search request
    if 'fromdate' in request.GET:


        advsearch_template = True
        standard_search = False
        #Date format from form is %m/%d/%Y
        url_from_date = request.GET['fromdate']
        url_to_date = request.GET['todate']


        #New variables change date format from '%m/%d/%Y' to '%Y-%m-%d 00:00:00' for mongodb query
        from_date = datetime.strptime(request.GET['fromdate'], '%m/%d/%Y')
        to_date = datetime.strptime(request.GET['todate'],'%m/%d/%Y')


        #from_date = datetime.strptime(request.GET['fromdate'], '%Y-%m-%d')
        #to_date = datetime.strptime(request.GET['todate'],'%Y-%m-%d')
        #Fetch results based on advanced search being all open access articles
        if 'openaccess' in request.GET:

            is_open_access = '&openaccess=True'
            #Fetch results based on advanced search being open access articles --and sorted in particular order
            if request.GET['openaccess'] and 'sort' in request.GET:
                searchresults = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}}, {'isopenaccess': True } ] }).sort([('datepublished', int(request.GET['sort']) )])
                totalresultsfound = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}},{'isopenaccess': True }  ] }).count()
            #Fetch results based on advanced search being open access articles -- no other filters
            else:
                searchresults = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}}, {'isopenaccess': True } ] })
                totalresultsfound = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}},{'isopenaccess': True }  ] }).count()

       #Fetch results based on advanced search articles being in a particular order -- but not filtered by just open access
        elif 'sort' in request.GET and 'openaccess' not in request.GET:

                searchresults = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}} ] }).sort([('datepublished',int(request.GET['sort']))])
                totalresultsfound = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}} ] }).count()

        #Fetch results based on just the keyword -- no particular order, and not filtered by open access
        else:
            searchresults = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}} ] })
            totalresultsfound = collection.find( { '$and':[{ "datepublished": { '$gte': from_date, '$lt': to_date } },{'$text':{'$search': request.GET['term']}} ] }).count()

    #Fetch standard search results
    else:
        if 'communication' in request.GET['term']:
            show_communication = True
            standard_search = False
        elif 'rehabilitation' in request.GET['term']:
            show_rehab = True
            standard_search = False
        elif 'invasive implant' in request.GET['term']:
            show_invasive = True
            standard_search = False

        #Sort results according to user query
        if 'sort' in request.GET:
            #'-1' indicates search results are desired in order by 'most recent' first
            if request.GET['sort'] == '-1':
                searchresults = collection.find({'$text':{'$search': request.GET['term']}}).sort([('datepublished', -1)])
                totalresultsfound = collection.find({'$text':{'$search': request.GET['term']}}).count()
           #'1' indicates search results are desired in order by 'earliest' first
            elif request.GET['sort'] == '1':
                searchresults = collection.find({'$text':{'$search': request.GET['term']}}).sort([('datepublished', 1)])
                totalresultsfound = collection.find({'$text':{'$search': request.GET['term']}}).count()
        #Standard search with no particular order desired
        else:
            searchresults = collection.find({'$text':{'$search': request.GET['term']}})
            totalresultsfound = collection.find({'$text':{'$search': request.GET['term']}}).count()


    context = {
    'searchrequest': request.GET['term'],
    'searchresults' : list(searchresults),
    'totalresultsfound': totalresultsfound,
    'subjectsearch': { 'showcommunication': show_communication, 'showrehab': show_rehab, 'showinvasive': show_invasive, 'standardsearch': standard_search, 'advancedsearch': advsearch_template, 'fromdate': url_from_date, 'todate': url_to_date, 'openaccess': is_open_access}

    }


    return render(request, 'articles/search.html', context)


def article(request):
    #Fetch particular article based on the title
    article = collection.find({'title': request.GET['article']})
    article = list(article)
    context = {
    'article' : article[0]
    }

    return render(request, 'articles/article.html', context)



def journals(request):

    journal_list = []
    get_journals = collection.aggregate([ { '$group': { '_id': { 'journal': "$journal", 'publisher': "$publisher"  }}}  ])

    for journal in get_journals:
        journal_list.append(journal['_id'])


    context = { 'journal_list': journal_list  }

    return render(request, 'articles/journals.html',context)
