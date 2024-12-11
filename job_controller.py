import json
import os
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import requests

flink_url = "http://13.64.58.7:8081"
def getMetrics(request, jobId):
    if request.method == "GET":
        url = f"{flink_url}/jobs/{jobId}/metrics"
        response = requests.get(url)
        if (response.status_code) == 200:
            metric_ids = [metric["id"] for metric in response.json()]
            print(metric_ids)
            # Step 2: Fetch the actual metric values
            if not metric_ids:
                return JsonResponse({"jobid": jobId, "metrics": {}}, status=200)
            
            # Pass the metric IDs as a query parameter
            metrics_query = ','.join(metric_ids)
            metrics_value_url = f"{url}?get={metrics_query}"
            values_response = requests.get(metrics_value_url)
            values_response.raise_for_status()
            
            # Parse the response and return the results
            metrics_with_values = {
                metric["id"]: metric.get("value", "N/A") for metric in values_response.json()
            }
            return JsonResponse({"jobid": jobId, "metrics": metrics_with_values}, status=200)
        
        else: 
            print("Error: " + response.status_code)
            return JsonResponse(response.status_code)


def getExceptions(request, jobId):
    if request.method == "GET":
        url = f"{flink_url}/jobs/{jobId}/exceptions"
        response = requests.get(url)
        return JsonResponse(response.json())
    
def getConfig(request, jobId):
    if request.method == "GET":
        url = f"{flink_url}/jobs/{jobId}/config"
        response = requests.get(url)
        return JsonResponse(response.json())
       

def getStatus(request, jobId):
    if request.method == "GET":
        url = f"{flink_url}/jobs/{jobId}/status"
        response = requests.get(url)
        return JsonResponse(response.json())
    

def terminate(request, jobId):
    if request.method == "PATCH":
        url = f"{flink_url}/jobs/{jobId}"
        response = requests.patch(url)
        if response.status_code == 200:
            return HttpResponse("Success")
    return HttpResponse("Error")


def stop(request):
    if request.method == "POST":
        url = f"{flink_url}/jobs/{jobId}/stop"
        response = requests.patch(url)
        if response.status_code == 200:
            return HttpResponse("Success")
    return HttpResponse("Error")

def scale(request, jobId):
    if request.method == "POST":
        url = f"http://13.64.58.7:8081/jobs/{jobId}/rescaling"
        parallelism = request.POST.get("parallelism")
        if not parallelism:
            return HttpResponse("Error - Parallelism required")
        payload = {
            'parallelism' :int (parallelism)
        }
        print(payload)
        response = requests.patch(url, json=payload)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.json()}")
        return JsonResponse(response.json())
        
    return HttpResponse("Pong!")

def getDetails(request, jobId):
    print(jobId)
    if request.method == "GET":
        url = f"http://13.64.58.7:8081/jobs/{jobId}"

        # Sending GET request to the API
        response = requests.get(url)

        # Checking if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()  # Parse the JSON data returned by the 
            print(data)
            return JsonResponse(data)
        else:
            print(f"Error: {response.status_code}")
            return HttpResponse("error")
    return HttpResponse("Not get")

def planJar(request, jarId):
    if request.method == "POST":
        url = f"{flink_url}/jars/{jarId}/plan"
        payload = {
            "programArg" : request.POST.get("programArg"),
            "entry-class" : request.POST.get("entry-class"),
            "parallelism" : int(request.POST.get("parallelism"))
        }
        response = requests.post(url, json=payload)
        return JsonResponse(response.json())

def uploadJar(request):
    if request.method == "POST":
        url = f"http://13.64.58.7:8081/jars/upload"
        uploaded_file = request.FILES['jarfile']
        
        # Step 2: Save the JAR file to a temporary location
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path  = os.path.join(settings.MEDIA_ROOT ,filename)
        
        # Sending GET request to the API
        with open(file_path, 'rb') as f:
            files = {'jarfile': (filename, f, 'application/x-java-archive')}
            response = requests.post(url, files=files)

        # Checking if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()  # Parse the JSON data returned by the 
            print(data)
            return JsonResponse(data)
        else:
            print(response.json())
            print(f"Error: {response.status_code}")
            return HttpResponse("error")
    return HttpResponse("Not get")


def runJar(request, jarId):
    if request.method == "POST":
        url = f"http://13.64.58.7:8081/jars/{jarId}/run"
        payload = {
            "programArg": request.POST.get("programArg"),
            "parallelism": int(request.POST.get("parallelism"))
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()  # Parse the JSON data returned by the 
            print(data)
            return JsonResponse(data)
        else:
            print(response.json())
            print(f"Error: {response.status_code}")
            return HttpResponse("error")
    return HttpResponse("Not get")

def getJobsOverview(request):
    url = f"{flink_url}/jobs/"
    response = requests.get(url)
    if response.status_code ==200:
        return JsonResponse(response.json())
    else: 
        print (f"Error: {response.status_code}")
        return JsonResponse(response.json())