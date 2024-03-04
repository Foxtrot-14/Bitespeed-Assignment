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
    if not email and not phoneNumber:
        return JsonResponse({'error': 'Email or phoneNumber is required in the request body'}, status=400)
    if email is not None and phoneNumber is not None:
        customers = Customer.objects.filter(Q(email=email) | Q(phoneNumber=phoneNumber))
        if customers.exists():
            if customers.count() == 1:
                customer = customers.first()
                serializer = CustomerSerializer(instance=customer)
                return JsonResponse(serializer.data, status=200)
            else:
                older_customer = None
                younger_customers = None
                for customer in customers.order_by('createdAt'):
                    if customer.linkPrecedence == 'Pri':
                        older_customer = customer
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
                else:
                    return JsonResponse({"error": "No Record Found"}, status=404)    
    customer = Customer.objects.filter(
            id=Subquery(Customer.objects.filter(Q(email=email) | Q(phoneNumber=phoneNumber),linkPrecedence="Sec").values('linkedId')[:1])
        ).first()
    if customer!=None and (email is not None and phoneNumber is not None):
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
    elif customer!=None and email or phoneNumber:
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
    elif customer==None and email and phoneNumber:
        customer1 = Customer.objects.get(Q(email=email) | Q(phoneNumber=phoneNumber),linkPrecedence="Pri")
        if customer1!=None:
            serializer = CustomerSerializer(
            data={
                'email': email,
                'phoneNumber': phoneNumber,
                "linkedId":customer1.id,
                'linkPrecedence': "Sec",
            }
        )
            if serializer.is_valid():
                serializer.save()
                data = Customer.objects.filter(linkedId=customer1)
                emls = []
                phN = []
                secId = []
                emls.append(customer1.email)
                phN.append(customer1.phoneNumber)
                for person in data:
                    emls.append(person.email)
                    phN.append(person.phoneNumber)
                    secId.append(person.id)    
                return JsonResponse({'contact': {'primaryContatctId': customer.id, 'emails': emls, 'phoneNumbers': phN, 'secondaryContactIds': secId}}, status=200)
        else:
            serializer = CustomerSerializer(
                data={
                    'email': email,
                    'phoneNumber': phoneNumber,
                    'linkPrecedence': "Pri",
                }
            )
            if serializer.is_valid():
                instance = serializer.save()
                customer_id = instance.id
            return JsonResponse({'contact': {'primaryContatctId': customer_id,'secondaryContactIds': []}}, status=201)
    return JsonResponse({'error': 'No record found'}, status=404)   