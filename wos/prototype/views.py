from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, render

from django.conf import settings
from suds.client import Client
from lxml import etree
import base64
from wos.utils.utils import cache_function

REL_PATH   = "prototype/wsdl"
NSMAP   = {"ns": "http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord"}

def get_auth_client():
    url = "file://%s/%s/WOKMWSAuthenticate.xml" % (settings.BASE_PATH, REL_PATH)
    # "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl"
    username    = settings.WOS_USERNAME
    password    = settings.WOS_PASSWORD
    headers = {
        "Authorization":    "Basic %s" % base64.b64encode("%s:%s" % (username, password))
    }
    return Client(url, headers=headers)


def get_search_client(sid):
    url = "file://%s/%s/WokSearch.xml" % (settings.BASE_PATH, REL_PATH)
    # "http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl"
    headers = {
        "Cookie":   'SID="%s"' % sid
    }
    return Client(url, headers=headers)


@cache_function()
def get_sid():
    aclient = get_auth_client()
    return aclient.service.authenticate()


def get_records(client, q):
    ed1  = client.factory.create("editionDesc")
    ed1.collection  = "WOS"
    ed1.edition     = "SCI"
    
    qp  = client.factory.create("queryParameters")
    qp.databaseId   = "WOS"
    qp.userQuery    = "TS=%s" % q   #"TS=(cadmium OR lead)"
    qp.editions     = [ed1]
    qp.queryLanguage    = "en"
    
    rp  = client.factory.create("retrieveParameters")
    rp.firstRecord  = 1
    rp.count    = 5
    
    titles  = []
    
    try:
        res = client.service.search(qp, rp)
        #print (res.recordsFound, res.recordsSearched, res.records)
        root    = etree.XML(res.records)
        recs    = root.xpath("//ns:REC", namespaces=NSMAP)
        for rec in recs:
            els    = rec.xpath(".//ns:title[@type='item']", namespaces=NSMAP)
            if len(els) > 0:
                titles.append(els[0].text.strip())
    except Exception, e:    #WebFault
        pass
    return titles
    

def search(request):
    q   = request.GET.get("q", "")
    p   = request.GET.get("p", None)
    sid = get_sid()
    print sid
    sclient = get_search_client(sid)
    recs    = get_records(sclient, q)
    c   = {
        "records": recs,
        "q":    q
    }
    return render(request, "prototype/search_list.html", c)
