import requests, time

i = 1
count = 1
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
failed_urls = []
start_time = time.time()
while count <= 5000:
    url = 'http://localhost:8000/campaigns/' + str(i)
    # print(url)
    response = requests.get(url, headers=headers)

    if not response.status_code == 200:
        failed_urls.append(url)
    i += 1
    if i >= 50:
        i = 1
    count += 1

end_time = time.time()
print("Total time in seconds :: ")
print(end_time - start_time)

if len(failed_urls) > 0:
    print("Failed URLs :: ")
    for failure in failed_urls:
        print(failure)
else:
    print("No failures found!!")
