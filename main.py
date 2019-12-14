import requests
from bs4 import BeautifulSoup
import os.path

# Set the price range for your search (lower, upper)
priceRange = (0, 30)


def get_benchmark_data():
    # check if benchmark data needs to be downloaded
    if not os.path.isfile('GPU_UserBenchmarks.csv'):
        print("Downloading userbenchmark data...")
        file_data = requests.get("https://www.userbenchmark.com/resources/download/csv/GPU_UserBenchmarks.csv")
        with open('GPU_UserBenchmarks.csv', 'wb') as f:
            f.write(file_data.content)

    print("Parsing benchmark data...")
    with open('GPU_UserBenchmarks.csv') as f:
        return {d.split(",")[3]: d.split(",")[5] for d in f}


get_benchmark_data()


def search_benchmark_data(gpu_name, benchmark_dict):
    gpu_speed = -1
    # test if name exists
    if gpu_name in benchmark_dict.keys():
        gpu_speed = benchmark_dict[gpu_name]
    else:
        # clean name and try again
        gpu_name_cleaned = clean_gpu_name(gpu_name)

        if gpu_name_cleaned in benchmark_dict:
            gpu_speed = benchmark_dict[gpu_name_cleaned]
        else:
            for name in benchmark_dict.keys():
                if gpu_name_cleaned in name:
                    gpu_speed = benchmark_dict[name]

    return gpu_speed


def clean_gpu_name(gpu_name):
    brands = ['Radeon', 'GeForce', 'OEM']

    for brand in brands:
        if brand in gpu_name:
            gpu_name = gpu_name.strip(brand)

    return gpu_name


def get_price(gpu_name):
    cex_url = 'https://wss2.cex.uk.webuy.io/v3/boxes?q={}&firstRecord=1&count=50&sortOrder=desc&sortBy=relevance'.format(
        gpu_name)
    data = requests.get(cex_url).json()['response']
    prices = []
    if data['data'] is not None:
        for item in data['data']['boxes']:
            if item['outOfStock'] == 0:
                prices.append(item['sellPrice'])
            else:
                prices.append(-1)
        return max(prices)
    else:
        return -1


def get_gpus():
    gpus = []
    print("Fetching suitable GPU data...")
    for vram in ["256 MB", "512 MB", "1024 MB", "2 GB", "3 GB", "4 GB"]:
        url = 'https://www.techpowerup.com/gpu-specs/?mobile=No&workstation=No&igp=No&memsize={}&powerplugs=None&sort=released'.format(
            vram)
        page_as_text = requests.get(url).content
        page_as_soup = BeautifulSoup(page_as_text, 'html.parser')
        table = page_as_soup.find('table', class_="processors")

        for row in table.find_all('tr'):
            for cell in row('td')[0::8]:
                gpus.append(cell.get_text().strip())

    return gpus


file_name = "£" + str(priceRange[0]) + "-" + str(priceRange[1]) + ".csv"
suitable_gpus = get_gpus()
benchmark_data = get_benchmark_data()
combined_data = {}
gpu_num = len(suitable_gpus)
gpu_counter = 0

print("Matching prices and speed...")
for gpu in suitable_gpus:
    gpu_counter += 1
    print('\r{:.2%}'.format((gpu_counter / gpu_num)), end='')
    price = get_price(gpu)

    # if the price can't be found, skip
    if price == -1 or price < priceRange[0] or price > priceRange[1]:
        continue
    speed = search_benchmark_data(gpu, benchmark_data)
    combined_data[gpu] = {'price': price, 'speed': speed}

with open(file_name, "w") as f:
    f.write('Name,Price (£),Speed (% Effective), £/%\n')
    for gpu in combined_data.keys():
        price, speed = combined_data[gpu]['price'], combined_data[gpu]['speed']
        pound_per_percent = (price / float(speed)) if speed != '-1' else -1
        f.write("{},{},{},{:.2f}\n".format(gpu, price, speed, pound_per_percent))

print('\nDone!\nData in {}'.format(file_name))
