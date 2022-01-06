import requests
import lxml.html as html
import os
import datetime
from trycourier import Courier
from dotenv import load_dotenv

load_dotenv()

HOME_URL = 'https://www.canyon.com/es-cl/bicicletas-de-carretera/bicicletas-carreras/ultimate/cf-sl/ultimate-cf-sl-8/2752.html?dwvar_2752_pv_rahmenfarbe=BK%2FBK'
XPATH_SECTION_TO_WATCH = '//div[@data-product-size="XS"]//div[@class="productConfiguration__availabilityMessage"]/text()'


def send_mail(result_diff):
    client = Courier(auth_token=os.getenv('COURIER_TOKEN'))

    resp = client.send(
        event=os.getenv('COURIER_EVENT'),
        recipient=os.getenv('COURIER_RECIPIENT'),
        brand=os.getenv('COURIER_BRAND'),
        profile={
            "email": os.getenv('COURIER_EMAIL_FROM'),
        },
        data={
            "home_url_shortened": HOME_URL,
            "home_url_full": HOME_URL,
            "current_log_date": result_diff["current_log_date"],
            "current_log_content": result_diff["current_log_content"],
            "last_log_date": result_diff["last_log_date"],
            "last_log_content": result_diff["last_log_content"],
        },
    )

    print(resp['messageId'])


def format_date_from_filename(filename):
    date = f'{filename[0:4]}-{filename[4:6]}-{filename[6:8]} {filename[9:11]}:{filename[11:13]}:{filename[13:15]}'
    return date


def check_diff_with_last_log():
    files = os.listdir('logs')
    files.sort()

    if len(files) > 1:
        last_log = files[-2]
        current_log = files[-1]
        current_log_date = format_date_from_filename(current_log)
        last_log_date = format_date_from_filename(last_log)
        
        with open(f'logs/{last_log}', 'r', encoding='utf-8') as f:
            last_log_content = f.read()
        with open(f'logs/{current_log}', 'r', encoding='utf-8') as f:
            current_log_content = f.read()
        if last_log_content != current_log_content:
            print('There are changes from last log')
            print(f'{current_log_date}: {current_log_content}\n')
            print(f'{last_log_date}: {last_log_content}')

            return {
                "current_log_date": current_log_date,
                "current_log_content": current_log_content,
                "last_log_date": last_log_date,
                "last_log_content": last_log_content,
            }
        else:
            print('No changes')
            print(f'{current_log_date}: {current_log_content}')
    else:
        pass


def save_log():
    try:
        response = requests.get(HOME_URL)
        if response.status_code == 200:
            home = response.content.decode('utf-8')
            parsed = html.fromstring(home)
            section_to_watch = parsed.xpath(XPATH_SECTION_TO_WATCH)[0]
            section_to_watch = section_to_watch.strip()

            if not os.path.isdir('logs'):
                os.makedirs('logs')

            now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(f'logs/{now}.txt', 'w', encoding='utf-8') as f:
                f.write(section_to_watch)
        else:
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)


def run():
    save_log()
    result_diff = check_diff_with_last_log()
    if (result_diff != None):
        send_mail(result_diff)


if __name__ == '__main__':
    run()
