import json
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Subquery
from .models import Customer 
from .serializers import CustomerSerializer
    
@api_view(['POST'])
def identify(request):
    email = request.data.get('email')
    phoneNumber = request.data.get('phoneNumber')
    #handling empty request
    if not email and not phoneNumber:
        return JsonResponse({'error': 'Email or phoneNumber is required in the request body'}, status=400)
    #only email provided
    elif email and not phoneNumber:
        #check if there exists a record with same email and get the linkedId
        customer = Customer.objects.filter(
            id=Subquery(Customer.objects.filter(email=email,linkPrecedence="Sec").values('linkedId')[:1])
        ).first()
        if customer is not None:
            #querying to find all records linked to the primary record    
            data = Customer.objects.filter(linkedId=customer)
            emls = []
            phN = []
            secId = []
            emls.append(customer.email)
            phN.append(customer.phoneNumber)
            for person in data:
                emls.append(person.email)
                phN.append(person.phoneNumber)
                secId.append(person.id)    
            return JsonResponse({'contact': {'primaryContatctId': customer.id, 'emails': emls, 'phoneNumbers': phN, 'secondaryContactIds': secId}}, status=200)
        #maybe the provided email is not yet linked to any other record
        elif customer is None:
            customer = Customer.objects.get(email=email)
            if customer is not None:
                serializer = CustomerSerializer(instance=customer)
                return JsonResponse(serializer.data, status=200)
            return JsonResponse({"msg":"No Record Found"},status=404)
    #only phoneNumber provided
    elif phoneNumber and not email:
        #check if there exists a record with same phoneNumber and get the linkedId
        customer = Customer.objects.filter(
            id=Subquery(Customer.objects.filter(phoneNumber=phoneNumber,linkPrecedence="Sec").values('linkedId')[:1])
        ).first()
        if customer is not None:
            #querying to find all records linked to the primary record
            data = Customer.objects.filter(linkedId=customer)
            emls = []
            phN = []
            secId = []
            emls.append(customer.email)
            phN.append(customer.phoneNumber)
            for person in data:
                emls.append(person.email)
                phN.append(person.phoneNumber)
                secId.append(person.id)    
            return JsonResponse({'contact': {'primaryContatctId': customer.id, 'emails': emls, 'phoneNumbers': phN, 'secondaryContactIds': secId}}, status=200)
        #maybe the provided phoneNumber is not yet linked to any other record
        elif customer is None:
            customer = Customer.objects.get(phoneNumber=phoneNumber)
            if customer is not None:
                serializer = CustomerSerializer(instance=customer)
                return JsonResponse(serializer.data, status=200)
            return JsonResponse({"msg":"No Record Found"},status=404)
    #both email and phoneNumber provided
    elif email and phoneNumber:
        try:
            #check if there exists a record with both exact matches
            customer = Customer.objects.get(email=email,phoneNumber=phoneNumber)
            if customer is not None:
                serializer = CustomerSerializer(instance=customer)
                return JsonResponse(serializer.data, status=200)
        except Customer.DoesNotExist:
            #check if either match to any record
            customer = Customer.objects.filter(
                id=Subquery(Customer.objects.filter(Q(email=email) | Q(phoneNumber=phoneNumber),linkPrecedence="Sec").values('linkedId')[:1])
            ).first()
            #maybe email is new or phoneNumber is new so add the new record along with the linkedId
            if customer is not None:
                serializer = CustomerSerializer(
                data={
                    'email': email,
                    'phoneNumber': phoneNumber,
                    "linkedId":customer.id,
                    'linkPrecedence': "Sec",
                }
            )
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=200)
            if customer is None:
            #if both are from different ones set the younger one to secondary
                '''getting all records that match email and phoneNumber some will be secondary one will be 
                primary'''
                customers = Customer.objects.filter(Q(email=email) | Q(phoneNumber=phoneNumber))
                if customers.exists():
                    older_customer = None
                    younger_customers = None
                    for customer in customers.order_by('createdAt'):
                        if customer.linkPrecedence == 'Pri':
                            '''getting the old one that is primary'''
                            older_customer = customer
                            break
                    if older_customer:
                        younger_customers = customers.exclude(id=older_customer.id)
                    emls = []
                    phn = []
                    ids = []
                    if younger_customers is not None and younger_customers.exists():        
                        for younger_customer in younger_customers:
                            younger_customer.linkedId = older_customer
                            younger_customer.linkPrecedence = 'Sec'
                            emls.append(younger_customer.email)
                            phn.append(younger_customer.phoneNumber)
                            ids.append(younger_customer.id)
                    younger_customers.update(linkedId=older_customer.id,linkPrecedence='Sec')    
                    return JsonResponse({"contact":{"primaryContatctId":older_customer.id,"emails":emls,"phoneNumbers":phn,"secondaryContactIds":ids}}, status=202)        
            #if none of them match create a new with Pri
                serializer = CustomerSerializer(
                data={
                    'email': email,
                    'phoneNumber': phoneNumber,
                    "linkedId":None,
                    'linkPrecedence': "Pri",
                }
            )
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
    return JsonResponse({"msg":"Something wrong with your request"},status=401)    