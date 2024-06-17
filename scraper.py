import json
import boto3
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
from pyppeteer import launch

### These sites helped me resolve puppeteer issues 
# https://github.com/pyppeteer/pyppeteer/issues/108
# https://linuxbeast.com/blog/how-to-build-and-deploy-python-libraries-for-aws-lambda-layers/

# URL of the webpage to scrape
TAIPEI_MAIN_URL = "https://booking-tpsc.sporetrofit.com/Home/LocationPeopleNum"
XINYI_URL = "https://xysc.teamxports.com/"
WSSC_URL = "https://wssc.cyc.org.tw/"

async def fetch_content(url):
    print("Fetching content start")

    browser = await launch(headless=True, args=['--no-sandbox','--single-process','--disable-dev-shm-usage','--disable-gpu','--no-zygote'], userDataDir='/tmp')
    print("Launched Browser")

    page = await browser.newPage()
    print("New Page")

    await page.goto(url, {'waitUntil': 'networkidle2'})
    print("goto url")
    
    content = await page.content()
    await browser.close()
    return content

async def fetch_all_contents(urls):
    tasks = [fetch_content(url) for url in urls]
    return await asyncio.gather(*tasks)


def upload_to_s3(data, bucket_name, year, month, day, timestamp):
    s3 = boto3.client('s3')
    
    # Convert data to JSON
    json_data = json.dumps(data)
    
    # Define the file path with timestamp to ensure uniqueness
    file_path = f'year={year}/month={month:02d}/day={day:02d}/data_{timestamp}.json'
    
    # Upload to S3
    s3.put_object(Bucket=bucket_name, Key=file_path, Body=json_data)


def scraper(event, context):
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M")

    # Initialize S3 client
    s3 = boto3.client('s3')
    bucket_name = 'taipeisportsarena'
    s3_key = 'sports_centers_count.json'
    

    # Fetch the rendered HTML content
    loop = asyncio.get_event_loop()
    contents = loop.run_until_complete(fetch_all_contents([TAIPEI_MAIN_URL, XINYI_URL, WSSC_URL]))

    # Parse the HTML content of the webpage
    taipei_soup = BeautifulSoup(contents[0], 'html.parser')
    xinyi_soup = BeautifulSoup(contents[1], 'html.parser')
    wssc_soup = BeautifulSoup(contents[2], 'html.parser')
    # Initialize a list to store the results
    results = []

    # Iterate over each sports center
    # Wanhua WHSC and Songshan SSSC are broken as now. Can be added if they're ever fixed.
    center_acronyms = ["BTSC", "DTSC", "JJSC", "NGSC", "NHSC", "SLSC", "ZSSC"]

    for center in center_acronyms:
        swimmers = taipei_soup.find(id=f'CurSwPNum_{center}')
        gymmers = taipei_soup.find(id=f'CurGymPNum_{center}')
        
        if swimmers and gymmers:
            center_data = {
                "datetime": formatted_now,
                "center": center,
                "swimmers": int(swimmers.text),
                "gymmers": int(gymmers.text)
            }
            results.append(center_data)
    
    ### Xinyi 
    xinyi_swimmers = xinyi_soup.find(id="poolCount")
    xinyi_gymmers = xinyi_soup.find(id="gymCount")
    yongchun_gymmers = xinyi_soup.find(id="gymCount3")
    
    xinyi_data = {
        "datetime": formatted_now,
        "center": "XYSC",
        "swimmers": int(xinyi_swimmers.text),
        "gymmers": int(xinyi_gymmers.text)
    }
    
    # 永春活力館
    yongchun_data = {
        "datetime": formatted_now,
        "center": "YCHLG",
        "swimmers": None,
        "gymmers": int(yongchun_gymmers.text)
    }
    results.extend([xinyi_data, yongchun_data])
    
    # 文山
    wssc_swimmers = wssc_soup.find(id="swim_on")
    wssc_gymmers = wssc_soup.find(id="gym_on")
    jmyyc_swimmers = wssc_soup.find(id="ice_on")
    

    wssc_data = {
        "datetime": formatted_now,
        "center": "WSSC",
        "swimmers": int(wssc_swimmers.text),
        "gymmers": int(wssc_gymmers.text),
    }
    
    jmyyc_data = {
        "datetime": formatted_now,
        "center": "JMYYC",
        "swimmers": int(jmyyc_swimmers.text),
        "gymmers": None
    }
    
    results.extend([wssc_data, jmyyc_data])

    print(results)
    
    # upload_to_s3(results, bucket_name, now.year, now.month, now.day, formatted_now)

if __name__ == "__main__":
    scraper(None, None)
